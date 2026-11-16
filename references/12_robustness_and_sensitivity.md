# 12 — Robustness and sensitivity analysis (S8)

A finding that survives only one parameter setting is a property of that setting. Sensitivity
analysis is cheap, and it is the strongest signal a reviewer can get that the analyst was honest.

Deliverable: `08_Robustness/Robustness_Report.md` + a resumable script per check.

---

## 12.1 The standard menu (run what the claim needs)

| Check | Question answered | Typical implementation |
|---|---|---|
| Exclusion sensitivity | Does the result depend on the excluded samples? | re-run with all samples (flagged, not removed); re-run excluding each outlier individually |
| Influence | Does one sample/donor drive it? | leave-one-sample-out (or donor-out) effect-size range; report the range, not a p-value |
| Covariate sensitivity | Does adjustment change the conclusion? | model with/without each covariate; report the direction and CI shift |
| Normalisation | Is it an artefact of one normalisation? | median-of-ratios vs TMM vs VST-based sanity; array: RMA vs quantile |
| Model family | Is the conclusion method-specific? | DESeq2 vs limma-voom vs edgeR; Wilcoxon vs pseudobulk-DESeq2 for scRNA |
| Threshold | Is it one cutoff? | multiple FDR (0.01/0.05/0.1), multiple \|log2FC\| floors; report the stable core set |
| Clustering resolution | Do the populations survive? | resolutions 0.2–1.2; cluster stability (ARI/bootstrap); do the DE conclusion per resolution |
| QC thresholds | Is it a QC artefact? | tighter/looser cell or gene filters (scRNA); depth downsampling |
| Batch handling | Is it a correction artefact? | covariate vs corrected vs uncorrected; do not report only the best |
| Imputation | Is it an imputation artefact? | proteomics: with/without imputation, alternative imputation |
| Cutoff/derivation | Is it cutoff optimism? | pre-specified vs data-derived cutoff; split-cohort derivation |
| Dataset dependence | Does it need one cohort? | per-cohort effects; random-effects meta-analysis (I², τ²) |
| Random seed | Is it stochastic? | re-run with ≥3 seeds for anything seeded (UMAP, clustering, bootstraps, DL) |

**Not a sensitivity analysis:** rerunning the identical script and getting the identical number.
That is a reproducibility check — useful, but it answers a different question.

---

## 12.2 Reporting format

For each check, one row:

| Finding | Perturbation | Baseline estimate | Perturbed estimate | Conclusion changed? |
|---|---|---|---|---|
| Gene X higher in disease | drop the 2 QC-flagged samples | log2FC 1.8 (FDR 1e-4) | 1.6 (FDR 3e-4) | no |
| Cell type Y expands | pseudobulk vs sccomp | +8.2% (P=0.01) | +5.0% (P=0.06) | weakened → downgrade to "suggestive" |

Then a summary sentence the user can quote: *"The primary finding was stable across
normalisation, model family, and leave-one-donor-out (log2FC range 1.5–1.9); it weakened when
the two QC-flagged samples were reinstated (FDR 0.08) and is therefore reported as suggestive."*

---

## 12.3 Rules

1. Choose the perturbation set **before** seeing which ones threaten the result (otherwise it is
   fishing for the setting that supports the story).
2. Report the full set, including checks that passed trivially — omissions are noticed.
3. Never present only the version that survives. If the finding is fragile, that is the finding.
4. Quantify, don't binary: a range of effect estimates is more informative than "still significant".
5. Where a perturbation changes the conclusion, propagate the change into `Findings_Ledger.csv`
   grades and the claim verbs.
6. Keep every perturbation as a runnable script (`08_Robustness/scripts/NN_*.R`) so the check can
   be re-run when reviewers ask.

---

## 12.4 Checklist

- [ ] Perturbation set chosen in advance and documented
- [ ] Leave-one-donor-out or equivalent influence check on every headline finding
- [ ] At least one alternative model/normalisation and one threshold sweep
- [ ] Seed sensitivity for any stochastic step
- [ ] All checks reported, including those that passed
- [ ] Grade changes propagated to the ledger and the prose
- [ ] Summary sentence written in plain language, quotable
