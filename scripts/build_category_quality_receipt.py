"""Audit missingness and candidate NHANES special codes without cleaning data.

This is intentionally an audit, not an imputation or clinical preprocessing
step. Candidate codes are counted and retained as source observations until
the official field codebooks and intended-use rules are reviewed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from build_category_data_receipt import (  # noqa: E402
    FIELD_MAP as PRIMARY_FIELD_MAP,
    _find,
    _read_source,
)  # noqa: E402


SCHEMA_VERSION = 1
CANDIDATE_SPECIAL_CODES = (7, 9, 77, 99, 777, 999, 7777, 9999, 99999)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--scope",
        choices=("primary", "2013_2014", "2017_2018_liver"),
        default="primary",
    )
    parser.add_argument("--check", action="store_true")
    return parser


def _field_audit(frame: Any, source: str, field: str) -> dict[str, Any]:
    if "SEQN" not in frame.columns or field not in frame.columns:
        raise ValueError(f"{source} is missing required field {field}")
    values = frame[["SEQN", field]]
    present = values.dropna(subset=[field])
    numeric = pd.to_numeric(present[field], errors="coerce")
    candidate_counts: dict[str, int] = {}
    candidate_participants: dict[str, int] = {}
    for code in CANDIDATE_SPECIAL_CODES:
        matches = present.loc[numeric == code]
        if len(matches):
            candidate_counts[str(code)] = int(len(matches))
            candidate_participants[str(code)] = int(matches["SEQN"].nunique())
    return {
        "source": source,
        "field": field,
        "source_rows": int(len(values)),
        "missing_rows": int(values[field].isna().sum()),
        "nonmissing_rows": int(len(present)),
        "unique_participants_with_value": int(present["SEQN"].nunique()),
        "numeric_rows": int(numeric.notna().sum()),
        "candidate_special_code_rows": candidate_counts,
        "candidate_special_code_unique_participants": candidate_participants,
        "interpretation": "candidate code counts only; no values were removed or classified as invalid",
    }


def _scope_map(scope: str) -> tuple[str, dict[str, tuple[tuple[str, str], ...]]]:
    if scope == "primary":
        return (
            "NHANES_2011_2012 plus explicitly mapped older component cycles",
            PRIMARY_FIELD_MAP,
        )
    if scope == "2013_2014":
        from build_category_cycle_receipt import FIELD_MAP as cycle_field_map

        return "NHANES_2013_2014", cycle_field_map
    return "NHANES_2017_2018", {
        "liver_health": tuple(
            ("LUX_J.XPT", field)
            for field in (
                "LUAXSTAT",
                "LUANMVGP",
                "LUARXNC",
                "LUARXND",
                "LUARXIN",
                "LUAPNME",
                "LUANMTGP",
                "LUATECH",
                "LUXSMED",
                "LUXSIQR",
                "LUXSIQRM",
                "LUXCAPM",
                "LUXCPIQR",
            )
        )
    }


def build_receipt(data_dir: Path, scope: str = "primary") -> dict[str, Any]:
    scope_label, field_map = _scope_map(scope)
    sources = sorted({source for fields in field_map.values() for source, _ in fields})
    paths = {source: _find(data_dir, source) for source in sources}
    frames = {source: _read_source(path) for source, path in paths.items()}
    categories = {
        category: {
            "fields": [
                _field_audit(frames[source], source, field) for source, field in fields
            ],
            "quality_status": "candidate_special_codes_audited_no_cleaning_applied",
        }
        for category, fields in field_map.items()
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "nhanes-category-quality-audit-v1",
        "scope": scope,
        "cycle_scope": scope_label,
        "candidate_special_codes": list(CANDIDATE_SPECIAL_CODES),
        "categories": categories,
        "boundary": {
            "raw_rows_emitted": False,
            "measurements_emitted": False,
            "participant_ids_emitted": False,
            "values_removed": False,
            "clinical_use": False,
            "e005_status": "blocked",
        },
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        serialized = (
            json.dumps(
                build_receipt(args.data_dir, args.scope), indent=2, sort_keys=True
            )
            + "\n"
        ).encode("utf-8")
        if args.check:
            if args.output.read_bytes() != serialized:
                print("ERROR: category quality receipt drift", file=sys.stderr)
                return 3
            print(f"category quality receipt verified: {args.output}")
            return 0
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(serialized)
        print(f"category quality receipt written: {args.output}")
        return 0
    except (OSError, ValueError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
