"""Build a privacy-safe receipt for official NHANES 2017-2018 category data."""

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
CYCLE = "NHANES_2017_2018"
DATA_URL = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/"

_FIELD_MAP_2015 = {
    "body_composition": (
        ("BMX_I.XPT", "BMXWT"),
        ("BMX_I.XPT", "BMXHT"),
        ("BMX_I.XPT", "BMXBMI"),
        ("BMX_I.XPT", "BMXWAIST"),
        ("BMX_I.XPT", "BMXARMC"),
    ),
    "muscle_health": (("DXX_I.XPT", "DXDLALE"), ("DXX_I.XPT", "DXDRALE")),
    "bone_health": (
        ("DXX_I.XPT", "DXDSTBMD"),
        ("DXX_I.XPT", "DXDSTBMC"),
        ("DXX_I.XPT", "DXDSTFAT"),
        ("DXX_I.XPT", "DXXLSBMD"),
    ),
    "joint_health": (("MCQ_I.XPT", "MCQ160A"), ("MCQ_I.XPT", "MCQ160N")),
    "skin_health": tuple(
        ("DEQ_I.XPT", field)
        for field in (
            "DED031",
            "DEQ034A",
            "DEQ034C",
            "DEQ034D",
            "DEQ038G",
            "DEQ038Q",
            "DED120",
            "DED125",
        )
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
    "sleep_and_recovery": tuple(
        ("SLQ_I.XPT", field)
        for field in ("SLD012", "SLQ030", "SLQ040", "SLQ050", "SLQ120")
    ),
    "lifestyle_and_function": tuple(
        ("PFQ_I.XPT", field)
        for field in ("PFQ049", "PFQ054", "PFQ061B", "PFQ061M", "PFQ061N")
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
FIELD_MAP = {
    category: tuple(
        (source.replace("_I.XPT", "_J.XPT"), field) for source, field in fields
    )
    for category, fields in _FIELD_MAP_2015.items()
}
FIELD_MAP["lifestyle_and_function"] = FIELD_MAP["lifestyle_and_function"] + (
    ("PAQ_J.XPT", "PAQ605"),
    ("ALQ_J.XPT", "ALQ111"),
    ("SMQ_J.XPT", "SMQ020"),
)


def _find(data_dir: Path, filename: str) -> Path:
    matches = sorted(path for path in data_dir.rglob(filename) if path.is_file())
    if len(matches) != 1:
        raise ValueError(f"expected exactly one local source for {filename}")
    return matches[0]


def build_receipt(data_dir: Path) -> dict[str, Any]:
    sources = sorted({source for fields in FIELD_MAP.values() for source, _ in fields})
    paths = {source: _find(data_dir, source) for source in sources}
    frames = {source: read_xpt(path) for source, path in paths.items()}
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
                "filename": source_path.name,
                "url": DATA_URL + source_path.name,
                "sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
                "rows": int(len(frames[source])),
                "columns": int(len(frames[source].columns)),
                "cycle": CYCLE,
            }
            for source, source_path in paths.items()
        ],
        "categories": categories,
        "not_collected_in_cycle": {
            "fluid_and_cellular": "No official BIA source file was identified in the 2017-2018 mapped intake.",
            "brain_cognitive_health": "No CFQ cognitive source file was identified in the 2017-2018 mapped intake.",
            "liver_health_direct_elastography": "Direct elastography is recorded separately in LUX_J.XPT; this category receipt covers laboratory liver fields.",
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
                print("ERROR: 2017-2018 category receipt drift", file=sys.stderr)
                return 3
            print(f"2017-2018 category receipt verified: {args.output}")
            return 0
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(serialized)
        print(f"2017-2018 category receipt written: {args.output}")
        return 0
    except (OSError, ValueError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
