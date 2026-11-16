# Final Report — <project>

State **S9**. This document must be readable by a scientist who has not seen the working files, and
must let a reviewer check every claim against a file.

---

## 1. Research question and hypothesis
<2–4 sentences: question, system, primary outcome, mode (exploratory/confirmatory). From
`Analysis_Plan.md` §1–2.>

## 2. Datasets and provenance

| Role | Accession | Repository | Publication | n | Groups | Notes |
|---|---|---|---|---|---|---|
| discovery | | | | | | |
| validation | | | | | | |
| reference | | | | | | |

Why these datasets, and what was rejected (`01_Dataset_Discovery/Dataset_Selection_Report.md`):
<2–3 sentences.>

## 3. Sample annotation

- Samples: <n> · donors: <n> · per group: <…>
- Ambiguities found: <n>; resolution: <…>
- Full audit: `02_Metadata/Metadata_Audit_Report.md`
- **Statement:** <"Group assignments were verified against repository metadata, the publication,
  the supplementary sample table and data-internal evidence.">

## 4. Experimental design and statistical plan

- Design: <…>; unit of inference: <biological sample>
- Model: `<formula>`; test: <…>; multiplicity: <BH FDR 0.05>; effect-size threshold: <…>
- Confounders carried: <…>; not estimable: <…>

## 5. Quality control

- Samples in/out: <n>/<n>; exclusions: <n> with reasons
- Batch: <variance share and decision>
- Adequacy: <…>
- Full detail: `05_QC/QC_Report.md`

## 6. Methods (reproducible detail)

For each step: software + version, parameters, and the script that ran it.

| Step | Tool + version | Key parameters | Script | Log |
|---|---|---|---|---|
| preprocessing | | | `Scripts/01_…` | `Logs/…` |
| primary analysis | | | | |
| interpretation | | | | |
| validation | | | | |

Environment: `Environment/env_R.txt`, `Environment/env_python.txt`.

## 7. Main findings (each with its grade)

| # | Claim | Statistic (effect, CI, FDR) | n | Grade | Figure/Table |
|---|---|---|---|---|---|
| F01 | | | | E1 | |
| F02 | | | | E2 | |

Language rule: the verb in this table must match the grade (`15` §15.6). "Associated" at E1;
"replicated" at E2; "corroborated" at E3; "shown to drive" only at E4.

## 8. Biological interpretation
<Per-finding blocks from reference 10: known function, disease role, consistency with literature
(PMIDs retrieved), alternatives, discriminating next test. Explicitly separate: established
knowledge · this dataset · independent datasets · computational hypothesis · requires experiment.>

## 9. Independent validation
<Which findings replicated, which did not, concordance metrics, and the grade changes. If not
possible: why, and what the claims are therefore limited to.>

## 10. Robustness and sensitivity
<Table from `08_Robustness/Robustness_Report.md`: perturbation, baseline, perturbed, conclusion
changed? Summary sentence in plain language.>

## 11. Limitations
<Written by the analyst, naming what could be wrong — including issues no reviewer has raised:
design limits, n, confounding, platform, annotation uncertainty, inference from bulk composition,
absence of protein-level or functional evidence.>

## 12. Reproducibility package
- Scripts run in this order: <list>; README: `README.md`
- Environment lock: <renv.lock / requirements.txt / container>
- Data availability: <accessions; raw vs processed; controlled-access process>
- Code DOI: <Zenodo> · `handoff.md` current: <yes>

## 13. Proposed follow-up experiments
| Finding | Experiment | What it would establish | Grade if positive |
|---|---|---|---|
| F01 | <CRISPR knockdown in primary cells> | causal role | E4 |

## 14. Reviewer scorecard (self-audit)

| Class | Issue | Evidence | Corrective action | Status |
|---|---|---|---|---|
| Critical | <none / …> | | | |
| Major | <…> | | | |
| Minor | <…> | | | |

**Verdict:** scientifically reliable | reliable with important limitations | requires substantial
reanalysis | not sufficiently supported by the available data.

**Strongest claim the data support:** <one sentence.>
**Most likely reviewer objection:** <one sentence, with the mitigation.>

## 15. Evidence-grade distribution
<e.g. "2 findings at E2, 6 at E1, 1 withdrawn; no E3/E4 evidence is available from these data.">
