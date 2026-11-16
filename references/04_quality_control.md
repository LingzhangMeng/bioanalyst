# 04 — Quality control and batch assessment (S4)

QC exists to protect inference, not to increase significance. Every threshold is pre-specified,
recorded, and applied uniformly across groups. An exclusion that exists only because the result
improved is scientific misconduct, not QC.

Deliverables: `05_QC/Sample_QC.tsv` (one row per sample), `05_QC/QC_Report.md`,
`05_QC/Batch_Effect/Assessment.md`, `05_QC/Figures/`.

---

## 4.1 Universal QC block (all modalities)

| Check | Method | Red flag | Action |
|---|---|---|---|
| File integrity | checksum vs download log, row/column counts, truncated files | mismatch | re-download; never "fix" silently |
| Sample identity | correlation matrix, hierarchical clustering, genotype/SNP concordance, sex-chromosome expression vs annotated sex | duplicate or swapped samples; a "control" clustering with cases | investigate → G1 escalation |
| Duplicate observations | exact and near-duplicate rows/columns | two GSMs = same data | collapse to one biological sample |
| Missing values | per-feature and per-sample missingness | structural (one group all-missing) | distinguish MNAR/MAR (07) |
| Outliers | PCA distance, robust z-score on QC metrics, Mahalanobis | single sample off manifold | justify, never auto-drop |
| Distributions | per-sample density/boxplot before and after normalisation | shifts that track group | confounder, not biology |
| Negative/positive controls | spike-ins, ERCC, control probes (if present) | poor control performance | declare platform limitation |

