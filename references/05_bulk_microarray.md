# 05 — Bulk RNA-seq and microarray (S5)

Applies to: bulk polyA/total RNA-seq, 3′-tag counting (QuantSeq, TaqMan arrays), microarray
(one-/two-colour), and derived matrices (counts, TPM, FPKM, log-intensity). Covers preprocessing
verification, normalisation, differential expression, and the inputs enrichment analyses inherit.

---

## 5.1 Verify before you normalise

| Check | Pass condition | Failure mode prevented |
|---|---|---|
| Counts are integers | `all(x == round(x))`, `min(x) >= 0` | DESeq2 on TPM/FPKM (the single most common method error) |
| No negative or NA values in the count matrix | 0 negatives; NAs handled explicitly | silent model garbage |
| Gene identifiers resolvable | Ensembl/Entrez/Symbol map to the annotation version used | 30% of genes silently dropped |
| Annotation version recorded | e.g. `Ensembl 110 / GRCh38`, array `hgu133plus2.db 3.13.0` | irreproducible enrichment |
| Sample columns match annotation | set equality, verified by script | mis-join → group swap |
| Strandedness consistent | all libraries from the same kit | quantitation bias |
| Gene filtering documented | e.g. keep genes with ≥10 counts in ≥ smallest-group n samples | inflated FDR, unstable dispersion |
| Reference/annotation from raw reprocessing | record fasta/GTF version and aligner version | irreproducible |

**Counts vs alternatives** — pick the route by what you have:

| Input | Correct route | Forbidden |
|---|---|---|
| Raw integer counts | DESeq2, edgeR, limma-voom, or `limma-trend` | — |
| Salmon/kallisto estimated counts | `tximport` with `lengthScaledTPM` + `DESeqDataSetFromTximport`, or voom with offsets | treating TPM as counts |
| TPM/FPKM only (no counts) | limma-trend on `log2(TPM+1)` with a stated limitation, or re-quantify from raw | DESeq2/edgeR directly |
| Microarray log-intensities | limma (`lmFit` → `eBayes`), appropriate array-specific normalisation | any count model |
| Already-normalised matrix of unknown provenance | limma on log scale after checking distribution; document the unknown | pretending it is counts |
| Single-sample / n=1 per group | **no inference possible** — descriptive only | any DE test |

If raw reads exist and the processed matrix is ambiguous, re-quantify. It is cheaper than a
retraction.

---

## 5.2 Normalisation and transformation

**Bulk RNA-seq.** DESeq2's median-of-ratios (default) or edgeR TMM. Check:
- size factors / norm factors are not extreme (e.g. >3-fold spread) — extreme factors often mean a
  few hyper-abundant genes (rRNA, haemoglobin, immunoglobulins) are dominating;
- per-sample distributions align after normalisation;
- RLE / MA plots are centred after normalisation, and any residual structure is not group-aligned.

VST/rlog for exploratory visualisation (PCA, clustering, heatmaps) — **not** as DE input.
Never apply `log2(x+1)` to counts as a substitute for a count model.

**Microarray.** Use the assay-appropriate pipeline (RMA for Affymetrix 3′, neqc for Illumina,
loess/quantile for two-colour) and state the version. Don't mix arrays processed with different
methods; don't re-normalise a published series' processed matrix without saying so.

---

## 5.3 Differential expression

| Method | Use when | Assumptions | Outputs to report |
|---|---|---|---|
| **DESeq2** | raw counts, n≥2 per group, wide dynamic range | NB, independence, shrinkage valid | log2FC (shrunken), SE, Wald/ LRT P, BH FDR, baseMean |
| **edgeR** (QL) | raw counts, small n, high dispersion uncertainty | NB; quasi-likelihood robust | logFC, F, FDR |
| **limma-voom** | raw counts, larger n or complex designs | log-CPM mean-variance weights | logFC, t, FDR |
| **limma-trend** | log-CPM/TPM with stable depth | — | logFC, t, FDR |
| **limma (array)** | microarray intensities | moderated t | logFC, t, FDR |

Requirements for any DE run:
1. Model formula matches the design from `03_statistical_design.md` (paired, batch covariate,
   interaction). Not `~ group` by default.
2. Dispersion estimated with the actual sample size; if n is tiny, say so and use shrinkage-aware
   methods (apeglm/ashr) — and still report the uncertainty.
3. Both raw and adjusted P reported; the FDR threshold stated; effect-size threshold stated.
4. Contrasts written explicitly (e.g. `disease - control`, not "the coefficient").
5. Genomic control sanity: is the P-value histogram flat/appropriate? Is there a global shift that
   suggests a confounder or a failed normalisation?
6. Never filter genes *after* testing to obtain a nicer list; filter genes only by the
   pre-specified expression threshold *before* testing.

**Effect-size sanity.** A 1.02-fold change with FDR 1e-8 at n=200 is a precise measurement of a
biologically trivial difference. Report log2FC and CI, and treat |log2FC| < 0.5 (bulk) as
"quantitatively small" in the interpretation.

---

## 5.4 Alternative splicing, isoforms, allelic imbalance (when relevant)

- Isoform-level: `DESeq2`+`tximport` at transcript level, or `DEXSeq`/`rMATS`/`IRFinder` for
  events; report event-level FDR and junction support (≥20 reads).
- Allelic imbalance: requires genotype; otherwise state that it is not addressed.
- Don't infer isoform switching from gene-level counts.

---

## 5.5 Enrichment inputs (what the interpretation inherits)

- Universe = genes **expressed and tested**, not all annotated genes (a wrong universe is the
  commonest cause of a spurious enrichment).
- Ranking metric: moderated t or shrunken log2FC (state which). For GSEA use the full ranked list,
  not a hard threshold.
- Report database versions (GO release date, KEGG/Reactome version) and access date.
- Separate "genes up" and "genes down" analyses; don't pool them.
- Redundancy: report representative terms plus the full table in `10_Tables/`.
- Label gene-set analysis as **hypothesis-generating** unless a specific set was pre-specified.

---

## 5.6 Bulk checklist

- [ ] Integer counts verified; identifier/annotation versions recorded
- [ ] Model formula matches the design; batch/paired structure handled
- [ ] Shrinkage/uncertainty reported; FDR and effect-size thresholds stated
- [ ] Filtering rules applied before testing and documented
- [ ] VST/rlog used only for visualisation, never as DE input
- [ ] Enrichment universe = tested genes; DB versions recorded
- [ ] Results table in `10_Tables/`, figures in `09_Figures/`, both with the script prefix
- [ ] The headline genes were checked against independent data (S7) before being called biomarkers
