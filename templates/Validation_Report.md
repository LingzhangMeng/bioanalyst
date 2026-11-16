# Validation Report — <project>

State **S7**. Purpose: decide which E1 findings become E2, which stay E1, and which are withdrawn.
The model/signature/thresholds were **frozen before** any validation data were opened.

- Discovery dataset: <GSE…> (<n> vs <n>)
- Freeze date of the signature/model: <YYYY-MM-DD> · file: <path/commit>
- Validation datasets considered: <n> · used: <n> · rejected: <n>

---

## 1. Candidate validation datasets

| Accession | Publication | Organism / tissue | Assay · platform | n per group | Group definition match | Sample overlap with discovery | Verdict |
|---|---|---|---|---|---|---|---|
| <GSE…> | <DOI> | <human kidney> | <bulk RNA-seq> | <12/12> | <same criteria> | <none (patient IDs disjoint)> | use |
| <GSE…> | <DOI> | <mouse kidney> | <microarray> | <8/8> | <model, not patients> | none | use-with-caveat (cross-species) |
| <GSE…> | <DOI> | <human blood> | <bulk> | <20/20> | <different definition> | none | reject — different compartment |

Overlap check method: <accession/GSM comparison; patient ID intersection; genotype concordance>.

## 2. Per-finding validation

| Finding | Discovery effect (CI, FDR, n) | Validation effect (CI, P, n) | Direction concordant? | Verdict | New grade |
|---|---|---|---|---|---|
| <gene X higher in disease> | <log2FC 1.8 (1.4–2.2), FDR 3e-5, 8v6> | <log2FC 1.2, P=0.004, 12v12> | yes | replicated | E2 |
| <population Y enriched> | <+8.2%, P=0.01, 5/6 donors> | <+3.1%, P=0.21, 3/6 donors> | yes | not significant | stays E1 |
| <pathway P> | <FDR 1e-4> | <FDR 0.31> | no | inconsistent | downgraded / withdrawn |

## 3. Concordance metrics

| Level | Metric | Result | Interpretation |
|---|---|---|---|
| Gene-level direction | sign concordance among testable genes | <74% (95% CI …)> | supporting |
| Effect size | Spearman ρ of log2FC | <0.42 (0.25–0.57)> | moderate |
| Signature score | frozen-weight score, group difference | <P=0.008> | replicated |
| Biomarker performance | AUC in validation | <0.71 (0.58–0.84)> | modest; not a classifier |
| Protein corroboration | <IHC / MS direction> | <…> | E3 candidate |

## 4. What did not validate

<Report with the same prominence as successes: which findings failed, and the resulting language
change. Example: "The X–Y axis was not replicated in GSE##### (log2FC 0.1, P=0.6); the manuscript
must therefore describe it as dataset-specific.">

## 5. Grade changes

| Finding | Before | After | Reason |
|---|---|---|---|
| <…> | E1 | E2 | replicated in independent cohort |
| <…> | E1 | withdrawn | failed validation |

Ledger updated: `13_Reports/Findings_Ledger.csv` (<n> rows changed).

## 6. Limitations of the validation

1. <e.g. only one independent cohort; different platform; modest n>
2. <e.g. no protein-level data available>

## 7. If validation was not possible

- Reason: <no independent cohort exists / controlled access / unique tissue>
- Compensating internal evidence: <split-half reproducibility, bootstrap stability, alternative
  platform reanalysis, protein check>
- Consequence for the claims: max grade E1; verbs limited to "associated"; absence of validation
  stated in the abstract-level summary.
