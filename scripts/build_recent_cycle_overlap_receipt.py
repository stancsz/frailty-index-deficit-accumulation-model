"""Build privacy-safe participant overlap receipts for recent NHANES cycles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from frailty_engine.nhanes import read_xpt  # noqa: E402


SCHEMA_VERSION = 1

FIELD_MAP: dict[str, dict[str, tuple[tuple[str, str], ...]]] = {
    "NHANES_2013_2014": {
        "body_composition": (("BMX_H.XPT", "BMXWT"),),
        "muscle_health": (("DXX_H.XPT", "DXDLALE"),),
        "bone_health": (("DXX_H.XPT", "DXDSTBMD"),),
        "brain_cognitive_health": (("CFQ_H.XPT", "CFDCCS"),),
        "joint_health": (("MCQ_H.XPT", "MCQ160A"),),
        "skin_health": (("DEQ_H.XPT", "DED031"),),
        "blood_health": (("CBC_H.XPT", "LBXWBCSI"),),
        "cardiovascular_health": (("BPX_H.XPT", "BPXPLS"),),
        "cardiorespiratory_health": (("BPX_H.XPT", "BPXPLS"),),
        "immune_inflammatory_health": (("CBC_H.XPT", "LBXWBCSI"),),
        "metabolic_health": (("GLU_H.XPT", "LBXGLU"),),
        "kidney_health": (("ALB_CR_H.XPT", "URXUMA"),),
        "sleep_and_recovery": (("SLQ_H.XPT", "SLD010H"),),
        "lifestyle_and_function": (("PFQ_H.XPT", "PFQ049"),),
        "mental_health_history": (("DPQ_H.XPT", "DPQ010"),),
    },
    "NHANES_2015_2016": {
        "body_composition": (("BMX_I.XPT", "BMXWT"),),
        "muscle_health": (("DXX_I.XPT", "DXDLALE"),),
        "bone_health": (("DXX_I.XPT", "DXDSTBMD"),),
        "joint_health": (("MCQ_I.XPT", "MCQ160A"),),
        "skin_health": (("DEQ_I.XPT", "DED031"),),
        "blood_health": (("CBC_I.XPT", "LBXWBCSI"),),
        "cardiovascular_health": (("BPX_I.XPT", "BPXPLS"),),
        "cardiorespiratory_health": (("BPX_I.XPT", "BPXPLS"),),
        "immune_inflammatory_health": (("CBC_I.XPT", "LBXWBCSI"),),
        "metabolic_health": (("GLU_I.XPT", "LBXGLU"),),
        "kidney_health": (("ALB_CR_I.XPT", "URXUMA"),),
        "liver_health": (("BIOPRO_I.XPT", "LBXSAL"),),
        "sleep_and_recovery": (("SLQ_I.XPT", "SLD012"),),
        "lifestyle_and_function": (("PFQ_I.XPT", "PFQ049"),),
        "mental_health_history": (("DPQ_I.XPT", "DPQ010"),),
    },
    "NHANES_2017_2018": {
        "body_composition": (("BMX_J.XPT", "BMXWT"),),
        "muscle_health": (("DXX_J.XPT", "DXDLALE"),),
        "bone_health": (("DXX_J.XPT", "DXDSTBMD"),),
        "joint_health": (("MCQ_J.XPT", "MCQ160A"),),
        "skin_health": (("DEQ_J.XPT", "DED031"),),
        "blood_health": (("CBC_J.XPT", "LBXWBCSI"),),
        "cardiovascular_health": (("BPX_J.XPT", "BPXPLS"),),
        "cardiorespiratory_health": (("BPX_J.XPT", "BPXPLS"),),
        "immune_inflammatory_health": (("CBC_J.XPT", "LBXWBCSI"),),
        "metabolic_health": (("GLU_J.XPT", "LBXGLU"),),
        "kidney_health": (("ALB_CR_J.XPT", "URXUMA"),),
        "liver_health": (("BIOPRO_J.XPT", "LBXSAL"),),
        "sleep_and_recovery": (("SLQ_J.XPT", "SLD012"),),
        "lifestyle_and_function": (("PAQ_J.XPT", "PAQ605"),),
        "mental_health_history": (("DPQ_J.XPT", "DPQ010"),),
    },
    "NHANES_2021_2023": {
        "body_composition": (("BMX_L.XPT", "BMXWT"),),
        "joint_health": (("MCQ_L.XPT", "MCQ160A"),),
        "skin_health": (("DEQ_L.XPT", "DEQ034A"),),
        "blood_health": (("CBC_L.XPT", "LBXWBCSI"),),
        "cardiovascular_health": (("TCHOL_L.XPT", "LBXTC"),),
        "immune_inflammatory_health": (("CBC_L.XPT", "LBXWBCSI"),),
        "metabolic_health": (("GLU_L.XPT", "LBXGLU"),),
        "kidney_health": (("ALB_CR_L.XPT", "URXUMA"),),
        "liver_health": (("BIOPRO_L.XPT", "LBXSAL"),),
        "sleep_and_recovery": (("SLQ_L.XPT", "SLD012"),),
        "mental_health_history": (("DPQ_L.XPT", "DPQ010"),),
        "lifestyle_and_function": (("PAQ_L.XPT", "PAD790Q"),),
    },
}


def _find(data_dir: Path, filename: str) -> Path:
    matches = sorted(path for path in data_dir.rglob(filename) if path.is_file())
    if len(matches) != 1:
        raise ValueError(f"expected exactly one local source for {filename}")
    return matches[0]


def _category_sets(
    data_dir: Path, mapping: dict[str, tuple[tuple[str, str], ...]]
) -> dict[str, set[Any]]:
    sources = sorted({source for fields in mapping.values() for source, _ in fields})
    frames = {source: read_xpt(_find(data_dir, source)) for source in sources}
    result: dict[str, set[Any]] = {}
    for category, fields in mapping.items():
        participants: set[Any] = set()
        for source, field in fields:
            frame = frames[source]
            if "SEQN" not in frame.columns or field not in frame.columns:
                raise ValueError(f"{source} is missing required field {field}")
            participants.update(frame.loc[frame[field].notna(), "SEQN"].tolist())
        result[category] = participants
    return result


def build_receipt(data_dirs: dict[str, Path]) -> dict[str, Any]:
    cycles: dict[str, Any] = {}
    for cycle, mapping in FIELD_MAP.items():
        sets = _category_sets(data_dirs[cycle], mapping)
        names = sorted(sets)
        pairwise = {
            f"{left}__{right}": len(sets[left] & sets[right])
            for index, left in enumerate(names)
            for right in names[index + 1 :]
        }
        cycles[cycle] = {
            "category_count": len(sets),
            "categories": {
                name: {"unique_participants_with_any_mapped_field": len(sets[name])}
                for name in names
            },
            "pairwise_overlap_unique_participants": pairwise,
            "all_mapped_categories_intersection_unique_participants": len(
                set.intersection(*sets.values()) if sets else set()
            ),
            "interpretation": "same-cycle public-use participant overlap only; no eligibility, survey-weight, clinical-validity, or harmonization claim",
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "nhanes-recent-category-participant-overlap-v1",
        "cycles": cycles,
        "privacy_boundary": {
            "participant_ids_emitted": False,
            "raw_rows_emitted": False,
            "measurements_emitted": False,
            "cross_cycle_joins_performed": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir", action="append", nargs=2, metavar=("CYCLE", "PATH"), required=True
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        data_dirs = {cycle: Path(path) for cycle, path in args.data_dir}
        missing = sorted(set(FIELD_MAP) - set(data_dirs))
        if missing:
            raise ValueError(f"missing cycle directories: {', '.join(missing)}")
        serialized = (
            json.dumps(build_receipt(data_dirs), indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        if args.check:
            if args.output.read_bytes() != serialized:
                print("ERROR: recent overlap receipt drift", file=sys.stderr)
                return 3
            print(f"recent overlap receipt verified: {args.output}")
            return 0
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(serialized)
        print(f"recent overlap receipt written: {args.output}")
        return 0
    except (OSError, ValueError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
