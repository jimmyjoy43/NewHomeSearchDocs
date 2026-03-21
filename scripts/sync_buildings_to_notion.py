#!/usr/bin/env python3
"""
sync_buildings_to_notion.py

Reads data/buildings.csv and upserts each row into the Notion
"Apartment Units" database.

Upsert logic: match on (building_name + unit_number). If a page
with that combo already exists, update it. If not, create it.

Required environment variables (set in .env locally or GitHub Secrets in CI):
    NOTION_TOKEN          - Your Notion internal integration token
    NOTION_DATABASE_ID    - The ID of the "Apartment Units" database

Usage:
    python scripts/sync_buildings_to_notion.py
    python scripts/sync_buildings_to_notion.py --dry-run
"""

import os
import sys
import csv
import argparse
from datetime import date, datetime

try:
    from notion_client import Client
    from notion_client.errors import APIResponseError
except ImportError:
    print("FAIL: notion-client is not installed. Run: pip install notion-client")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional; env vars may be set directly


# --------------------------------------------------------------------
# Config
# --------------------------------------------------------------------

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")
BUILDINGS_CSV = "data/buildings.csv"

# Scores come in as strings; these fields get cast to numbers
NUMERIC_FIELDS = {
    "base_rent", "net_effective_rent", "lease_term_months",
    "application_fee", "admin_fee", "security_deposit",
    "parking_cost", "pet_rent", "sqft",
    "quiet_score", "management_score", "amenity_score",
    "adult_vibe_score", "nice_to_have_yes_count"
}

# Checkbox fields - any truthy string ("yes", "true", "1") -> checked
CHECKBOX_FIELDS = {
    "in_unit_laundry", "dishwasher", "central_ac", "package_room",
    "controlled_access", "gym", "pool", "coworking", "conference_room",
    "ev_charging", "rooftop", "essential_amenities_all_yes",
    "deep_research_done", "review_scan_done", "news_scan_done"
}

# Date fields - must be YYYY-MM-DD or empty
DATE_FIELDS = {"available_date", "tour_date", "last_updated"}

# The Notion Title property (always required)
TITLE_FIELD = "building_name"


# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------

def parse_bool(value):
    return str(value).strip().lower() in ("yes", "true", "1", "x")


def parse_number(value):
    if value is None or str(value).strip() == "":
        return None
    try:
        f = float(str(value).replace(",", "").replace("$", ""))
        return int(f) if f == int(f) else f
    except ValueError:
        return None


