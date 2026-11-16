#!/usr/bin/env python3
"""
bap.py — Bioinformatics Analysis Protocol (bioanalyst skill)

Makes the BAP gates machine-checkable instead of prose-only.

Commands
  scaffold  DIR [--layout protocol|meng] [--force]   create the project tree + artifact stubs
  status    DIR                                      which states/artifacts exist, gate verdicts
  check-annotation CSV                               validate Sample_Annotation.csv
  gate      DIR --gate {g0,g1,g2,g3}                 run a gate; exit 0 pass / 2 blocked / 1 invalid
  ledger-init DIR                                    create Findings_Ledger.csv if absent

Exit codes: 0 = PASS (possibly with warnings), 2 = BLOCKED (needs human decision), 1 = invalid/error.
Stdlib only; no third-party dependency.
"""

from __future__ import annotations

import argparse
import csv
import shutil
import sys
from datetime import date
from pathlib import Path

VERSION = "1.0.0"
PASS, WARN, BLOCK, FAIL = "PASS", "WARN", "BLOCK", "FAIL"
LEVELS = {PASS: 0, WARN: 1, BLOCK: 2, FAIL: 3}
CODES = {PASS: 0, WARN: 0, BLOCK: 2, FAIL: 1}

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_DIR / "templates"

CORE_COLS = [
    "sample_id", "repository_id", "patient_id", "group", "group_source", "tissue",
    "technology", "platform", "batch", "biological_replicate_id",
    "technical_replicate_id", "ambiguity_flag",
]
TRUTHY = {"1", "true", "yes", "y", "?", "ambiguous", "na?", "tbd"}

DIRS = [
    "00_Project_Design", "01_Dataset_Discovery/Publications", "02_Metadata/Original_Metadata",
    "03_Raw_Data", "04_Processed_Data", "05_QC/Sample_QC", "05_QC/Batch_Effect", "05_QC/Figures",
    "06_Analysis/01_Preprocessing", "06_Analysis/02_Differential_Analysis", "06_Analysis/03_Clustering",
    "06_Analysis/04_Pathway_Enrichment", "06_Analysis/05_Immune_Analysis", "06_Analysis/06_Other_Analysis",
    "07_Validation/Independent_Datasets", "07_Validation/Validation_Results", "08_Robustness",
    "09_Figures/Figure_1", "09_Figures/Supplementary_Figures", "10_Tables", "11_Literature",
    "12_Manuscript", "13_Reports", "Scripts", "Logs", "Environment",
]

MENG_DIRS = [
    "06_Analysis/1_R/1_Rscripts", "06_Analysis/1_R/2_Plots", "06_Analysis/1_R/3_Tables",
    "06_Analysis/1_R/4_Plots_selected", "06_Analysis/1_R/5_rds", "06_Analysis/1_R/6_logs",
    "06_Analysis/2_Python/1_PythonScripts", "06_Analysis/2_Python/2_Plots", "06_Analysis/2_Python/3_Tables",
    "06_Analysis/2_Python/4_Plots_selected", "06_Analysis/2_Python/5_Data", "06_Analysis/2_Python/6_logs",
]

MD_TEMPLATES = {
    "00_Project_Design/Analysis_Plan.md": "Analysis_Plan.md",
    "02_Metadata/Metadata_Audit_Report.md": "Metadata_Audit_Report.md",
    "05_QC/QC_Report.md": "QC_Report.md",
    "13_Reports/Final_Report.md": "Final_Report.md",
    "README.md": "README_project.md",
}

# csv template -> destination (header preserved, example rows dropped)
CSV_TEMPLATES = {
    "01_Dataset_Discovery/Dataset_Inventory.csv": "Dataset_Inventory.csv",
    "02_Metadata/Sample_Annotation.csv": "Sample_Annotation.csv",
    "02_Metadata/Ambiguous_Samples.csv": "Ambiguous_Samples.csv",
    "13_Reports/Findings_Ledger.csv": "Findings_Ledger.csv",
}

