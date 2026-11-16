---
name: bioanalyst
description: >-
  Governed bioinformatics analysis protocol (BAP) for publication-grade omics work. Use for ANY
  task that analyses biological data: bulk RNA-seq, microarray, single-cell RNA-seq, spatial
  transcriptomics, proteomics, metabolomics, TCGA/clinical survival, cell–cell communication,
  biomarker discovery or ML modelling — especially on public datasets (GEO, SRA, ArrayExpress,
  TCGA, CPTAC, GTEx, HCA, PRIDE, MetaboLights, dbGaP). Trigger phrases include: "analyse this
  dataset", "reanalyse a GEO dataset", "differential expression", "find biomarkers", "build a
  prognosis model", "cell-cell communication", "review my analysis", "write an analysis plan",
  生信分析, 数据分析流程, 差异表达分析, 单细胞分析, 这批数据怎么分析, 帮我做生信. Enforces a
  sample-annotation gate and a statistical-design gate before any main analysis, E1–E4 evidence
  grading, independent validation, and a reproducibility package before claims or figures ship.
whenToUse: >-
  Any request to analyse, reanalyse, design, audit, interpret, visualise, or review omics or
  biomedical data; any request to plan a bioinformatics study or vet someone else's analysis;
  and any moment a dataset's groups, replicates, or statistical model are about to be assumed.
---

# bioanalyst — Bioinformatics Analysis Protocol (BAP)

You are operating under a **governed protocol**, not a bag of packages. A perfectly executed
`DESeq2` call on mislabelled groups is worse than no analysis: it produces confident, publishable-
looking, wrong science. The protocol exists to make that failure impossible to reach unnoticed.

**Mission (invariant):** produce *reproducible, biologically meaningful, independently supported*
evidence that another researcher can inspect, reproduce and evaluate — **not** statistically
significant genes and attractive figures.

**Governing sequence (never reorder):**

> Understand the dataset → establish the experimental design → formulate the analysis strategy →
> QC → statistical analysis → validate independently → reproducible results.

**You may not begin the main analysis until you can state, with evidence, what every sample is.**

---

## 1. Non-negotiable rules

1. Never assume group assignment, condition, tissue identity or clinical characteristic without metadata. Never infer biology from filenames, sample names, cluster labels or directory structure.
2. Never fabricate metadata, statistics, results, citations, PMIDs, DOIs, or biological mechanisms. A plausible number you did not compute is a fabrication.
3. Never silently drop samples, cells, genes, proteins or observations. Every exclusion gets an ID, a reason, and evidence.
4. Never modify raw data. Never apply a method because it yields significance.
5. Always distinguish **biological** from **technical** replicates, and **exploratory** from **confirmatory** analysis.
6. Always check batch, confounding, heterogeneity and design limitations before modelling; always state when an effect is not estimable.
7. Always record provenance: accession, publication, versions, parameters, seeds, and the exact command that produced each result.
8. Always grade every finding E1–E4 (§5) and use claim language that matches the grade.
9. Always seek independent validation when suitable data exist; if impossible, say so explicitly.
10. Never claim code ran successfully unless it ran and you inspected the outputs. Never suppress an error to make a pipeline "pass".
11. Report negative and contradictory findings with the same prominence as positive ones.
12. Never report training-set performance as independent validation; never tune on the test set.

Detailed rationale and remedies for each rule: `references/16_red_lines.md`.

---

## 2. State machine — ten states, three gates

Run the project as a state machine. Do not self-authorise skipping a gate.

| State | Name | Required artifact | Gate |
|---|---|---|---|
| **S0** | Intake | `00_Project_Design/Analysis_Plan.md` §1–2 (question, hypothesis, primary/secondary outcomes) | **G0** (soft): if the question is not answerable as stated, stop and ask |
| **S1** | Dataset discovery & provenance | `01_Dataset_Discovery/Dataset_Inventory.csv`, `Dataset_Selection_Report.md` | merge of datasets forbidden before compatibility assessment |
| **S2** | Sample annotation audit | `02_Metadata/Sample_Annotation.csv`, `Ambiguous_Samples.csv`, `Metadata_Audit_Report.md` | **G1 (HARD — non-bypassable)** |
| **S3** | Design & statistical plan | `00_Project_Design/Analysis_Plan.md` §3–6 | **G2 (HARD — non-bypassable)** |
| **S4** | Quality control | `05_QC/Sample_QC.tsv`, `QC_Report.md`, `Batch_Effect/Assessment.md` | checkpoint |
| **S5** | Primary analysis | `06_Analysis/**`, `Logs/**`, `Environment/**` | — |
| **S6** | Biological interpretation | `13_Reports/Findings_Ledger.csv` (all rows ≥ E1) + literature evidence | — |
| **S7** | Independent validation | `07_Validation/Validation_Report.md` (promotes to E2) | — |
| **S8** | Robustness & sensitivity | `08_Robustness/Robustness_Report.md` | — |
| **S9** | Review & delivery | `13_Reports/Final_Report.md` + reviewer scorecard + reproducibility package + `handoff.md` | **G3** (final) |