**Exclusion policy** (write it before looking at results):
1. Pre-specify the rule (e.g. "sample excluded if <5,000 genes detected AND mitochondrial >30%
   AND this is corroborated by low correlation with its own group").
2. Any exclusion requires: `sample_id`, which rule, the measured values, evidence, and the
   consequence for the primary contrast.
3. Excluded samples stay in the annotation table with `quality_flag` set — never deleted from
   the record.
4. Report the analysis with and without exclusions when the exclusion changes a headline result.

---

## 4.2 Modality-specific metrics

### Bulk RNA-seq
library size (post-trim total counts) · mapping rate (uniquely mapped %) · assignment rate to
features · detected genes (≥1 count; typical human bulk ≥12–15k) · rRNA fraction · mitochondrial
fraction (high in bulk suggests degradation) · duplication rate · gene-body coverage uniformity
(3′ bias) · strandedness consistency · library complexity · contamination (xenobiotic/viral/
other-species reads) · insert size · GC bias vs group.
**Also verify: counts are integers; no TPM/FPKM passed as counts** (`17_recipes.md` §3).

### Microarray
background intensity · probe-level detection P · normalisation method (RMA/quantile/loess) and
its effect on distribution · batch/scan date · cross-hybridisation · probe annotation version ·
saturation · negative-control performance · array-quality metrics from the scanner file.

### Single-cell RNA-seq
cells with ≥ 500–1,000 genes (adjust by tissue/depth) · UMI counts per cell · mitochondrial %
(higher thresholds for metabolically active tissue; state it) · haemoglobin/platelet genes for
blood-contaminated solid tissue · doublet rate (10x multiplet rate table; run `scDblFinder` or
`DoubletFinder`, record expected vs observed) · ambient RNA (`SoupX`/`CellBender`; decide once,
apply consistently) · empty droplets (`emptyDrops`) · sample-level cell counts (imbalanced
capture is itself a confounder) · saturation/sequencing depth per sample · reference genome and
`CellRanger` version · batch = 10x channel/library.

### Spatial
spots/cells per section · counts per spot · mitochondrial % · tissue coverage / off-tissue spots ·
image alignment and nuclei segmentation quality (for Xenium/MERFISH: transcript counts per cell,
background probe counts) · section-to-section comparability · number of sections per donor
(the unit of replication).

### Proteomics (MS)
identifications per sample · precursor/intensity distributions · missingness pattern (see 07) ·
carry-over between runs · digest efficiency · contaminant (keratin/trypsin) fraction · retention-
time alignment · injection order vs signal (drift) · normalisation choice · batch = run day/column.
Report identification confidence (FDR at PSM and protein level) and the search-engine/database version.

### Metabolomics
identification level (MSI/confidence level 1–4) · internal-standard recovery · QC-pool (pooled
sample) drift across the run · injection-order effects · normalisation (TIC/median/batch) ·
missingness · annotation source and library version.

### Clinical / survival
follow-up completeness · censoring pattern · event count (not sample count) drives power ·
time-zero definition (diagnosis, surgery, treatment start) · consistency of stage/TNM version ·
immortal-time bias (landmark analysis needed when a post-baseline event defines the group).

---

## 4.3 Is it an outlier, or is it the biology?

Before excluding, test the alternative explanation:

| Observation | Alternative explanation | Test |
|---|---|---|
| One sample far off PC1 | genuine extreme biology (e.g. a severely inflamed sample) | check whether it is extreme on the phenotype of interest; compare with published extremes |
| "Tumour" samples scattered | tissue composition / purity variation | estimate purity/immune content; test association with group |
| One group systematically lower depth | library prep or input amount | normalise; check whether depth correlates with group (if yes → confounder) |
| A cluster of samples separates | batch / plate / run date | batch association test (§4.4) |
| Sample looks like the other group | swap or mislabelling | genotype/sex/marker check → G1 |

Never exclude a *group-level* pattern as "outliers" — that is removing the effect, not cleaning
the data. Report patterns you cannot explain; the reviewer will find them.

---

## 4.4 Batch-effect assessment (assess → decide → document)

**Step 1 — detect.** Variance partition: PVCA / variancePartition / `kBET` / `iSEE` / PCA coloured
by batch, sample correlation heatmap with batch annotation, hierarchical clustering concordance
with batch (ARI). Quantify: fraction of variance attributable to batch vs group vs donor.

**Step 2 — decide** using this table:

| Situation | Decision |
|---|---|
| Batch not associated with data | no action; note it |
| Batch associated, balanced within group, small share of variance | include `batch` as a **covariate** in the model (keeps biology intact) |
| Batch associated, balanced, dominant share | covariate + sensitivity analysis with correction; report both |
| Batch **confounded** with group (every case in one batch) | effect not estimable → abort comparison or analyse within batch only; state plainly |
| Batch = donor/tissue (fully nested) | use a mixed model; do not "correct" |
| Batch unknown / unrecorded | state the limitation; if samples were processed in runs, say so in Limitations |

**Step 3 — correct only when justified.** Covariate adjustment first. Expression-scale correction
(ComBat-seq for counts; Harmony/scVI for embedding only) second. Rules:
- **Never** use batch-corrected (integrated) values as input to a DE test that expects counts.
- Never integrate across modalities or species without an explicit bridge.
- Never correct a batch that carries the biological signal (e.g. "control drawn from another
  cohort" is a design confound, not a technical artefact).
- After correction, verify the group separation survived and that the correction did not create it.

---

## 4.5 QC_Report.md structure

1. Scope and pre-specified thresholds (table)
2. Per-sample QC table and figures (`05_QC/Sample_QC.tsv`, violin/box/scatter with group colouring)
3. Exclusions and their evidence (or "none")
4. Identity checks (sex concordance, correlation, duplicates)
5. Batch assessment: variance shares, decision, and what was adjusted
6. Data adequacy for the planned analysis (enough depth? enough cells? enough events?)
7. Known limitations carried forward

## 4.6 Checklist

- [ ] Thresholds written before inspection and applied to all groups identically
- [ ] Every exclusion has ID + rule + measured values + evidence; none deleted from the record
- [ ] Sample identity verified independently of filenames
- [ ] Batch assessed quantitatively and a decision recorded (covariate / correction / abort)
- [ ] Corrected values never used as DE input
- [ ] Analysis repeated with and without exclusions where a headline result depends on them
- [ ] QC results feed the annotation table (`quality_flag`) rather than living in isolation
