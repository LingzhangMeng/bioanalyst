# 17 — Copy-paste recipes

Small, correct, dependency-light snippets for the checks this protocol requires. Adapt paths; keep
the logic. R and Python where both are plausible.

---

## 1. Preflight: do the matrix and the metadata actually match?

R

```r
preflight <- function(counts, meta, sample_col = "sample_id", group_col = "group") {
  stopifnot(is.matrix(counts) || is.data.frame(counts))
  m_samples <- colnames(counts); a_samples <- meta[[sample_col]]
  dup <- a_samples[duplicated(a_samples)]
  miss_a <- setdiff(m_samples, a_samples); miss_m <- setdiff(a_samples, m_samples)
  num <- if (is.matrix(counts)) counts else as.matrix(counts[, m_samples, drop = FALSE])
  is_int <- all(abs(num - round(num)) < 1e-8, na.rm = TRUE)
  list(n_features = nrow(num), n_samples = ncol(num),
       duplicated_annotation_ids = dup,
       in_matrix_not_metadata = miss_a, in_metadata_not_matrix = miss_m,
       counts_integer = is_int, negatives = any(num < 0, na.rm = TRUE),
       na_total = sum(is.na(num)),
       group_sizes = table(meta[[group_col]]))
}
# stop if duplicated_annotation_ids, miss_a or miss_m are non-empty, or counts_integer is FALSE
```

Python

```python
def preflight(adata, meta, sample_col="sample_id", group_col="group"):
    import numpy as np, pandas as pd
    m = list(adata.obs_names); a = list(meta[sample_col].astype(str))
    X = adata.X[:50].toarray() if hasattr(adata.X, "toarray") else np.asarray(adata.X[:50])
    return {
        "n_obs": adata.n_obs, "n_vars": adata.n_vars,
        "duplicated_annotation_ids": [s for s in set(a) if a.count(s) > 1],
        "in_matrix_not_metadata": sorted(set(m) - set(a)),
        "in_metadata_not_matrix": sorted(set(a) - set(m)),
        "counts_integer": bool(np.allclose(X, np.round(X), atol=1e-8)),
        "negatives": bool((X < 0).any()),
        "group_sizes": meta[group_col].value_counts().to_dict(),
    }
```

---

## 2. Annotation table QA (also `scripts/bap.py check-annotation`)

```r
qa_annotation <- function(meta, group_col = "group", batch_col = "batch", amb_col = "ambiguity_flag") {
  stopifnot(!"sample_id" %in% duplicated(meta$sample_id))
  cnt <- table(meta[[group_col]])
  bad <- if (amb_col %in% names(meta)) which(toupper(as.character(meta[[amb_col]])) %in% c("1","TRUE","YES","Y","?")) else integer(0)
  confounded <- if (batch_col %in% names(meta)) {
    tab <- table(meta[[batch_col]], meta[[group_col]])
    rownames(tab)[apply(tab > 0, 1, sum) == 1]
  } else character(0)
  list(group_sizes = cnt, min_group = min(cnt), ambiguous_rows = bad,
       batches_with_single_group = confounded)
}
```

Interpretation: `batches_with_single_group` non-empty and covering all samples ⇒ batch is confounded
with group ⇒ the group effect is not estimable (`03` §3.2, `04` §4.4).

---

## 3. Count guard before DESeq2/edgeR

```r
assert_counts <- function(m) {
  num <- as.matrix(m)
  if (any(num < 0, na.rm = TRUE)) stop("negative values: not a count matrix")
  if (!all(abs(num - round(num)) < 1e-8, na.rm = TRUE))
    stop("non-integer values: TPM/FPKM/normalised data must NOT be given to DESeq2/edgeR — ",
         "use limma(-voom/-trend) or re-quantify from raw reads")
  if (any(is.na(num))) stop("NA values present: handle explicitly")
  invisible(TRUE)
}
```

---

## 4. Worker sizing (one level of parallelism, BLAS pinned)

