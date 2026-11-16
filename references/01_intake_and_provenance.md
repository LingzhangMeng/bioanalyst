# 01 — Intake and dataset provenance (S0–S1)

Purpose: pin the question and the evidence base *before* touching data. Two failure classes are
prevented here — analysing the wrong question, and analysing a dataset that cannot answer it.

---

## 1.1 The twelve intake categories

Establish each; record the answer (or "unknown → asked") in `Analysis_Plan.md` §1–2 and
`Dataset_Inventory.csv`. Do not start work with categories 1–3, 5–6, 9 unresolved.

| # | Category | What must be established | Consequence if skipped |
|---|---|---|---|
| 1 | Research objective | Biological question, hypothesis, expected findings, deliverable | Analysis defines itself after the fact |
| 2 | Sample information | Sample IDs, group assignment, tissue types | Misclassification — the single most common fatal error |
| 3 | Experimental design | Case-control, paired, longitudinal, treatment, dose, crossover | Wrong statistical model |
| 4 | Clinical metadata | Age, sex, stage, treatment, outcome, comorbidity | Confounding invisible |
| 5 | Provenance | GEO/SRA/ArrayExpress/PRIDE/EGA accession, publication DOI | Untraceable, unverifiable |
| 6 | Technology | Bulk RNA-seq, scRNA-seq, spatial, microarray, MS proteomics, metabolomics, methylation, ATAC | Wrong workflow |
| 7 | Technical detail | Platform, read length, depth, library prep, chemistry, batch structure | Systematic bias mistaken for biology |
| 8 | Data quality | Missingness, outliers, low-quality samples, contamination | Unreliable results |
| 9 | Statistical design | Replicates (bio vs tech), n, covariates, multiplicity | Invalid inference |
| 10 | Biological validation | Independent cohorts, known markers, plausibility, pathway prior | Unanchored interpretation |
| 11 | Reproducibility | Software/package versions, parameters, seeds, scripts | Irreproducible |
| 12 | Publication requirements | Figure/table standards, word limits, reporting consortia | Rework at submission |

**Ask, don't invent.** For a vague request ("analyse this dataset, find something interesting"),
the correct first output is a short scoping message with the 5–8 questions that change the
analysis (question, groups, tissue, species, design, deliverable), not a pipeline.

Two clarifications worth asking every time:
- *Exploratory or confirmatory?* Confirmatory needs a pre-specified hypothesis, primary endpoint
  and model; exploratory needs explicit "hypothesis-generating" labelling in every output.
- *What would make you abandon this line?* A negative-result threshold prevents post-hoc
  reframing of noise as a finding.

---

## 1.2 Dataset discovery

Repositories and what they actually hold:

| Repository | Content | Access | Notes |
|---|---|---|---|
| **GEO** | expression (microarray/RNA-seq/scRNA), series/GSM/GSE | open | processed + raw; `GSE` series, `GSM` samples; supplementary files often carry the real annotation |
| **SRA / ENA** | raw reads (fastq/sra), linked to BioProject/BioSample | open | biosample attributes are the ground truth for group |
| **ArrayExpress / BioStudies** | microarray + some sequencing | open | `E-MTAB-*` |
| **TCGA / GDC** | tumour + adjacent normal, clinical, survival | open (controlled subset via dbGaP) | patient vs sample ID distinction is critical |
| **CPTAC** | proteomics (mass spec) with clinical | open/controlled | assay-level missingness |
| **GTEx** | normal tissue reference expression | open (dbGaP for some) | tissue-composition confounds |
| **Human Cell Atlas / CELLxGENE** | curated scRNA atlases | open | use for reference-based annotation |
| **Single Cell Expression Atlas** | curated scRNA | open | harmonised metadata |
| **PRIDE / ProteomeXchange** | MS proteomics | open | `PXD` accession; look for the *search* settings |
| **MetaboLights / Metabolomics Workbench** | metabolomics | open | identification confidence varies wildly |
| **dbGaP / EGA** | controlled-access human data | **authorisation required** | never claim access you do not have |

Discovery mechanics (GEO/SRA) are in `17_recipes.md` §10 (E-utilities/esearch/efetch, `GEOparse`,
`pysradb`, `rentrez`). Record the query, the date, and the number of hits — a search is evidence too.

**Suitability screen** for each candidate, before selection:
species and strain · tissue/cell type match · technology match · group match (are the groups you
need actually present?) · n per group · availability of the comparison you need (control present?
adjacent normal? treatment arm?) · metadata completeness · raw-data availability (needed for
re-processing?) · prior reuse (has this series already been mined for the same claim? then it is
not independent evidence) · licence.

**Never merge datasets before a compatibility assessment.** Fill in the compatibility block:

| Check | Compatible | Borderline | Incompatible |
|---|---|---|---|
| Species / strain | same | — | different (needs orthologue mapping, declare it) |
| Tissue / cell type | same ontology term | related but distinct | different |
| Technology / platform | same assay | cross-platform (bulk vs array; 10x v2 vs v3) | different molecule (RNA vs protein) |
| Library prep / chemistry | same protocol family | different kit | polyA vs total RNA with different depletion |
| Quantification unit | counts / TPM / log-intensity | mixed units (requires explicit bridge) | raw intensities vs counts |
| Group definitions | same definitions | similar clinical criteria | different criteria for "disease" |
| Batch/metadata | harmonisable | partially missing | no batch information at all |

If any row is "Incompatible", integrate with explicit caveats **or** do not integrate — analysis
per cohort with a meta-analytic summary is usually more defensible than forced concatenation.

---

## 1.3 Provenance record (per dataset)

Mandatory fields, one row per dataset in `Dataset_Inventory.csv`
(`templates/Dataset_Inventory.csv`):

`dataset_id · accession · repository · publication_doi · pmid · release_date · version ·
technology · platform · organism · tissue · cell_type · n_samples · groups_available ·
n_per_group · raw_available · processed_available · clinical_fields · licence ·
access_conditions · prior_reuse · suitability_score · limitations`

Persist: the downloaded file names, MD5/SHA of each raw file, download date, and the exact
retrieval command. "I downloaded it from GEO" is not provenance.

**Licensing / ethics.** Check before use: repository terms, whether consent permits the intended
reuse (especially for controlled-access human data), publication-level data-use statements, and
institutional policy for human genomic data. Record the licence in the inventory. Never use
controlled-access data without documented authorisation; never re-identify individuals; never
upload identifiable human data to third-party services.

---

## 1.4 S0/S1 exit criteria

- [ ] Question, hypothesis, primary and secondary outcomes written; exploratory vs confirmatory labelled
- [ ] Deliverable defined (report / figure set / model / manuscript section)
- [ ] ≥1 dataset selected with a completed suitability screen; alternatives recorded with reasons for rejection
- [ ] Provenance fields filled; raw files checksummed; licence recorded
- [ ] `Dataset_Selection_Report.md` states **why this dataset can answer this question** and **what it cannot**
- [ ] Any merge decision documented with the compatibility matrix
- [ ] If a required dataset is inaccessible → report the blocker; do not substitute silently
