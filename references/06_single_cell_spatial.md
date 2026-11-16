# 06 — Single-cell RNA-seq and spatial transcriptomics (S5)

Applies to droplet (10x), plate (Smart-seq), hashed/multiplexed scRNA, and spatial assays
(Visium, Xenium, MERFISH/MERSCOPE, CosMx, Slide-tags). The dominant risk in this modality is
**pseudo-replication**: treating thousands of cells as independent observations turns a 4-donor
comparison into a fake n = 20,000.

---

## 6.1 Pipeline checkpoints before biology

| Stage | Must be recorded | Common defect |
|---|---|---|
| Demultiplexing / counting | CellRanger/STARsolo/alevin version, reference (GENCODE/Ensembl build), chemistry (v2/v3/v3.1/5′), intron handling | mismatched references between samples |
| Sample identity | 10x channel ↔ sample map, hashtag demultiplexing (HTODemux/MULTI-seq) | channels swapped → the whole study inverts |
| Cell calling | `emptyDrops`/CellRanger `--force-cells` decision | air/ambient droplets as cells |
| Ambient RNA | `SoupX`/`CellBender` applied and documented, or explicitly not applied | ambient contamination driving "markers" (e.g. hepatocyte transcripts in immune cells) |
| Doublets | `scDblFinder` per sample (never on the merged object before splitting), expected multiplet rate from loading | doublets forming fake "novel" populations |
| Cell QC | nCount, nFeature, mito %, ribo %, haemoglobin/platelet genes, log-library complexity | a group with systematically fewer genes (depth confound) |
| Sample-level balance | cells per sample, per donor, per group | one donor supplying 70% of a group |
| Normalisation | `SCTransform` vs `LogNormalize` + why | comparing normalised-to-different-total samples |

**Depth is a confounder.** If disease samples were sequenced shallower, gene detection drops and
"loss of markers" is an artefact. Check nFeature/nCount per sample vs group; report; consider
downsampling-based sensitivity analysis.

---

## 6.2 Integration: when, how much, and what it must not destroy

1. **Check first**: are differences biological (donor/condition) or technical (channel/library/
   run)? Use per-sample PCA, `kBET`, variance partition, or `scikit-learn`/`milor`-style assessment.
2. **Prefer the mildest option that removes technical structure**: don't integrate → integrate by
   donor only → Harmony/scVI/CBB-ANCHOR with batch = channel (NOT group).
3. **Never put the condition in the batch variable.** Integrating away the disease effect then
   "finding" it again is circular.
4. **Integration is for embedding/visualisation/annotation transfer, not for DE testing.** DE must
   be run on unintegrated (or count-scale) data with sample-aware statistics (§6.4).
5. Record algorithm + parameters + which layers were replaced; keep the unintegrated object.

---

## 6.3 Cell-type annotation with an evidence ladder

| Level | Evidence | Permitted claim |
|---|---|---|
| L1 | single canonical marker (e.g. CD3E) | "T-cell-like cluster" |
| L2 | multi-marker panel, consistent across clusters and samples | "T cells" |
| L3 | + reference-based label transfer (SingleR/Azimuth/scanvi) agreeing with markers | "CD8 effector memory T cells (reference-consistent)" |
| L4 | + differential expression vs a purified reference, or protein/flow validation | "CD8 TEM cells" as a validated annotation |

Rules: check markers in a dot plot **and** per-sample presence (a cluster driven by one sample is
a sample artefact, not a cell type); report the marker genes in a table; store annotation in
`colData` with the evidence level; never name a population after a disease association you have
not tested; be honest about ambiguous/doublet-contaminated clusters, and about populations whose
markers are ambient (see §6.1).

---

## 6.4 Differential expression and abundance (the unit-of-inference rule)

| Question | Correct method | Never |
|---|---|---|
| Cell-type-specific DE between conditions | **Pseudobulk** per sample × cell type (sum counts) → DESeq2/edgeR with the design from `03` | Wilcoxon on all cells pooled across donors |
| DE when few cells per sample | mixed model on aggregated or per-cell with `(1|sample)`; report cells-per-sample | treating cells as replicates |
| Composition change (does cell type X expand?) | per-sample proportions (or `speckle`/`propeller`/`sccomp`/`scCODA`) with the donor as unit | comparing cluster sizes across samples without normalising to total cells |
| Marker detection for annotation | Wilcoxon/`MAST` within the comparison, with effect-size floor | interpreting P alone |
| Trajectory/pseudotime | `monocle3`/`slingshot`/`scVelo` + statistical test of condition along pseudotime | claiming a temporal mechanism from a snapshot |

Pseudobulk minimum: ≥3 donors per group per cell type, ≥10–20 cells per donor per type (state what
you used). If a cell type appears in only one group, that is **absence**, not a fold change —
report as presence/absence with a caveat, not as an infinite log2FC.

Also report the number of cells and donors behind every DE claim in the figure legend. A claim
from 2 donors is a hypothesis.

---

## 6.5 Copy number, clonality, TCR/BCR (when the question requires it)

`inferCNV`/`CopyKAT` for malignant vs normal epithelium (needs a normal reference and a stated
window/gene-order; a "CNV" heatmap without a reference is decoration); `scRepertoire` for TCR/BCR
clonality (report clonotype definitions and rarefaction); mutation calling from scRNA is
unreliable — say so if asked.

---

## 6.6 Spatial transcriptomics specifics

| Assay | Resolution | Replication trap |
|---|---|---|
| Visium (spots) | ~55 µm, multi-cell spots | spots ≠ cells ≠ patients; deconvolution (cell2location/RCTD) is an estimate |
| Visium HD | 2–8 µm bins | bin-level pseudo-replication again |
| Xenium / CosMx / MERSCOPE | single-cell, probe panel | panel-limited: absence of a transcript ≠ absence of expression |
| Slide-seq / Stereo-seq | high density | segmentation quality drives everything |

Required before biological claims:
1. Section ↔ donor map; **n sections per group** is the replication unit.
2. Image registration and segmentation QC (nuclei counts per cell, transcript counts per cell,
   off-tissue fraction).
3. Spatially variable genes (`SPARK-X`/`nnSVG`/`Moran's I`) — report the method and the FDR.
4. Domain detection (`BayesSpace`/`graphST`/`Banksy`) — report resolution and stability across seeds.
5. Cell-type deconvolution (Visium) or annotation (imaging-based) with the same evidence ladder as §6.3.
6. Cell–cell proximity/communication: label as **spatial co-localisation or inferred signalling**,
   never as demonstrated contact; see `09_cell_cell_communication.md`.
7. Cross-modality check: does the spatial finding agree with the scRNA finding from the same
   tissue? That agreement is the strongest evidence available from these data.

---

## 6.7 scRNA/spatial checklist

- [ ] Counting reference and versions recorded; channel↔sample map verified
- [ ] Ambient RNA and doublet decisions documented (applied or explicitly not applied)
- [ ] Depth per sample vs group checked and reported as a confounder
- [ ] Integration: batch = technical only; unintegrated object retained
- [ ] Annotation carries an evidence level and appears in a marker table
- [ ] Every DE claim is pseudobulk/mixed-model-based with donors and cells reported
- [ ] Composition claims use a proportion-aware test, not raw cluster counts
- [ ] Spatial claims state the replication unit and the deconvolution uncertainty
- [ ] Headline populations tested in independent data (S7) before being called biomarkers
