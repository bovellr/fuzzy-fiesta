#!/usr/bin/env python3
"""Generate an Azure DevOps-friendly measures register from PBIP TMDL and vNext DAX assets."""
from __future__ import annotations

import csv
import re
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

REPO = Path(__file__).resolve().parents[1]
ZIP_PATH = REPO / "Finance_WS_Semantic_Models.zip"
VNEXT_DAX = REPO / "docs/implementation/refactored_measures_and_calculation_groups.dax"
OUT_CSV = REPO / "docs/registers/azure_devops_measures_register.csv"
OUT_MD = REPO / "docs/registers/measures_register_readme.md"

FIELDS = [
    "Work Item Type",
    "Title",
    "Area Path",
    "Tags",
    "Model Name",
    "Object Type",
    "Table Name",
    "Measure Name",
    "Definition",
    "Format String",
    "Display Folder",
    "Hidden",
    "Lifecycle Status",
    "Governance Status",
    "Source Artefact",
    "Business Definition",
    "Technical Notes",
    "Dependencies",
    "Replacement Measure",
    "Owner",
    "Validation Status",
]


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("```", "").strip())


def extract_dependencies(expr: str) -> str:
    deps = sorted(set(re.findall(r"(?<![A-Za-z0-9_])\[([^\]]+)\]", expr or "")))
    return "; ".join(f"[{d}]" for d in deps if d)


def parse_tmdl_measures(tmdl: Path) -> list[dict[str, str]]:
    lines = tmdl.read_text(encoding="utf-8", errors="ignore").splitlines()
    rows: list[dict[str, str]] = []
    i = 0
    pending_doc: list[str] = []
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("///"):
            pending_doc.append(stripped[3:].strip())
            i += 1
            continue
        m = re.match(r"\s*measure\s+(?:'([^']+)'|([^=]+?))\s*=\s*(.*)$", line)
        if not m:
            if stripped:
                pending_doc = []
            i += 1
            continue
        name = (m.group(1) or m.group(2)).strip()
        after = m.group(3)
        expr_parts: list[str] = []
        attrs: list[str] = []
        if "```" in after:
            after_expr = after.split("```", 1)[1]
            if "```" in after_expr:
                expr_parts.append(after_expr.split("```", 1)[0])
            else:
                expr_parts.append(after_expr)
                i += 1
                while i < len(lines):
                    if "```" in lines[i]:
                        expr_parts.append(lines[i].split("```", 1)[0])
                        break
                    expr_parts.append(lines[i])
                    i += 1
        elif after.strip():
            expr_parts.append(after.strip())
        i += 1
        attribute_started = False
        attr_re = re.compile(r"\s*(?:isHidden\b|displayFolder:|formatString:|lineageTag:|annotation\b|changedProperty\b)")
        while i < len(lines):
            nxt = lines[i]
            if re.match(r"\s*measure\s+(?:'[^']+'|[^=]+?)\s*=", nxt):
                i -= 1
                break
            if nxt.strip().startswith("///"):
                i -= 1
                break
            if attr_re.match(nxt):
                attribute_started = True
            if attribute_started:
                attrs.append(nxt)
            else:
                expr_parts.append(nxt)
            i += 1
        attr_text = "\n".join(attrs)
        fmt = "General"
        fm = re.search(r"\n\s*formatString:\s*(.+)", "\n" + attr_text)
        if fm:
            fmt = fm.group(1).strip()
        elif "PBI_FormatHint" in attr_text:
            fmt = "General Number (PBI_FormatHint)"
        folder = ""
        dm = re.search(r"\n\s*displayFolder:\s*(.+)", "\n" + attr_text)
        if dm:
            folder = dm.group(1).strip()
        hidden = "Yes" if re.search(r"\n\s*isHidden\b", "\n" + attr_text) else "No"
        lifecycle = "Current - Hidden" if hidden == "Yes" else "Current - Visible"
        business = clean(" ".join(pending_doc)) if pending_doc else "Missing - requires business-owner definition"
        expr = clean("\n".join(expr_parts))
        rows.append({
            "Work Item Type": "Task",
            "Title": f"Measure register: {name}",
            "Area Path": "Finance\\Semantic Model",
            "Tags": "PowerBI;SemanticModel;MeasureRegister;Current",
            "Model Name": "sm_finance_core",
            "Object Type": "Measure",
            "Table Name": "_Measures",
            "Measure Name": name,
            "Definition": expr,
            "Format String": fmt,
            "Display Folder": folder,
            "Hidden": hidden,
            "Lifecycle Status": lifecycle,
            "Governance Status": "Imported from current PBIP; review required" if "Missing" in business else "Imported from current PBIP; definition present",
            "Source Artefact": "Finance_WS_Semantic_Models.zip::_Measures.tmdl",
            "Business Definition": business,
            "Technical Notes": "Current model measure extracted from TMDL static inspection.",
            "Dependencies": extract_dependencies(expr),
            "Replacement Measure": "",
            "Owner": "Finance / BI owner to confirm",
            "Validation Status": "Pending regression test",
        })
        pending_doc = []
        i += 1
    return rows


