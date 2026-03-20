#!/usr/bin/env python3
"""
generate_markdown_reports.py

Reads data/buildings.csv and regenerates two docs:
  - docs/02_neighborhood_breadth_scan.md  (status table, auto-section)
  - docs/10_unit_comparison.md            (sortable comparison table)

Safe to run repeatedly. Only the auto-generated sections are touched;
any manually written content above the AUTO-GENERATED marker is preserved.

Usage:
    python scripts/generate_markdown_reports.py
    python scripts/generate_markdown_reports.py --dry-run
"""

import csv
import argparse
from pathlib import Path
from datetime import date

# --------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent
BUILDINGS_CSV = REPO_ROOT / "data" / "buildings.csv"
BREADTH_SCAN_MD = REPO_ROOT / "docs" / "02_neighborhood_breadth_scan.md"
COMPARISON_MD = REPO_ROOT / "docs" / "10_unit_comparison.md"

AUTO_MARKER = "<!-- AUTO-GENERATED: do not edit below this line -->"


# --------------------------------------------------------------------
# CSV reader
# --------------------------------------------------------------------

def load_buildings():
    if not BUILDINGS_CSV.exists():
        print(f"FAIL: {BUILDINGS_CSV} not found.")
        return []
    with open(BUILDINGS_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# --------------------------------------------------------------------
# Breadth scan table generator
# --------------------------------------------------------------------

def build_breadth_scan_section(rows):
    today = date.today().isoformat()

    lines = [
        AUTO_MARKER,
        f"\n_Last regenerated: {today}_\n",
        "| Building | Address | Neighborhood | Distance from Camden | Class | Management Score | Quiet Score | Status | Notes |",
        "|---|---|---|---|---|---|---|---|---|",
    ]

    for row in rows:
        name = row.get("building_name", "").strip()
        if not name:
            continue

        url = row.get("url", "").strip()
        name_cell = f"[{name}]({url})" if url else name

        lines.append(
            f"| {name_cell} "
            f"| {row.get('address', '')} "
            f"| {row.get('neighborhood', '')} "
            f"| "  # distance: not in schema, left blank
            f"| "  # class: not in schema, left blank
            f"| {row.get('management_score', '')} "
            f"| {row.get('quiet_score', '')} "
            f"| {_infer_status(row)} "
            f"| {row.get('remarks', '')[:80]} |"
        )

    return "\n".join(lines)


def _infer_status(row):
    """Infer a human-readable status from workflow flags in the row."""
    if row.get("tour_date", "").strip():
        return "Touring"
    deep = str(row.get("deep_research_done", "")).strip().lower()
    review = str(row.get("review_scan_done", "")).strip().lower()
    if deep in ("yes", "true", "1"):
        return "Deep research done"
    if review in ("yes", "true", "1"):
        return "Basic scan done"
    return "Not started"


# --------------------------------------------------------------------
# Unit comparison table generator
# --------------------------------------------------------------------

def build_comparison_section(rows):
    today = date.today().isoformat()

    # Sort by net_effective_rent ascending, blanks last
    def sort_key(r):
        v = r.get("net_effective_rent", "") or r.get("base_rent", "")
        try:
            return float(str(v).replace(",", "").replace("$", ""))
        except ValueError:
            return 9999999

    rows_sorted = sorted(rows, key=sort_key)

    lines = [
        AUTO_MARKER,
        f"\n_Last regenerated: {today}. Sorted by net effective rent ascending._\n",
        "| Building | Unit | Bed/Bath | sqft | Base Rent | Net Effective | Available | Cat | W/D | Quiet | Mgmt | Adult Vibe | Tour Date |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]

    for row in rows_sorted:
        name = row.get("building_name", "").strip()
        if not name:
            continue

        def yn(field):
            v = str(row.get(field, "")).strip().lower()
            return "Y" if v in ("yes", "true", "1") else ("N" if v in ("no", "false", "0") else v)

        def money(field):
            v = row.get(field, "").strip()
            if not v:
                return ""
            try:
                return f"${int(float(v.replace(',', '').replace('$', ''))):,}"
            except ValueError:
                return v

        lines.append(
            f"| {name} "
            f"| {row.get('unit_number', '')} "
            f"| {row.get('bed_bath', '')} "
            f"| {row.get('sqft', '')} "
            f"| {money('base_rent')} "
            f"| {money('net_effective_rent')} "
            f"| {row.get('available_date', '')} "
            f"| {yn('cat_policy')} "
            f"| {yn('in_unit_laundry')} "
            f"| {row.get('quiet_score', '')} "
            f"| {row.get('management_score', '')} "
            f"| {row.get('adult_vibe_score', '')} "
            f"| {row.get('tour_date', '')} |"
        )

    return "\n".join(lines)


# --------------------------------------------------------------------
# File writers
# --------------------------------------------------------------------

def update_file_with_auto_section(filepath, new_auto_section, dry_run=False):
    """
    If the file already has an AUTO_MARKER, replace everything after it.
    If not, append the auto section to whatever is already there.
    """
    filepath = Path(filepath)

    if filepath.exists():
        existing = filepath.read_text(encoding="utf-8")
    else:
        existing = ""

    if AUTO_MARKER in existing:
        before = existing.split(AUTO_MARKER)[0].rstrip()
        new_content = before + "\n\n" + new_auto_section + "\n"
    else:
        new_content = existing.rstrip() + "\n\n" + new_auto_section + "\n"

    if dry_run:
        print(f"DRY RUN: would write {len(new_content)} chars to {filepath}")
        return

    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(new_content, encoding="utf-8")
    print(f"  WROTE: {filepath}")


def write_comparison_doc(auto_section, dry_run=False):
    """
    The comparison doc is fully auto-generated each run.
    Prepend a static header.
    """
    header = (
        "# Unit Comparison Table\n\n"
        "All units currently in `data/buildings.csv`, sorted by net effective rent.\n"
        "Edit data in the CSV, not this file. It is regenerated on every push.\n\n"
    )
    content = header + auto_section + "\n"

    if dry_run:
        print(f"DRY RUN: would write {len(content)} chars to {COMPARISON_MD}")
        return

    COMPARISON_MD.parent.mkdir(parents=True, exist_ok=True)
    COMPARISON_MD.write_text(content, encoding="utf-8")
    print(f"  WROTE: {COMPARISON_MD}")


# --------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------

def main(dry_run=False):
    rows = load_buildings()

    if not rows:
        print("No data rows found. Skipping report generation.")
        return

    data_rows = [r for r in rows if r.get("building_name", "").strip()]
    print(f"Loaded {len(data_rows)} building row(s) from CSV.")

    print("Updating 02_neighborhood_breadth_scan.md...")
    breadth_section = build_breadth_scan_section(data_rows)
    update_file_with_auto_section(BREADTH_SCAN_MD, breadth_section, dry_run)

    print("Writing 10_unit_comparison.md...")
    comparison_section = build_comparison_section(data_rows)
    write_comparison_doc(comparison_section, dry_run)

    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Regenerate markdown reports from CSV")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would happen without writing files")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
