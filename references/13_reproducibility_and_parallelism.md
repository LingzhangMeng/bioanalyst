# 13 — Reproducibility, environment capture and parallel execution (S5/S9)

A result you cannot rerun is not a result. This file defines the script contract, the environment
record, the logging rules, and the mandatory parallel-execution convention.

---

## 13.1 Directory and naming contract

```
MyProject/
├── 00_Project_Design/       Analysis_Plan.md, Research_Question.md, Research_Hypothesis.md
├── 01_Dataset_Discovery/    Dataset_Inventory.csv, Publications/, Dataset_Selection_Report.md
├── 02_Metadata/             Sample_Annotation.csv, Ambiguous_Samples.csv, Group_Definition.csv,
│                            Clinical_Metadata.csv, Metadata_Audit_Report.md, Original_Metadata/
├── 03_Raw_Data/             untouched downloads (read-only, checksummed)
├── 04_Processed_Data/       normalised/quantified objects, saved intermediate RDS/h5ad
├── 05_QC/                   Sample_QC.tsv, QC_Report.md, Batch_Effect/, Figures/
├── 06_Analysis/             01_Preprocessing → 06_Other_Analysis/  (+ 1_R/ and 2_Python/ with --layout meng)
├── 07_Validation/           Independent_Datasets/, Validation_Results/, Validation_Report.md
├── 08_Robustness/           Robustness_Report.md, scripts/
├── 09_Figures/              Figure_1/, Figure_2/, Supplementary_Figures/
├── 10_Tables/
├── 11_Literature/           evidence.tsv, PDFs
├── 12_Manuscript/
├── 13_Reports/              Findings_Ledger.csv, Final_Report.md
├── Scripts/                 (or 06_Analysis/1_R/1_Rscripts + 06_Analysis/2_Python/1_PythonScripts)
├── Logs/
├── Environment/
└── README.md
```

Naming rules (both languages):

- Scripts carry pipeline order: `00_ingest.R`, `01_annotate.R`, `05c_cell_type.R`; sub-steps use
  letters so the 2-digit root keeps sorting.
- **Every output inherits the generating script's own prefix**: `05c_cell_type.R` →
  `05c_*_markers.csv`, `05c_*_dotplot.pdf`. Never a bare `05_*` prefix.
- Figures and tables land in `09_Figures/` / `10_Tables/` (or `2_Plots/`, `3_Tables/` under the
  `meng` layout) with prefixed names, so provenance is readable from the filename alone.
- One script = one analytical step, with a header block stating purpose, inputs, outputs,
  model/formula, and worker count.

---

## 13.2 Mandatory parallel execution

Bioinformatics work is compute-bound; serial default runs waste the machine. **Every analysis
script parallelises its parallelisable steps**, with the degree chosen from hardware *and* dataset
size, and the decision recorded in the script header.

**Sizing rule (portable — measure, then choose):**

| Workload | Workers | Notes |
|---|---|---|
| Heavy FP/BLAS (large GEMM, NMF, deconvolution, heavy model fits) | physical cores (not SMT threads) | measured speedup saturates near physical-core count |
| Light / I/O-bound (per-sample GLMs, file parsing, plot generation, per-cell-type loops) | up to 2× physical cores, capped at logical CPUs | fork overhead dominates below ~0.1 s per task |
| Very small jobs (< ~1 s total, < 20 tasks) | serial, and say why | avoid paying fork/IPC cost for nothing |
| Memory-heavy tasks | workers ≈ min(cores, RAM_budget / peak_RSS_per_worker) | keep total working set ≤ ~80% of RAM |

On a 6-core/12-thread desktop with 61 GiB RAM (this workstation class): 6 workers for heavy FP,
≤12 for light tasks, total working set < 50 GiB; measured speedups are ~3–5×, **not linear**.
`parallel::detectCores()` returns SMT threads on such machines — never pass it blindly to FP workers.

**One level of parallelism only.** Either N process workers with **BLAS pinned to 1 thread each**,
or a single multi-threaded BLAS call. Never both (workers × BLAS threads oversubscribe the CPU and
can be slower than serial).

R:

```r
# --- header: workers chosen from physical cores; BLAS pinned to 1 per worker ---
n_phys  <- parallel::detectCores(logical = FALSE)   # physical, not SMT
workers <- min(n_phys, 6L)                          # heavy FP workload
Sys.setenv(OMP_NUM_THREADS = "1", OPENBLAS_NUM_THREADS = "1", MKL_NUM_THREADS = "1")
if (requireNamespace("RhpcBLASctl", quietly = TRUE)) RhpcBLASctl::blas_set_num_threads(1L)

# fork-based (Linux/macOS): future.apply
future::plan(future::multicore, workers = workers)
res <- future.apply::future_lapply(samples, fit_one_sample, future.seed = TRUE)
future::plan(future::sequential)   # reset before heavy BLAS work if you switch strategies

# Bioconductor route
BiocParallel::register(BiocParallel::MulticoreParam(workers = workers, RNGseed = 42, progressbar = TRUE))
```

