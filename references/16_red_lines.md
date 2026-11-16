# 16 — Red lines: the forbidden-move catalogue

Every entry is a real failure mode that has produced retractions, irreproducible papers, or silently
wrong analyses. Format: **move → why it is fatal → what to do instead.** When you are tempted, come
back to this file and comply.

---

## 16.1 Data integrity

| # | Never | Why fatal | Instead |
|---|---|---|---|
| 1 | Modify, overwrite, or "clean in place" downloaded data | destroys auditability; the original can never be re-checked | raw read-only in `03_Raw_Data/`, checksummed; derive into `04_Processed_Data/` |
| 2 | Fabricate or interpolate metadata, statistics, citations, or IDs | research misconduct, once detected, invalidates the whole body of work | mark unknown; ask; cite only what you retrieved |
| 3 | Delete samples/cells/genes without a record | invisible selection bias | `quality_flag` + reason + evidence; keep the row |
| 4 | Trust filenames or folder names as biological truth | the commonest source of group inversion | G1 four-source cross-check (`02`) |
| 5 | Reuse controlled-access data without authorisation | legal and ethical violation | document access; never work around it |
| 6 | Upload identifiable human data to third-party services | privacy breach | aggregate/de-identify; check terms first |
| 7 | Report a result you did not compute ("I ran it and got …") | fabrication; destroys trust in everything else | run it, inspect it, quote it; if not run, say "not run" |

## 16.2 Statistics

| # | Never | Why fatal | Instead |
|---|---|---|---|
| 8 | Choose the test after seeing the P value | guarantees significance, destroys validity | pre-specify in `Analysis_Plan.md` |
| 9 | Treat cells/spots/genes/technical replicates as biological replicates | pseudo-replication; can turn n=3 into n=10,000 | pseudobulk or mixed models (`06`) |
| 10 | DESeq2/edgeR on TPM/FPKM/CPM | the model's mean–variance relation is wrong | raw counts (`05`), or limma/voST with a stated limitation |
| 11 | Feed batch-corrected values into a count-based DE test | double correction; distorted dispersion | DE on count scale with batch as covariate |
| 12 | Remove samples because it improves significance | selection on the outcome | pre-specified QC rules only (`04`) |
| 13 | Ignore pairing/nesting | power loss, wrong SEs, sometimes sign flips | encode `patient_id`; mixed model or paired test |
| 14 | Report P without effect size and CI | precision mistaken for importance | report log2FC/HR/mean difference with CI |
| 15 | Skip multiplicity correction "because we focused on one gene" | the gene was chosen after looking | pre-specify the gene or correct |
| 16 | Pool heterogeneous groups to gain n (all stages, all subtypes) | creates a synthetic population that answers no real question | subgroup analysis with interaction tests, labelled exploratory |
| 17 | Dichotomise a continuous variable at the "optimal" cutoff on the same cohort | cutoff optimism inflates performance | pre-specified cutoff, or derive on training split (`08`) |
| 18 | Report training-set performance as validation | overfitting presented as evidence | held-out, patient-level, nested CV |

## 16.3 Inference and interpretation

| # | Never | Why fatal | Instead |
|---|---|---|---|
| 19 | Claim causation from observational transcriptomic/proteomic correlation | evidence class mismatch | E1 verbs: "associated with" (`15`) |
| 20 | Conflate enrichment with pathway activation | membership ≠ activity | TF/activity inference or protein evidence (`10`) |
| 21 | Present inferred ligand–receptor signalling as demonstrated communication | over-claim; common reviewer objection | "candidate/inferred signalling" (`09`) |
| 22 | Call same-cohort reanalysis "independent validation" | circular; the central fraud pattern in AI-assisted papers | independent accession (`11`) |
| 23 | Upgrade an E1 finding to "validated/mechanistic" for narrative convenience | misrepresents evidence | grade per `15`; upgrade only with new evidence |
| 24 | Hide negative or contradictory results | censorship; the reviewer will find them | report with equal prominence |
| 25 | Cite a paper you did not retrieve (from memory or a plausible reconstruction) | fabricated citation = misconduct | retrieve and verify PMID/DOI, or omit |
| 26 | Attach a mechanism from a different tissue/species without qualification | false extrapolation | state the system and the gap |
| 27 | Interpret tissue-composition change as cell-intrinsic change in bulk data | composition confound | adjust or deconvolve; state the assumption |

## 16.4 Machine learning

| # | Never | Why fatal | Instead |
|---|---|---|---|
| 28 | Select features on the full dataset before splitting | leakage; AUC inflated massively | split first, select inside training folds |
| 29 | Let the validation cohort influence feature choice or tuning | leakage via the analyst | freeze the model before touching validation |
| 30 | SMOTE/oversample before splitting | synthetic test samples | balance inside training only |
| 31 | Split at the sample/cell level when patients repeat | same patient in train and test | patient-level split / `GroupKFold` |
| 32 | Report only AUC | discrimination without calibration is not clinical utility | AUC + calibration + decision curve (`14`) |

## 16.5 Execution and reproducibility

| # | Never | Why fatal | Instead |
|---|---|---|---|
| 33 | Claim successful execution without inspecting outputs | silent mis-join, empty tables, unwritten plots | check counts/IDs/files (`13.5`) |
| 34 | Suppress errors/warnings to make a pipeline "pass" | failures become invisible | read them, fix, log them |
| 35 | Hard-code absolute paths, seeds or thresholds inside functions | not reproducible elsewhere | config block at the top, relative paths |
| 36 | Run serially by inertia on a multi-core machine | wasted capacity; slows the whole project | parallelise, one level, sized to hardware (`13.2`) |
| 37 | Nest parallelism (workers × multithreaded BLAS) | oversubscription; often slower than serial | pin BLAS to 1 per worker |
| 38 | Overwrite a previous run's outputs when parameters change | loses the comparison you will need at review | dated/versioned run folders |
| 39 | Ship a figure without its underlying data | unverifiable | `09_Figures/Figure_N/data/` |
| 40 | Deliver without `handoff.md` and a rerun contract | next session restarts from scratch | `13.7` + the `handoff` skill |

---

## 16.6 The three questions that catch most violations

1. **"What is my unit of inference?"** — If the answer is a cell, a spot, a gene, or a technical
   replicate, stop.
2. **"Would this decision have been the same if I had not seen the result?"** — If no, it is
   selection bias.
3. **"What would a hostile reviewer ask first?"** — Answer it in the report before delivery.
