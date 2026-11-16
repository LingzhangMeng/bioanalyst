# 02 — Sample annotation audit and group verification (S2 / **G1 HARD GATE**)

This is the highest-leverage file in the pack. Most retracted or irreproducible public-data
papers fail here, not in the statistics. A `DESeq2` run on swapped groups produces beautiful,
confident, publishable nonsense.

**Rule: you may not test a hypothesis until every sample has a defensible group assignment with
a cited source.**

---

## 2.1 Build the annotation table first

One row per **biological sample** (not per file, not per cell, not per lane). Use
`templates/Sample_Annotation.csv`. Required columns:

| Field | Why it is needed | Failure if missing |
|---|---|---|
| `sample_id` | primary key, must match the expression matrix columns exactly | silent mis-join |
| `repository_id` (GSM/ERR/SRR/sample) | provenance of that row | unverifiable |
| `patient_id` / `subject_id` | pairing, repeated measures, leakage control | pseudo-replication, leakage |
| `group` (final assignment) | the variable being tested | — |
| `group_source` (metadata / publication / supplement / inferred-from-data) | auditability | guessing becomes invisible |
| `disease_status`, `disease_subtype`, `stage`, `severity` | phenotype definition | heterogeneous "disease" |
| `treatment_status`, `treatment_detail`, `timepoint` | intervention and longitudinal structure | wrong model |
| `tissue`, `tissue_ontology`, `cell_type` | biology; ontology prevents "tumour vs normal" confusion | mixing compartments |
| `age`, `sex` | standard confounders, and sex-check QC | confounding, sample swap undetected |
| `biological_replicate_id` | the unit of inference | inflated n |
| `technical_replicate_id`, `lane`, `run` | must be collapsed before inference | inflated n |
| `batch` (processing/sequencing/library batch) | confounder or correction decision | batch = signal |
| `platform`, `library_prep`, `chemistry`, `read_length` | technical covariates | platform effects read as biology |
| `quality_flag` | links QC to annotation | ad-hoc exclusions |
| `ambiguity_flag` + `ambiguity_note` | **the gate** | silent guessing |

Non-negotiable: `sample_id` values are identical to the matrix column names (or to
`rownames(colData)`), verified programmatically — `scripts/bap.py check-annotation` and
`17_recipes.md` §1.

---

## 2.2 Four-source cross-check (do all four, not two)

For every group assignment, seek confirmation from:

1. **Repository metadata** — GSM characteristics, `sra` biosample attributes, ENA sample XML.
2. **The primary publication** — sample description table, supplementary Table S1, methods text
   ("n = 6 per group … biopsies from patients with …"), and the figure legends.
3. **Supplementary files / sample sheets** — often contain the only patient-level truth
   (`GSE*_series_matrix`, `*_sample_sheet.csv`, `metadata.xlsx`, `cell_annotation.csv`).
4. **Data-internal evidence** — correlation structure, hierarchical clustering of samples,
   PCA, expressed sex-chromosome genes vs annotated sex, genotype/SNP concordance, presence of
   expected marker genes, library complexity, tumour purity, immune/stromal content.

Record the outcome per sample: `group_source` = which sources agreed. When sources **conflict**,
that sample goes to `Ambiguous_Samples.csv` and is *reported*, never resolved by preference.

**Common conflict patterns and what they usually mean**

| Pattern | Usual explanation | Action |
|---|---|---|
| Repository says control, publication says disease | submitter mislabelled a channel | escalate; check genotype/sex and marker profile |
| Sample count in metadata ≠ files on disk | discarded or duplicated sample | reconcile; document the missing one |
| `treated` label but no timepoint | treatment arm unidentified | escalate; do not split by guess |
| Two GSMs from the same patient both labelled "control" | technical replicate or paired tissue | set `patient_id` and `biological_replicate_id` correctly |
| Adjacent normal labelled "normal" in a tumour study | not healthy control — adjacent tissue | relabel `tissue = adjacent_normal`; affects interpretation |
| Tumour purity varies wildly across "tumour" samples | bulk mixture | add purity covariate or acknowledge |
| Sex annotation contradicts XIST/RPS4Y1 | sample swap | hard escalate |

---

## 2.3 The mandatory group-verification questions

Answer each in writing (in `Metadata_Audit_Report.md`), even when the answer is "none":

