# 08 — Clinical cohorts, survival analysis and machine learning (S5)

Applies to TCGA/GDC, GEO series with follow-up, institutional cohorts, and any predictive model
(diagnostic, prognostic, response). The two dominant failures are **patient-level data leakage**
and **cutoff optimism** — both inflate performance in a way reviewers now actively hunt for.

---

## 8.1 Cohort integrity checks (before any model)

| Check | Rule |
|---|---|
| Patient vs sample ID | one row per patient per relevant timepoint; multiple samples per patient must not be split across train/test |
| Tumour vs normal | primary tumour, adjacent normal, metastatic, recurrent are **different** entities; never pool |
| Time zero | defined identically for all patients (diagnosis date vs surgery vs treatment start); state it |
| Outcome definition | OS / DSS / DFS / PFS / RFS — define event and censoring precisely; verify no immortal time |
| Follow-up | median follow-up reported; censoring rate reported; patients with 0 follow-up flagged |
| Clinical versioning | TNM/AJCC edition, grade system, staging year; inconsistent editions = inconsistency to report |
| Missingness | per-variable missingness; complete-case vs imputation decision stated; n after filtering |
| Treatment | therapy era and regimen are confounders for outcome — include or acknowledge |
| Batch/platform | sequencing centre and platform as covariates in large consortia |

**Immortal-time bias**: if group membership is defined by something that happens after baseline
(response, treatment received, a post-surgery event), the naive comparison is biased. Use a
landmark analysis or time-dependent covariates, and say which was used.

---

## 8.2 Survival analysis

- Kaplan–Meier for description only; the log-rank test for a univariable comparison. Report n at
  risk per interval.
- Cox proportional hazards for multivariable models; **test the PH assumption** (`cox.zph`) and
  report the result — if violated, use stratification, time-varying coefficients, or a
  time-dependent model.
- Report HR with 95% CI, the number of events, and events-per-variable (≥10 preferred).
- Continuous markers: keep them continuous in the primary model (per-SD or per-unit HR). **Dichotomising
  at an "optimal" cutoff fitted on the same cohort is a form of overfitting** — if a cutoff is
  clinically required, pre-specify it, or derive it on a training split and report test performance
  only, or use a cutpoint method with explicit optimism correction and say so.
- Competing risks (e.g. non-cancer death in an elderly cohort): `Fine-Gray`/`cmprsk`, and say why.
- Multiple endpoints: pre-specify the primary; correct secondaries; never report the significant one
  as "the" endpoint.

---

## 8.3 Predictive modelling without leakage

**Non-negotiable sequence**

1. **Split first**, at the patient level (never at the sample or cell level). Report sizes.
2. **Everything learned from data happens inside training folds**: normalisation parameters,
   imputation, feature selection, hyperparameter tuning, threshold choice, class balancing.
3. **Nested cross-validation** when tuning: inner loop selects, outer loop estimates performance.
4. **Report optimism-corrected performance** on held-out data, with 95% CI (bootstrap).
5. Freeze the model, then apply to a genuinely external cohort → that is validation (E2).

**Leakage checklist** — answer all with evidence:

- [ ] Feature selection (DE, univariate screening, LASSO) run **after** the split, inside training only
- [ ] Normalisation/imputation fit on training data only, applied to test
- [ ] No patient appears in both train and test; no technical replicate spans the split
- [ ] Hyperparameters never chosen with test-set information
- [ ] The validation cohort did not influence feature choice, thresholds, or model family
- [ ] Class balancing (SMOTE etc.) applied only to training data
- [ ] Reported metrics are from held-out data, not training
- [ ] Cross-validation folds respect the grouping (patient/centre), i.e. `GroupKFold`

**Reporting**: cohort sizes, splitting strategy, features selected and how, algorithm and version,
hyperparameter grid, AUC (with CI), calibration (calibration plot + Brier score), decision-curve
analysis for clinical utility, and a statement of what the model must not be used for.

**Interpretation of feature importance**: coefficients/importances are association, not mechanism;
correlated features split importance; report stability across resamples (e.g. selection frequency).

---

## 8.4 Clinical associations (non-survival)

- Continuous outcomes: linear model with the covariates from G2; check residual diagnostics.
- Binary outcomes: logistic regression; report OR with CI; avoid the "significant after
  dichotomising a continuous variable" trick without justification.
- Ordinal: proportional-odds model; test the proportional-odds assumption.
- Repeated measures: mixed model, donor random effect.
- Multiple comparisons across clinical variables: pre-specify the primary association.
- Correlation ≠ prediction ≠ causation: three separate statements, three separate evidence grades.

---

## 8.5 Checklist

- [ ] Patient/sample/time-zero/outcome definitions recorded before analysis
- [ ] Event count (not n) reported; events-per-variable checked
- [ ] Cox PH assumption tested and reported; competing risks considered
- [ ] No "optimal cutoff" fitted and evaluated on the same cohort
- [ ] Split performed before any feature selection; nested CV for tuning
- [ ] Leakage checklist fully answered with evidence
- [ ] External validation attempted; performance reported with CI and calibration
- [ ] Model limitations and prohibited uses stated in plain language
