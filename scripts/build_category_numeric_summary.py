"""Build the compact privacy-safe numeric summary from a category receipt."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def build_summary(receipt: dict[str, Any]) -> dict[str, Any]:
    fields: dict[str, dict[str, Any]] = {}
    for category in receipt["categories"].values():
        for field in category["fields"]:
            numeric = field.get("descriptive_numeric_summary")
            if numeric is None:
                continue
            key = f"{field['source'].removesuffix('.XPT')}:{field['field']}"
            fields[key] = {
                name: numeric[name] for name in ("n", "mean", "median", "min", "max")
            }
    return {
        "schema_version": "nhanes-category-numeric-summary-v1",
        "generated_by": "scripts/build_category_numeric_summary.py",
        "generated_at": "2026-09-11",
        "source_boundary": (
            "unfiltered non-missing public-use source distributions; "
            "not clinical reference intervals"
        ),
        "fields": fields,
        "clinical_gate": receipt["boundary"]["e005_status"],
        "numeric_category_age": receipt["boundary"]["numeric_category_age"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = json.loads(args.receipt.read_text(encoding="utf-8"))
    serialized = (json.dumps(build_summary(payload), indent=2) + "\n").encode("utf-8")
    if args.check:
        if args.output.read_bytes() != serialized:
            print("ERROR: numeric summary drift")
            return 3
        print(f"numeric summary verified: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(serialized)
    print(f"numeric summary written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
