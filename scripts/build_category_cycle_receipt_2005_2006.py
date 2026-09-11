"""Build a privacy-safe receipt for the official NHANES 2005-2006 cycle."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


CYCLE = "NHANES_2005_2006"
BASE_URL = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2005/DataFiles"
FIELD_MAP: dict[str, tuple[tuple[str, str], ...]] = {
    "body_composition": (
        ("BMX_D.XPT", "BMXWT"),
        ("BMX_D.XPT", "BMXBMI"),
        ("BMX_D.XPT", "BMXWAIST"),
    ),
    "bone_health": (
        ("DXX_D.XPT", "DXDTOBMC"),
        ("DXX_D.XPT", "DXDTOBMD"),
        ("DXX_D.XPT", "DXDTOFAT"),
    ),
    "muscle_health": (("DXX_D.XPT", "DXDSTBMC"), ("DXX_D.XPT", "DXXRABMC")),
    "blood_health": (
        ("CBC_D.XPT", "LBXWBCSI"),
        ("CBC_D.XPT", "LBXHGB"),
        ("CBC_D.XPT", "LBXPLTSI"),
    ),
    "cardiovascular_health": (
        ("BPX_D.XPT", "BPXSY1"),
        ("BPX_D.XPT", "BPXDI1"),
        ("TCHOL_D.XPT", "LBXTC"),
        ("TRIGLY_D.XPT", "LBXTR"),
    ),
    "cardiorespiratory_health": (("BPX_D.XPT", "BPXSY1"), ("BPX_D.XPT", "BPXDI1")),
    "immune_inflammatory_health": (
        ("CBC_D.XPT", "LBXLYPCT"),
        ("CBC_D.XPT", "LBDLYMNO"),
        ("CBC_D.XPT", "LBDNENO"),
    ),
    "joint_health": (
        ("MCQ_D.XPT", "MCQ160A"),
        ("MCQ_D.XPT", "MCQ160C"),
        ("PFQ_D.XPT", "PFQ054"),
        ("PFQ_D.XPT", "PFQ059"),
    ),
    "kidney_health": (("ALB_CR_D.XPT", "URXUMA"), ("ALB_CR_D.XPT", "URXUCR")),
    "liver_health": (
        ("BIOPRO_D.XPT", "LBXSATSI"),
        ("BIOPRO_D.XPT", "LBXSASSI"),
        ("BIOPRO_D.XPT", "LBXSTB"),
        ("BIOPRO_D.XPT", "LBXSTP"),
    ),
    "lifestyle_and_function": (
        ("PFQ_D.XPT", "PFQ049"),
        ("PFQ_D.XPT", "PFQ054"),
        ("PFQ_D.XPT", "PFQ059"),
    ),
    "mental_health_history": (
        ("DPQ_D.XPT", "DPQ010"),
        ("DPQ_D.XPT", "DPQ050"),
        ("DPQ_D.XPT", "DPQ100"),
    ),
    "metabolic_health": (
        ("GLU_D.XPT", "LBXGLU"),
        ("GHB_D.XPT", "LBXGH"),
        ("TRIGLY_D.XPT", "LBXTR"),
    ),
    "skin_health": (
        ("DEQ_D.XPT", "DED031"),
        ("DEQ_D.XPT", "DEQ034C"),
        ("DEQ_D.XPT", "DEQ038G"),
    ),
    "sleep_and_recovery": (
        ("SLQ_D.XPT", "SLD010H"),
        ("SLQ_D.XPT", "SLQ050"),
        ("SLQ_D.XPT", "SLQ060"),
    ),
}
ALL_CATEGORIES = tuple(
    sorted(set(FIELD_MAP) | {"brain_cognitive_health", "fluid_and_cellular"})
)


def _field_record(data_dir: Path, filename: str, field: str) -> dict[str, Any]:
    frame = pd.read_sas(data_dir / filename, format="xport", encoding="utf-8")
    if "SEQN" not in frame.columns or field not in frame.columns:
        raise ValueError(f"missing SEQN or {field} in {filename}")
    numeric = pd.to_numeric(frame[field], errors="coerce")
    present = numeric.notna()
    return {
        "source": filename,
        "field": field,
        "source_rows": int(len(frame)),
        "source_columns": int(len(frame.columns)),
        "nonmissing_rows": int(present.sum()),
        "unique_participants_with_value": int(frame.loc[present, "SEQN"].nunique()),
    }


def build_receipt(data_dir: Path) -> dict[str, Any]:
    categories: dict[str, dict[str, Any]] = {}
    source_files: dict[str, dict[str, Any]] = {}
    for category, mappings in FIELD_MAP.items():
        fields = [
            _field_record(data_dir, filename, field) for filename, field in mappings
        ]
        categories[category] = {
            "cycle": CYCLE,
            "clinical_validity": "not_established",
            "fields": fields,
        }
        for filename, _ in mappings:
            if filename in source_files:
                continue
            path = data_dir / filename
            source_files[filename] = {
                "filename": filename,
                "cycle": "2005-2006",
                "url": f"{BASE_URL}/{filename}",
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper(),
                "rows": int(
                    pd.read_sas(path, format="xport", encoding="utf-8").shape[0]
                ),
            }
    return {
        "schema_version": "nhanes-category-cycle-receipt-v1",
        "receipt_type": "nhanes-category-cycle-receipt-v1",
        "cycle": CYCLE,
        "data_sources": list(source_files.values()),
        "categories": {
            category: categories[category]
            for category in ALL_CATEGORIES
            if category in categories
        },
        "not_collected_in_cycle": {
            "brain_cognitive_health": "no usable CFQ_D.XPT source file was available",
            "fluid_and_cellular": "no usable BIX_D.XPT source file was available",
        },
        "boundary": {
            "participant_ids_emitted": False,
            "raw_rows_emitted": False,
            "measurements_emitted": False,
            "clinical_use": False,
            "clinical_validity": "not_established",
            "numeric_category_age": "withheld",
            "e005_status": "blocked",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    serialized = (json.dumps(build_receipt(args.data_dir), indent=2) + "\n").encode(
        "utf-8"
    )
    if args.check:
        if args.output.read_bytes() != serialized:
            print("ERROR: 2005-2006 receipt drift")
            return 3
        print(f"2005-2006 receipt verified: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(serialized)
    print(f"2005-2006 receipt written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
