# 07 — Proteomics and metabolomics (S5)

Applies to MS-based proteomics (DDA/DIA, label-free, TMT/iTRAQ, affinity-proteomics) and
metabolomics (LC-MS, GC-MS, CE-MS, untargeted/targeted). Two rules dominate: **identify the
missingness mechanism before imputing**, and **respect identification confidence**.

---

## 7.1 Proteomics pre-analysis checks

| Check | Record | Failure mode prevented |
|---|---|---|
| Acquisition | DDA vs DIA; instrument; gradient; FAIMS; MS1/MS2 resolution | incomparable runs |
| Search engine + version | MaxQuant/DIANN/Spectronaut/FragPipe; enzyme, modifications, FDR (PSM & protein) | irreproducible IDs |
| Database | UniProt release, isoform policy, contaminant DB | identifier drift |
| Quantification | LFQ/iBAQ/TMT reporter; normalisation applied by the tool | double normalisation |
| Identification depth | proteins per sample; unique peptides | depth confound vs condition |
| Missingness | per-protein missingness rate, and per-group pattern | unmodelled MNAR |
| Contaminants | keratin, trypsin, albumin depletion | signal dilution |
| Run order | injection order vs intensity/ID drift | drift as biology |
| Batch | day, column, operator, sample-prep batch | confounding |
| PTM data | enrichment efficiency, localisation probability | over-claiming phospho-sites |

**TMT-specific:** reporter ion ratio compression, plex-to-plex batch effects, correct for
`plex` as a batch, use protein-level ratios, and never compare across plexes without bridging.

**DIA-specific:** document the library (empirical vs predicted), the extraction window, and the
normalisation; report q-values at peptide and protein level.

---

## 7.2 Missing values — model the mechanism, then decide

Classify before acting:

| Mechanism | Signature | Correct handling |
|---|---|---|
| **MNAR-by-detection** (below LOD, the usual case for low abundance) | missingness correlates with intensity/abundance; more missing in low-load samples | `MinDet`/`MinProb` imputation with a **left-shifted narrow distribution sized from the observed low-abundance variance**, or model with a hurdle/`msqrob`-style approach; report sensitivity |
| **MNAR-by-absence** (protein truly not present in a group) | missing only in specific group | do **not** impute to a "found" value; treat as presence/absence or state non-estimable |
| **MAR** (random dropout) | missingness unrelated to abundance and to group | `kNN`/`missForest`/`RF` imputation acceptable; report which |
| **Structural** (protein not quantified in the run design) | whole-sample gaps | exclude protein or sample, document |

Absolute bans: replacing all missing with `0`; replacing with a single global minimum; imputing
TMT zeros as if they were real ratios; imputing >30–40% of a protein's values without labelling
the result an estimate.

Always run the headline comparison with and without imputation (§`12`), and report how many
values per protein were imputed.

---

## 7.3 Proteomics normalisation and statistics

- Prefer intensity-domain `log2` then median/quantile normalisation, or the tool's LFQ; state it once.
- Filter: proteins with ≥2 unique peptides and quantified in ≥ a pre-specified fraction of samples.
- Test: `limma` (with `trend`/`arrayWeights`), `msqrob2`, or `DEqMS` (variance depends on
  peptide count) rather than a plain t-test; `Perseus` defaults are acceptable if parameters are reported.
- Use BH FDR; report effect size (log2 ratio) with CI; guard against the "one-peptide protein"
  claim.
- For PTM: normalise site intensity to total protein abundance of that protein, otherwise you are
  measuring abundance, not occupancy.

---

## 7.4 Metabolomics pre-analysis checks

| Check | Requirement |
|---|---|
| Identification confidence | label every feature with MSI level (1 = authentic standard, 2 = library/MS2, 3 = putative, 4 = unknown); novel-marker claims need level ≤2 |
| QC samples | pooled QC injected regularly; RSD of features across QCs (e.g. keep features with RSD < 20–30%) |
| Drift | injection order vs signal (LOESS/`qcCorrection`); report whether drift correction was applied |
| Normalisation | total signal / median / probabilistic quotient / internal standard; state which, and why |
| Missingness | report % missing per feature and per group; same mechanism logic as §7.2 |
| Annotation source | HMDB/METLIN/MassBank/GNPS version and score cut-offs |
| Batch | run day/column/batch as covariate |

Statistics: `limma`/`limma-trend` on log-transformed, normalised intensities; `MetaboAnalyst`-style
univariate + multivariate is acceptable if the univariate result is the primary evidence (a PLS-DA
separation alone is not a finding). Report FDR, fold change, and the identification level together.

---

## 7.5 Multi-omics linkage (proteome ↔ transcriptome ↔ metabolome)

- Join by stable identifiers (UniProt ↔ Ensembl/HGNC), report how many features mapped and how many
  were dropped.
- Protein–mRNA concordance is typically weak (ρ ≈ 0.3–0.6); a discordant protein is not an error,
  it is post-transcriptional regulation — which itself needs evidence before being claimed.
- Do not present a "multi-omics integrative network" as validation of a mechanism unless the
  modalities were measured in the **same samples** (state if they were not).
- For causality-adjacent claims, prefer overlap statistics with explicit thresholds over
  hand-picked intersections.

---

## 7.6 Checklist

- [ ] Acquisition, search engine, database, FDR and normalisation versions recorded
- [ ] Identification confidence reported per feature (peptide count; MSI level)
- [ ] Missingness classified (MNAR-detection / MNAR-absence / MAR / structural) before imputation
- [ ] No blanket zero/minimum imputation; imputed fraction reported per feature
- [ ] Batch and injection order assessed as confounders
- [ ] Statistics appropriate to peptide-count-dependent variance; PTM normalised to protein
- [ ] Multi-omics joins report the identifier mapping loss
- [ ] Same-sample requirement checked before any cross-modality "validation" claim