STATES = [
    ("S0", "Intake", ["00_Project_Design/Analysis_Plan.md"]),
    ("S1", "Dataset discovery", ["01_Dataset_Discovery/Dataset_Inventory.csv",
                                 "01_Dataset_Discovery/Dataset_Selection_Report.md"]),
    ("S2", "Sample annotation", ["02_Metadata/Sample_Annotation.csv",
                                 "02_Metadata/Metadata_Audit_Report.md",
                                 "02_Metadata/Ambiguous_Samples.csv"]),
    ("S3", "Design & statistics", ["00_Project_Design/Analysis_Plan.md"]),
    ("S4", "Quality control", ["05_QC/QC_Report.md", "05_QC/Sample_QC.tsv"]),
    ("S5", "Primary analysis", ["06_Analysis"]),
    ("S6", "Interpretation", ["13_Reports/Findings_Ledger.csv"]),
    ("S7", "Independent validation", ["07_Validation/Validation_Report.md"]),
    ("S8", "Robustness", ["08_Robustness/Robustness_Report.md"]),
    ("S9", "Review & delivery", ["13_Reports/Final_Report.md", "Environment"]),
]


# ----------------------------------------------------------------------------- helpers

def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        rows = [{k.strip(): (v or "").strip() for k, v in r.items() if k is not None} for r in reader]
        header = [h.strip() for h in (reader.fieldnames or [])]
    return header, rows


def exists_nonempty(path: Path) -> bool:
    if not path.exists():
        return False
    if path.is_dir():
        return any(p.is_file() and p.stat().st_size > 0 for p in path.rglob("*"))
    return path.stat().st_size > 0


def is_stub(path: Path) -> bool:
    """True when a deliverable is still an untouched template (placeholders / token-thin)."""
    if not path.is_file():
        return True
    text = path.read_text(encoding="utf-8", errors="replace")
    low = text.lower()
    markers = sum(low.count(m) for m in ("<…", "<n>", "<fill", "<template", "<pending",
                                         "<e.g.", "<control>", "<disease>", "<path", "<list>"))
    return markers >= 3 or len(text.split()) < 40


def report(verdict: str, messages) -> int:
    icon = {PASS: "✅", WARN: "⚠️ ", BLOCK: "🛑", FAIL: "❌"}
    for level, text in messages:
        print(f"{icon.get(level, '  ')} [{level}] {text}")
    print(f"\nVERDICT: {verdict}")
    if verdict == BLOCK:
        print("Do not proceed. Emit the G1/G2 escalation payload (SKILL.md §4) and wait for the user.")
    elif verdict == FAIL:
        print("Fix the invalid artifact(s) before re-running this gate.")
    return CODES[verdict]


# ----------------------------------------------------------------------------- annotation

def check_annotation(path: Path):
    msgs = []
    verdict = PASS

    def note(level, text):
        nonlocal verdict
        msgs.append((level, text))
        if LEVELS[level] > LEVELS[verdict]:
            verdict = level

    if not path.exists():
        note(FAIL, f"annotation table not found: {path}")
        return verdict, msgs

    header, rows = read_csv(path)
    missing = [c for c in CORE_COLS if c not in header]
    if missing:
        note(FAIL, "missing required columns: " + ", ".join(missing))
        return verdict, msgs
    if not rows:
        note(FAIL, "annotation table has no data rows (header only)")
        return verdict, msgs

    ids = [r["sample_id"] for r in rows]
    dups = sorted({i for i in ids if ids.count(i) > 1})
    if dups:
        note(FAIL, "duplicated sample_id values: " + ", ".join(dups))
    blanks = [r["sample_id"] or f"row{idx + 2}" for idx, r in enumerate(rows) if not r.get("group")]
    if blanks:
        note(FAIL, "empty group assignment for: " + ", ".join(blanks))

    groups = {}
    for r in rows:
        groups.setdefault(r.get("group", ""), []).append(r)

    flagged = [r["sample_id"] for r in rows if r.get("ambiguity_flag", "").lower() in TRUTHY]
    if flagged:
        note(BLOCK, "unresolved ambiguity_flag on samples: " + ", ".join(flagged)
             + " — resolve in Ambiguous_Samples.csv or clear the flag with evidence in the note")
    ungraded = [r["sample_id"] for r in rows if not r.get("group_source")]
    if ungraded:
        note(WARN, "group_source empty (no cited evidence) for: " + ", ".join(ungraded))

    for g, members in groups.items():
        donors = {r.get("patient_id") or r["sample_id"] for r in members}
        tech = {r.get("technical_replicate_id") for r in members if r.get("technical_replicate_id")}
        if len(donors) < 2:
            note(FAIL, f"group '{g}' has {len(donors)} independent donor(s) — no inference possible")
        elif len(donors) == 2:
            note(WARN, f"group '{g}' has only 2 donors — report as underpowered")
        if len(tech) > 1 or (len(tech) == 1 and None not in tech):
            note(WARN, f"group '{g}' contains technical replicates (ids: "
                       + ", ".join(sorted(t for t in tech if t)) + ") — collapse before modelling")
        print(f"  · group '{g}': {len(members)} samples / {len(donors)} donors")

    batches = {r.get("batch") for r in rows if r.get("batch")}
    if len(batches) > 1 and len(groups) > 1:
        conf = {}
        for r in rows:
            if r.get("batch"):
                conf.setdefault(r["batch"], set()).add(r.get("group"))
        single = sorted(b for b, gs in conf.items() if len(gs) == 1)
        if single and len(single) == len(conf):
            note(WARN, "batch is FULLY confounded with group (" + ", ".join(single)
                 + ") — the group effect is not estimable; analyse within batch or abort")
        elif single:
            note(WARN, "batches containing a single group: " + ", ".join(single)
                 + " — partial confounding; report it")

    note(PASS if verdict == PASS else verdict,
         f"{len(rows)} samples, {len(groups)} groups, {len(batches) or 0} batch(es) checked")
    return verdict, msgs


