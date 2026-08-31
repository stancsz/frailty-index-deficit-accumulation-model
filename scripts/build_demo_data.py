"""Build safe, synthetic assessment fixtures for the static documentation site."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from frailty_engine import assess, build_progress_report  # noqa: E402

from attestation import verify_sidecar, write_sidecar  # noqa: E402


def _base() -> dict[str, object]:
    return {
        "fasting_glucose": 92,
        "hba1c": 5.3,
        "hs_crp": 0.7,
        "albumin": 4.2,
        "egfr": 98,
        "wbc": 6.0,
        "hypertension": 0,
        "t2d": 0,
        "osteoarthritis": 0,
        "sleep_apnea": 0,
    }


def _examples() -> list[dict[str, object]]:
    balanced = _base()
    balanced.update(
        {
            "age": 45,
            "sex": "female",
            "bmi": 23.4,
            "phase_angle": 6.1,
            "ecw_tbw": 0.39,
        }
    )
    support = _base()
    support.update(
        {
            "age": 62,
            "sex": "male",
            "bmi": 31.2,
            "systolic_bp": 146,
            "diastolic_bp": 92,
            "resting_hr": 96,
            "waist_circumference": 107,
            "phase_angle": 4.8,
            "ecw_tbw": 0.46,
            "ffmi": 16.5,
            "skeletal_muscle_mass": 30.0,
            "visceral_fat": 18.0,
            "fasting_glucose": 128,
            "hba1c": 6.8,
            "hs_crp": 4.0,
            "albumin": 3.4,
            "creatinine": 1.3,
            "egfr": 55,
            "alp": 180,
            "wbc": 11,
            "rdw": 16.8,
            "fib_4": 2.8,
            "hypertension": 1,
            "t2d": 1,
            "osteoarthritis": 1,
            "sleep_apnea": 1,
            "grip_strength": 21,
            "chair_rise_time": 16,
            "smoking_status": "current",
            "alcohol_heavy_use": 1,
            "sleep_hours": 5.5,
        }
    )
    seca_style = _base()
    seca_style.update(
        {
            "age": 51,
            "sex": "male",
            "bmi": 24.1,
            "phase_angle": 5.7,
            "ecw_tbw": 0.42,
            "ffmi": 21.2,
            "skeletal_muscle_mass": 31.6,
            "visceral_fat": 6.8,
        }
    )
    return [
        {
            "id": "balanced",
            "label": "Balanced baseline",
            "description": "Synthetic complete profile with a broad but not exhaustive measurement set.",
            "payload": {"patient_id": "demo-balanced", "measurements": balanced},
        },
        {
            "id": "support",
            "label": "More focus areas",
            "description": "Synthetic profile with several values outside the development display bands.",
            "payload": {"patient_id": "demo-support", "measurements": support},
        },
        {
            "id": "seca-style",
            "label": "SECA-informed BIA example",
            "description": "Synthetic BIA values informed by the SECA field set; this profile is intentionally separate from any local equipment export.",
            "payload": {"patient_id": "demo-seca-style", "measurements": seca_style},
        },
    ]


def _previous_payload(example: dict[str, object]) -> dict[str, object]:
    """Return a synthetic earlier snapshot for the Pages progress panel."""

    payload = example["payload"]
    assert isinstance(payload, dict)
    measurements = dict(payload["measurements"])
    if example["id"] == "balanced":
        measurements.update({"bmi": 26.1, "phase_angle": 5.2, "ecw_tbw": 0.44})
    elif example["id"] == "support":
        measurements.update(
            {
                "bmi": 33.0,
                "systolic_bp": 154,
                "phase_angle": 4.5,
                "ecw_tbw": 0.48,
            }
        )
    else:
        measurements.update(
            {
                "phase_angle": 5.35,
                "ecw_tbw": 0.44,
                "ffmi": 20.7,
                "skeletal_muscle_mass": 30.4,
                "visceral_fat": 8.2,
            }
        )
    return {"patient_id": payload["patient_id"], "measurements": measurements}


def _build_document() -> dict[str, object]:
    output = []
    for example in _examples():
        current_result = assess(example["payload"])
        previous_payload = _previous_payload(example)
        previous_result = assess(previous_payload)
        progress = build_progress_report(
            previous_result,
            current_result,
            previous_assessed_at="2026-01-15",
            current_assessed_at="2026-08-15",
        )
        output.append(
            {
                **example,
                "result": current_result,
                "progress": {
                    "previous_assessed_at": "2026-01-15",
                    "current_assessed_at": "2026-08-15",
                    "report": progress,
                },
            }
        )
    return {
        "schema_version": "0.1",
        "generated_by": "scripts/build_demo_data.py",
        "privacy_note": "Synthetic examples only; no patient export is embedded.",
        "examples": output,
    }


def _render_document(document: dict[str, object]) -> str:
    return json.dumps(document, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build or verify the synthetic Pages assessment artifact"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare the deterministic render with docs/demo-data.json without writing",
    )
    args = parser.parse_args(argv)

    destination = ROOT / "docs" / "demo-data.json"
    rendered = _render_document(_build_document())
    if args.check:
        try:
            current = destination.read_text(encoding="utf-8")
        except OSError as error:
            print(f"synthetic demo artifact check failed: {error}", file=sys.stderr)
            return 1
        if current != rendered:
            print(
                "synthetic demo artifact is out of date; run "
                "scripts/build_demo_data.py",
                file=sys.stderr,
            )
            return 1
        ok, message = verify_sidecar(destination, root=ROOT)
        if not ok:
            print(
                f"synthetic demo artifact {message}; run scripts/build_demo_data.py",
                file=sys.stderr,
            )
            return 1
        print("synthetic demo artifact is reproducible and up to date")
        return 0

    destination.write_text(rendered, encoding="utf-8")
    write_sidecar(destination, root=ROOT)
    print(f"synthetic demo artifact written: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
