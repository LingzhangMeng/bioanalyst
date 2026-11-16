# 03 — Experimental design and statistical feasibility (S3 / **G2 HARD GATE**)

Design comes before method. A method chosen before the design is understood is a guess with a
citation attached. Output of this state: `Analysis_Plan.md` §3–6, containing a design statement,
confounder list, model specification, multiplicity plan, and a feasibility verdict.

---

## 3.1 Design taxonomy → the questions that decide the method

| Design | Signature in the metadata | Model shape | Specific trap |
|---|---|---|---|
| Case–control, unpaired | one sample per donor per group | `~ group + covariates` | imbalance on age/sex/stage |
| Paired (same donor, two conditions) | same `patient_id` in two groups | `~ patient + group` or random effect | ignored pairing → power loss, sometimes sign flip |
| Longitudinal / repeated measures | `timepoint` per donor | `~ group * time + (1|donor)`, or spline | treating timepoints as replicates |
| Intervention / treatment arm | treated vs untreated, pre/post | `~ treatment + time + treatment:time` | baseline drift mistaken for effect |
| Nested (cells in donors; sections in patients) | many units per donor | mixed model / pseudobulk | pseudo-replication (the classic scRNA error) |
| Cross-sectional survey of tissue | many donors, one tissue | `~ group + composition covariate` | tissue-composition confounding |
| Dose–response | ≥3 doses | trend test / spline, not pairwise-only | multiple pairwise tests instead of trend |
| Multi-centre | `centre` populated | `~ group + centre + (1|centre)` | centre × group confounded |
| Case-only (subtype comparison) | no healthy control | within-disease contrasts only | over-generalising to disease-vs-health |

**Independence audit** — answer for every dataset before modelling:
Are replicates independent biological units? Are there repeated measures? Are samples nested in
patients/centres/plates? Are there technical replicates still present (must collapse)? Is any
group a mixture of compartments (tumour + adjacent normal)?

---

## 3.2 Confounders and identifiability

Candidate covariates: age, sex, disease stage/subtype, treatment history, comorbidity,
smoking/exposure, tissue composition (purity, immune/stromal fraction), collection centre,
collection period, sequencing batch, library prep, platform, read depth, RNA integrity.

Rules:
1. **Do not include every available covariate.** Judge: biological relevance, completeness
   (missingness), n, collinearity (VIF), and model identifiability. A model that cannot be fit
   is not "adjusted".
2. **Fully confounded variable** (e.g. batch identical to group; sex identical to group): state
   plainly that its effect is **not estimable** and that the group effect absorbs it. Do not
   "adjust" for it — that removes the effect you are testing.
3. **Never adjust for a mediator** (e.g. adjusting for immune infiltration when infiltration is
   the hypothesised mechanism) — that answers a different question; report it as a separate
   analysis and say which is which.
4. **Never adjust for a collider**; do not select covariates by stepwise P values.
5. Report the missingness of every covariate carried into the model, and what the model does
   with incomplete rows (complete-case vs imputation) — silently dropping donors is a scope change.

---

## 3.3 Power and feasibility

Before modelling, judge whether the data can support the intended claim:

- n per group, after collapsing technical replicates and excluding failed samples;
- expected effect size from the literature or a pilot; if unknown, state the minimum effect
  detectable at the planned n and α;
- dispersion/variance structure (bulk RNA-seq needs realistic dispersion; scRNA pseudobulk needs
  donor-level variance);
- number of covariates relative to n (rule of thumb: events-per-variable ≥10 for regression;
  for GLMs keep the model simpler than the design suggests);
- multiplicity burden (number of tested features and contrasts).

**Verdict language** to use verbatim when underpowered: *"With n = 3 vs 3 this design can detect
only large effects; results are hypothesis-generating and cannot support a biomarker claim."*
Never rescue an underpowered design by lowering the significance threshold, pooling groups, or
switching to a more permissive test.

---

## 3.4 Multiplicity

| Situation | Default | Notes |
|---|---|---|
| Genome-wide DE (bulk) | BH FDR 0.05 (+ lfcShrink) | report raw and adjusted P; state the FDR used |
| scRNA marker detection | BH within comparison, plus effect-size floor (log2FC ≥ 0.25–0.5) | P values are near-meaningless at high n; effect size governs |
| Enrichment over gene sets | BH over tested sets; state the background universe | universe error is a common inflation |
| Many clinical endpoints | pre-specify primary; correct secondaries (BH/Holm) | never pick the significant endpoint |
| Subgroup analyses | label exploratory; correct or state as hypothesis | "significant in males only" needs a formal interaction test |
| ML hyperparameter search | nested CV; report optimism-corrected performance | tuning on test set = leakage |

Also report **effect sizes with confidence intervals** wherever reported P values appear — a
significant 1.05-fold change and a significant 4-fold change are different scientific claims.

---

## 3.5 Batch: covariate, correction, or abort

Decide in this order (details in `04_quality_control.md` §4.4):

1. Is there a batch variable, and is it associated with the data structure? (PCA/ kBET / PVCA /
   variance partition)
2. Is batch **confounded** with group? → if yes, the group effect is not separable: abort the
   cross-batch comparison or analyse within batch and say so.
3. Is batch balanced within group? → include as covariate in the model (preferred; keeps biology).
4. Only if batch dominates and is balanced-and-uninformative → consider correction (ComBat/
   Harmony), and **never** feed corrected values into a DE test that expects counts.
5. Document the decision and run the headline finding with and without correction (sensitivity).

---

## 3.6 Model specification block (required in `Analysis_Plan.md`)

Write this out explicitly — prose, not vibes:

```
Unit of inference:      biological sample (donor × condition)
Response:               raw counts (integer, verified) / log2 intensity / protein abundance (log2 LFQ)
Model:                  ~ group + sex + age + batch        (DESeq2 / limma-voom)
Random effects:         (1|patient)  [paired design]
Primary contrast:       disease - control  (Wald test)
Multiplicity:           BH FDR 0.05 across all genes; effect-size floor |log2FC| >= 0.5
Secondary analyses:     exploratory, labelled as such
Assumptions:            counts ~ NB; independence of samples; no group×batch interaction
Known violations:       batch partially confounded with sex (state the consequence)
Discovery/validation:   GSE##### discovery; GSE#####/GSE##### validation (independent cohorts)
Pre-specified exclusions: samples failing prespecified QC only
```

Then a one-paragraph **feasibility verdict** and the list of analyses you will *not* run and why.

---

## 3.7 G2 pass criteria

- Design type named; unit of inference named; n per group stated (biological, post-collapse)
- Model written with its assumptions; identifiability issues named
- Multiplicity strategy named; effect-size threshold named
- Discovery vs validation datasets named (or "validation impossible because …")
- Feasibility verdict present, including what the data cannot support
- `bap.py gate <project> --gate g2` passes (checks `Analysis_Plan.md` contains the statistical
  plan, model and feasibility sections)

Only after G2 may `06_Analysis/` be populated with hypothesis tests.
