"""Build privacy-safe participant-overlap evidence for real category sources.

The output reports unique participant counts and pairwise overlap counts within
the same public-use survey cycle. It emits no participant identifiers, raw
rows, or measurements. Cross-cycle categories are kept separate because a
matching SEQN is not evidence that two records describe the same person.
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
    FIELD_MAP,
    _find,
    _read_source,
)


SCHEMA_VERSION = 1
SOURCE_CYCLES = {
    "BIX_C.XPT": "NHANES_2003_2004",
    "DEX_C.XPT": "NHANES_2003_2004",
    "ARQ_F.XPT": "NHANES_2009_2010",
    "ARX_F.XPT": "NHANES_2009_2010",
    "CRP_F.XPT": "NHANES_2009_2010",
    "ALB_CR_G.XPT": "NHANES_2011_2012",
    "ALQ_G.XPT": "NHANES_2011_2012",
    "APOB_G.XPT": "NHANES_2011_2012",
    "BIOPRO_G.XPT": "NHANES_2011_2012",
    "BMX_G.XPT": "NHANES_2011_2012",
    "BPX_G.XPT": "NHANES_2011_2012",
    "CBC_G.XPT": "NHANES_2011_2012",
    "CFQ_G.XPT": "NHANES_2011_2012",
    "DEQ_G.XPT": "NHANES_2011_2012",
    "DIQ_G.XPT": "NHANES_2011_2012",
    "DPQ_G.XPT": "NHANES_2011_2012",
    "DXXAG_G.XPT": "NHANES_2011_2012",
    "DXX_G.XPT": "NHANES_2011_2012",
    "ENX_G.XPT": "NHANES_2011_2012",
    "GLU_G.XPT": "NHANES_2011_2012",
    "GHB_G.XPT": "NHANES_2011_2012",
    "HSQ_G.XPT": "NHANES_2011_2012",
    "MCQ_G.XPT": "NHANES_2011_2012",
    "MGX_G.XPT": "NHANES_2011_2012",
    "OCQ_G.XPT": "NHANES_2011_2012",
    "PAXDAY_G.XPT": "NHANES_2011_2012",
    "PAXHD_G.XPT": "NHANES_2011_2012",
    "PAQ_G.XPT": "NHANES_2011_2012",
    "PFQ_G.XPT": "NHANES_2011_2012",
    "P_LUX.XPT": "NHANES_2017_MARCH_2020_PREPANDEMIC",
    "SLQ_G.XPT": "NHANES_2011_2012",
    "SMQ_G.XPT": "NHANES_2011_2012",
    "SPX_G.XPT": "NHANES_2011_2012",
    "TCHOL_G.XPT": "NHANES_2011_2012",
    "TRIGLY_G.XPT": "NHANES_2011_2012",
    "xr.dat": "NHANES_1991_1994",
}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    return parser


def _category_participants(
    frames: dict[str, pd.DataFrame],
    category: str,
) -> dict[str, set[Any]]:
    by_cycle: dict[str, set[Any]] = {}
    for source, field in FIELD_MAP[category]:
        cycle = SOURCE_CYCLES[source]
        frame = frames[source]
        if "SEQN" not in frame.columns or field not in frame.columns:
            raise ValueError(f"{source} is missing required field {field}")
        present = frame.loc[frame[field].notna(), "SEQN"]
        by_cycle.setdefault(cycle, set()).update(present.tolist())
    return by_cycle


def build_receipt(data_dir: Path) -> dict[str, Any]:
    sources = sorted({source for fields in FIELD_MAP.values() for source, _ in fields})
    paths = {source: _find(data_dir, source) for source in sources}
    frames = {source: _read_source(path) for source, path in paths.items()}
    category_sets = {
        category: _category_participants(frames, category) for category in FIELD_MAP
    }
    cycles = sorted({cycle for values in category_sets.values() for cycle in values})
    cycle_receipts: dict[str, Any] = {}
    for cycle in cycles:
        sets = {
            category: values[cycle]
            for category, values in category_sets.items()
            if cycle in values
        }
        categories = {
            category: {"unique_participants_with_any_mapped_field": len(values)}
            for category, values in sorted(sets.items())
        }
        pairwise: dict[str, int] = {}
        names = sorted(sets)
        for index, left in enumerate(names):
            for right in names[index + 1 :]:
                pairwise[f"{left}__{right}"] = len(sets[left] & sets[right])
        cycle_receipt: dict[str, Any] = {
            "category_count": len(categories),
            "categories": categories,
            "pairwise_overlap_unique_participants": pairwise,
        }
        if cycle == "NHANES_2011_2012":
            demographic = _read_source(_find(data_dir, "DEMO_G.XPT"))
            reference_participants = set(
                demographic.loc[demographic["SEQN"].notna(), "SEQN"].tolist()
            )
            coverage: dict[str, Any] = {}
            for category, values in sorted(sets.items()):
                in_reference = len(values & reference_participants)
                coverage[category] = {
                    "unique_participants_in_reference": in_reference,
                    "reference_coverage_percent": round(
                        100 * in_reference / len(reference_participants), 3
                    ),
                }
            all_categories = set.intersection(*sets.values()) if sets else set()
            cycle_receipt["reference_population"] = {
                "source": "DEMO_G.XPT",
                "unique_participants": len(reference_participants),
                "interpretation": "cycle-level public-use participant denominator; not an eligibility or analytic-weight denominator",
            }
            cycle_receipt["category_reference_coverage"] = coverage
            cycle_receipt["all_mapped_categories_intersection_unique_participants"] = (
                len(all_categories & reference_participants)
            )
        cycle_receipts[cycle] = cycle_receipt
    return {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "nhanes-category-participant-overlap-v1",
        "privacy_boundary": {
            "participant_ids_emitted": False,
            "raw_rows_emitted": False,
            "measurements_emitted": False,
            "cross_cycle_joins_performed": False,
        },
        "cycles": cycle_receipts,
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        receipt = build_receipt(args.data_dir)
        serialized = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode(
            "utf-8"
        )
        if args.check:
            if args.output.read_bytes() != serialized:
                print("ERROR: category overlap receipt drift", file=sys.stderr)
                return 3
            print(f"category overlap receipt verified: {args.output}")
            return 0
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(serialized)
        print(f"category overlap receipt written: {args.output}")
        return 0
    except (OSError, ValueError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
