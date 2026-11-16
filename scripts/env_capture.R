#!/usr/bin/env Rscript
# env_capture.R — record the R environment, hardware and thread settings for a BAP project.
# Usage:  Rscript scripts/env_capture.R [output_dir]
# Output: <output_dir>/env_R.txt   (default: Environment/env_R.txt, created if absent)
# Design: never fails because a package is missing; records what exists, and what does not.

args <- commandArgs(trailingOnly = TRUE)
out_dir <- if (length(args) >= 1) args[1] else "Environment"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
out_file <- file.path(out_dir, "env_R.txt")

have <- function(pkg) {
  ok <- suppressWarnings(requireNamespace(pkg, quietly = TRUE))
  if (ok) {
    v <- tryCatch(as.character(utils::packageVersion(pkg)), error = function(e) "unknown")
    origin <- tryCatch(utils::packageDescription(pkg, fields = "Repository"), error = function(e) NA)
    if (is.na(origin) || !nzchar(origin)) origin <- "local/GitHub"
    sprintf("%-28s %-12s %s", pkg, v, origin)
  } else {
    sprintf("%-28s %-12s %s", pkg, "-", "NOT INSTALLED")
  }
}

read_first <- function(path, pattern, what = "model name") {
  if (!file.exists(path)) return(NA_character_)
  ln <- grep(pattern, readLines(path, warn = FALSE), value = TRUE)
  if (!length(ln)) return(NA_character_)
  trimws(sub(".*:", "", ln[1]))
}

cpuinfo <- "/proc/cpuinfo"
meminfo <- "/proc/meminfo"

phys_cores <- tryCatch({
  if (file.exists(cpuinfo)) {
    ln <- readLines(cpuinfo, warn = FALSE)
    ids <- grep("^core id", ln, value = TRUE)
    sockets <- grep("^physical id", ln, value = TRUE)
    if (length(ids) && length(sockets)) {
      length(unique(paste(trimws(sub(".*:", "", sockets)), trimws(sub(".*:", "", ids)))))
    } else {
      parallel::detectCores(logical = FALSE)
    }
  } else {
    parallel::detectCores(logical = FALSE)
  }
}, error = function(e) NA_integer_)

logical_cpus <- tryCatch(parallel::detectCores(logical = TRUE), error = function(e) NA_integer_)
ram_gib <- tryCatch({
  if (file.exists(meminfo)) {
    ln <- grep("^MemTotal", readLines(meminfo, warn = FALSE), value = TRUE)
    round(as.numeric(sub("\\D*(\\d+).*", "\\1", ln)) / 1024^2, 1)
  } else NA_real_
}, error = function(e) NA_real_)

blas_threads <- tryCatch({
  if (requireNamespace("RhpcBLASctl", quietly = TRUE)) RhpcBLASctl::blas_get_num_procs() else NA_integer_
}, error = function(e) NA_integer_)

workers_heavy <- if (!is.na(phys_cores)) max(1L, as.integer(phys_cores)) else 1L
workers_light <- if (!is.na(phys_cores) && !is.na(logical_cpus)) {
  max(1L, min(2L * as.integer(phys_cores), as.integer(logical_cpus)))
} else workers_heavy

core_pkgs <- c("DESeq2", "edgeR", "limma", "tximport", "apeglm", "ashr",
               "Seurat", "SeuratObject", "SingleCellExperiment", "scater", "scran",
               "scDblFinder", "SingleR", "celldex", "batchelor", "harmony",
               "CellChat", "nichenetr", "liana", "SCP",
               "sva", "variancePartition", "lme4", "survival", "survminer",
               "GEOquery", "Biobase", "SummarizedExperiment", "AnnotationDbi",
               "clusterProfiler", "org.Hs.eg.db", "org.Mm.eg.db", "ReactomePA", "fgsea",
               "ComplexHeatmap", "ggplot2", "data.table", "dplyr", "tidyr", "Matrix",
               "future", "future.apply", "BiocParallel", "foreach", "doParallel",
               "RhpcBLASctl", "renv", "rmarkdown", "knitr")

lines <- c(
  "==============================================================",
  "BAP environment record — R",
  sprintf("captured_at           : %s", format(Sys.time(), "%Y-%m-%d %H:%M:%S %Z")),
  sprintf("project_dir           : %s", normalizePath(".", mustWork = FALSE)),
  "==============================================================",
  "",
  "## R",
  sprintf("R_version             : %s", R.version.string),
  sprintf("platform              : %s", R.version$platform),
  sprintf("arch                  : %s", R.version$arch),
  sprintf("libPaths              : %s", paste(.libPaths(), collapse = " | ")),
  "",
  "## Hardware (used to size parallelism)",
  sprintf("cpu_model             : %s", read_first(cpuinfo, "^model name")),
  sprintf("physical_cores        : %s", phys_cores),
  sprintf("logical_cpus          : %s", logical_cpus),
  sprintf("ram_gib               : %s", ram_gib),
  sprintf("blas_threads_current  : %s", blas_threads),
  sprintf("recommended_workers   : heavy FP = %s | light/IO = %s (one level only; pin BLAS to 1 per worker)",
          workers_heavy, workers_light),
  "",
  "## Thread environment variables",
  sprintf("OMP_NUM_THREADS       : %s", Sys.getenv("OMP_NUM_THREADS", "<unset>")),
  sprintf("OPENBLAS_NUM_THREADS  : %s", Sys.getenv("OPENBLAS_NUM_THREADS", "<unset>")),
  sprintf("MKL_NUM_THREADS       : %s", Sys.getenv("MKL_NUM_THREADS", "<unset>")),
  "",
  "## Packages (name / version / origin)",
  vapply(core_pkgs, have, character(1)),
  "",
  "## sessionInfo()",
  capture.output(utils::sessionInfo())
)

con <- file(out_file, open = "wt")
writeLines(lines, con)
close(con)

cat(sprintf("✅ wrote %s\n", out_file))
cat(sprintf("   R %s | %s physical cores | %s GiB RAM | heavy workers = %s\n",
            paste(R.version$major, R.version$minor, sep = "."), phys_cores, ram_gib, workers_heavy))
cat("   Reminder: write the worker count into each analysis script header.\n")