def parse_date(value):
    if not value or str(value).strip() == "":
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(str(value).strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def build_notion_properties(row):
    """
    Convert a buildings.csv row dict into a Notion properties payload.
    Only includes fields that have a value; skips empties to avoid
    overwriting existing Notion data with blanks on partial updates.
    """
    props = {}

    for key, value in row.items():
        if value is None or str(value).strip() == "":
            continue

        if key == TITLE_FIELD:
            unit = row.get("unit_number", "").strip()
            title_text = value.strip()
            if unit:
                title_text = f"{title_text} | Unit {unit}"
            props["Name"] = {
                "title": [{"text": {"content": title_text}}]
            }

        elif key in CHECKBOX_FIELDS:
            props[key] = {"checkbox": parse_bool(value)}

        elif key in NUMERIC_FIELDS:
            num = parse_number(value)
            if num is not None:
                props[key] = {"number": num}

        elif key in DATE_FIELDS:
            d = parse_date(value)
            if d:
                props[key] = {"date": {"start": d}}

        else:
            # Everything else goes in as rich text
            props[key] = {
                "rich_text": [{"text": {"content": str(value).strip()[:2000]}}]
            }

    return props


def get_existing_pages(client, database_id):
    """
    Fetch all pages in the database and return a dict keyed by
    (building_name_lower, unit_number_lower) -> page_id.
    """
    existing = {}
    cursor = None

    while True:
        kwargs = {"database_id": database_id, "page_size": 100}
        if cursor:
            kwargs["start_cursor"] = cursor

        try:
            response = client.databases.query(**kwargs)
        except APIResponseError as e:
            print(f"FAIL: Notion API error while fetching pages: {e}")
            sys.exit(1)

        for page in response.get("results", []):
            props = page.get("properties", {})

            # Extract building_name from the Name title property
            name_prop = props.get("Name", {})
            title_parts = name_prop.get("title", [])
            full_title = "".join(t.get("plain_text", "") for t in title_parts)

            building_name_prop = props.get("building_name", {})
            rt = building_name_prop.get("rich_text", [])
            building_name = "".join(t.get("plain_text", "") for t in rt).strip().lower()

            unit_prop = props.get("unit_number", {})
            unit_rt = unit_prop.get("rich_text", [])
            unit_number = "".join(t.get("plain_text", "") for t in unit_rt).strip().lower()

            # Fall back to parsing title if building_name field is empty
            if not building_name and "|" in full_title:
                building_name = full_title.split("|")[0].strip().lower()

            key = (building_name, unit_number)
            existing[key] = page["id"]

        if not response.get("has_more"):
            break
        cursor = response.get("next_cursor")

    return existing


# --------------------------------------------------------------------
# Core sync
# --------------------------------------------------------------------

def sync(dry_run=False):
    if not NOTION_TOKEN:
        print("FAIL: NOTION_TOKEN environment variable is not set.")
        sys.exit(1)
    if not NOTION_DATABASE_ID:
        print("FAIL: NOTION_DATABASE_ID environment variable is not set.")
        sys.exit(1)

    client = Client(auth=NOTION_TOKEN)

    # Read CSV
    try:
        with open(BUILDINGS_CSV, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"FAIL: {BUILDINGS_CSV} not found. Run from the repo root.")
        sys.exit(1)

    if not rows:
        print(f"OK: {BUILDINGS_CSV} has no data rows. Nothing to sync.")
        return

    print(f"Read {len(rows)} row(s) from {BUILDINGS_CSV}.")

    if dry_run:
        print("DRY RUN: No changes will be written to Notion.")

    # Fetch existing pages for upsert logic
    print("Fetching existing Notion pages...")
    existing = get_existing_pages(client, NOTION_DATABASE_ID)
    print(f"Found {len(existing)} existing page(s) in database.")

    created = 0
    updated = 0
    skipped = 0
    errors = 0

    for row in rows:
        building_name = str(row.get("building_name", "")).strip()
        unit_number = str(row.get("unit_number", "")).strip()

        if not building_name:
            print(f"SKIP: Row with empty building_name skipped.")
            skipped += 1
            continue

        key = (building_name.lower(), unit_number.lower())
        properties = build_notion_properties(row)

        if not properties.get("Name"):
            print(f"SKIP: Could not build Name property for '{building_name}'. Skipping.")
            skipped += 1
            continue

        if dry_run:
            action = "UPDATE" if key in existing else "CREATE"
            print(f"  [{action}] {building_name} | unit: '{unit_number}'")
            continue

        try:
            if key in existing:
                page_id = existing[key]
                client.pages.update(page_id=page_id, properties=properties)
                print(f"  UPDATED: {building_name} | unit: '{unit_number}'")
                updated += 1
            else:
                client.pages.create(
                    parent={"database_id": NOTION_DATABASE_ID},
                    properties=properties
                )
                print(f"  CREATED: {building_name} | unit: '{unit_number}'")
                created += 1

        except APIResponseError as e:
            print(f"  ERROR: {building_name} | unit: '{unit_number}' -> {e}")
            errors += 1

    if not dry_run:
        print(
            f"\nSync complete. "
            f"Created: {created}, Updated: {updated}, "
            f"Skipped: {skipped}, Errors: {errors}"
        )
        if errors > 0:
            sys.exit(1)


# --------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync buildings.csv to Notion")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would happen without writing to Notion"
    )
    args = parser.parse_args()
    sync(dry_run=args.dry_run)