```r
bap_workers <- function(heavy = TRUE, ram_gib = NULL, peak_gib_per_worker = NULL) {
  n_phys <- parallel::detectCores(logical = FALSE)
  w <- if (heavy) n_phys else min(2L * n_phys, parallel::detectCores(logical = TRUE))
  if (!is.null(ram_gib) && !is.null(peak_gib_per_worker))
    w <- min(w, floor(ram_gib * 0.8 / peak_gib_per_worker))
  Sys.setenv(OMP_NUM_THREADS = "1", OPENBLAS_NUM_THREADS = "1", MKL_NUM_THREADS = "1")
  if (requireNamespace("RhpcBLASctl", quietly = TRUE)) RhpcBLASctl::blas_set_num_threads(1L)
  max(1L, as.integer(w))
}
future::plan(future::multicore, workers = bap_workers(heavy = TRUE))
```

```python
import os
def bap_workers(heavy=True, ram_gib=None, peak_gib_per_worker=None):
    for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ.setdefault(v, "1")
    logical = len(os.sched_getaffinity(0))
    phys = max(1, logical // 2)
    w = phys if heavy else min(logical, 2 * phys)
    if ram_gib and peak_gib_per_worker:
        w = min(w, int(ram_gib * 0.8 // peak_gib_per_worker))
    return max(1, w)
```

---

## 5. Pseudobulk for cell-type-specific DE (the unit-of-inference fix)

```r
# counts: genes x cells; sce$sample, sce$cell_type; one column per (sample, cell_type)
make_pseudobulk <- function(counts, cell_type, sample, min_cells = 10) {
  key <- paste(sample, cell_type, sep = "__")
  keep <- names(which(table(key) >= min_cells))
  agg <- sapply(keep, function(k) Matrix::rowSums(counts[, key == k, drop = FALSE]))
  list(pb = as.matrix(agg),
       meta = data.frame(pb_id = keep,
                         sample = sub("__.*$", "", keep),
                         cell_type = sub("^.*__", "", keep)))
}
# then: DESeqDataSetFromMatrix(pb, meta, ~ group + batch) per cell_type, with one row per sample
```

Report, for every pseudobulk test: donors per group, cells per donor (median), and the `min_cells`
threshold used.

---

## 6. Batch association, quantified not eyeballed

```r
assess_batch <- function(vsd_mat, batch, group) {
  pc  <- prcomp(t(vsd_mat), scale. = TRUE)$x[, 1:5]
  aov_b <- sapply(1:5, function(i) summary(aov(pc[, i] ~ batch))[[1]][["Pr(>F)"]][1])
  aov_g <- sapply(1:5, function(i) summary(aov(pc[, i] ~ group))[[1]][["Pr(>F)"]][1])
  inci  <- table(batch, group)
  list(pc_vs_batch = aov_b, pc_vs_group = aov_g,
       fully_confounded = all(apply(inci > 0, 1, sum) == 1) || all(apply(inci > 0, 2, sum) == 1))
}
```

Decision: not associated → nothing; balanced+small → covariate; balanced+dominant → covariate +
sensitivity; confounded → abort/within-batch (`04` §4.4).

---

## 7. Sample-identity check independent of filenames

```r
# sex concordance: annotated sex vs expression of XIST (X) and RPS4Y1/DDX3Y (Y)
sex_check <- function(norm_mat, meta, sex_col = "sex") {
  g <- intersect(c("XIST", "RPS4Y1", "DDX3Y"), rownames(norm_mat))
  if (length(g) < 2) return("markers unavailable — use genotype/SNP fingerprint instead")
  s <- colMeans(norm_mat[g, , drop = FALSE])
  data.frame(sample = colnames(norm_mat), inferred = ifelse(s > median(s), "M_marker_high", "F_marker_high"),
             annotated = meta[[sex_col]][match(colnames(norm_mat), meta$sample_id)])
}
```

A mismatch is a hard G1 escalation: it often means a sample swap, not a mislabelled sex column.

---

## 8. Correlation / duplicate detection

