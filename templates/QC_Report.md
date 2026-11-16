# QC Report — <project / dataset>

State **S4**. Every threshold here was pre-specified in `Analysis_Plan.md` §4.6 and applied
identically to all groups.

- QC date: <YYYY-MM-DD> · Script: `Scripts/01_qc.*` · Log: `Logs/01_qc_<timestamp>.log`
- Samples in: <n> → after QC: <n> (excluded: <n>)

---

## 1. Pre-specified criteria

| Metric | Threshold | Applies to | Rationale |
|---|---|---|---|
| detected genes (≥1 count) | <≥ 12,000> | bulk | below this, library complexity is inadequate |
| mitochondrial % | <≤ 20%> | bulk / scRNA | high fraction indicates degradation / stressed cells |
| library size | <within Group median ± 3 SD> | all | extreme depth distorts normalisation |
| correlation with group median | <≥ 0.85> | all | outlier / mislabelled sample |
| doublet score | <scDblFinder threshold per sample> | scRNA | doublets form fake populations |
| cells per sample | <≥ 500> | scRNA | unstable per-sample estimates below this |

## 2. Per-sample summary

Table: `05_QC/Sample_QC.tsv` (one row per sample, all metrics + `quality_flag`).
Figures: `05_QC/Figures/` — violin/box per metric coloured by group; PCA coloured by group and by
batch; correlation heatmap with annotations.

| Sample | Group | Detected genes | Mito % | Library size | Correlation to group median | Flag |
|---|---|---|---|---|---|---|
| <S01> | <control> | <…> | <…> | <…> | <…> | pass |

## 3. Exclusions

| Sample | Rule triggered | Measured values | Evidence | Effect on primary contrast |
|---|---|---|---|---|
| <S07> | <mapping < 30% and cor < 0.6> | <…> | <…> | <n> genes change FDR status; headline genes unchanged |

If no exclusions: state "none" and show the QC distribution so the reader can verify nothing was
quietly dropped. Excluded samples remain in `Sample_Annotation.csv` with `quality_flag` set.

## 4. Identity checks

- Sex-chromosome expression vs annotated sex: <n concordant / n discordant — escalated>
- Near-duplicate pairs (r > 0.999): <n — collapsed / escalated>
- Samples clustering with the wrong group: <n — investigated at G1>

## 5. Batch assessment

- Method: <PCA + PVCA / kBET / variancePartition>
- Variance shares: group <…%> · donor <…%> · batch <…%> · residual <…%>
- Batch × group table: <balanced / partially / fully confounded>
- **Decision:** <no action / batch as covariate / covariate + sensitivity with correction / abort>
- Justification: <…>
- If corrected: method, parameters, and confirmation that group separation was not created by the
  correction. Corrected values were NOT used as DE input.

## 6. Adequacy for the planned analysis

- Enough depth / cells / events per group? <yes/no + numbers>
- Enough biological replicates after collapse? <n per group>
- Any group now too small to test? <…>

## 7. Limitations carried forward

1. <…>
2. <…>

## 8. G-checkpoint statement

QC checkpoint: <PASS / PASS-WITH-CAVEATS>. Proceeding to `06_Analysis/` under the frozen plan from
`Analysis_Plan.md` §4. Any deviation from the plan must be recorded here and in the final report.
