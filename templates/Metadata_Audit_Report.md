# Metadata Audit Report — <dataset / project>

Produced under **G1** of the BAP protocol. This document is the evidence that group assignment is
defensible. If it is incomplete, the gate stays blocked.

- Datasets audited: <GSE…, GSE…>
- Audit date: <YYYY-MM-DD>
- Annotation table: `Sample_Annotation.csv` (<n> rows)
- Machine check: `python3 scripts/bap.py check-annotation 02_Metadata/Sample_Annotation.csv`

---

## 1. Sources consulted

| Source | Retrieved? | What it contributed |
|---|---|---|
| Repository metadata (GSM characteristics / SRA biosample attributes) | <yes/no> | <…> |
| Original publication (methods + supplementary tables) | <yes/no>, DOI <…> | <…> |
| Supplementary sample sheet / series matrix | <yes/no>, file <…> | <…> |
| Data-internal evidence (correlation, sex-chromosome expression, marker profile) | <yes/no> | <…> |

## 2. Final group assignment

| Group | n samples | n donors | Biological replicates | Technical replicates | Definition used |
|---|---|---|---|---|---|
| <control> | <…> | <…> | <…> | <…> | <…> |
| <disease> | <…> | <…> | <…> | <…> | <…> |

## 3. The ten verification questions

1. **Control / disease / treatment samples:** <lists or counts>
2. **Subgroups** (stage, subtype, responder, severity): <…>
3. **Paired or unpaired:** <…>; same donor across groups? <yes/no/partial>
4. **Longitudinal:** <n timepoints, interval> — or none
5. **Multiple tissues/cell types per donor:** <…>
6. **Biological replicates per group:** <…>; **technical replicates:** <…> (collapse rule: <sum counts / mean log / none>)
7. **Balance and confounding:** <age/sex/stage balance; variable fully confounded with group = …>
8. **Ambiguous samples:** <n> open, listed in `Ambiguous_Samples.csv`; critical to primary comparison? <yes/no>
9. **Appropriateness of the reference group:** <e.g. "adjacent normal, not healthy donor — interpretation limited to tumour-vs-adjacent contrasts">
10. **Do publication and metadata define groups identically?** <yes/no; if no, which governs and why>

## 4. Conflicts found

| Sample | Field | Conflict | Sources | Resolution |
|---|---|---|---|---|
| <S04> | group | metadata: control; supplement: severe LN | GEO vs S1 | <pending user confirmation> |

*(No conflict may be "resolved" by preference. Unresolved critical conflicts block the analysis.)*

## 5. Confounders and design consequences

| Variable | Association with group | Consequence for the model |
|---|---|---|
| <batch> | <balanced / partial / full> | covariate / sensitivity analysis / **not estimable** |
| <sex> | <…> | <…> |
| <tissue composition> | <…> | <…> |

## 6. Sex / identity check

- Method: <XIST vs RPS4Y1/DDX3Y expression; genotype concordance; none available>
- Result: <n concordant, n discordant — discordant samples escalated>
- Duplicate detection: <n near-duplicate pairs (r > 0.999) — collapsed / escalated>

## 7. Gate statement

- **G1 verdict:** PASS | BLOCKED
- If BLOCKED: blocking question, samples affected, and the consequence — see §4 and the escalation
  payload sent to the user.
- If PASS: the primary contrast is `<group A> vs <group B>`, unit of inference is
  `<biological sample>`, and the design statement carries forward to `Analysis_Plan.md` §4.

Signed: <agent / analyst> · <date>
