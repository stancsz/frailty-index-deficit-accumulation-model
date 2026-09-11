"""Build an aggregate, privacy-safe quality summary for every category."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def build_summary(source: dict[str, Any]) -> dict[str, Any]:
    categories: dict[str, dict[str, Any]] = {}
    for category, payload in source["categories"].items():
        fields = payload["fields"]
        if not fields:
            raise ValueError(f"category has no quality fields: {category}")
        missingness = [
            field["missing_rows"] / field["source_rows"]
            for field in fields
            if field["source_rows"]
        ]
        special_fields = [
            field for field in fields if field["candidate_special_code_rows"]
        ]
        special_labels = sorted(
            {
                code
                for field in special_fields
                for code in field["candidate_special_code_rows"]
            }
        )
        categories[category] = {
            "quality_status": payload["quality_status"],
            "field_count": len(fields),
            "source_file_count": len({field["source"] for field in fields}),
            "min_source_rows": min(field["source_rows"] for field in fields),
            "max_source_rows": max(field["source_rows"] for field in fields),
            "min_nonmissing_rows": min(field["nonmissing_rows"] for field in fields),
            "max_nonmissing_rows": max(field["nonmissing_rows"] for field in fields),
            "min_unique_participants": min(
                field["unique_participants_with_value"] for field in fields
            ),
            "max_unique_participants": max(
                field["unique_participants_with_value"] for field in fields
            ),
            "min_missingness_rate": min(missingness),
            "max_missingness_rate": max(missingness),
            "fields_with_candidate_special_codes": len(special_fields),
            "candidate_special_code_labels": special_labels,
            "max_candidate_special_code_rows_in_field": max(
                (
                    sum(field["candidate_special_code_rows"].values())
                    for field in fields
                ),
                default=0,
            ),
        }
    return {
        "schema_version": "nhanes-category-quality-summary-v1",
        "generated_by": "scripts/build_category_quality_summary.py",
        "generated_at": "2026-09-11",
        "source_receipt": "CATEGORY_QUALITY_RECEIPT_2026-09-11",
        "category_count": len(categories),
        "categories": categories,
        "boundary": {
            "participant_ids_emitted": False,
            "raw_rows_emitted": False,
            "measurements_emitted": False,
            "values_filtered": False,
            "clinical_validity": "not_established",
            "numeric_category_age": "withheld",
            "e005_status": "blocked",
            "interpretation": (
                "aggregate source quality counts; candidate special codes are "
                "reported but not classified or removed"
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
        json.dumps(build_summary(source), indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    if args.check:
        if args.output.read_bytes() != serialized:
            print("ERROR: category quality summary drift")
            return 3
        print(f"category quality summary verified: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(serialized)
    print(f"category quality summary written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