# ----------------------------------------------------------------------------- gates

def gate_g0(root: Path):
    msgs = []
    verdict = PASS
    plan = root / "00_Project_Design/Analysis_Plan.md"
    if not exists_nonempty(plan):
        msgs.append((FAIL, "Analysis_Plan.md missing or empty"))
        return FAIL, msgs
    text = plan.read_text(encoding="utf-8", errors="replace").lower()
    for kw, label in [("research question", "research question"),
                      ("hypothes", "hypothesis"),
                      ("outcome", "primary/secondary outcomes")]:
        if kw not in text:
            msgs.append((FAIL, f"Analysis_Plan.md lacks a {label} section"))
            verdict = FAIL
    inv = root / "01_Dataset_Discovery/Dataset_Inventory.csv"
    if not inv.exists():
        msgs.append((FAIL, "Dataset_Inventory.csv missing"))
        return FAIL, msgs
    _, rows = read_csv(inv)
    if not rows:
        msgs.append((FAIL, "Dataset_Inventory.csv has no datasets"))
        verdict = FAIL
    else:
        msgs.append((PASS, f"{len(rows)} dataset(s) inventoried"))
    if "tbd" in text or "fill every section" in text:
        msgs.append((WARN, "Analysis_Plan.md still contains template placeholders"))
    return verdict, msgs


def gate_g1(root: Path):
    msgs = []
    verdict, ann_msgs = check_annotation(root / "02_Metadata/Sample_Annotation.csv")
    msgs.extend(ann_msgs)

    audit = root / "02_Metadata/Metadata_Audit_Report.md"
    if not exists_nonempty(audit):
        msgs.append((FAIL, "Metadata_Audit_Report.md missing or empty"))
        verdict = FAIL if LEVELS[FAIL] > LEVELS[verdict] else verdict
    else:
        atext = audit.read_text(encoding="utf-8", errors="replace").lower()
        if "g1 verdict" not in atext:
            msgs.append((WARN, "Metadata_Audit_Report.md has no 'G1 verdict' statement"))
        if "<pending" in atext or "tbd" in atext:
            msgs.append((BLOCK, "Metadata_Audit_Report.md still contains unresolved placeholders"))
            verdict = BLOCK if LEVELS[BLOCK] > LEVELS[verdict] else verdict

    amb = root / "02_Metadata/Ambiguous_Samples.csv"
    if amb.exists():
        header, rows = read_csv(amb)
        if "status" in header:
            open_rows = [r.get("sample_id", "?") for r in rows if r.get("status", "").lower() not in {"resolved", "closed", "fixed"}]
            if open_rows:
                msgs.append((BLOCK, "Ambiguous_Samples.csv has open rows: " + ", ".join(open_rows)))
                verdict = BLOCK if LEVELS[BLOCK] > LEVELS[verdict] else verdict
            elif rows:
                msgs.append((PASS, f"{len(rows)} ambiguity record(s), all resolved"))
    return verdict, msgs


def gate_g2(root: Path):
    msgs = []
    plan = root / "00_Project_Design/Analysis_Plan.md"
    if not exists_nonempty(plan):
        return FAIL, [(FAIL, "Analysis_Plan.md missing — cannot have a statistical plan")]
    text = plan.read_text(encoding="utf-8", errors="replace").lower()
    required = [
        ("statistical analysis plan", "§4 statistical analysis plan"),
        ("model", "model specification"),
        ("feasibility", "feasibility verdict"),
        ("multiplic", "multiplicity strategy"),
        ("unit of inference", "unit of inference"),
    ]
    verdict = PASS
    for kw, label in required:
        if kw not in text:
            msgs.append((FAIL, f"Analysis_Plan.md lacks {label}"))
            verdict = FAIL
    placeholders = text.count("<…") + text.count("<n>")
    if placeholders > 6:
        msgs.append((BLOCK, f"Analysis_Plan.md still has {placeholders} unfilled placeholders — "
                            "the design is not actually specified"))
        verdict = BLOCK if LEVELS[BLOCK] > LEVELS[verdict] else verdict
    if "validation" not in text:
        msgs.append((WARN, "no validation strategy stated (independent cohort or explicit impossibility)"))
    if verdict == PASS:
        msgs.append((PASS, "design, model, multiplicity and feasibility recorded"))
    return verdict, msgs


