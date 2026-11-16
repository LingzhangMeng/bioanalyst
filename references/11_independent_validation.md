# 11 — Independent validation (S7)

Validation is the only mechanism that converts a computational finding (E1) into reproducible
evidence (E2). It is also the most commonly faked step in AI-assisted bioinformatics: re-running
the same accession, a subset of the same samples, or the same cohort with a different package is
**not** validation.

---

## 11.1 What counts as independent

| Criterion | Independent | Not independent |
|---|---|---|
| Samples | different individuals not in the discovery set | same donors, re-analysed; overlapping GSE/SRA sample sets |
| Institution / cohort | different hospital, country, or consortium | re-download of the same study |
| Time | different collection period | same publication's second figure |
| Technology | same assay from another lab, or a different platform with a stated bridge | same processed matrix, other package |
| Purpose of reuse | second study asking a related question | the study that generated the signature |
| Analysis | signature/model frozen before touching validation data | re-deriving features on the combined data |

**Critical test:** would the validation result have been the same if the discovery data had never
existed? If the model/genes/thresholds were re-selected after seeing validation data, the answer is
no, and the "validation" is circular.

`scripts/bap.py gate` cannot police this — the reviewer in `15` must.

---

## 11.2 Finding validation datasets

Search strategy (record the query + date):
1. GEO/SRA/ArrayExpress by **biological condition + tissue + assay** (not by the discovered gene).
2. Consortium data: TCGA/GDC (other cancer types as a specificity test), CPTAC, GTEx (normal
   reference), HCA/CELLxGENE (single-cell reference), PRIDE for proteomic corroboration.
3. The discovery paper's own "related datasets" / meta-analyses — check for the reuse trap.
4. Literature: a study reporting the same phenotype with raw data available.

For each candidate, fill a validation suitability row:
`accession · publication · organism/strain · tissue/cell type · assay+platform · n per group ·
group definition match · clinical fields available · sample overlap with discovery · raw available ·
verdict (use / use-with-caveat / reject + reason)`.

Reject rather than stretch: a validation set with a different disease definition, different tissue
compartment, or a different species does not validate — it explores.

---

## 11.3 What to validate, and how

| Level | Metric | Pass criterion (state explicitly) |
|---|---|---|
| Gene-level direction | sign concordance of the headline gene set | e.g. ≥70% same direction among genes testable in both |
| Effect size | correlation of log2FC (Spearman/Pearson) | report ρ with CI; ρ>0 with CI excluding 0 |
| Set-level | GSEA/ssGSEA score direction for the pre-specified pathway | same sign, FDR<0.05 |
| Signature score | per-sample score computed with **frozen weights**, group difference | same direction, P<0.05 |
| Biomarker performance | AUC (or HR) in the held-out cohort | report with CI; compare to discovery with optimism correction |
| Association after adjustment | same covariate-adjusted model | same direction, CI excluding null |
| Protein corroboration | IHC/flow/MS abundance | same direction |
| Spatial corroboration | co-localisation of the two populations | proximity beyond random |

Minimum reporting set per validated finding: discovery effect, validation effect, n, direction,
P/FDR, and an explicit statement of **what did not validate**.

---

## 11.4 Concordance that is not validation

Be explicit when the evidence is weaker than validation:
- **Overlap significance only** (hypergeometric overlap of gene lists) — modest support; report it
  as such, with the background set.
- **Same-cohort reanalysis** with a second pipeline — a reproducibility check (valuable!), not
  independent validation. Label it "technical reproducibility".
- **Pan-cancer consistency** — a specificity/consistency analysis; can strengthen or weaken a claim
  but is not an independent cohort for the same disease.
- **Cross-species** (mouse model) — supports plausibility (E3 at best), not human replication.

---

## 11.5 If validation is impossible

Sometimes there is genuinely no second cohort (rare disease, unique tissue, proprietary data).
Then: (a) say so in the abstract-level claims, not only in Limitations; (b) substitute the strongest
available internal evidence — held-out samples, split-half reproducibility, bootstrap stability,
alternative-platform reanalysis, protein-level check — and grade accordingly (E1); (c) downgrade
the verbs in every summary sentence; (d) propose the experiment/dataset that would be needed.

Never let "no validation available" become silence about the absence of validation.

---

## 11.6 Validation_Report.md structure

1. Discovery summary (dataset, n, statistic)
2. Candidate validation datasets with suitability verdicts and rejections
3. Per-finding validation table (discovery → validation, direction, effect, P, verdict)
4. Concordance metrics with CI
5. Findings that failed to validate — reported with the same prominence
6. Grade changes (which findings moved E1→E2, which stayed E1, which were withdrawn)
7. Remaining uncertainty and the experiments that would resolve it

## 11.7 Checklist

- [ ] No sample overlap between discovery and validation (verified by accession/patient IDs)
- [ ] Model/signature/thresholds frozen before touching validation data
- [ ] Suitability verdicts recorded for every candidate, including rejected ones
- [ ] Per-finding concordance reported with effect sizes, direction, and n
- [ ] Failed validations reported, and affected claims downgraded or withdrawn
- [ ] Findings_Ledger.csv grades updated (11 → `15`)
- [ ] Absence of validation stated where applicable, with the reason
