"""Build a privacy-safe receipt for the official NHANES 2015-2016 cycle."""

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
CYCLE = "NHANES_2015_2016"
DATA_URL = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2015/DataFiles/"

FIELD_MAP: dict[str, tuple[tuple[str, str], ...]] = {
    "body_composition": (
        ("BMX_I.XPT", "BMXWT"),
        ("BMX_I.XPT", "BMXHT"),
        ("BMX_I.XPT", "BMXBMI"),
        ("BMX_I.XPT", "BMXWAIST"),
        ("BMX_I.XPT", "BMXARMC"),
        ("BMX_I.XPT", "BMXSAD1"),
    ),
    "muscle_health": (("DXX_I.XPT", "DXDLALE"), ("DXX_I.XPT", "DXDRALE")),
    "bone_health": (
        ("DXX_I.XPT", "DXDSTBMD"),
        ("DXX_I.XPT", "DXDSTBMC"),
        ("DXX_I.XPT", "DXDSTFAT"),
        ("DXX_I.XPT", "DXXLSBMD"),
    ),
    "joint_health": (
        ("MCQ_I.XPT", "MCQ160A"),
        ("MCQ_I.XPT", "MCQ160N"),
        ("MCQ_I.XPT", "MCQ180A"),
        ("MCQ_I.XPT", "MCQ180N"),
    ),
    "skin_health": (
        ("DEQ_I.XPT", "DED031"),
        ("DEQ_I.XPT", "DEQ034A"),
        ("DEQ_I.XPT", "DEQ034C"),
        ("DEQ_I.XPT", "DEQ034D"),
        ("DEQ_I.XPT", "DEQ038G"),
        ("DEQ_I.XPT", "DEQ038Q"),
        ("DEQ_I.XPT", "DED120"),
        ("DEQ_I.XPT", "DED125"),
    ),
    "blood_health": (
        ("CBC_I.XPT", "LBXWBCSI"),
        ("CBC_I.XPT", "LBXHGB"),
        ("CBC_I.XPT", "LBXHCT"),
        ("CBC_I.XPT", "LBXPLTSI"),
        ("BIOPRO_I.XPT", "LBXSAL"),
        ("BIOPRO_I.XPT", "LBXSCR"),
        ("TCHOL_I.XPT", "LBXTC"),
        ("TRIGLY_I.XPT", "LBXTR"),
        ("TRIGLY_I.XPT", "LBDLDL"),
    ),
    "cardiovascular_health": (
        ("BPX_I.XPT", "BPXPLS"),
        ("BPX_I.XPT", "BPXSY1"),
        ("BPX_I.XPT", "BPXDI1"),
        ("BPX_I.XPT", "BPXSY2"),
        ("BPX_I.XPT", "BPXDI2"),
        ("BPX_I.XPT", "BPXSY3"),
        ("BPX_I.XPT", "BPXDI3"),
        ("TCHOL_I.XPT", "LBXTC"),
        ("TRIGLY_I.XPT", "LBXTR"),
        ("TRIGLY_I.XPT", "LBDLDL"),
    ),
    "cardiorespiratory_health": (
        ("BPX_I.XPT", "BPXPLS"),
        ("BPX_I.XPT", "BPXSY1"),
        ("BPX_I.XPT", "BPXDI1"),
        ("BPX_I.XPT", "BPXSY2"),
        ("BPX_I.XPT", "BPXDI2"),
        ("BPX_I.XPT", "BPXSY3"),
        ("BPX_I.XPT", "BPXDI3"),
    ),
    "immune_inflammatory_health": (
        ("CBC_I.XPT", "LBXWBCSI"),
        ("CBC_I.XPT", "LBXLYPCT"),
        ("CBC_I.XPT", "LBXMOPCT"),
        ("CBC_I.XPT", "LBXNEPCT"),
        ("BIOPRO_I.XPT", "LBXSAL"),
    ),
    "metabolic_health": (
        ("GLU_I.XPT", "LBXGLU"),
        ("GHB_I.XPT", "LBXGH"),
        ("TCHOL_I.XPT", "LBXTC"),
        ("TRIGLY_I.XPT", "LBXTR"),
        ("TRIGLY_I.XPT", "LBDLDL"),
    ),
    "kidney_health": (
        ("ALB_CR_I.XPT", "URXUMA"),
        ("ALB_CR_I.XPT", "URXUMS"),
        ("ALB_CR_I.XPT", "URXUCR"),
        ("ALB_CR_I.XPT", "URXCRS"),
        ("ALB_CR_I.XPT", "URDACT"),
        ("BIOPRO_I.XPT", "LBXSCR"),
        ("BIOPRO_I.XPT", "LBXSBU"),
        ("BIOPRO_I.XPT", "LBXSUA"),
    ),
    "liver_health": (
        ("BIOPRO_I.XPT", "LBXSAL"),
        ("BIOPRO_I.XPT", "LBXSATSI"),
        ("BIOPRO_I.XPT", "LBXSASSI"),
        ("BIOPRO_I.XPT", "LBXSAPSI"),
        ("BIOPRO_I.XPT", "LBXSGTSI"),
        ("BIOPRO_I.XPT", "LBXSTB"),
        ("BIOPRO_I.XPT", "LBXSTP"),
    ),
    "sleep_and_recovery": (
        ("SLQ_I.XPT", "SLD012"),
        ("SLQ_I.XPT", "SLQ030"),
        ("SLQ_I.XPT", "SLQ040"),
        ("SLQ_I.XPT", "SLQ050"),
        ("SLQ_I.XPT", "SLQ120"),
    ),
    "lifestyle_and_function": (
        ("PFQ_I.XPT", "PFQ049"),
        ("PFQ_I.XPT", "PFQ054"),
        ("PFQ_I.XPT", "PFQ061B"),
        ("PFQ_I.XPT", "PFQ061M"),
        ("PFQ_I.XPT", "PFQ061N"),
    ),
    "mental_health_history": tuple(
        ("DPQ_I.XPT", field)
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
}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    return parser


def _find(data_dir: Path, filename: str) -> Path:
    matches = sorted(path for path in data_dir.rglob(filename) if path.is_file())
    if len(matches) != 1:
        raise ValueError(f"expected exactly one local source for {filename}")
    return matches[0]


def _source_receipt(path: Path, frame: Any) -> dict[str, Any]:
    return {
        "filename": path.name,
        "url": DATA_URL + path.name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "rows": int(len(frame)),
        "columns": int(len(frame.columns)),
        "cycle": CYCLE,
    }


def _field_receipt(frame: Any, source: str, field: str) -> dict[str, Any]:
    if "SEQN" not in frame.columns or field not in frame.columns:
        raise ValueError(f"{source} is missing required field {field}")
    values = frame[["SEQN", field]].dropna(subset=[field])
    return {
        "source": source,
        "field": field,
        "nonmissing_rows": int(len(values)),
        "unique_participants_with_value": int(values["SEQN"].nunique()),
    }


def build_receipt(data_dir: Path) -> dict[str, Any]:
    sources = sorted({source for fields in FIELD_MAP.values() for source, _ in fields})
    paths = {source: _find(data_dir, source) for source in sources}
    frames = {source: read_xpt(path) for source, path in paths.items()}
    categories = {
        category: {
            "status": "real_source_fields_present",
            "cycle": CYCLE,
            "fields": [
                _field_receipt(frames[source], source, field)
                for source, field in fields
            ],
            "clinical_validity": "not_established",
            "mapping_review": "pending",
        }
        for category, fields in FIELD_MAP.items()
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "nhanes-category-cycle-receipt-v1",
        "cycle": CYCLE,
        "data_sources": [
            _source_receipt(paths[source], frames[source]) for source in sources
        ],
        "categories": categories,
        "not_collected_in_cycle": {
            "fluid_and_cellular": "No official BIA source file was identified in the 2015-2016 mapped intake.",
            "brain_cognitive_health": "No CFQ cognitive source file was identified in the 2015-2016 mapped intake.",
            "liver_health_direct_elastography": "No LUX transient-elastography source was included; liver coverage here is laboratory-only.",
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
    args = _parser().parse_args(argv)
    try:
        serialized = (
            json.dumps(build_receipt(args.data_dir), indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        if args.check:
            if args.output.read_bytes() != serialized:
                print("ERROR: 2015-2016 category receipt drift", file=sys.stderr)
                return 3
            print(f"2015-2016 category receipt verified: {args.output}")
            return 0
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(serialized)
        print(f"2015-2016 category receipt written: {args.output}")
        return 0
    except (OSError, ValueError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