def gate_g3(root: Path):
    msgs = []
    verdict = PASS

    def note(level, text):
        nonlocal verdict
        msgs.append((level, text))
        if LEVELS[level] > LEVELS[verdict]:
            verdict = level

    final = root / "13_Reports/Final_Report.md"
    if not exists_nonempty(final):
        note(FAIL, "Final_Report.md missing or empty")
    elif is_stub(final):
        note(BLOCK, "Final_Report.md is still a template — the review and verdict are not written")

    robust = root / "08_Robustness/Robustness_Report.md"
    if not exists_nonempty(robust) or is_stub(robust):
        note(FAIL, "Robustness_Report.md missing or still a stub — the headline finding has no "
                   "sensitivity check")

    env = root / "Environment"
    env_files = [p.name for p in env.rglob("env_*")] if env.is_dir() else []
    if not env_files:
        note(FAIL, "Environment/ has no env_R.txt / env_python.txt — run scripts/env_capture.{R,py}")
    else:
        note(PASS, "environment captured: " + ", ".join(sorted(env_files)))

    val = root / "07_Validation/Validation_Report.md"
    justified = (exists_nonempty(final)
                 and "validation was not possible" in final.read_text(encoding="utf-8", errors="replace").lower())
    if not exists_nonempty(val) or is_stub(val):
        if justified:
            note(WARN, "no usable Validation_Report.md — absence justified in Final_Report.md")
        else:
            note(FAIL, "Validation_Report.md missing or still a stub, with no justification in "
                       "Final_Report.md")

    ledger = root / "13_Reports/Findings_Ledger.csv"
    if not ledger.exists():
        note(FAIL, "Findings_Ledger.csv missing")
        return verdict, msgs
    header, rows = read_csv(ledger)
    if "grade" not in header:
        note(FAIL, "Findings_Ledger.csv lacks a 'grade' column")
        return verdict, msgs
    if not rows:
        note(FAIL, "Findings_Ledger.csv has no findings — nothing has been claimed, so there is "
                   "nothing to deliver")
        return verdict, msgs
    graded = [r for r in rows if r.get("grade", "").upper() in {"E1", "E2", "E3", "E4"}]
    ungraded = [r.get("finding_id") or "?" for r in rows if r.get("grade", "").upper() not in
                {"E1", "E2", "E3", "E4"}]
    if not graded:
        note(FAIL, "no finding carries an E1–E4 grade")
    elif ungraded:
        note(WARN, "ungraded ledger rows: " + ", ".join(ungraded))
    if graded:
        dist = {}
        for r in graded:
            dist[r["grade"].upper()] = dist.get(r["grade"].upper(), 0) + 1
        note(PASS, "evidence grades: " + ", ".join(f"{k}×{v}" for k, v in sorted(dist.items())))
    return verdict, msgs


GATES = {"g0": gate_g0, "g1": gate_g1, "g2": gate_g2, "g3": gate_g3}


# ----------------------------------------------------------------------------- commands

