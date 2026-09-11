"""Build a privacy-safe per-category numeric coverage receipt."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def build_receipt(source: dict[str, Any]) -> dict[str, Any]:
    categories: dict[str, dict[str, Any]] = {}
    for category, payload in source["categories"].items():
        fields = [
            field
            for field in payload["fields"]
            if field.get("descriptive_numeric_summary") is not None
        ]
        if not fields:
            raise ValueError(f"category has no numeric field summary: {category}")
        summaries = [field["descriptive_numeric_summary"] for field in fields]
        participants = [field["unique_participants_with_value"] for field in fields]
        categories[category] = {
            "status": "real_numeric_source_data_present",
            "field_count": len(fields),
            "field_keys": [f"{field['source']}:{field['field']}" for field in fields],
            "min_nonmissing_rows_across_fields": min(
                summary["n"] for summary in summaries
            ),
            "max_nonmissing_rows_across_fields": max(
                summary["n"] for summary in summaries
            ),
            "min_unique_participants_across_fields": min(participants),
            "max_unique_participants_across_fields": max(participants),
        }
    return {
        "schema_version": "nhanes-category-numeric-coverage-v1",
        "generated_by": "scripts/build_category_numeric_coverage_receipt.py",
        "generated_at": "2026-09-11",
        "source_receipt": "CATEGORY_DATA_RECEIPT_2026-09-11",
        "category_count": len(categories),
        "categories": categories,
        "boundary": {
            "participant_ids_emitted": False,
            "raw_rows_emitted": False,
            "measurements_emitted": False,
            "clinical_validity": "not_established",
            "numeric_category_age": "withheld",
            "e005_status": "blocked",
            "interpretation": (
                "non-missing public-use source counts by category; "
                "not a clinical reference interval or harmonized cohort"
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    source = json.loads(args.receipt.read_text(encoding="utf-8"))
    serialized = (
        json.dumps(build_receipt(source), indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    if args.check:
        if args.output.read_bytes() != serialized:
            print("ERROR: category numeric coverage receipt drift")
            return 3
        print(f"category numeric coverage receipt verified: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(serialized)
    print(f"category numeric coverage receipt written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
