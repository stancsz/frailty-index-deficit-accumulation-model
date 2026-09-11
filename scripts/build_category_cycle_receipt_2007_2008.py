"""Build a privacy-safe receipt for the official NHANES 2007-2008 cycle."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


CYCLE = "NHANES_2007_2008"
BASE_URL = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles"
FIELD_MAP: dict[str, tuple[tuple[str, str], ...]] = {
    "body_composition": (
        ("BMX_E.XPT", "BMXWT"),
        ("BMX_E.XPT", "BMXBMI"),
        ("BMX_E.XPT", "BMXWAIST"),
    ),
    "muscle_health": (("BMX_E.XPT", "BMXARMC"),),
    "blood_health": (
        ("CBC_E.XPT", "LBXWBCSI"),
        ("CBC_E.XPT", "LBXHGB"),
        ("CBC_E.XPT", "LBXPLTSI"),
    ),
    "cardiovascular_health": (
        ("BPX_E.XPT", "BPXSY1"),
        ("BPX_E.XPT", "BPXDI1"),
        ("TCHOL_E.XPT", "LBXTC"),
        ("TRIGLY_E.XPT", "LBXTR"),
    ),
    "cardiorespiratory_health": (("BPX_E.XPT", "BPXSY1"), ("BPX_E.XPT", "BPXDI1")),
    "immune_inflammatory_health": (
        ("CBC_E.XPT", "LBXLYPCT"),
        ("CBC_E.XPT", "LBDLYMNO"),
        ("CBC_E.XPT", "LBDNENO"),
    ),
    "joint_health": (
        ("MCQ_E.XPT", "MCQ160A"),
        ("MCQ_E.XPT", "MCQ160C"),
        ("PFQ_E.XPT", "PFQ054"),
        ("PFQ_E.XPT", "PFQ059"),
    ),
    "kidney_health": (("ALB_CR_E.XPT", "URXUMA"), ("ALB_CR_E.XPT", "URXUCR")),
    "liver_health": (
        ("BIOPRO_E.XPT", "LBXSATSI"),
        ("BIOPRO_E.XPT", "LBXSASSI"),
        ("BIOPRO_E.XPT", "LBXSTB"),
        ("BIOPRO_E.XPT", "LBXSTP"),
    ),
    "lifestyle_and_function": (
        ("PFQ_E.XPT", "PFQ049"),
        ("PFQ_E.XPT", "PFQ054"),
        ("PFQ_E.XPT", "PFQ059"),
    ),
    "mental_health_history": (
        ("DPQ_E.XPT", "DPQ010"),
        ("DPQ_E.XPT", "DPQ050"),
        ("DPQ_E.XPT", "DPQ100"),
    ),
    "metabolic_health": (
        ("GLU_E.XPT", "LBXGLU"),
        ("GHB_E.XPT", "LBXGH"),
        ("TRIGLY_E.XPT", "LBXTR"),
    ),
    "sleep_and_recovery": (
        ("SLQ_E.XPT", "SLD010H"),
        ("SLQ_E.XPT", "SLQ050"),
        ("SLQ_E.XPT", "SLQ060"),
    ),
}
ALL_CATEGORIES = tuple(
    sorted(
        set(FIELD_MAP)
        | {"bone_health", "brain_cognitive_health", "fluid_and_cellular", "skin_health"}
    )
)


def _field_record(data_dir: Path, filename: str, field: str) -> dict[str, Any]:
    frame = pd.read_sas(data_dir / filename, format="xport", encoding="utf-8")
    if "SEQN" not in frame.columns or field not in frame.columns:
        raise ValueError(f"missing SEQN or {field} in {filename}")
    present = pd.to_numeric(frame[field], errors="coerce").notna()
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
    sources: dict[str, dict[str, Any]] = {}
    for category, mappings in FIELD_MAP.items():
        categories[category] = {
            "cycle": CYCLE,
            "clinical_validity": "not_established",
            "fields": [
                _field_record(data_dir, filename, field) for filename, field in mappings
            ],
        }
        for filename, _ in mappings:
            if filename not in sources:
                path = data_dir / filename
                frame = pd.read_sas(path, format="xport", encoding="utf-8")
                sources[filename] = {
                    "filename": filename,
                    "cycle": "2007-2008",
                    "url": f"{BASE_URL}/{filename}",
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper(),
                    "rows": int(len(frame)),
                    "columns": int(len(frame.columns)),
                }
    return {
        "schema_version": "nhanes-category-cycle-receipt-v1",
        "receipt_type": "nhanes-category-cycle-receipt-v1",
        "cycle": CYCLE,
        "data_sources": list(sources.values()),
        "categories": {
            category: categories[category]
            for category in ALL_CATEGORIES
            if category in categories
        },
        "not_collected_in_cycle": {
            "bone_health": "no usable DXX_E.XPT source file was available",
            "brain_cognitive_health": "no usable CFQ_E.XPT source file was available",
            "fluid_and_cellular": "no usable BIX_E.XPT source file was available",
            "skin_health": "no usable DEQ_E.XPT source file was available",
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
            print("ERROR: 2007-2008 receipt drift")
            return 3
        print(f"2007-2008 receipt verified: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(serialized)
    print(f"2007-2008 receipt written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
