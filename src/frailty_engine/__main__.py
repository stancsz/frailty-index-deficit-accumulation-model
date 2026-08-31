"""Command-line entry point for smoke testing the engine."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .exceptions import FrailtyEngineError, InsufficientDataError, ValidationError
from .intake_overlay import load_overlay, merge_with_seca, require_overlay_mvv
from .seca import read_seca_tableview_csv


RESEARCH_USE_NOTICE = (
    "research-use-only development artifact - not for clinical use - "
    "does not satisfy E-005"
)


def sample_payload() -> dict[str, Any]:
    return {
        "patient_id": "00000000-0000-0000-0000-000000000001",
        "measurements": {
            "age": 45,
            "sex": "female",
            "bmi": 23.4,
            "phase_angle": 6.1,
            "ecw_tbw": 0.39,
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
        },
    }


def _emit_cli_error(error: FrailtyEngineError) -> None:
    """Write one bounded, machine-readable error line to stderr."""

    detail: dict[str, Any] = {
        "code": type(error).__name__,
        "message": str(error),
    }
    if isinstance(error, InsufficientDataError):
        detail["missing_requirements"] = error.missing_requirements
    if isinstance(error, ValidationError):
        detail["field_errors"] = error.field_errors
    # Keep stderr machine-readable for callers that consume the structured
    # error envelope. Successful commands carry the human-facing research
    # boundary notice separately, while failures preserve the established
    # exact JSON shape.
    print(json.dumps({"error": detail}, ensure_ascii=False), file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Clinical healthspan engine")
    parser.add_argument(
        "command",
        choices=("sample", "assess", "seca", "assess-overlay"),
        nargs="?",
        default="sample",
    )
    parser.add_argument(
        "path", nargs="?", help="JSON request path for assess; stdin when omitted"
    )
    parser.add_argument(
        "--overlay",
        help="JSON measurement overlay for assess-overlay; stdin is not used",
    )
    parser.add_argument(
        "--patient-id",
        help=(
            "local identifier used only when the overlay omits patient_id; "
            "an existing overlay identifier wins"
        ),
    )
    args = parser.parse_args(argv)
    if args.command == "sample":
        payload = sample_payload()
    elif args.command == "seca":
        if not args.path:
            parser.error("seca requires a CSV path")
        export = read_seca_tableview_csv(args.path)
        print(RESEARCH_USE_NOTICE, file=sys.stderr)
        print(
            json.dumps(
                {
                    "source_format": export.source_format,
                    "latest_scan": {
                        "measured_at": export.latest.measured_at,
                        "measurements": export.latest.measurements,
                        "canonical_measurements": export.latest_measurements(),
                        "units": export.latest.units,
                        "segmental_skeletal_muscle_mass": export.latest.segmental_skeletal_muscle_mass,
                        "derivations": export.latest.derivations,
                        "unit_warnings": export.latest.unit_warnings,
                    },
                    "trend_latest_minus_previous": export.trend(),
                    "segmental_trend_latest_minus_previous": export.segmental_trend(),
                    "trend_note": export.trend_note,
                    "assessment_readiness": export.assessment_readiness,
                    "unmapped_labels": export.unmapped_labels,
                },
                indent=2,
            )
        )
        return 0
    elif args.command == "assess-overlay":
        if not args.path:
            parser.error("assess-overlay requires a SECA CSV path")
        if not args.overlay:
            parser.error("assess-overlay requires --overlay <path.json>")
        try:
            export = read_seca_tableview_csv(args.path)
            overlay = load_overlay(args.overlay)
            payload = merge_with_seca(
                overlay,
                export,
                patient_id_override=args.patient_id,
            )
            require_overlay_mvv(payload["measurements"])
            from .pipeline import assess

            result = assess(payload)
            if not isinstance(result, dict) or not result.get("data_quality", {}).get(
                "mvv_passed", False
            ):
                raise InsufficientDataError(
                    "minimum viable vector not satisfied",
                    missing_requirements=["assessment result did not pass MVV"],
                )
            print(RESEARCH_USE_NOTICE, file=sys.stderr)
            print(json.dumps(result, indent=2))
            return 0
        except InsufficientDataError as error:
            _emit_cli_error(error)
            return 2
        except ValidationError as error:
            _emit_cli_error(error)
            return 3
        except (OSError, ValueError):
            _emit_cli_error(
                ValidationError(
                    "SECA input validation failed",
                    field_errors={"seca": "unable to read or parse the TableView CSV"},
                )
            )
            return 3
        except FrailtyEngineError as error:
            _emit_cli_error(error)
            return 4
    elif args.path:
        with open(args.path, encoding="utf-8") as handle:
            payload = json.load(handle)
    else:
        payload = json.load(sys.stdin)
    from .pipeline import assess

    print(RESEARCH_USE_NOTICE, file=sys.stderr)
    print(json.dumps(assess(payload), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