1. Which samples are **control**? Which **disease**? Which **treated**? Any additional arms?
2. Are there subgroups within disease (stage, subtype, responder/non-responder, severity)?
3. **Paired or unpaired?** Same donor across groups? Same donor across timepoints?
4. **Longitudinal?** How many timepoints, and is the interval comparable?
5. Multiple tissues/cell types per donor? (nested structure — needs a mixed model)
6. **Biological** replicates per group — the real n. **Technical** replicates — collapse first.
7. Are cases and controls balanced on age/sex/stage? Any variable **fully confounded** with group?
8. Are there samples with `ambiguity_flag`? Are any of them critical to the primary comparison?
9. Is the reference/control appropriate at all (e.g. adjacent normal in a tumour study;
   healthy donor in an autoimmune study; untreated baseline in an intervention study)?
10. Is the group definition in the publication the same as in the metadata? If not, which governs?

---

## 2.4 G1 pass criteria (machine-checkable)

`python3 scripts/bap.py gate <project> --gate g1` passes only when:

- `02_Metadata/Sample_Annotation.csv` has all required columns, unique `sample_id`, non-empty `group`;
- no row has `ambiguity_flag` in {1, true, yes, Y, ?} **unless** it is non-critical and the note says
  why (the script blocks on any unresolved flag; document the exception in `Metadata_Audit_Report.md`
  and clear the flag with the evidence note);
- `02_Metadata/Ambiguous_Samples.csv` has no rows with `status = open`;
- `02_Metadata/Metadata_Audit_Report.md` exists and states the group counts;
- group × batch is not fully confounded (the script warns when a batch contains a single group);
- each group has ≥2 biological replicates (hard warning; ≥3 strongly preferred for any GLM).

Then report, in chat and in the report: samples per group, biological vs technical replicate
counts, unresolved non-critical gaps, and confounders carried into the model.

---

## 2.5 Escalation (never guess)

```
GATE G1 — BLOCKED
Blocking issue:  3 GSMs labelled "control" in the series metadata are described as
                 "severe lupus nephritis" in Supplementary Table S1.
Evidence:        GEO characteristics: control (GSM####, GSM####, GSM####)
                 | Publication S1: LN-Severe | Data: these 3 cluster with disease samples
                 | (corr > 0.94) and show high ISG score.
Samples affected:3
Why it matters:  If they are disease, the control group drops from 8 to 5 and the primary
                 contrast changes; the top 40 DE genes reorder.
Proposed reading (NOT applied): treat as disease (disease n = 11, control n = 5).
Decision needed: confirm which source governs, or supply the sample sheet from the authors.
```

A gate is not a formality: after escalation you **stop**. Do not run the primary analysis "to see
what happens", because seeing it contaminates every later decision (that is selection bias
introduced by the analyst).

---

## 2.6 Structures that need explicit encoding

- **Paired / repeated measures**: one donor contributing disease and control tissue is a *block*.
  Encode `patient_id`; model with `~ patient + group` (or a random effect). Ignoring pairing
  loses power and can invert conclusions.
- **Longitudinal**: encode `timepoint` as factor (few levels) or spline (many); account for
  within-donor correlation; never treat timepoints as independent replicates.
- **Multiple tissues per donor**: nested — `tissue` within `patient_id`.
- **Technical replicates**: `technical_replicate_id` populated; collapse by sum (counts) or mean
  (log-scale) at the level the pipeline requires, and document the collapse.
- **Multiplexed / pooled designs** (hashed scRNA, 10x multiplexing, MERCURIUS-style): the
  demultiplexed sample is the unit, not the pool.
- **Case-control with batch = plate**: if every case came from plate 1 and every control from
  plate 2, the group effect is **confounded with batch and cannot be estimated**. Say so; propose
  a design fix or interpret only within-batch contrasts (which then have no control).

---

## 2.7 Checklist

- [ ] One row per biological sample; IDs match the matrix exactly (verified by script)
- [ ] Four-source cross-check performed; `group_source` recorded per row
- [ ] All ten verification questions answered in `Metadata_Audit_Report.md`
- [ ] Ambiguous samples isolated in `Ambiguous_Samples.csv`; none `open` at gate time
- [ ] Confounded variables identified and named as non-estimable
- [ ] `bap.py gate g1` exits 0; group/replicate summary reported to the user
- [ ] No analysis beyond QC/annotation-level exploration has been run before this pass