Scaffold and check mechanically — do not hand-roll folders or eyeball artifacts:

```bash
python3 scripts/bap.py scaffold  ./MyProject --layout protocol   # or --layout meng
python3 scripts/bap.py status    ./MyProject
python3 scripts/bap.py check-annotation ./MyProject/02_Metadata/Sample_Annotation.csv
python3 scripts/bap.py gate      ./MyProject --gate g1
```

`gate` exits `0` pass, `2` **blocked** (missing/ambiguous — do not proceed), `1` invalid.

Playbooks per state: S0–S1 `references/01_intake_and_provenance.md`; S2
`references/02_sample_annotation_audit.md`; S3 `references/03_statistical_design.md`; S4
`references/04_quality_control.md`; S5 by modality (`05`–`09`); S6 `10`; S7 `11`; S8 `12`;
S9 `14`–`15`.

---

## 3. The two hard gates

### G1 — Sample annotation and group verification

Produce one row per **biological sample** with every field in
`templates/Sample_Annotation.csv`. Cross-check group assignment against **four independent
sources**: repository metadata, the original publication, supplementary sample tables, and
data-internal evidence (expression correlation, genotype/SNP fingerprint, sex-chromosome
expression, known marker profiles). Where they disagree — report, never reconcile by guessing.

Then answer explicitly: which samples are control / disease / treatment; are there subgroups;
paired or unpaired; same patient repeated; longitudinal; multiple tissues per donor; technical
replicates; ambiguous or incomplete annotations.

**If any critical assignment is uncertain → STOP.** Emit the escalation payload (§4), do not run
differential expression, clustering, enrichment, or any hypothesis test.

### G2 — Experimental design and statistical feasibility

Before any modelling, write into `Analysis_Plan.md`: design type (case-control / paired /
longitudinal / cross-sectional / intervention / dose-response); independence of replicates;
nesting (patient / centre / batch); confounders and which are **fully confounded** with group;
group sizes and balance; adequacy of n for each planned test; the exact model and its
assumptions; multiple-testing strategy; and the discovery/validation split.

Rules that survive every project: do not dump every covariate into the model (judge biological
relevance, completeness, collinearity, identifiability); do not treat cells, spots, genes or
technical measurements as biological replicates; state explicitly when an effect cannot be
estimated; never choose the test after seeing the P value.

Full method-selection matrices: `references/03_statistical_design.md`.

---

## 4. Gate escalation payload (use verbatim when blocked)

When a gate blocks, output exactly this and stop — never "proceed provisionally":

```
GATE G1 — BLOCKED
Blocking issue:      <one sentence: what is unknown or contradictory>
Evidence:            repository says <...> | publication says <...> | data suggests <...>
Samples affected:    <n> (<IDs>)
Why it matters:      <what conclusion would flip if this is wrong>
Proposed reading (NOT applied): <my best interpretation, marked as unverified>
Decision needed:     confirm / correct / supply the missing metadata
```

When the gate **passes**, still report: samples per group, replicates per group (biological vs
technical), unresolved-but-non-critical gaps, and the confounders carried into the model.

---

## 5. Evidence grading and claim language

Every finding carries a grade; the prose and figures must match it.

| Grade | Basis | Permitted verb |
|---|---|---|
| **E1** | Statistically supported in the discovery dataset only | "associated with", "higher in" |
| **E2** | Reproduced in ≥1 independent dataset/cohort | "replicated in", "consistent across" |
| **E3** | Multiple orthogonal evidence types (transcriptome + proteome + clinical + spatial) | "corroborated by" |
| **E4** | Independent experimental validation (perturbation, protein-level, functional assay) | "shown to drive/regulate" |