```r
cor_mat <- cor(norm_mat, method = "pearson")
diag(cor_mat) <- NA
flag_pairs <- which(cor_mat > 0.999, arr.ind = TRUE)   # near-duplicates -> collapse or escalate
hclust_ari <- function(cl1, cl2) { tab <- table(cl1, cl2); n <- sum(tab)
  sum(choose(tab, 2)) - sum(choose(rowSums(tab), 2)) * sum(choose(colSums(tab), 2)) / choose(n, 2) }
```

High correlation across *different groups* is the strongest single sign of mislabelling.

---

## 9. Effect size + CI for a group comparison (report both, always)

```r
report_effect <- function(x, y) {
  d  <- mean(x, na.rm = TRUE) - mean(y, na.rm = TRUE)
  se <- sqrt(var(x, na.rm = TRUE)/sum(!is.na(x)) + var(y, na.rm = TRUE)/sum(!is.na(y)))
  c(diff = d, ci_lo = d - 1.96*se, ci_hi = d + 1.96*se,
    n_x = sum(!is.na(x)), n_y = sum(!is.na(y)),
    p = t.test(x, y)$p.value)
}
```

For DE results, prefer the model's shrunken log2FC + SE, and report `padj` — never a bare `p`.

---

## 10. Dataset discovery (record the query and the date)

```bash
# GEO series search (E-utilities), record hits and date
q='(lupus nephritis[All Fields]) AND (single cell[All Fields]) AND (gse[Entry Type])'
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&retmode=json&retmax=50&term=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$q")" \
  | python3 -c "import json,sys; d=json.load(sys.stdin)['esearchresult']; print(d['count']); print('\n'.join(d['idlist']))"
```

```r
# R: GEO metadata + sample characteristics
gse  <- GEOquery::getGEO("GSE######", GSEMatrix = TRUE, getGPL = FALSE)
pdat <- Biobase::pData(gse[[1]])          # group labels live here — cross-check, don't trust alone
```

```python
# Python: series metadata without downloading matrices
import GEOparse
gse = GEOparse.get_GEO("GSE######", destdir="01_Dataset_Discovery/GEO")
gse.phenotype_data.head()
# SRA runs for a BioProject: pysradb
# from pysradb.sraweb import SRAweb; SRAweb().df = SRAweb().fetch_sra_runinfo("PRJNA######")
```

Provenance record: query string, date, hit count, accessions selected and rejected with reasons.

---

## 11. Figure saving that survives Linux graphics stacks

```r
p <- ggplot2::ggplot(df, ggplot2::aes(g, v)) + ggplot2::geom_violin()
print(p)                                     # show before save
pdf("09_Figures/Figure_1/01_violin.pdf", width = 3.5, height = 3)
print(p); dev.off()
jpeg("09_Figures/Figure_1/01_violin.jpeg", width = 3.5, height = 3, units = "in",
     res = 300, quality = 95, bg = "white")
print(p); dev.off()
```

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.close("all")
fig, ax = plt.subplots(figsize=(3.5, 3))
fig.savefig("09_Figures/Figure_1/01_violin.pdf")
fig.savefig("09_Figures/Figure_1/01_violin.jpeg", dpi=300, facecolor="white", format="jpeg")
```

---

## 12. Session/environment record

```bash
Rscript scripts/env_capture.R   > /dev/null && cat Environment/env_R.txt
python3 scripts/env_capture.py  > /dev/null && cat Environment/env_python.txt
```

Both scripts also print the recommended worker count for this machine, so the parallel decision in
each script header is reproducible.

---

## 13. Model-ladder sensitivity (one table, no fishing)

```r
# run the same contrast under several defensible models; report all results
models <- list(
  m1 = ~ group,
  m2 = ~ group + batch,
  m3 = ~ group + batch + sex + age,
  m4 = ~ patient + group            # only when paired
)
lapply(models, function(f) {
  dds <- DESeq2::DESeqDataSetFromMatrix(counts, meta, design = f)
  DESeq2::results(DESeq2::DESeq(dds), contrast = c("group", "disease", "control"))
})
```

Report the range of log2FC and FDR across models for the headline genes — that range *is* the
stability statement (`12`).
