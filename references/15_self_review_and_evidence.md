# 15 — Independent review and evidence grading (S9)

Two artefacts close a project: a reviewer-grade critique of your own analysis, and a grading table
that constrains every sentence you write. Run this before delivering anything.

---

## 15.1 The reviewer persona

> Act as a strict, independent reviewer for a high-quality biomedical or bioinformatics journal.
> Do not assume the analysis is correct because it completed without computational errors.
> Do not give a favourable assessment to satisfy the researcher.

Evaluate, in this order: research question and novelty · dataset selection and suitability ·
sample annotation accuracy · experimental design · statistical methods · sample size and power ·
quality control · batch management · differential analysis · multiplicity · biological
interpretation · independent validation · robustness · ML methodology and leakage ·
reproducibility · figure/table quality · consistency between results and conclusions.

---

## 15.2 Issue taxonomy (assign every defect a class)

| Class | Meaning | Consequence |
|---|---|---|
| **Critical** | could invalidate the main finding | must be fixed or the claim withdrawn before delivery |
| **Major** | substantially weakens the conclusion | fix, or downgrade the claim and disclose |
| **Minor** | needs clarification/improvement | fix or list as a limitation |

For each issue: `description · scientific rationale · evidence (file/line/figure) · corrective action`.

---

## 15.3 The audit checklist (18 domains)

**Design and data**
1. Is the research question answerable by these data, as posed?
2. Are datasets suitable, correctly cited, and non-overlapping between discovery and validation?
3. Is every sample's group assignment evidenced (four sources), with ambiguous samples escalated rather than guessed?
4. Is the design correctly identified (paired/nested/longitudinal), and is the model consistent with it?

**Statistics**
5. Are biological and technical replicates separated everywhere?
6. Is n adequate; is the model identifiable; are confounders handled (not over-adjusted)?
7. Is multiplicity controlled, with an effect-size threshold and CIs reported?
8. Are method assumptions tested (normality/PH/dispersion/independence) rather than asserted?

**Data handling**
9. Is QC pre-specified, uniform across groups, and are exclusions justified with evidence?
10. Is batch assessed and decided (covariate/correction/abort), with no corrected values used as DE input?
11. Are missing values handled by mechanism (07) rather than by convention?
12. Is the analysis free of leakage (patient-level splits, in-fold feature selection, no test-set tuning)?

**Interpretation**
13. Does every claim's verb match its E-grade?
14. Is enrichment separated from activity; association from mechanism; inference from communication?
15. Is contradicting literature acknowledged? Are references real and retrievable?

**Delivery**
16. Is independent validation attempted — or its absence stated with a reason?
17. Are robustness/sensitivity checks present on the headline finding, and are failures reported?
18. Can a fresh session reproduce every number and figure from `Scripts/` + `Environment/`?

---

## 15.4 Verdict

Conclude with exactly one of:

- **Scientifically reliable** — findings supported; limitations minor.
- **Reliable with important limitations** — main claim holds; named caveats must accompany it.
- **Requires substantial reanalysis** — a Critical/Major defect blocks the claim.
- **Not sufficiently supported by the available data** — the design cannot answer the question.

Then write the two sentences a reviewer would write: the strongest thing the study shows, and the
most likely reason a reviewer would reject it.

---

## 15.5 Evidence grading (E1–E4) — operational form

| Grade | Definition | Evidence required | Permitted verbs |
|---|---|---|---|
| **E1** | Statistically supported in the discovery dataset | effect size, CI, adjusted P, documented design | "was associated with", "was higher in", "is consistent with" |
| **E2** | Reproduced in ≥1 independent dataset/cohort | independent accession, frozen model/signature, concordant direction + effect | "replicated in", "was reproduced in", "consistent across cohorts" |
| **E3** | Supported by multiple evidence types | orthogonal modalities (transcriptome + proteome + clinical + spatial) in comparable samples | "corroborated by", "supported by convergent evidence" |
| **E4** | Supported by independent experimental validation | perturbation/knockout/blocking, protein-level or functional assay | "was shown to drive/regulate", "is required for" |

Mechanics:
- Grade at the **claim** level, not the paper level. One study routinely holds E1, E2 and E4 claims.
- Upgrading requires new evidence, not new prose. Downgrading is mandatory when a robustness check
  or validation fails.
- `Findings_Ledger.csv` is the single source of truth; the abstract, figures, and chat summaries
  must be consistent with it.
- State the grade distribution at the end of the report: *"3 findings at E2, 7 at E1, 1 withdrawn."*

---

## 15.6 Claim-language ladder (copy-paste discipline)

| Grade | ✅ Write | ⛔ Never write |
|---|---|---|
| E1 | "In GSE##### (n=8 vs 6), X expression was higher in disease (log2FC=1.8, FDR=3e-5)." | "X drives disease"; "X is a validated biomarker" |
| E1 (single-cell) | "The X population was enriched among donors with disease (5/6 vs 1/6 donors)." | "X cells expand and cause injury" |
| E1 (CCM) | "Ligand–receptor pairs for X–Y were enriched between populations." | "X signals to Y"; "communication was demonstrated" |
| E1 (pathway) | "The <set> was enriched among upregulated genes (FDR=…)." | "The pathway is activated" |
| E2 | "The association replicated in TCGA-LUAD (HR=1.4, 95% CI 1.1–1.8)." | "independently validated" (without the cohort named) |
| E3 | "Concordant transcriptomic, proteomic and clinical evidence supports a role for X." | "proven mechanism" |
| E4 | "Knockdown of X abolished the phenotype in vivo." | (anything stronger than the experiment) |

Also banned in any register: "significant" as a synonym for "important"; "novel" without a
literature check; "first"; "proves"; "validated" for same-cohort reuse; "biomarker" for an
E1-only association.

---

## 15.7 Final report skeleton (13_Reports/Final_Report.md)

Research question · dataset selection rationale · provenance · sample annotation summary ·
experimental design · QC results · statistical methods · main findings (with grades) ·
biological interpretation · independent validation · robustness · limitations · reproducibility
package · proposed follow-up experiments · reviewer scorecard (Critical/Major/Minor) · verdict ·
evidence-grade distribution.

The limitations section must be written by the analyst, not by the user, and it must name the
things that could be wrong — including the ones no reviewer has spotted yet.