def cmd_scaffold(args):
    root = Path(args.dir).expanduser().resolve()
    if root.exists() and any(root.iterdir()) and not args.force:
        print(f"❌ target exists and is not empty: {root}\n   use --force to write into it anyway")
        return 1
    root.mkdir(parents=True, exist_ok=True)
    for d in DIRS:
        (root / d).mkdir(parents=True, exist_ok=True)
    if args.layout == "meng":
        for d in MENG_DIRS:
            (root / d).mkdir(parents=True, exist_ok=True)

    created = 0
    for dest, tpl in MD_TEMPLATES.items():
        target = root / dest
        if target.exists() and not args.force:
            continue
        src = TEMPLATES / tpl
        target.parent.mkdir(parents=True, exist_ok=True)
        if src.exists():
            shutil.copyfile(src, target)
        else:
            target.write_text(f"# {target.stem.replace('_', ' ')}\n\n<template {tpl} not found>\n",
                              encoding="utf-8")
        created += 1

    for dest, tpl in CSV_TEMPLATES.items():
        target = root / dest
        if target.exists() and not args.force:
            continue
        src = TEMPLATES / tpl
        target.parent.mkdir(parents=True, exist_ok=True)
        if src.exists():
            header, _ = read_csv(src)
            target.write_text(",".join(header) + "\n", encoding="utf-8")
        else:
            target.write_text("sample_id,group\n", encoding="utf-8")
        created += 1

    for rel, text in [
        ("01_Dataset_Discovery/Dataset_Selection_Report.md",
         "# Dataset selection report\n\nWhy these datasets can answer the question, and what was rejected.\n"),
        ("07_Validation/Validation_Report.md",
         "# Validation report\n\n<fill from templates/Validation_Report.md — see the skill>\n"),
        ("08_Robustness/Robustness_Report.md",
         "# Robustness report\n\n<fill from the skill's reference 12>\n"),
        ("Environment/README.md",
         "# Environment\n\nRun scripts/env_capture.R and scripts/env_capture.py to populate this folder.\n"),
        ("handoff.md",
         "# Handoff\n\n<refresh with the `handoff` skill at every milestone>\n"),
    ]:
        target = root / rel
        if not target.exists() or args.force:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
            created += 1

    print(f"✅ scaffolded {root}  (layout={args.layout}, {created} artifact(s) written)")
    print("Next: fill Analysis_Plan.md §1–2 → python3 scripts/bap.py gate "
          f"'{root}' --gate g0")
    return 0


def cmd_status(args):
    root = Path(args.dir).expanduser().resolve()
    if not root.exists():
        print(f"❌ not found: {root}")
        return 1
    print(f"Project: {root}\n")
    print(f"{'State':5} {'Name':22} {'Artifacts':10} Detail")
    print("-" * 78)
    for sid, name, needed in STATES:
        have, missing = [], []
        for rel in needed:
            (have if exists_nonempty(root / rel) else missing).append(rel)
        detail = ("missing: " + ", ".join(missing)) if missing else "complete"
        print(f"{sid:5} {name:22} {len(have)}/{len(needed):<8} {detail}")
    print("\nGates:")
    for gid, fn in GATES.items():
        verdict, _ = fn(root)
        print(f"  {gid.upper()}: {verdict}")
    return 0


def cmd_check_annotation(args):
    verdict, msgs = check_annotation(Path(args.csv).expanduser().resolve())
    print(f"Annotation audit: {args.csv}\n")
    return report(verdict, msgs)


def cmd_gate(args):
    root = Path(args.dir).expanduser().resolve()
    if not root.exists():
        print(f"❌ not found: {root}")
        return 1
    fn = GATES[args.gate]
    verdict, msgs = fn(root)
    print(f"Gate {args.gate.upper()} — {root}\n")
    return report(verdict, msgs)


def cmd_ledger_init(args):
    root = Path(args.dir).expanduser().resolve()
    target = root / "13_Reports/Findings_Ledger.csv"
    if target.exists():
        print(f"⚠️  already exists: {target}")
        return 0
    src = TEMPLATES / "Findings_Ledger.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        header, _ = read_csv(src)
        target.write_text(",".join(header) + "\n", encoding="utf-8")
    else:
        target.write_text("finding_id,claim,evidence_type,dataset_s,statistic,n,grade,"
                          "verb_used,contradicting_evidence,limitation,next_test,figure_table\n",
                          encoding="utf-8")
    print(f"✅ created {target}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="bap.py", description="Bioinformatics Analysis Protocol — scaffold, gates, artifact checks")
    p.add_argument("--version", action="version", version=f"bap.py {VERSION}")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scaffold", help="create the project tree and artifact stubs")
    s.add_argument("dir")
    s.add_argument("--layout", choices=["protocol", "meng"], default="protocol")
    s.add_argument("--force", action="store_true")
    s.set_defaults(func=cmd_scaffold)

    s = sub.add_parser("status", help="artifact and gate status")
    s.add_argument("dir")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("check-annotation", help="validate Sample_Annotation.csv")
    s.add_argument("csv")
    s.set_defaults(func=cmd_check_annotation)

    s = sub.add_parser("gate", help="run a gate")
    s.add_argument("dir")
    s.add_argument("--gate", required=True, choices=sorted(GATES))
    s.set_defaults(func=cmd_gate)

    s = sub.add_parser("ledger-init", help="create Findings_Ledger.csv")
    s.add_argument("dir")
    s.set_defaults(func=cmd_ledger_init)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