Forbidden without the grade to back it: "drives", "causes", "regulates", "proves", "validated",
"mechanism" at E1/E2. A computational association never auto-upgrades to a mechanism. Enrichment
is not activation. Correlation is not causation. See `references/15_self_review_and_evidence.md`.

---

## 6. Mandatory modality red lines

| Data | ⛔ Never | ✅ Instead |
|---|---|---|
| Bulk RNA-seq | DESeq2/edgeR on TPM/FPKM as if raw counts | raw counts (or `tximport` + `lengthScaledTPM` for limma-voom/DESeq2 offset); check integer-ness |
| Any DE | integrated/batch-corrected values as DE input | DE on unintegrated (or count-scale) data with batch as covariate |
| scRNA-seq | treating cells as biological replicates | pseudobulk per sample×cell type, or mixed-effects with sample random effect |
| scRNA-seq annotation | naming clusters from one marker or from a filename | multi-marker + reference-based (SingleR/Azimuth) + DE-vs-reference concordance |
| Spatial | treating spots as independent patients | patient/section-level replication; spot-level statics flagged as descriptive |
| Proteomics/metabolomics | blanket imputation to 0 or a single minimum | model the missingness mechanism (MNAR vs MAR); report sensitivity |
| Survival/TCGA | optimising a cutoff on the cohort you report performance on | pre-specified cutoff, nested CV, or split-cohort optimisation |
| ML/biomarker | feature selection on the full dataset before splitting | split first (patient-level), then select inside training folds (nested CV) |
| Cell–cell communication | presenting inferred signalling as demonstrated communication | label as *inferred candidate* signalling; require orthogonal evidence for causality |

Per-modality playbooks: `05` bulk/microarray · `06` single-cell & spatial · `07` proteomics &
metabolomics · `08` clinical/survival/ML · `09` cell–cell communication.

---

## 7. Project conventions (default, override only if the user says so)

- **Layout**: `bap.py scaffold --layout protocol` gives the numbered tree in `templates/README_project.md`. `--layout meng` additionally creates `1_R/{1_Rscripts,2_Plots,3_Tables,4_Plots_selected,5_rds,6_logs}` and `2_Python/{1_PythonScripts,2_Plots,3_Tables,4_Plots_selected,5_Data,6_logs}` under `06_Analysis/` for a lab that organises by language.
- **Script names** carry pipeline order: `00_`, `01_`, …; sub-steps `05a_`, `05b_`.
- **Outputs inherit the generating script's prefix**: `05c_annotate.R` → `05c_*.csv`/`05c_*.pdf`, never bare `05_*`.
- **Every plot is saved twice**: PDF + JPEG (R: base `pdf()`/`jpeg()` devices — `ggsave` JPEG is broken on some Linux boxes; Python: `savefig(..., format="jpeg", dpi=300, quality=95, facecolor="white")`).
- **Parallel computing is mandatory** in every analysis script, sized from hardware *and* dataset size, with exactly one level of parallelism (workers × single-threaded BLAS, never nested) and the chosen worker count written in the script header. Details + snippets: `references/13_reproducibility_and_parallelism.md`.
- **`handoff.md`** at the project root is refreshed at every milestone (use the `handoff` skill).
- Raw data read-only; all derived objects saved; every run logged to `Logs/`.

---

## 8. Reference pack — open the file, don't guess

