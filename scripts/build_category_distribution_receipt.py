"""Build privacy-safe distribution summaries for one real field per category."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


def _parse_fields(values: list[str]) -> dict[str, tuple[Path, str]]:
    result: dict[str, tuple[Path, str]] = {}
    for value in values:
        category, filename, field = value.split("=", 2)
        if category in result:
            raise ValueError(f"duplicate category: {category}")
        result[category] = (Path(filename), field)
    if len(result) != 17:
        raise ValueError(f"expected 17 category fields, got {len(result)}")
    return result


def _summary(path: Path, field: str) -> dict[str, Any]:
    frame = pd.read_sas(path, format="xport", encoding="utf-8")
    if "SEQN" not in frame.columns or field not in frame.columns:
        raise ValueError(f"missing SEQN or {field} in {path.name}")
    numeric = pd.to_numeric(frame[field], errors="coerce").dropna()
    if numeric.empty:
        raise ValueError(f"no numeric values for {field} in {path.name}")
    quantiles = numeric.quantile([0.05, 0.25, 0.5, 0.75, 0.95])
    return {
        "source": path.name,
        "field": field,
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper(),
        "source_rows": int(len(frame)),
        "n": int(len(numeric)),
        "unique_participants_with_value": int(
            frame.loc[
                pd.to_numeric(frame[field], errors="coerce").notna(), "SEQN"
            ].nunique()
        ),
        "mean": round(float(numeric.mean()), 6),
        "min": round(float(numeric.min()), 6),
        "q05": round(float(quantiles.loc[0.05]), 6),
        "q25": round(float(quantiles.loc[0.25]), 6),
        "median": round(float(quantiles.loc[0.5]), 6),
        "q75": round(float(quantiles.loc[0.75]), 6),
        "q95": round(float(quantiles.loc[0.95]), 6),
        "max": round(float(numeric.max()), 6),
    }


def build_receipt(fields: dict[str, tuple[Path, str]]) -> dict[str, Any]:
    distributions = {
        category: _summary(path, field)
        for category, (path, field) in sorted(fields.items())
    }
    return {
        "schema_version": "nhanes-category-distribution-receipt-v1",
        "generated_by": "scripts/build_category_distribution_receipt.py",
        "generated_at": "2026-09-11",
        "category_count": len(distributions),
        "distributions": distributions,
        "boundary": {
            "participant_ids_emitted": False,
            "raw_rows_emitted": False,
            "measurements_emitted": False,
            "interpretation": (
                "unfiltered public-use numeric or coded distributions for one "
                "representative field per category; not clinical reference intervals"
            ),
            "clinical_validity": "not_established",
            "numeric_category_age": "withheld",
            "e005_status": "blocked",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--field", action="append", required=True, metavar="CATEGORY=PATH=FIELD"
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    serialized = (
        json.dumps(build_receipt(_parse_fields(args.field)), indent=2, sort_keys=True)
        + "\n"
    ).encode("utf-8")
    if args.check:
        if args.output.read_bytes() != serialized:
            print("ERROR: category distribution receipt drift")
            return 3
        print(f"category distribution receipt verified: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(serialized)
    print(f"category distribution receipt written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
