# bioanalyst

**A governed bioinformatics analysis protocol (BAP) for AI agents — so an agent cannot quietly produce publishable-looking nonsense.**

<p align="left">
  <img alt="version" src="https://img.shields.io/badge/version-1.0.0-blue">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-green">
  <img alt="protocol" src="https://img.shields.io/badge/protocol-BAP-6f42c1">
  <img alt="agents" src="https://img.shields.io/badge/agents-Reasonix%20%7C%20Claude%20Code%20%7C%20Codex%20%7C%20OpenClaw-orange">
  <img alt="python" src="https://img.shields.io/badge/python-3.9%2B%20(stdlib%20only)-yellow">
  <img alt="R" src="https://img.shields.io/badge/R-optional%20(Bioconductor)-276DC3">
</p>

`bioanalyst` is a drop-in **agent skill** plus a small **enforcement CLI**. It teaches an AI agent how
to design, run, validate, and defend an omics analysis — and it refuses to let the agent advance
until the parts that actually determine scientific validity are settled: *what every sample is*, and
*what statistical model the design can support*.

```text
Understand the dataset → establish the design → formulate the strategy → QC
       → statistics → independent validation → reproducible results
```

---

## Table of contents

- [The problem this exists to solve](#the-problem-this-exists-to-solve)
- [How it works](#how-it-works)
- [Quick start](#quick-start)
- [Installation](#installation)
- [The workflow: ten states](#the-workflow-ten-states)
- [The gates: where the agent must stop](#the-gates-where-the-agent-must-stop)
- [Evidence grading and claim language](#evidence-grading-and-claim-language)
- [What's in the repository](#whats-in-the-repository)
- [CLI reference](#cli-reference)
- [Supported data types](#supported-data-types)
- [Conventions it enforces](#conventions-it-enforces)
- [Design principles and non-goals](#design-principles-and-non-goals)
- [Verification](#verification)
- [FAQ](#faq)
- [Provenance and citation](#provenance-and-citation)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## The problem this exists to solve

An agent can write technically flawless `DESeq2` code on **swapped groups** and produce a
publication-shaped result in ninety seconds. No linter catches it. No unit test fails. The error is
not in the code — it is in the assumptions the code silently inherited.

| Failure mode | What it looks like | What `bioanalyst` does |
|---|---|---|
| Group inversion | "the GSM titles look like controls" | **G1** requires a four-source cross-check and blocks on any unresolved ambiguity |
| Adjacent-normal treated as healthy control | "controls are fine, n = 12" | annotation schema forces `tissue` to be explicit; the audit question list names the trap |
| Cells counted as replicates | "n = 8,412 cells, P < 1e-300" | unit-of-inference rule + pseudobulk/mixed-model guidance; the validator warns on un-collapsed replicates |
| Batch = signal | correction applied first, then "discovery" | assess → decide → document tree; confounded batch is declared *not estimable* rather than "adjusted" |
| Method chosen by P value | three tests tried, the significant one reported | **G2** requires the model in writing before any test runs |
| Same cohort called validation | "replicated in GSE12345" (= the discovery series) | independence criteria + explicit non-validation categories |
| Training performance sold as validation | "AUC = 0.97" | leakage checklist, patient-level splits, nested CV |
| Enrichment read as activation | "the pathway is activated" | claim ladder: "enriched among upregulated genes (FDR = …)" |
| Inference sold as communication | "neutrophils signal to podocytes" | CCM module mandates "candidate/inferred signalling" |
| Works only in one setting | one cutoff, one normalisation, one seed | robustness menu + grade propagation when a check fails |

The premise: **the objective is not to find statistically significant genes or produce attractive
figures. It is to produce reproducible, biologically meaningful, independently supported evidence
that another researcher can inspect and re-derive.**

---

## How it works

Three layers, each usable on its own:

| Layer | Artefact | Role |
|---|---|---|
| **Rules** | [`SKILL.md`](SKILL.md) | Role, 12 non-negotiable rules, the ten-state machine, red lines, routing table. Always in the agent's context. |
| **Playbooks** | [`references/`](references/) | 17 deep guides opened on demand (annotation audit, study design, QC, per-modality methods, validation, figures, review). ~2,200 lines. |
| **Enforcement** | [`scripts/bap.py`](scripts/bap.py) | Scaffolds the project tree, validates the annotation table, and runs gates that exit `0` pass / `2` blocked / `1` invalid. |

`SKILL.md` is ordinary Markdown with YAML frontmatter, so it works as a skill in Reasonix, Claude
Code, Codex, OpenClaw, or any agent that reads instruction files. `bap.py` is pure Python 3 standard
library — no dependencies, no network, no data leaves the machine.

---

## Quick start

```bash
# 1. install as a skill
git clone https://github.com/LingzhangMeng/bioanalyst.git ~/.reasonix/skills/bioanalyst
~/.reasonix/skills/bioanalyst/scripts/install.sh --check      # verify the tree

# 2. create a project
S=~/.reasonix/skills/bioanalyst/scripts
python3 $S/bap.py scaffold ./LN_project --layout protocol
python3 $S/bap.py status   ./LN_project

# 3. work the gates in order
$EDITOR LN_project/00_Project_Design/Analysis_Plan.md         # question, hypothesis, outcomes
python3 $S/bap.py gate ./LN_project --gate g0

$EDITOR LN_project/02_Metadata/Sample_Annotation.csv          # one row per biological sample
python3 $S/bap.py gate ./LN_project --gate g1                 # blocks on any guess

$EDITOR LN_project/00_Project_Design/Analysis_Plan.md         # §3–6: design, model, feasibility
python3 $S/bap.py gate ./LN_project --gate g2                 # blocks until the model is written

# 4. record the environment, then analyse
Rscript $S/env_capture.R && python3 $S/env_capture.py
```

Typical conversation with the agent after installation:

> **You:** analyse GSE##### and find out whether interferon signalling is up in lupus nephritis.
>
> **Agent:** scaffolds the project, inventories the dataset, reports the sample table it extracted,
> and — if two GSMs disagree between the repository metadata and the publication — **stops** with
> the escalation payload below instead of guessing which label is real.

---

## Installation

### A. Clone straight into a skill root (recommended)

```bash
git clone https://github.com/LingzhangMeng/bioanalyst.git ~/.reasonix/skills/bioanalyst
```

The repository root *is* the skill, so the clone is immediately valid.

### B. Symlink from a working copy

```bash
cd /path/to/bioanalyst
./scripts/install.sh             # -> ~/.reasonix/skills/bioanalyst (symlink)
./scripts/install.sh --check     # validate frontmatter, file counts, and that the CLI parses
```

`SKILLS_ROOT=/path/to/somewhere ./scripts/install.sh` installs elsewhere; `--copy` copies instead of
linking; `--unlink` removes it; `--path` prints the config snippet if your agent discovers skills
through a path list.

### C. Register the folder as a skill root

```bash
./scripts/install.sh --path
# add the printed path to the agent's skill-path configuration, e.g. ~/.reasonix/config.toml:
#   [skills]
#   paths = ["/path/to/bioanalyst"]
```

### D. Other agents

- **Claude Code / Codex / OpenClaw:** copy this directory into the agent's skills or instructions
  directory, or reference `SKILL.md` directly — it is self-contained; the `references/` playbooks
  are optional depth.
- **No agent at all:** the playbooks work as a human checklist. Start with
  [`references/02_sample_annotation_audit.md`](references/02_sample_annotation_audit.md) and
  [`references/16_red_lines.md`](references/16_red_lines.md).

---

## The workflow: ten states

| State | Purpose | Required artefact | Gate |
|---|---|---|---|
| **S0** | Intake: question, hypothesis, primary/secondary outcomes, mode | `00_Project_Design/Analysis_Plan.md` §1–2 | **G0** |
| **S1** | Discovery and provenance: accessions, publications, suitability, licences | `Dataset_Inventory.csv`, `Dataset_Selection_Report.md` | compatibility check before any merge |
| **S2** | Sample annotation and group verification | `Sample_Annotation.csv`, `Ambiguous_Samples.csv`, `Metadata_Audit_Report.md` | **G1 (hard)** |
| **S3** | Design and statistical feasibility | `Analysis_Plan.md` §3–6 | **G2 (hard)** |
| **S4** | Quality control, batch assessment | `Sample_QC.tsv`, `QC_Report.md`, `Batch_Effect/` | checkpoint |
| **S5** | Primary analysis | `06_Analysis/**`, `Logs/**`, `Environment/**` | — |
| **S6** | Biological interpretation | `13_Reports/Findings_Ledger.csv` (graded) | — |
| **S7** | Independent validation | `07_Validation/Validation_Report.md` | promotes E1 → E2 |
| **S8** | Robustness and sensitivity | `08_Robustness/Robustness_Report.md` | — |
| **S9** | Review and delivery | `Final_Report.md`, reproducibility package, `handoff.md` | **G3** |

Only two states are **hard** gates. That is deliberate: everything else can be automated with
judgement, but annotation and design decide whether the analysis means anything at all.

---

## The gates: where the agent must stop

| Gate | Passes only when | Blocks when |
|---|---|---|
| **G0** | question, hypothesis and outcomes present; ≥1 dataset inventoried | the question is not answerable with these data, as posed |
| **G1** | annotation columns complete, IDs unique, groups non-empty, **no unresolved `ambiguity_flag`**, no `open` rows in the ambiguity table, ≥2 independent donors per group, audit report present | any group assignment rests on a guess |
| **G2** | statistical plan, model specification, multiplicity strategy, unit of inference, feasibility verdict; placeholder count under threshold | the design is still a template |
| **G3** | ledger graded E1–E4, validation report (or a justified absence), robustness report, environment capture, final report with verdict | a deliverable is a stub, missing, or ungraded |

Exit codes: **`0`** pass · **`2`** blocked → escalate and wait · **`1`** invalid → fix the artefact.
Warnings are always surfaced: un-collapsed technical replicates, a batch containing one group
(partial confounding), full batch × group confounding (*effect not estimable*), and two-donor groups.

When a gate blocks, the agent emits the same payload every time — not a shrug, not a guess:

```text
GATE G1 — BLOCKED
Blocking issue:     3 GSMs labelled "control" in the series metadata are described as
                    "severe lupus nephritis" in Supplementary Table S1.
Evidence:           repository: control | publication: LN-severe | data: these 3 cluster
                    with disease (r > 0.94) and carry a high ISG score
Samples affected:   3
Why it matters:     if they are disease, control drops 8 → 5 and the primary contrast changes
Proposed reading:   treat as disease (NOT applied)
Decision needed:    confirm which source governs, or supply the sample sheet
```

---

## Evidence grading and claim language

Every finding carries a grade, and the sentence you write must match it.

| Grade | Basis | Allowed verb | Not allowed |
|---|---|---|---|
| **E1** | statistically supported in the discovery dataset | "was associated with", "was higher in" | "drives", "validated", "biomarker" |
| **E2** | reproduced in ≥1 independent cohort | "replicated in", "consistent across cohorts" | "independently validated" without naming the cohort |
| **E3** | multiple orthogonal evidence types (transcriptome + proteome + clinical + spatial) | "corroborated by" | "proven mechanism" |
| **E4** | independent experimental validation (perturbation, protein-level, functional) | "was shown to drive/regulate" | anything stronger than the experiment |

`13_Reports/Findings_Ledger.csv` is the single source of truth: no claim appears in a figure, an
abstract sentence, or a chat summary without a graded row — claim, statistic with CI, n, grade, verb,
contradicting evidence, limitation, next test.

---

## What's in the repository

```text
bioanalyst/
├── SKILL.md                     # the protocol (frontmatter name: bioanalyst)
├── references/                  # 17 playbooks, opened on demand
├── templates/                   # 10 fill-in artefacts the gates inspect
├── scripts/
│   ├── bap.py                   # scaffold · status · check-annotation · gate · ledger-init
│   ├── env_capture.R            # R/Bioconductor versions, hardware, worker sizing
│   ├── env_capture.py           # Python packages, toolchains, hardware, worker sizing
│   └── install.sh               # link/copy/unlink/check into an agent skill root
├── LICENSE
└── .gitignore
```

### references/

| File | Use when |
|---|---|
| [`01_intake_and_provenance.md`](references/01_intake_and_provenance.md) | starting a project; 12 intake categories; repository table; compatibility matrix; licences |
| [`02_sample_annotation_audit.md`](references/02_sample_annotation_audit.md) | **G1** — annotation schema, four-source cross-check, conflict patterns, escalation |
| [`03_statistical_design.md`](references/03_statistical_design.md) | **G2** — design taxonomy → method, confounders, identifiability, power, multiplicity, batch decision |
| [`04_quality_control.md`](references/04_quality_control.md) | QC thresholds per modality, exclusion policy, batch assess → decide → document |
| [`05_bulk_microarray.md`](references/05_bulk_microarray.md) | count guards, normalisation, DE method matrix, enrichment inputs |
| [`06_single_cell_spatial.md`](references/06_single_cell_spatial.md) | pipeline checkpoints, integration rules, annotation evidence ladder, pseudobulk, spatial |
| [`07_proteomics_metabolomics.md`](references/07_proteomics_metabolomics.md) | missingness mechanisms, imputation policy, PTM normalisation, multi-omics joins |
| [`08_clinical_survival_ml.md`](references/08_clinical_survival_ml.md) | cohort integrity, Cox assumptions, cutoff optimism, leakage checklist |
| [`09_cell_cell_communication.md`](references/09_cell_cell_communication.md) | CellChat / NicheNet / FlowSig / SigXTalk selection, combined workflow, claim ladder |
| [`10_biological_interpretation.md`](references/10_biological_interpretation.md) | enrichment pitfalls, database versions, per-finding blocks, literature evidence |
| [`11_independent_validation.md`](references/11_independent_validation.md) | what counts as independent; concordance metrics; "concordance ≠ validation" |
| [`12_robustness_and_sensitivity.md`](references/12_robustness_and_sensitivity.md) | 13-check sensitivity menu; reporting format; grade propagation |
| [`13_reproducibility_and_parallelism.md`](references/13_reproducibility_and_parallelism.md) | naming contract, worker sizing, BLAS pinning, logging honesty, rerun contract |
| [`14_figures_and_reporting.md`](references/14_figures_and_reporting.md) | panel specification, axis/colour ethics, reporting guidelines, data availability |
| [`15_self_review_and_evidence.md`](references/15_self_review_and_evidence.md) | 18-domain audit, Critical/Major/Minor, E1–E4, claim-language ladder |
| [`16_red_lines.md`](references/16_red_lines.md) | 40 forbidden moves with rationale and remedy |
| [`17_recipes.md`](references/17_recipes.md) | copy-paste R/Python: preflight, count guard, pseudobulk, batch assessment, sex check, model ladder |

### templates/

`Analysis_Plan.md` · `Dataset_Inventory.csv` · `Sample_Annotation.csv` · `Ambiguous_Samples.csv` ·
`Metadata_Audit_Report.md` · `QC_Report.md` · `Validation_Report.md` · `Findings_Ledger.csv` ·
`Final_Report.md` · `README_project.md`

Each is a working document, not a form: the sample annotation table carries `group_source`
(which evidence supports the label), `biological_replicate_id` and `technical_replicate_id` (the unit
of inference), `batch`, and `ambiguity_flag` (the gate).

---

## CLI reference

### `bap.py`

```bash
bap.py scaffold DIR [--layout protocol|meng] [--force]
bap.py status   DIR                    # states, artefacts present/missing, gate verdicts
bap.py check-annotation CSV            # the G1 validator on its own
bap.py gate     DIR --gate g0|g1|g2|g3 # exit 0 pass / 2 blocked / 1 invalid
bap.py ledger-init DIR                 # create Findings_Ledger.csv
bap.py --version
```

`--layout meng` additionally creates `1_R/{1_Rscripts,2_Plots,3_Tables,4_Plots_selected,5_rds,6_logs}`
and `2_Python/{1_PythonScripts,2_Plots,3_Tables,4_Plots_selected,5_Data,6_logs}` under
`06_Analysis/` for labs that organise by language.

Example output:

```text
$ python3 scripts/bap.py check-annotation 02_Metadata/Sample_Annotation.csv
  · group 'control': 4 samples / 4 donors
  · group 'disease': 4 samples / 4 donors
✅ [PASS] 8 samples, 2 groups, 4 batch(es) checked
VERDICT: PASS
```

```text
$ python3 scripts/bap.py check-annotation 02_Metadata/bad_annotation.csv
❌ [FAIL] duplicated sample_id values: S01
🛑 [BLOCK] unresolved ambiguity_flag on samples: S03 — resolve in Ambiguous_Samples.csv
⚠️  [WARN] group 'control' has only 2 donors — report as underpowered
❌ [FAIL] group 'disease' has 1 independent donor(s) — no inference possible
VERDICT: FAIL
```

### `env_capture.R` / `env_capture.py`

Write `Environment/env_R.txt` and `Environment/env_python.txt`: language and package versions
(CRAN/Bioconductor/pip/conda origin), BLAS/LAPACK implementation and thread settings, CPU model,
physical cores, logical CPUs, RAM, and upstream toolchain versions (CellRanger, STAR, salmon,
samtools, MaxQuant, DIANN, containers). Both print the recommended worker count for the machine, so
the parallel decision recorded in each script header is reproducible.

### `install.sh`

```bash
./scripts/install.sh            # symlink into ${SKILLS_ROOT:-~/.reasonix/skills}
./scripts/install.sh --copy     # copy instead of link
./scripts/install.sh --check    # frontmatter, file counts, Python/R syntax
./scripts/install.sh --unlink   # remove (refuses to delete anything it did not install)
./scripts/install.sh --path     # print the skill-path config snippet
```

---

## Supported data types

| Data | Covered in | Notable hard rule |
|---|---|---|
| Bulk RNA-seq | [`05`](references/05_bulk_microarray.md) | never DESeq2/edgeR on TPM/FPKM |
| Microarray | [`05`](references/05_bulk_microarray.md) | assay-appropriate normalisation; no mixing pipelines |
| scRNA-seq | [`06`](references/06_single_cell_spatial.md) | cells are not replicates → pseudobulk or mixed model |
| Spatial (Visium, Xenium, MERFISH, CosMx) | [`06`](references/06_single_cell_spatial.md) | spots are not patients; panel-limited assays |
| Proteomics (DDA/DIA, LFQ, TMT) | [`07`](references/07_proteomics_metabolomics.md) | classify missingness before imputing |
| Metabolomics | [`07`](references/07_proteomics_metabolomics.md) | identification confidence travels with the claim |
| TCGA / survival / prediction models | [`08`](references/08_clinical_survival_ml.md) | no cutoff fitted and evaluated on the same cohort |
| Cell–cell communication | [`09`](references/09_cell_cell_communication.md) | inference is not demonstrated communication |
| Multi-omics integration | [`07`](references/07_proteomics_metabolomics.md) | same-sample requirement before "cross-modality validation" |

---

## Conventions it enforces

These are defaults, not dogma — edit `references/13` and the scaffold if your lab differs.

- **Script names carry pipeline order:** `00_`, `01_`, … with `05a_`, `05b_` for sub-steps.
- **Outputs inherit the generating script's prefix:** `05c_cell_type.R` → `05c_*.pdf`, never a bare `05_*`.
- **Every figure is written twice:** PDF (vector) + JPEG (300 dpi, white background). On some Linux
  graphics stacks `ggsave(device="jpeg")` fails, so the R recipe uses base devices.
- **Parallel computing is mandatory**, sized from hardware *and* dataset size, with exactly **one
  level** of parallelism: N workers each with single-threaded BLAS, or one multithreaded BLAS call —
  never both. Worker count goes in the script header.
- **Raw data is read-only**, every run is logged, every figure keeps its plotted data.
- **`handoff.md`** at the project root is refreshed at each milestone (pairs with the `handoff` skill).

---

## Design principles and non-goals

**Principles**

1. Gates beat prose. A rule the agent cannot fail is a rule that does not exist.
2. The unit of inference is the hardest question in omics; ask it on every page.
3. Grade before you write. Verbs are evidence claims.
4. Prefer the analysis that survives a hostile reviewer to the one that looks impressive.
5. Reproducibility is a deliverable, not a courtesy.
6. Say what the data cannot support, in the same document, with equal prominence.

**Non-goals**

- Not a pipeline engine or workflow manager (no Nextflow/Snakemake replacement).
- Not a statistics course: it enforces decisions and points at the playbook.
- Not a package: nothing here imports your data or phones home. `bap.py` is stdlib-only.
- Not a substitute for domain judgement — it is a structure that makes judgement explicit and auditable.

---

## Verification

Tested on Linux (Ubuntu, R 4.6.1, Python 3.13) on 2026-11-16:

| Check | Result |
|---|---|
| Python/R/shell syntax of all four scripts | pass |
| `scaffold` (both layouts) creates the tree, 14 artefacts, header-only CSVs | pass |
| `status` reports all ten states and gate verdicts | pass |
| Fresh scaffold gates | G0 fail, G1 fail, G2 block, G3 fail — as designed |
| Filled fixture gates | G0/G1/G2 pass; G3 fails on stubs and empty ledger |
| Duplicate IDs, unresolved ambiguity, single-donor group | BLOCK/FAIL with actionable messages |
| Batch confounding, un-collapsed technical replicates, two-donor group | warnings as designed |
| Clean-room end-to-end staged walkthrough | 8/8 exit-code assertions |
| `install.sh` link/unlink against a throwaway skill root | pass |
| `env_capture.R` / `.py` | correct versions, 6 physical cores, RAM, worker sizing |

Structural checks are scripted: frontmatter parses, all 17 references are routed from `SKILL.md`
(0 missing, 0 stale), 10 templates, no zero-byte or stray files.

---

## FAQ

**Does this slow the agent down?**
It adds two blocking checkpoints and a handful of artefacts. In exchange it removes the most
expensive failure class in the field — an analysis that must be redone, or retracted.

**Will it refuse to work without a validation cohort?**
No. It requires that the *absence* be stated, and it caps the affected claims at E1 with matching
verbs. Silence is what it forbids.

**Does it phone home or touch my data?**
No. `bap.py` reads CSV/Markdown files and exits. `env_capture.*` reads local version metadata.
Nothing is uploaded, and raw data is never modified.

**Can I use only the playbooks?**
Yes. `references/` reads as a human checklist; `SKILL.md` is optional context, `bap.py` optional tooling.

**Does it work for non-human data?**
Yes — organism is an inventory field, and the design/statistics/QC logic is species-agnostic. Human
clinical data adds the access and de-identification rules in [`01`](references/01_intake_and_provenance.md).

**How do I add a modality?**
Add `references/18_<modality>.md`, one line in the routing table in `SKILL.md`, and one row in the
red-line table. Then run `./scripts/install.sh --check`.

---

## Provenance and citation

The protocol derives from a specification document — *Bioinformatics skill prompts* — covering a
master analyst prompt, twelve intake categories, checkpoint prompts A–H, modality requirements A–F,
a ten-state workflow, a module decomposition, and E1–E4 evidence grading.

This repository adds: machine-checkable gates and the `bap.py` CLI, the artifact templates, the
parallel-computing convention with hardware-aware sizing, the figure/export policy, the red-line
catalogue, and the copy-paste recipe library.

If you use it in academic work, cite the repository:

```bibtex
@misc{meng2026bioanalyst,
  author       = {Meng, Lingzhang},
  title        = {bioanalyst: a governed bioinformatics analysis protocol (BAP) for AI agents},
  year         = {2026},
  publisher    = {GitHub},
  howpublished = {\url{https://github.com/LingzhangMeng/bioanalyst}},
  note         = {Version 1.0.0}
}
```

---

## Roadmap

- [ ] `bap.py gate g2 --plan path` cross-check the model against the annotation table (design vs realised n)
- [ ] Optional `--json` output for CI integration (fail a build when a gate is blocked)
- [ ] Starter `.Rmd` / Quarto report that reads `Findings_Ledger.csv` and emits the report skeleton
- [ ] Additional playbooks: ATAC-seq, microbiome, long-read/splicing, spatial multi-omics
- [ ] Worked end-to-end example project with a public dataset (GSE accession) in `examples/`

---

## Contributing

Issues and pull requests are welcome — especially **new red lines** (a failure mode you have seen and
a check that would have caught it) and **modality playbooks**.

Please keep the contract intact:

1. `SKILL.md` stays lean; depth belongs in `references/`.
2. Every new gate keeps the exit-code contract (`0` pass / `2` blocked / `1` invalid).
3. Every new artefact is registered in `bap.py` so it is scaffolded and checked, not just described.
4. Run `./scripts/install.sh --check` before opening the PR.

---

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, adapt the gates to your lab's standards; attribution
is appreciated.