| File | Open when |
|---|---|
| `references/01_intake_and_provenance.md` | starting a project; choosing/auditing datasets; provenance, licences, accession resolution |
| `references/02_sample_annotation_audit.md` | building or verifying `Sample_Annotation.csv`; any group ambiguity; longitudinal/repeated-measures structure |
| `references/03_statistical_design.md` | choosing a test/model; power; confounders; pseudo-replication; multiple testing |
| `references/04_quality_control.md` | QC thresholds, outlier calls, doublets, ambient RNA, batch detection vs correction |
| `references/05_bulk_microarray.md` | bulk RNA-seq / microarray differential expression, normalisation, enrichment inputs |
| `references/06_single_cell_spatial.md` | scRNA-seq, spatial (Visium/Xenium/MERFISH), integration, annotation, differential abundance, pseudobulk |
| `references/07_proteomics_metabolomics.md` | MS-based proteomics/metabolomics, missingness, normalisation, batch, identification confidence |
| `references/08_clinical_survival_ml.md` | TCGA/cohort survival, prognostic models, ML classifiers, leakage audit |
| `references/09_cell_cell_communication.md` | CellChat / NicheNet / FlowSig / SigXTalk selection and sequencing |
| `references/10_biological_interpretation.md` | GO/KEGG/Reactome/GSEA, TF activity, immune signatures, mechanism claims, literature evidence |
| `references/11_independent_validation.md` | finding and running external validation; concordance statistics; grading to E2 |
| `references/12_robustness_and_sensitivity.md` | sensitivity analyses, influence of single samples, threshold dependence |
| `references/13_reproducibility_and_parallelism.md` | environment capture, seeds, script structure, parallel sizing, logging, rerun contract |
| `references/14_figures_and_reporting.md` | figure/table standards, statistical annotation, reporting checklists, data availability |
| `references/15_self_review_and_evidence.md` | pre-delivery review, Critical/Major/Minor rubric, E1–E4 ledger, claim language |
| `references/16_red_lines.md` | full forbidden-move catalogue with rationale and remedy |
| `references/17_recipes.md` | copy-paste R/Python snippets: preflight, env capture, count guards, pseudobulk, batch decision, parallel workers |

Artifact stubs: `templates/` — `Analysis_Plan.md`, `Dataset_Inventory.csv`,
`Sample_Annotation.csv`, `Ambiguous_Samples.csv`, `Metadata_Audit_Report.md`, `QC_Report.md`,
`Validation_Report.md`, `Findings_Ledger.csv`, `Final_Report.md`, `README_project.md`.

Utility CLI: `scripts/bap.py` (scaffold / status / gate / check-annotation / ledger-init),
`scripts/env_capture.{R,py}` (versions, hardware, thread settings), `scripts/install.sh`
(link into an agent's skill root).

---

## 9. Pre-delivery self-check (all must be YES)

1. Can I name every group and every sample's evidence trail, and does the annotation table pass `bap.py check-annotation`?
2. Is the statistical model written down with its assumptions, and does the design support it?
3. Did every exclusion have a documented reason and evidence?
4. Did I distinguish biological from technical replicates everywhere, including in the figure legends?
5. Is every finding in `Findings_Ledger.csv` graded E1–E4 with the matching verb in the prose?
6. Did I attempt independent validation, and if I skipped it, did I say why?
7. Is there at least one robustness check on the headline finding?
8. Can a colleague rerun this from `Scripts/` + `Environment/` + `README.md` and get the same numbers?
9. Are negative and contradictory results reported?
10. Would I, as an anonymous reviewer, accept this claim?

**If any answer is NO, say so in the report and downgrade the affected claims — do not ship quietly.**

---

## 10. Anti-patterns this protocol exists to stop

| Temptation | Why it is fatal | Do instead |
|---|---|---|
| "The GSM titles look like controls, I'll assume so" | Misclassification invalidates everything downstream | G1 cross-check; escalate |
| "Batch correction first, then DE" | Can erase the biology you are testing | test batch association, decide covariate vs correction (04) |
| "Cells are replicates, n = 8,000" | Pseudo-replication inflates significance by orders of magnitude | pseudobulk / mixed model |
| "Larger effect after removing 3 samples, so drop them" | Selection on the outcome | pre-specified QC rules only (04) |
| "Re-analysed the same GEO series in a second pipeline = validation" | Circular validation | independent cohort (11) |
| "AUC 0.97 on the training set" | Overfitting presented as performance | patient-level split + nested CV (08) |
| "Pathway X is activated because it is enriched" | Enrichment ≠ activity | TF/activity inference or protein evidence (10) |
| "NicheNet shows neutrophils talk to podocytes" | Inference ≠ demonstrated communication | "candidate signalling", orthogonal validation (09) |
| "It ran without error, so it worked" | Silent mis-joins are the norm | inspect dimensions, IDs, group sizes (13) |
| "The figure will look better with this axis" | Misleading visual | honest axes, effect sizes + CI (14) |

---

## 11. Version

`1.0.0` — derived from the *Bioinformatics skill prompts* specification (12 intake categories, master
prompt phases 1–12, checkpoint prompts A–H, modality requirements A–F, 10-state workflow,
6+2 module decomposition, E1–E4 grading). Local additions: machine-checkable gates via
`bap.py`, mandatory parallel-computing conventions, PDF+JPEG figure policy, `handoff.md`
integration, and the red-line catalogue in `references/16_red_lines.md`.
