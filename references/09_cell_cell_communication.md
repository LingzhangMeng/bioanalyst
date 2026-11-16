# 09 — Cell–cell communication (S5, often + S7)

Ligand–receptor inference is the most over-claimed analysis in single-cell work. Every method here
infers **candidate signalling from expression plus prior knowledge**. None demonstrates that
physical communication occurred. Strong causal evidence requires perturbation, protein-level
evidence, or another orthogonal assay.

Vocabulary discipline: write "inferred/candidate signalling from X to Y", never "X signals to Y" or
"X–Y communication was demonstrated".

---

## 9.1 Method comparison (choose by question, not by familiarity)

| Feature | **CellChat** | **FlowSig** | **SigXTalk** | **NicheNet** |
|---|---|---|---|---|
| Ligand–receptor inference | Yes (built-in DB) | Uses CellChat output | Uses CellChat output | Uses ligand–target prior |
| Downstream gene response in receiver | Limited | Yes | Yes | Yes (target-gene programs) |
| Intracellular gene modules | No explicit flow model | Yes | Regulatory networks | Prior-knowledge network |
| Inter-pathway crosstalk | Limited | Intercellular flows | **Core objective** | Indirectly |
| Causal modelling | No | Graphical causal modelling | Not equivalent to causal inference | No |
| Spatial data | Not its primary requirement | Yes | Not its main focus | Not its main focus |
| Typical question | Which L–R pairs are enriched between populations? | Does sender signalling explain receiver response? | How do pathways cross-talk between populations? | Which ligands drive a receiver expression program? |

Attribution (as printed in the source specification; verify before citing in a manuscript):
FlowSig — PMID 39187683, `github.com/axelalmet/flowsig`; SigXTalk — PMID 40593827,
`github.com/LithiumHou/SigXTalk`; NicheNet — PMID 40038548, `github.com/saeyslab/nichenetr`
(note: NicheNet's original paper is Brouwer et al. 2019, PMID 31651192 — cite the version you
actually ran, and confirm the PMID against the paper before submission).

---

## 9.2 Recommended combined workflow (inflammatory/immune microenvironments, kidney disease, neutrophils, tumour immunology)

1. **Seurat/scanpy** — annotation with an evidence level (`06`), condition defined per G2.
2. **CellChat** — communication discovery: which L–R pairs and pathways are enriched between
   populations, per condition. Report the database used, the number of L–R pairs, the permutation
   test and the P/FDR, and the expression fraction thresholds.
3. **NicheNet** — for a population of interest, which ligands from the sender best explain the
   receiver's observed expression program; report the ligand activity ranking, the target-gene
   set, and the background sets used.
4. **FlowSig** — infer intercellular information flow including the receiver's intracellular
   response, and (with spatial data) spatially resolved flow.
5. **SigXTalk** — pathway cross-talk between populations; report the networks with their
   construction parameters.
6. **Independent validation** (`11`) — check candidate ligand/receptor genes in independent
   cohorts, in spatial data, and at the protein level where possible.

Do not run all four and pick the concordant result narratively: state the pre-specified primary
method and treat the others as corroboration (and say which was run first).

---

## 9.3 Parameters and assumptions that must be reported

- **Database/version** (CellChatDB version, NicheNet prior model + ligand–target matrix version,
  LR-pair set) and the access date.
- **Expression thresholds** (e.g. `min.cells`), the **normalisation** used, and whether the data
  were integrated (communication should generally use unintegrated or at least non-batch-masked
  expression; state what you used).
- **Statistical test**: permutation n, P values, FDR correction across pairs.
- **Population definition**: which clusters were merged/split for the analysis, and why. Results
  can flip with granularity — report at one level and state the sensitivity at another.
- **Sample-level consistency**: run per sample where possible; a "communication" present in one
  donor out of six is a hypothesis. Report the number of donors supporting each pair.
- **Abundance confound**: populations with more cells have more statistical power — a "stronger"
  interaction may be a size effect.
- **Compartment plausibility**: for the interaction to be credible, the two populations must be
  able to meet in space. Check proximity in spatial data when available.

---

## 9.4 Interpretation ladder (bind claims to evidence)

| Evidence available | Permitted statement | Grade |
|---|---|---|
| CellChat enrichment only | "Ligand–receptor pairs enriched between X and Y in this dataset" | E1 |
| + per-sample consistency + independent cohort concordance of L/R expression | "Candidate X→Y signalling, replicated at the expression level" | E2 |
| + spatial co-localisation / proximity | "Candidate X→Y signalling with spatial proximity support" | E2–E3 |
| + protein-level evidence (IHC/flow/secreted ligand) | "Supported signalling axis" | E3 |
| + perturbation/blocking experiment | "Demonstrated functional communication" | E4 |

Never: "neutrophils activate podocytes", "X drives Y via Z", "intercellular flow proves …" from
transcriptome-only inference. Intracellular "flow" is a model fit, not a flux measurement.

---

## 9.5 Checklist

- [ ] One pre-specified primary method; the others labelled corroborative
- [ ] DB/model versions + access date recorded; expression thresholds and permutations reported
- [ ] Unintegrated/unmasked expression used; stated explicitly
- [ ] Per-donor support reported for every headline interaction
- [ ] Population granularity sensitivity check performed
- [ ] Spatial/protein corroboration sought; absence stated if unavailable
- [ ] All claims phrased as *inferred/candidate*, graded E1–E4 with matching verbs
- [ ] Citations verified against the actual papers before any manuscript use
