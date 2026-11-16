#!/usr/bin/env python3
"""
env_capture.py — record the Python environment, hardware and thread settings for a BAP project.

Usage:  python3 scripts/env_capture.py [output_dir]
Output: <output_dir>/env_python.txt   (default: Environment/env_python.txt)

Stdlib only. Optional packages are reported as installed/absent, never required.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from importlib import metadata
from pathlib import Path

PACKAGES = [
    "numpy", "scipy", "pandas", "polars", "matplotlib", "seaborn", "scikit-learn",
    "statsmodels", "lifelines", "scanpy", "anndata", "muon", "squidpy", "scvi-tools",
    "decoupler", "pydeseq2", "pysam", "GEOparse", "pysradb", "gseapy",
    "celltypist", "harmonypy", "leidenalg", "igraph", "joblib", "dask", "ray",
    "torch", "tensorflow", "jax", "squidpy", "spatialdata", "napari",
]

TOOLCHAINS = ["R", "Rscript", "cellranger", "STAR", "salmon", "kallisto", "samtools",
              "bwa", "bowtie2", "hisat2", "fastp", "trimmomatic", "nextflow", "snakemake",
              "comet", "msconvert", "MaxQuant", "diann", "docker", "singularity", "apptainer"]


def cpu_info():
    model, phys, logical = None, None, os.cpu_count()
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        text = cpuinfo.read_text(errors="replace")
        for line in text.splitlines():
            if line.lower().startswith("model name") and model is None:
                model = line.split(":", 1)[1].strip()
        core_ids = {ln.split(":", 1)[1].strip() for ln in text.splitlines() if ln.startswith("core id")}
        phys_ids = {ln.split(":", 1)[1].strip() for ln in text.splitlines() if ln.startswith("physical id")}
        if core_ids and phys_ids:
            phys = len(core_ids) * len(phys_ids)
        elif core_ids:
            phys = len(core_ids)
    if phys is None:
        try:
            logical = len(os.sched_getaffinity(0))
            phys = max(1, logical // 2)
        except AttributeError:
            phys = logical
    try:
        logical = len(os.sched_getaffinity(0))
    except AttributeError:
        logical = os.cpu_count()
    return model, phys, logical


def ram_gib():
    meminfo = Path("/proc/meminfo")
    if meminfo.exists():
        for line in meminfo.read_text().splitlines():
            if line.startswith("MemTotal"):
                kb = int("".join(c for c in line.split(":")[1] if c.isdigit()))
                return round(kb / 1024 ** 2, 1)
    return None


def pkg_row(name: str) -> str:
    try:
        return f"{name:<28} {metadata.version(name):<14} {origin(name)}"
    except metadata.PackageNotFoundError:
        return f"{name:<28} {'-':<14} NOT INSTALLED"


def origin(name: str) -> str:
    try:
        dist = metadata.distribution(name)
        installer = (dist.read_text("INSTALLER") or "").strip()
        return installer or "unknown"
    except Exception:
        return "unknown"


def tool_row(tool: str) -> str:
    exe = shutil.which(tool)
    if not exe:
        return f"{tool:<20} not on PATH"
    version = ""
    for flag in ("--version", "-version", "version"):
        try:
            out = subprocess.run([exe, flag], capture_output=True, text=True, timeout=10)
            version = (out.stdout or out.stderr).strip().splitlines()[0][:70]
            if version:
                break
        except Exception:
            continue
    return f"{tool:<20} {exe}  {version}"


def main() -> int:
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Environment")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "env_python.txt"

    model, phys, logical = cpu_info()
    ram = ram_gib()
    workers_heavy = max(1, phys or 1)
    workers_light = max(1, min(2 * (phys or 1), logical or 1))
    threads = {v: os.environ.get(v, "<unset>") for v in
               ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")}

    lines = [
        "=" * 62,
        "BAP environment record — Python",
        f"captured_at           : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"project_dir           : {Path.cwd()}",
        "=" * 62,
        "",
        "## Python",
        f"python_version        : {sys.version.split()[0]}",
        f"implementation        : {platform.python_implementation()} {platform.python_version()}",
        f"executable            : {sys.executable}",
        f"platform              : {platform.platform()}",
        f"virtualenv            : {os.environ.get('VIRTUAL_ENV', os.environ.get('CONDA_DEFAULT_ENV', '<none>'))}",
        "",
        "## Hardware (used to size parallelism)",
        f"cpu_model             : {model or '<unknown>'}",
        f"physical_cores        : {phys}",
        f"logical_cpus          : {logical}",
        f"ram_gib               : {ram}",
        f"recommended_workers   : heavy FP = {workers_heavy} | light/IO = {workers_light} "
        "(one level only; pin BLAS to 1 per worker)",
        "",
        "## Thread environment variables",
        *[f"{k:<22}: {v}" for k, v in threads.items()],
        "",
        "## Python packages (name / version / installer)",
        *[pkg_row(p) for p in dict.fromkeys(PACKAGES)],
        "",
        "## External toolchains (upstream steps are not captured by pip/conda)",
        *[tool_row(t) for t in TOOLCHAINS],
        "",
        "## Notes",
        " - Record versions of every upstream tool used (aligner, quantifier, search engine).",
        " - Prefer a lock file: requirements.txt / conda env export / container digest.",
        " - Write the chosen worker count into each analysis script header.",
    ]

    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"✅ wrote {out_file}")
    print(f"   Python {sys.version.split()[0]} | {phys} physical cores | {ram} GiB RAM | heavy workers = {workers_heavy}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
