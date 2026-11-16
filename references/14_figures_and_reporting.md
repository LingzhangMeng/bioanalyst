# 14 — Figures, tables and reporting standards (S5/S9)

A figure is an argument, not decoration. Every panel must have a claim it supports, and the claim
must be traceable to a ledger row.

---

## 14.1 Panel specification (before plotting)

For each panel, write one line: `claim → data → statistical test → n → panel type → reader takeaway`.
If you cannot fill all six fields, the panel is not ready. Typical mapping:

| Claim type | Panel | Must show |
|---|---|---|
| Groups differ | violin/box + points, or dot plot | individual samples (not only bars), n, test, effect size |
| Effect size & uncertainty | forest plot / coefficient plot | estimate + 95% CI, reference line |
| Structure | PCA/UMAP | % variance on axes, group labels, **n samples/cells**, what was corrected |
| Composition | stacked bar / per-sample proportions with a test | the statistical test for composition, not just the bar |
| Correlation | scatter + regression CI | ρ/r, P, n, fitted line, axes on the natural scale |
| Survival | KM + risk table | n at risk, events, HR + CI, log-rank or adjusted HR |
| Performance | ROC / calibration / decision curve | AUC + CI, calibration slope, cohort sizes |
| Multi-gene pattern | heatmap | row/column annotation, scaling stated (row z-score?), dendrogram policy, sample IDs |
| Cell population | dot plot + UMAP | marker expression + % expressing, per-sample presence |
| Spatial | section image + domain map | scale bar, section ID, donor ID |

---

## 14.2 Standards

- **Sample-level visibility.** Bulk/cohort panels show points per sample. scRNA panels show the
  number of donors behind each group; a UMAP coloured by condition with 3 donors per group is
  labelled as such.
- **Statistics on the figure.** Name the test, give n, and give exact P or FDR (not `*`/`**` alone)
  in the legend or panel. Corrected P must be labelled as adjusted.
- **Axes honest.** No truncated bars, no log scale without saying so, no dual axes to imply
  correlation, no crop that hides the distribution, no "arbitrary units" without justification.
- **Colour.** Colour-vision-safe palettes (Okabe–Ito, viridis), consistent condition colours across
  every figure in the paper, sequential for magnitude, diverging only around a meaningful zero;
  avoid rainbow for continuous data.
- **Typography.** Monotone, ≥7 pt in final size, consistent fonts, panel letters A/B/C in a corner,
  no gratuitous 3D, no shadows.
- **Resolution and format.** PDF (vector) for line art; 300+ dpi JPEG preview; if a journal demands
  TIFF, provide 300–600 dpi at final size. Save both PDF and JPEG for every figure (see 13.6).
- **Consistency across the paper.** One colour per condition, one ordering, one abbreviation table;
  the same gene set keeps the same visual encoding throughout.
- **Every figure has its data.** `09_Figures/Figure_N/data/` with the exact table plotted.

---

## 14.3 Tables

- One table = one question; the primary results table carries effect size + CI + P/FDR + n.
- Supplementary tables carry the full result (all genes/proteins/features tested), not only the
  significant subset — the reviewer needs the null distribution.
- Column names explicit (`log2FoldChange`, `padj`, `baseMean`); never ship default R column names
  as a final table.
- Round sensibly (P to 3 significant digits, effect sizes to 2–3 decimals); never strip the
  uncertainty.
- Machine-readable tables (CSV/TSV/XLSX) alongside any formatted table in the manuscript.

---

## 14.4 Reporting standards and metadata

Declare the applicable guidelines in `README_project.md` and follow the corresponding checklist:

| Study type | Guideline |
|---|---|
| Animal experiments | ARRIVE 2.0 |
| Human observational studies | STROBE |
| Systematic reviews / meta-analysis | PRISMA 2020 (+ PRISMA-DTA / -P for variants) |
| Tumour marker prognostic studies | REMARK |
| Prediction models | TRIPOD(+AI) |
| Diagnostic accuracy | STARD |
| Microbiome | MIxS / STORMS |
| MS proteomics | MIAPE / journal MCP guidelines + PRIDE deposition |
| Metabolomics | MSI reporting standards + MetaboLights deposition |
| Sequencing data | MINSEQE; submit raw reads (SRA/ENA) and processed matrices (GEO) |
| Single-cell | include cell-level metadata with the object (CELLxGENE schema where possible) |
| Code | Zenodo DOI for the release; licence + README + environment lock |

**Data availability statement** must state: accessions (GEO/SRA/PRIDE/MetaboLights/Zenodo),
what is raw vs processed, what is controlled-access and how to apply, and the code repository with
a version DOI. "Data available on request" is a last resort requiring justification.

---

## 14.5 Reporting the analysis in the manuscript

Methods must contain enough to reproduce the model: dataset accession(s) + version + date, n per
group, preprocessing software + version + parameters, model formula, test, multiplicity method and
threshold, effect-size threshold, software/package versions, seeds, and the validation cohort
accession. Figures must state n and the test. The Discussion must carry the E-grade-appropriate
verbs (`15`).

---

## 14.6 Checklist

- [ ] Every panel has claim/data/test/n/takeaway recorded
- [ ] Sample-level points shown for cohort data; donor counts shown for single-cell data
- [ ] Test names and exact P/FDR values in legends; adjusted P labelled
- [ ] No truncated axes, dual axes, or rainbow colour maps
- [ ] PDF + JPEG for every figure; data behind every figure saved
- [ ] Tables include effect sizes, CIs, and the full (not only significant) feature list in supplements
- [ ] Reporting guideline declared and checklist completed
- [ ] Data/code availability statements with accessions and a code DOI