Also available on typical Bioconductor installs: `parallel::mclapply`, `foreach` + `doParallel`,
`data.table::setDTthreads()` (set to workers for data wrangling).

Python:

```python
# --- header: workers from physical cores, BLAS pinned per process ---
import os
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[v] = "1"                       # set BEFORE importing numpy
os.environ["OPENBLAS_NUM_THREADS"] = "1"

from concurrent.futures import ProcessPoolExecutor
import os as _os
n_phys  = len({c for c in _os.sched_getaffinity(0)}) // 2 or 1   # rough physical estimate
workers = max(1, min(n_phys, 6))

with ProcessPoolExecutor(max_workers=workers) as ex:
    results = list(ex.map(fit_one_sample, samples))
```

`joblib.Parallel(n_jobs=workers, prefer="processes")` and `dask`/`mirai` scale further; keep the
same one-level rule. For CLI tools: `make -j<phys>`, `xargs -P<phys>`, `samtools -@`,
`STAR --runThreadN`, `salmon -p`, `CellRanger --localcores` — sized the same way.

Write the choice in the script header, e.g.:
`# parallel: 6 workers (physical cores) / dataset 8,400 cells × 24 samples — fork overhead amortised; BLAS pinned to 1`

And record measured wall-clock in `Logs/` so the sizing decision is auditable.

---

## 13.3 Environment capture

Run once at project start and after any package change:

```bash
Rscript  scripts/env_capture.R   # -> Environment/env_R.txt
python3  scripts/env_capture.py  # -> Environment/env_python.txt
```

Both record: language version, platform, package versions (including Bioconductor/CRAN source or
pip/conda origin), BLAS/LAPACK implementation and thread settings, CPU model/physical cores/logical
CPUs, RAM, and timestamp. Also capture the toolchain for upstream steps (CellRanger/STAR/salmon/
MaxQuant/DIANN versions), which are **not** recoverable from R/Python session info.

Rules: never rely on "latest"; pin versions in `renv.lock`, `requirements.txt`, `conda env export`,
or a container definition, and commit that file. If a package was installed from GitHub, record the
commit SHA, not the branch.

---

## 13.4 Seeds, determinism and intermediate objects

- Set a seed for every stochastic step (UMAP/t-SNE, clustering, bootstraps, subsampling, DL
  initialisation, permutation tests). Record the seed in the header and in the log.
- Save the objects you would hate to recompute: filtered counts, normalised object, DE results,
  model fits, pseudobulk matrices. `04_Processed_Data/` and per-step `*.rds`/`.h5ad`.
- Do not overwrite a previous run's output: use `run_<date>` subfolders or version suffixes when a
  parameter changes, and note the change in the report.
- Validate inputs before processing (dimensions, ID match, integer counts, no duplicated IDs);
  fail loudly rather than "fixing" silently.

---

## 13.5 Logging and execution honesty

- Every script writes to `Logs/<script>_<timestamp>.log` with: start/end time, input paths,
  parameter values, package versions (from the env capture), warnings, session info.
- Never `suppressMessages`/`suppressWarnings` a message you have not read; never wrap the main
  pipeline in `tryCatch` that returns `NULL` on failure.
- Warnings are evidence: report how many and what kind (e.g. "DESeq2 reported 14 outlier
  replacements, listed in `Logs/05a_deseq2.log`").
- **Never claim a script succeeded without inspecting its output.** Check: row/column counts,
  group sizes after filtering, number of cells/genes retained, that every expected file exists and
  is non-empty, that the plot actually renders.
- If a run fails, diagnose and record the cause; do not delete the failing script.

---

## 13.6 Figures and tables as artefacts

- Every plot saved twice: PDF (vector, for submission) **and** JPEG (dpi 300, quality 95, white
  background, for review).
- R: `pdf(file=...)` / `jpeg(file=..., width=..., height=..., units="in", res=300, quality=95, bg="white")`
  with `print(p)` inside the device block; on Linux with mismatched graphics stacks `ggsave(...,
  device="jpeg")` can fail — the base-device route is the reliable one.
- Python: `matplotlib.use("Agg")` headless, `plt.close("all")` before saving, then two
  `fig.savefig(..., format="pdf")` / `format="jpeg", dpi=300, facecolor="white"` calls.
- Keep the underlying plotting data (`09_Figures/Figure_1/data/…`) so any figure can be verified
  or regenerated. Standards in `14_figures_and_reporting.md`.

---

## 13.7 The rerun contract

Before delivery, hand the project to a colleague (or to a fresh session) and check:

- [ ] `Environment/` pins every toolchain version; a lock file reproduces the environment
- [ ] `Scripts/` runs in order with a single documented command per step
- [ ] Paths are relative/configurable; no absolute `/home/<user>/...` hardcoding
- [ ] Raw data untouched; derived objects present; no step depends on a manual GUI action
- [ ] `README.md` states: how to run, expected runtime, expected outputs and their checksums/sizes
- [ ] `handoff.md` current, with stage, parameters, decisions and blockers
- [ ] Every figure in `09_Figures/` regenerable by exactly one script
- [ ] Logs present and readable; warnings accounted for
- [ ] Parallel settings documented per script, with the measured runtime recorded
