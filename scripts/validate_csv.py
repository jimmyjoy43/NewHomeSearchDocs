#!/usr/bin/env python3
"""
validate_csv.py

Validates apartment search CSV files before Notion sync or report generation.
Called by GitHub Actions on every push that touches data/*.csv.

Usage:
    python scripts/validate_csv.py data/buildings.csv
    python scripts/validate_csv.py data/tours.csv
    python scripts/validate_csv.py data/contacts.csv
    python scripts/validate_csv.py data/decisions.csv
"""

import sys
import csv
from datetime import datetime

# --------------------------------------------------------------------
# Schema definitions
# --------------------------------------------------------------------

SCHEMAS = {
    "buildings.csv": {
        "required_columns": [
            "building_name", "address", "neighborhood", "url",
            "unit_number", "bed_bath", "sqft", "base_rent",
            "net_effective_rent", "available_date", "lease_term_months",
            "application_fee", "admin_fee", "security_deposit",
            "parking_cost", "pet_rent", "cat_policy", "in_unit_laundry",
            "dishwasher", "central_ac", "package_room", "controlled_access",
            "gym", "pool", "coworking", "conference_room", "ev_charging",
            "rooftop", "quiet_score", "management_score", "amenity_score",
            "adult_vibe_score", "essential_amenities_all_yes",
            "missing_essential_amenities", "nice_to_have_yes_count",
            "tour_date", "deep_research_done", "review_scan_done",
            "news_scan_done", "remarks", "last_updated"
        ],
        "nonempty": ["building_name", "address"],
        "numeric": ["base_rent", "quiet_score", "management_score",
                    "amenity_score", "adult_vibe_score"],
        "score_range": ["quiet_score", "management_score",
                        "amenity_score", "adult_vibe_score"],
        "date_fields": ["available_date", "tour_date", "last_updated"],
    },
    "contacts.csv": {
        "required_columns": [
            "building_name", "contact_name", "role", "phone", "email",
            "date_contacted", "method", "response_received", "notes",
            "last_updated"
        ],
        "nonempty": ["building_name"],
        "numeric": [],
        "score_range": [],
        "date_fields": ["date_contacted", "last_updated"],
    },
    "tours.csv": {
        "required_columns": [
            "building_name", "unit_number", "tour_date", "tour_type",
            "leasing_agent", "first_impression_score", "noise_observation",
            "unit_condition", "common_area_condition", "staff_responsiveness",
            "questions_answered", "red_flags", "follow_up_needed",
            "notes", "last_updated"
        ],
        "nonempty": ["building_name", "tour_date"],
        "numeric": ["first_impression_score"],
        "score_range": ["first_impression_score"],
        "date_fields": ["tour_date", "last_updated"],
    },
    "decisions.csv": {
        "required_columns": [
            "date", "building_name", "unit_number", "decision",
            "reason", "next_action", "decided_by", "last_updated"
        ],
        "nonempty": ["date", "building_name", "decision"],
        "numeric": [],
        "score_range": [],
        "date_fields": ["date", "last_updated"],
    },
}


# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------

def is_numeric(value):
    if value == "" or value is None:
        return True  # allow empty numeric fields
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_valid_score(value):
    if value == "" or value is None:
        return True  # allow empty score fields
    try:
        v = float(value)
        return 1.0 <= v <= 5.0
    except ValueError:
        return False


def is_valid_date(value):
    if value == "" or value is None:
        return True  # allow empty date fields
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            datetime.strptime(value, fmt)
            return True
        except ValueError:
            continue
    return False


# --------------------------------------------------------------------
# Core validator
# --------------------------------------------------------------------

def validate(filepath):
    filename = filepath.split("/")[-1]

    if filename not in SCHEMAS:
        print(f"WARNING: No schema defined for {filename}. Skipping validation.")
        return True

    schema = SCHEMAS[filename]
    errors = []
    warnings = []

    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            actual_columns = reader.fieldnames or []
            rows = list(reader)
    except FileNotFoundError:
        print(f"FAIL: File not found: {filepath}")
        return False
    except Exception as e:
        print(f"FAIL: Could not read {filepath}: {e}")
        return False

    # 1. Column presence check
    missing_cols = [c for c in schema["required_columns"] if c not in actual_columns]
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")

    # 2. Extra columns warning (not a failure, just noise)
    extra_cols = [c for c in actual_columns if c not in schema["required_columns"]]
    if extra_cols:
        warnings.append(f"Extra columns not in schema (ok, just noting): {extra_cols}")

    # If columns are broken, stop here - row-level checks will be misleading
    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        return False

    if not rows:
        print(f"OK: {filename} has only a header row and no data. Nothing to validate.")
        return True

    # 3. Row-level checks
    for i, row in enumerate(rows, start=2):  # start=2 because row 1 is header

        for col in schema["nonempty"]:
            if not row.get(col, "").strip():
                errors.append(f"Row {i}: '{col}' is empty (required)")

        for col in schema["numeric"]:
            val = row.get(col, "")
            if not is_numeric(val):
                errors.append(f"Row {i}: '{col}' is not numeric (got: '{val}')")

        for col in schema["score_range"]:
            val = row.get(col, "")
            if not is_valid_score(val):
                errors.append(
                    f"Row {i}: '{col}' score out of range 1-5 (got: '{val}')"
                )

        for col in schema["date_fields"]:
            val = row.get(col, "")
            if not is_valid_date(val):
                errors.append(
                    f"Row {i}: '{col}' is not a valid date (got: '{val}'). "
                    f"Use YYYY-MM-DD."
                )

    # 4. Report
    for w in warnings:
        print(f"WARN: {w}")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        print(f"\nValidation FAILED for {filename}: {len(errors)} error(s).")
        return False

    print(f"OK: {filename} passed validation. {len(rows)} data row(s) checked.")
    return True


# --------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_csv.py <path/to/file.csv>")
        sys.exit(1)

    success = validate(sys.argv[1])
    sys.exit(0 if success else 1)
