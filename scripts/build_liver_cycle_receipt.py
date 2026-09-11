"""Build a privacy-safe receipt for a later NHANES liver-elastography file."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from frailty_engine.nhanes import read_xpt  # noqa: E402


SOURCE = "LUX_J.XPT"
CYCLE = "NHANES_2017_2018"
FIELDS = (
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        matches = sorted(args.data_dir.rglob(SOURCE))
        if len(matches) != 1:
            raise ValueError(f"expected exactly one local source for {SOURCE}")
        path = matches[0]
        frame: Any = read_xpt(path)
        if "SEQN" not in frame.columns:
            raise ValueError("LUX_J.XPT is missing SEQN")
        fields = []
        for field in FIELDS:
            if field not in frame.columns:
                raise ValueError(f"LUX_J.XPT is missing required field {field}")
            values = frame[["SEQN", field]].dropna(subset=[field])
            fields.append(
                {
                    "source": SOURCE,
                    "field": field,
                    "nonmissing_rows": int(len(values)),
                    "unique_participants_with_value": int(values["SEQN"].nunique()),
                }
            )
        receipt = {
            "schema_version": 1,
            "receipt_type": "nhanes-liver-cycle-receipt-v1",
            "cycle": CYCLE,
            "data_sources": [
                {
                    "filename": SOURCE,
                    "url": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/LUX_J.XPT",
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "rows": int(len(frame)),
                    "columns": int(len(frame.columns)),
                }
            ],
            "category": {
                "name": "liver_health",
                "status": "real_direct_transient_elastography_fields_present",
                "fields": fields,
                "clinical_validity": "not_established",
                "mapping_review": "pending",
            },
            "boundary": {
                "raw_rows_emitted": False,
                "measurements_emitted": False,
                "participant_ids_emitted": False,
                "clinical_use": False,
                "numeric_category_age": "withheld",
                "e005_status": "blocked",
            },
        }
        serialized = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode(
            "utf-8"
        )
        if args.check:
            if args.output.read_bytes() != serialized:
                print("ERROR: liver cycle receipt drift", file=sys.stderr)
                return 3
            print(f"liver cycle receipt verified: {args.output}")
            return 0
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(serialized)
        print(f"liver cycle receipt written: {args.output}")
        return 0
    except (OSError, ValueError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
