"""Build a cycle-by-category source coverage matrix from checked receipts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def build_matrix(receipts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    categories = sorted(
        {
            category
            for receipt in receipts.values()
            for category in receipt["categories"]
        }
    )
    matrix: dict[str, dict[str, dict[str, Any]]] = {}
    for cycle, receipt in receipts.items():
        cycle_rows: dict[str, dict[str, Any]] = {}
        absences = receipt.get("not_collected_in_cycle", {})
        for category in categories:
            payload = receipt["categories"].get(category)
            if payload is None:
                cycle_rows[category] = {
                    "status": "absent_in_receipt",
                    "absence_reason": absences.get(
                        category, "not mapped in this receipt"
                    ),
                }
                continue
            fields = payload["fields"]
            participant_counts = [
                field["unique_participants_with_value"] for field in fields
            ]
            cycle_rows[category] = {
                "status": "real_numeric_source_data_present",
                "field_count": len(fields),
                "source_files": sorted({field["source"] for field in fields}),
                "min_unique_participants": min(participant_counts),
                "max_unique_participants": max(participant_counts),
            }
        matrix[cycle] = cycle_rows
    return {
        "schema_version": "nhanes-category-cycle-matrix-v1",
        "generated_by": "scripts/build_category_cycle_matrix.py",
        "generated_at": "2026-09-11",
        "category_count": len(categories),
        "categories": categories,
        "cycles": matrix,
        "boundary": {
            "participant_ids_emitted": False,
            "raw_rows_emitted": False,
            "measurements_emitted": False,
            "cross_cycle_joins_performed": False,
            "clinical_validity": "not_established",
            "numeric_category_age": "withheld",
            "e005_status": "blocked",
            "interpretation": (
                "cycle-separated source coverage matrix; absent categories are "
                "not silently treated as missing patient measurements"
            ),
        },
    }


def parse_receipts(values: list[str]) -> dict[str, dict[str, Any]]:
    receipts: dict[str, dict[str, Any]] = {}
    for value in values:
        try:
            cycle, filename = value.split("=", 1)
        except ValueError as exc:
            raise ValueError(f"expected CYCLE=PATH, got {value!r}") from exc
        if cycle in receipts:
            raise ValueError(f"duplicate cycle: {cycle}")
        receipts[cycle] = json.loads(Path(filename).read_text(encoding="utf-8"))
    if not receipts:
        raise ValueError("at least one receipt is required")
    return receipts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    serialized = (
        json.dumps(build_matrix(parse_receipts(args.receipt)), indent=2, sort_keys=True)
        + "\n"
    ).encode("utf-8")
    if args.check:
        if args.output.read_bytes() != serialized:
            print("ERROR: category cycle matrix drift")
            return 3
        print(f"category cycle matrix verified: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(serialized)
    print(f"category cycle matrix written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
