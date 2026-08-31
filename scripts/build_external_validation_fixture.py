"""Build the committed synthetic external-validation fixture.

The fixture is an engineering harness for exercising the held-out validation
plumbing before an approved cohort is available. It is not a clinical cohort,
not a performance estimate, and not a source of model-training evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from attestation import verify_sidecar, write_sidecar

from frailty_engine.__main__ import sample_payload


DEFAULT_SEED = 20260827
ROW_COUNT = 300
ETHNICITIES = ("synthetic-group-a", "synthetic-group-b", "synthetic-group-c")
AGE_VALUES = ((25, 35), (45, 55), (65, 75), (85, 95))


def build_rows(
    *, seed: int = DEFAULT_SEED, row_count: int = ROW_COUNT
) -> list[dict[str, Any]]:
    """Return deterministic, fully observed NHANES-like engineering rows."""

    if seed < 0:
        raise ValueError("seed must be non-negative")
    if row_count < 24:
        raise ValueError("row_count must cover every sex/age-band/ethnicity cell")
    base = dict(sample_payload()["measurements"])
    combinations = [
        (sex, age_band, ethnicity)
        for sex in ("female", "male")
        for age_band in range(4)
        for ethnicity in ETHNICITIES
    ]
    rows: list[dict[str, Any]] = []
    for index in range(row_count):
        sex, age_band, ethnicity = combinations[index % len(combinations)]
        age = AGE_VALUES[age_band][(index // len(combinations)) % 2]
        sex_offset = 0.25 if sex == "male" else 0.0
        cycle = ((index + seed) % 11) - 5
        measurements = dict(base)
        measurements.update(
            {
                "age": age,
                "sex": sex,
                "bmi": round(22.0 + 0.22 * cycle + sex_offset, 3),
                "phase_angle": round(6.45 + sex_offset + 0.04 * cycle, 3),
                "ecw_tbw": round(0.395 - 0.0015 * cycle, 4),
                "fasting_glucose": round(89.0 + 0.8 * (cycle + 5), 3),
                "hba1c": round(5.1 + 0.025 * (cycle + 5), 3),
                "hs_crp": round(0.5 + 0.05 * ((index + seed) % 8), 3),
                "albumin": round(4.35 - 0.015 * ((index + seed) % 8), 3),
                "egfr": round(104.0 - 0.45 * max(age - 25, 0), 3),
                "wbc": round(5.8 + 0.06 * cycle, 3),
            }
        )
        event = (index + seed + age_band + (sex == "male")) % 3 != 0
        duration = (
            3.0 + float((index + seed) % 7)
            if event
            else 10.0 + float((index + seed) % 9)
        )
        rows.append(
            {
                "patient_id": f"synthetic-external-{index + 1:03d}",
                "duration": duration,
                "event": event,
                "ethnicity": ethnicity,
                **measurements,
            }
        )
    return rows


def build_fixture(
    *, seed: int = DEFAULT_SEED, row_count: int = ROW_COUNT
) -> dict[str, Any]:
    """Return the versioned fixture envelope used by the smoke runner."""

    return {
        "fixture_type": "synthetic_external_validation",
        "fixture_version": "1",
        "provenance": {
            "kind": "synthetic",
            "seed": seed,
            "row_count": row_count,
            "generator": "scripts/build_external_validation_fixture.py",
            "clinical_use": "forbidden",
            "note": (
                "Generated engineering rows only; not a clinical cohort, not a "
                "training source, and not evidence of model performance."
            ),
        },
        "rows": build_rows(seed=seed, row_count=row_count),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--row-count", type=int, default=ROW_COUNT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify that the existing output is byte-for-byte reproducible",
    )
    args = parser.parse_args()
    fixture = build_fixture(seed=args.seed, row_count=args.row_count)
    serialized = json.dumps(fixture, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file():
            raise FileNotFoundError(args.output)
        if args.output.read_text(encoding="utf-8") != serialized:
            raise ValueError(f"synthetic fixture is not reproducible: {args.output}")
        ok, message = verify_sidecar(args.output, root=args.output.parent.parent)
        if not ok:
            raise ValueError(message)
        print(f"synthetic external-validation fixture is reproducible: {args.output}")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8", newline="\n")
        write_sidecar(args.output, root=args.output.parent.parent)
        print(f"wrote synthetic external-validation fixture: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
