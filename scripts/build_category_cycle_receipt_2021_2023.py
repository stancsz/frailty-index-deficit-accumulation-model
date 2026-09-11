"""Build a privacy-safe receipt for official NHANES 2021-2023 category data."""

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


SCHEMA_VERSION = 1
CYCLE = "NHANES_2021_2023"
DATA_URL = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/"
FIELD_MAP: dict[str, tuple[tuple[str, str], ...]] = {
    "body_composition": tuple(
        ("BMX_L.XPT", field)
        for field in ("BMXWT", "BMXHT", "BMXBMI", "BMXWAIST", "BMXARMC")
    ),
    "joint_health": (("MCQ_L.XPT", "MCQ160A"),),
    "skin_health": tuple(
        ("DEQ_L.XPT", field) for field in ("DEQ034A", "DEQ034C", "DEQ034D")
    ),
    "blood_health": (
        ("CBC_L.XPT", "LBXWBCSI"),
        ("CBC_L.XPT", "LBXHGB"),
        ("CBC_L.XPT", "LBXHCT"),
        ("CBC_L.XPT", "LBXPLTSI"),
        ("BIOPRO_L.XPT", "LBXSAL"),
        ("BIOPRO_L.XPT", "LBXSCR"),
        ("TCHOL_L.XPT", "LBXTC"),
        ("TRIGLY_L.XPT", "LBXTLG"),
        ("TRIGLY_L.XPT", "LBDLDL"),
    ),
    "cardiovascular_health": (
        ("TCHOL_L.XPT", "LBXTC"),
        ("TRIGLY_L.XPT", "LBXTLG"),
        ("TRIGLY_L.XPT", "LBDLDL"),
    ),
    "immune_inflammatory_health": (
        ("CBC_L.XPT", "LBXWBCSI"),
        ("CBC_L.XPT", "LBXLYPCT"),
        ("CBC_L.XPT", "LBXMOPCT"),
        ("CBC_L.XPT", "LBXNEPCT"),
        ("BIOPRO_L.XPT", "LBXSAL"),
    ),
    "metabolic_health": (
        ("GLU_L.XPT", "LBXGLU"),
        ("GHB_L.XPT", "LBXGH"),
        ("TCHOL_L.XPT", "LBXTC"),
        ("TRIGLY_L.XPT", "LBXTLG"),
        ("TRIGLY_L.XPT", "LBDLDL"),
    ),
    "kidney_health": (
        ("ALB_CR_L.XPT", "URXUMA"),
        ("ALB_CR_L.XPT", "URXUMS"),
        ("ALB_CR_L.XPT", "URXUCR"),
        ("ALB_CR_L.XPT", "URXCRS"),
        ("ALB_CR_L.XPT", "URDACT"),
        ("BIOPRO_L.XPT", "LBXSCR"),
        ("BIOPRO_L.XPT", "LBXSBU"),
        ("BIOPRO_L.XPT", "LBXSUA"),
    ),
    "liver_health": tuple(
        ("BIOPRO_L.XPT", field)
        for field in (
            "LBXSAL",
            "LBXSATSI",
            "LBXSASSI",
            "LBXSAPSI",
            "LBXSGTSI",
            "LBXSTB",
            "LBXSTP",
        )
    ),
    "sleep_and_recovery": tuple(
        ("SLQ_L.XPT", field)
        for field in ("SLD012", "SLQ300", "SLQ310", "SLQ320", "SLQ330", "SLD013")
    ),
    "mental_health_history": tuple(
        ("DPQ_L.XPT", field)
        for field in (
            "DPQ010",
            "DPQ020",
            "DPQ030",
            "DPQ040",
            "DPQ050",
            "DPQ060",
            "DPQ070",
            "DPQ080",
            "DPQ090",
            "DPQ100",
        )
    ),
    "lifestyle_and_function": (
        ("PAQ_L.XPT", "PAD790Q"),
        ("PAQ_L.XPT", "PAD800"),
        ("ALQ_L.XPT", "ALQ111"),
        ("SMQ_L.XPT", "SMQ020"),
    ),
}


def build_receipt(data_dir: Path) -> dict[str, Any]:
    sources = sorted({source for fields in FIELD_MAP.values() for source, _ in fields})
    paths = {source: next(data_dir.rglob(source), None) for source in sources}
    if any(path is None or not path.is_file() for path in paths.values()):
        missing = [source for source, path in paths.items() if path is None]
        raise ValueError(f"missing local source files: {', '.join(missing)}")
    frames = {
        source: read_xpt(path) for source, path in paths.items() if path is not None
    }
    categories: dict[str, Any] = {}
    for category, fields in FIELD_MAP.items():
        field_receipts = []
        for source, field in fields:
            frame = frames[source]
            if "SEQN" not in frame.columns or field not in frame.columns:
                raise ValueError(f"{source} is missing required field {field}")
            values = frame[["SEQN", field]].dropna(subset=[field])
            field_receipts.append(
                {
                    "source": source,
                    "field": field,
                    "nonmissing_rows": int(len(values)),
                    "unique_participants_with_value": int(values["SEQN"].nunique()),
                }
            )
        categories[category] = {
            "status": "real_source_fields_present",
            "cycle": CYCLE,
            "fields": field_receipts,
            "clinical_validity": "not_established",
            "mapping_review": "pending",
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "nhanes-category-cycle-receipt-v1",
        "cycle": CYCLE,
        "data_sources": [
            {
                "filename": paths[source].name,
                "url": DATA_URL + paths[source].name,
                "sha256": hashlib.sha256(paths[source].read_bytes()).hexdigest(),
                "rows": int(len(frames[source])),
                "columns": int(len(frames[source].columns)),
                "cycle": CYCLE,
            }
            for source in sources
        ],
        "categories": categories,
        "not_collected_in_cycle": {
            "fluid_and_cellular": "No official BIA source file was identified in the 2021-2023 mapped intake.",
            "muscle_health": "No mapped grip-strength or DXA muscle source was identified in the 2021-2023 intake.",
            "bone_health": "No mapped DXA source was identified in the 2021-2023 intake.",
            "brain_cognitive_health": "No CFQ cognitive source file was identified in the 2021-2023 mapped intake.",
            "cardiorespiratory_health": "No mapped BPX or spirometry source was identified; lipid fields remain separately mapped to cardiovascular health.",
            "lifestyle_and_function": "No mapped PFQ or objective activity-monitor source was identified; PAQ, alcohol, and smoking fields are included above.",
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        serialized = (
            json.dumps(build_receipt(args.data_dir), indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        if args.check:
            if args.output.read_bytes() != serialized:
                print("ERROR: 2021-2023 category receipt drift", file=sys.stderr)
                return 3
            print(f"2021-2023 category receipt verified: {args.output}")
            return 0
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(serialized)
        print(f"2021-2023 category receipt written: {args.output}")
        return 0
    except (OSError, ValueError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