def parse_vnext_measures(dax: Path) -> list[dict[str, str]]:
    text = dax.read_text(encoding="utf-8")
    pattern = re.compile(r"MEASURE\s+'([^']+)'\[([^\]]+)\]\s*=\s*(.*?)(?=\nMEASURE\s+'|\n-+\n--\s+CALCULATION GROUP:|\Z)", re.S)
    rows: list[dict[str, str]] = []
    for table, name, body in pattern.findall(text):
        fmt = "General"
        fm = re.search(r"\n\s*FORMAT_STRING\s*=\s*([^\n]+)", body)
        if fm:
            fmt = fm.group(1).strip().strip('"')
        folder = ""
        dm = re.search(r"\n\s*DISPLAY_FOLDER\s*=\s*([^\n]+)", body)
        if dm:
            folder = dm.group(1).strip().strip('"')
        desc = ""
        desc_match = re.search(r"\n\s*DESCRIPTION\s*=\s*\"(.*?)\"\s*$", body, re.S)
        if desc_match:
            desc = clean(desc_match.group(1))
        expr = re.split(r"\n\s*(?:FORMAT_STRING|DISPLAY_FOLDER|DESCRIPTION)\s*=", body, maxsplit=1)[0]
        expr = clean(expr)
        rows.append({
            "Work Item Type": "Task",
            "Title": f"vNext measure register: {name}",
            "Area Path": "Finance\\Semantic Model",
            "Tags": "PowerBI;SemanticModel;MeasureRegister;vNext",
            "Model Name": "sm_finance_core",
            "Object Type": "Measure",
            "Table Name": table,
            "Measure Name": name,
            "Definition": expr,
            "Format String": fmt,
            "Display Folder": folder,
            "Hidden": "No",
            "Lifecycle Status": "vNext - Proposed",
            "Governance Status": "Proposed side-by-side implementation; business validation required",
            "Source Artefact": str(dax.relative_to(REPO)),
            "Business Definition": desc or "Proposed vNext measure; definition requires confirmation",
            "Technical Notes": "Proposed vNext measure from non-destructive implementation script.",
            "Dependencies": extract_dependencies(expr),
            "Replacement Measure": "To be mapped during regression testing",
            "Owner": "Finance / BI owner to confirm",
            "Validation Status": "Pending regression test",
        })
    return rows


def main() -> None:
    if not ZIP_PATH.exists():
        raise SystemExit(f"Missing {ZIP_PATH}")
    with TemporaryDirectory() as tmp:
        with zipfile.ZipFile(ZIP_PATH) as zf:
            zf.extractall(tmp)
        tmdl = next(Path(tmp).glob("*/definition/tables/_Measures.tmdl"))
        rows = parse_tmdl_measures(tmdl)
    rows.extend(parse_vnext_measures(VNEXT_DAX))
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    current = sum(1 for r in rows if r["Lifecycle Status"].startswith("Current"))
    vnext = sum(1 for r in rows if r["Lifecycle Status"].startswith("vNext"))
    missing_defs = sum(1 for r in rows if r["Business Definition"].startswith("Missing"))
    OUT_MD.write_text(f"""# Azure DevOps Measures Register

## Purpose

`azure_devops_measures_register.csv` is an Azure DevOps-friendly register of the `sm_finance_core` measures. It is designed for upload, backlog triage, governance review, or conversion into Azure DevOps work items.

## Contents

- Current PBIP measures extracted from `_Measures.tmdl`: **{current}**
- Proposed vNext measures extracted from `docs/implementation/refactored_measures_and_calculation_groups.dax`: **{vnext}**
- Total register rows: **{len(rows)}**
- Current measures missing business definitions/descriptions in TMDL: **{missing_defs}**

## Azure DevOps import notes

The CSV includes Azure DevOps-oriented columns such as `Work Item Type`, `Title`, `Area Path`, and `Tags`, plus model governance fields such as measure name, definition, format string, display folder, lifecycle status, governance status, owner, dependencies, and validation status.

Recommended Azure DevOps import approach:

1. Import the CSV into a dedicated governance backlog or query it from Excel.
2. Keep `Work Item Type` as `Task` unless your process template uses a custom work item type.
3. Map `Title`, `Area Path`, and `Tags` to native Azure DevOps fields.
4. Keep the remaining columns as imported fields in Excel, a wiki table, or custom fields if your Azure DevOps process supports them.
5. Use `Lifecycle Status`, `Governance Status`, and `Validation Status` to prioritize review and regression testing.

## Required governance actions

- Confirm business definitions for rows where `Business Definition` starts with `Missing`.
- Validate current-vs-vNext replacement mappings before report migration.
- Update `Replacement Measure` once a current measure is superseded by a vNext measure.
- Attach DAX regression evidence to Azure DevOps tasks before changing lifecycle status to `Active` or `Deprecated`.
""", encoding="utf-8")
    print(f"Wrote {OUT_CSV.relative_to(REPO)} with {len(rows)} rows ({current} current, {vnext} vNext)")
    print(f"Wrote {OUT_MD.relative_to(REPO)}")


if __name__ == "__main__":
    main()
