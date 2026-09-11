"""Build a privacy-safe receipt for one additional NHANES category cycle."""

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
CYCLE = "NHANES_2013_2014"
FIELD_MAP: dict[str, tuple[tuple[str, str], ...]] = {
    "body_composition": (
        ("BMX_H.XPT", "BMXWT"),
        ("BMX_H.XPT", "BMXHT"),
        ("BMX_H.XPT", "BMXBMI"),
        ("BMX_H.XPT", "BMXWAIST"),
        ("BMX_H.XPT", "BMXARMC"),
        ("BMX_H.XPT", "BMXSAD1"),
    ),
    "muscle_health": (("DXX_H.XPT", "DXDLALE"), ("DXX_H.XPT", "DXDRALE")),
    "bone_health": (
        ("DXX_H.XPT", "DXDSTBMD"),
        ("DXX_H.XPT", "DXDSTBMC"),
        ("DXX_H.XPT", "DXDSTFAT"),
        ("DXX_H.XPT", "DXXLSBMD"),
    ),
    "brain_cognitive_health": (
        ("CFQ_H.XPT", "CFASTAT"),
        ("CFQ_H.XPT", "CFDCCS"),
        ("CFQ_H.XPT", "CFDCRNC"),
        ("CFQ_H.XPT", "CFDCST1"),
        ("CFQ_H.XPT", "CFDCSR"),
        ("CFQ_H.XPT", "CFDCIT1"),
        ("CFQ_H.XPT", "CFDAPP"),
        ("CFQ_H.XPT", "CFDAST"),
        ("CFQ_H.XPT", "CFDDS"),
    ),
    "sleep_and_recovery": (
        ("SLQ_H.XPT", "SLD010H"),
        ("SLQ_H.XPT", "SLQ050"),
        ("SLQ_H.XPT", "SLQ060"),
        ("PAXDAY_H.XPT", "PAXVMD"),
        ("PAXDAY_H.XPT", "PAXSWMD"),
        ("PAXDAY_H.XPT", "PAXQFD"),
    ),
    "lifestyle_and_function": (
        ("PFQ_H.XPT", "PFQ049"),
        ("PFQ_H.XPT", "PFQ054"),
        ("PFQ_H.XPT", "PFQ061B"),
        ("PFQ_H.XPT", "PFQ061M"),
        ("PFQ_H.XPT", "PFQ061N"),
        ("PAXDAY_H.XPT", "PAXVMD"),
        ("PAXDAY_H.XPT", "PAXQFD"),
    ),
    "mental_health_history": tuple(
        ("DPQ_H.XPT", field)
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
    "blood_health": (
        ("CBC_H.XPT", "LBXWBCSI"),
        ("CBC_H.XPT", "LBXHGB"),
        ("CBC_H.XPT", "LBXHCT"),
        ("CBC_H.XPT", "LBXPLTSI"),
        ("BIOPRO_H.XPT", "LBXSAL"),
        ("BIOPRO_H.XPT", "LBXSCR"),
        ("TCHOL_H.XPT", "LBXTC"),
        ("TRIGLY_H.XPT", "LBXTR"),
        ("TRIGLY_H.XPT", "LBDLDL"),
    ),
    "cardiovascular_health": (
        ("BPX_H.XPT", "BPXPLS"),
        ("BPX_H.XPT", "BPXSY1"),
        ("BPX_H.XPT", "BPXDI1"),
        ("BPX_H.XPT", "BPXSY2"),
        ("BPX_H.XPT", "BPXDI2"),
        ("BPX_H.XPT", "BPXSY3"),
        ("BPX_H.XPT", "BPXDI3"),
        ("TCHOL_H.XPT", "LBXTC"),
        ("TRIGLY_H.XPT", "LBXTR"),
        ("TRIGLY_H.XPT", "LBDLDL"),
    ),
    "cardiorespiratory_health": (
        ("BPX_H.XPT", "BPXPLS"),
        ("BPX_H.XPT", "BPXSY1"),
        ("BPX_H.XPT", "BPXDI1"),
        ("BPX_H.XPT", "BPXSY2"),
        ("BPX_H.XPT", "BPXDI2"),
        ("BPX_H.XPT", "BPXSY3"),
        ("BPX_H.XPT", "BPXDI3"),
    ),
    "immune_inflammatory_health": (
        ("CBC_H.XPT", "LBXWBCSI"),
        ("CBC_H.XPT", "LBXLYPCT"),
        ("CBC_H.XPT", "LBXMOPCT"),
        ("CBC_H.XPT", "LBXNEPCT"),
        ("BIOPRO_H.XPT", "LBXSAL"),
    ),
    "metabolic_health": (
        ("GLU_H.XPT", "LBXGLU"),
        ("GHB_H.XPT", "LBXGH"),
        ("TCHOL_H.XPT", "LBXTC"),
        ("TRIGLY_H.XPT", "LBXTR"),
        ("TRIGLY_H.XPT", "LBDLDL"),
    ),
    "kidney_health": (
        ("ALB_CR_H.XPT", "URXUMA"),
        ("ALB_CR_H.XPT", "URXUMS"),
        ("ALB_CR_H.XPT", "URXUCR"),
        ("ALB_CR_H.XPT", "URXCRS"),
        ("ALB_CR_H.XPT", "URDACT"),
        ("BIOPRO_H.XPT", "LBXSCR"),
        ("BIOPRO_H.XPT", "LBXSBU"),
        ("BIOPRO_H.XPT", "LBXSUA"),
    ),
    "joint_health": (
        ("MCQ_H.XPT", "MCQ160A"),
        ("MCQ_H.XPT", "MCQ160N"),
        ("MCQ_H.XPT", "MCQ180A"),
        ("MCQ_H.XPT", "MCQ180N"),
    ),
    "skin_health": (
        ("DEQ_H.XPT", "DED031"),
        ("DEQ_H.XPT", "DEQ034A"),
        ("DEQ_H.XPT", "DEQ034C"),
        ("DEQ_H.XPT", "DEQ034D"),
        ("DEQ_H.XPT", "DEQ038G"),
        ("DEQ_H.XPT", "DEQ038Q"),
        ("DEQ_H.XPT", "DED120"),
        ("DEQ_H.XPT", "DED125"),
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
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "filename": path.name,
        "url": f"https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/{path.name}",
        "sha256": digest,
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
    categories = {}
    for category, fields in FIELD_MAP.items():
        categories[category] = {
            "status": "real_source_fields_present",
            "cycle": CYCLE,
            "fields": [
                _field_receipt(frames[source], source, field)
                for source, field in fields
            ],
            "clinical_validity": "not_established",
            "mapping_review": "pending",
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "nhanes-category-cycle-receipt-v1",
        "cycle": CYCLE,
        "data_sources": [
            _source_receipt(framesource, frames[source])
            for source, framesource in paths.items()
        ],
        "categories": categories,
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
                print("ERROR: category cycle receipt drift", file=sys.stderr)
                return 3
            print(f"category cycle receipt verified: {args.output}")
            return 0
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(serialized)
        print(f"category cycle receipt written: {args.output}")
        return 0
    except (OSError, ValueError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
