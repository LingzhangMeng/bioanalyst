# <Project name> — README

<One paragraph: what question this project answers, which datasets, and the current stage.>

**Protocol:** this project runs under `bioanalyst` / BAP. Current state: **S?** (see
`00_Project_Design/Analysis_Plan.md` sign-off table). Gates: G0 <pass/blocked> · G1 <pass/blocked>
· G2 <pass/blocked> · G3 <pending>.

---

## How to run

```bash
# 1. environment (record once, re-run after any package change)
Rscript scripts/env_capture.R
python3 scripts/env_capture.py

# 2. pipeline, in order (each script is idempotent and writes to Logs/)
Rscript Scripts/00_ingest.R          # -> 04_Processed_Data/, Logs/00_ingest_*.log
Rscript Scripts/01_qc.R              # -> 05_QC/
Rscript Scripts/02_normalise.R       # -> 04_Processed_Data/
Rscript Scripts/03_primary.R         # -> 06_Analysis/02_Differential_Analysis/
Rscript Scripts/04_interpret.R       # -> 10_Tables/, 09_Figures/
Rscript Scripts/05_validate.R        # -> 07_Validation/
Rscript Scripts/06_robustness.R      # -> 08_Robustness/
Rscript Scripts/07_figures.R         # -> 09_Figures/
```

Expected runtime on <hardware>: ~<…> min total; the heaviest step is `<…>` (<…> min at <n> workers).
Parallel settings: <workers> workers, one level of parallelism, BLAS pinned to 1 per worker
(see the header of each script and `references/13_reproducibility_and_parallelism.md`).

## Directory map

| Path | Contents |
|---|---|
| `00_Project_Design/` | `Analysis_Plan.md` (authoritative plan + gate sign-off) |
| `01_Dataset_Discovery/` | inventory, publications, selection rationale |
| `02_Metadata/` | `Sample_Annotation.csv`, `Ambiguous_Samples.csv`, `Metadata_Audit_Report.md` |
| `03_Raw_Data/` | untouched downloads (read-only, checksummed) |
| `04_Processed_Data/` | normalised objects, saved intermediates |
| `05_QC/` | per-sample metrics, QC report, batch assessment |
| `06_Analysis/` | analysis steps (or `1_R/` + `2_Python/` under the `meng` layout) |
| `07_Validation/` | external cohorts and validation results |
| `08_Robustness/` | sensitivity analyses |
| `09_Figures/` | figures (PDF + JPEG) with their plotted data |
| `10_Tables/` | result tables (CSV/TSV) |
| `11_Literature/` | retrieved evidence (`evidence.tsv`, PDFs) |
| `12_Manuscript/` | manuscript sections |
| `13_Reports/` | `Findings_Ledger.csv`, `Final_Report.md` |
| `Scripts/` `Logs/` `Environment/` | code, execution logs, version capture |

## Conventions

- Scripts are prefixed with pipeline order (`00_`, `01_`, `05a_`, `05b_`).
- Outputs inherit their script's prefix (`05c_*.csv`, `05c_*.pdf`); no bare step prefixes.
- Every figure is written twice: PDF (vector) + JPEG (300 dpi).
- Raw data is never modified; every derived object is saved; every run is logged.
- `handoff.md` at the project root is refreshed at each milestone.

## Data and access

- Accessions: <list>
- Raw vs processed: <what is deposited where>
- Controlled access: <process, or "none">
- Licence/consent constraints: <…>

## Reporting guideline

<ARRIVE / STROBE / REMARK / TRIPOD / PRISMA / MIAPE / MSI / MINSEQE> — checklist: <path>

## Status and known limitations

- Current stage and next step: <…>
- Known blockers: <…>
- Findings graded so far: <n E1 / n E2 / n E3 / n E4>

## Citation

<Authors, year, journal, DOI — once available. Code: Zenodo DOI.>
