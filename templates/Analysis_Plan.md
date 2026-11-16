# Analysis Plan — <project name>

> Fill every section. Sections 1–2 gate **G0**; sections 3–6 gate **G2**. Placeholders in `<…>`
> are to be replaced; a section left as a placeholder fails its gate.
> Machine check: `python3 scripts/bap.py gate . --gate g2`

---

## 1. Research question

- **Biological question:** <one sentence, specific and answerable with these data>
- **System / model:** <organism, tissue, cell type, disease or process>
- **Exposure / intervention / independent variable:** <…>
- **Primary outcome:** <the one comparison or quantity the study is built on>
- **Secondary outcomes:** <list, marked exploratory>
- **Mode:** exploratory | hypothesis-driven | validation-oriented *(pick one, and keep the language consistent with it)*
- **Deliverable:** <report / figure set / model / manuscript section>
- **What would falsify the hypothesis:** <a result you would accept as negative>

## 2. Hypothesis

- **Primary hypothesis:** <…>
- **Alternative hypotheses worth testing:** <…>
- **Prior evidence:** <2–4 lines with PMIDs/DOIs you actually retrieved>
- **Expected effect size (for planning):** <… or "unknown — planning for detection of ≥…">

### Datasets

| Role | Accession | Repository | Publication (DOI/PMID) | n | Groups | Notes |
|---|---|---|---|---|---|---|
| discovery | <GSE…> | GEO | <…> | <…> | <…> | <…> |
| validation | <GSE…> | GEO | <…> | <…> | <…> | independent cohort, different institution |
| reference | <…> | <…> | <…> | <…> | — | <atlas / normal control / protein corroboration> |

Full provenance: `01_Dataset_Discovery/Dataset_Inventory.csv`.
Rationale for selection and rejections: `01_Dataset_Discovery/Dataset_Selection_Report.md`.

---

## 3. Sample annotation status

- Annotation table: `02_Metadata/Sample_Annotation.csv` — **<n>** samples, **<n>** donors
- Ambiguities: `02_Metadata/Ambiguous_Samples.csv` — **<0 open>** rows at gate time
- Audit report: `02_Metadata/Metadata_Audit_Report.md`
- **G1 status:** PASS (<date>) | BLOCKED (<reason, awaiting user>)

| Group | n samples | n donors | biological replicates | technical replicates |
|---|---|---|---|---|
| <control> | <…> | <…> | <…> | <…> |
| <disease> | <…> | <…> | <…> | <…> |

---

## 4. Statistical analysis plan

### 4.1 Design

- **Design type:** case–control | paired | longitudinal | intervention | cross-sectional | dose–response | nested | multi-centre
- **Unit of inference:** <biological sample = donor × condition / spot? cell? — must not be a cell, spot, gene or technical replicate>
- **Independence:** <are replicates independent? any repeated measures, nesting in donor/centre/plate?>
- **Discovery vs validation split:** <which dataset is which; the model/signature is frozen before validation is touched>

### 4.2 Model specification

```
Response:            <raw counts | log2 intensity | protein abundance log2 | proportion>
Model:               ~ group + <covariates>
Random effects:      <(1|patient) or none>
Primary contrast:    <disease - control>
Test:                <Wald / LRT / moderated t / Cox / mixed model>
Multiplicity:        <BH FDR 0.05 over all features> + effect-size floor <|log2FC| >= 0.5>
Assumptions:         <NB dispersion; independence; PH; homoscedasticity — as applicable>
Known violations:    <e.g. batch partially confounded with sex — consequence stated>
```

### 4.3 Confounders

| Variable | Available? | Complete? | Included in model? | Rationale |
|---|---|---|---|---|
| age | <yes/no> | <…%> | <yes/no> | <…> |
| sex | | | | |
| stage | | | | |
| treatment | | | | |
| tissue composition / purity | | | | |
| batch | | | | |
| <other> | | | | |

- **Fully confounded with group (effect not estimable):** <name them, or "none">
- **Deliberately excluded and why:** <e.g. mediator — adjusting would remove the effect of interest>

### 4.4 Feasibility verdict

<One paragraph: can this design support the intended claim? State n per group after collapse,
the minimum detectable effect at this n, the covariates the model can afford, and the claims the
data cannot support. If underpowered, say so here in plain words.>

### 4.5 Analyses explicitly NOT run

- <e.g. cell-level Wilcoxon DE (pseudo-replication)>
- <e.g. "optimal" survival cutoff fitted on the evaluation cohort>
- <…>

### 4.6 Pre-specified exclusions and QC thresholds

<Rules written before inspecting results; the QC report will apply them uniformly.>

---

## 5. Analysis pipeline (planned steps)

| # | Step | Script (planned) | Inputs | Outputs | Method / key parameters |
|---|---|---|---|---|---|
| 00 | ingest & checksums | `Scripts/00_ingest.*` | raw | `04_Processed_Data/` | … |
| 01 | QC | `Scripts/01_qc.*` | … | `05_QC/` | … |
| 02 | preprocessing / normalisation | | | | |
| 03 | primary analysis | | | | |
| 04 | (biological, modality-specific) | | | | |
| 05 | interpretation | | | | |
| 06 | validation | | | | |
| 07 | robustness | | | | |
| 08 | figures | | | | |

Parallelisation: <workers, chosen from physical cores and dataset size; one level only; BLAS pinned to 1 per worker>

---

## 6. Reporting and validation plan

- **Reporting guideline:** <ARRIVE / STROBE / REMARK / TRIPOD / PRISMA / MIAPE / MSI / MINSEQE>
- **Validation strategy:** <independent cohort(s) + level of concordance required (direction, effect
  correlation, signature score, AUC retention)>
- **Robustness menu:** <which checks from reference 12 will be run on the headline finding>
- **Figure plan:** <Figure 1 …; each panel's claim>
- **Evidence-grade expectation:** <what the best achievable grade is for the primary claim>

---

## Sign-off

| Gate | Status | Date | Note |
|---|---|---|---|
| G0 intake | <pass/blocked> | | |
| G1 annotation | <pass/blocked> | | |
| G2 design & statistics | <pass/blocked> | | |
| G3 final review | <pass/blocked> | | |
