"""Run the deterministic synthetic external-validation engineering smoke."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from frailty_engine.validation import validate_external_cohort


EXPECTED_AGE_BANDS = {"18-39", "40-59", "60-79", "80+"}
EXPECTED_ETHNICITIES = {
    "synthetic-group-a",
    "synthetic-group-b",
    "synthetic-group-c",
}


def load_fixture(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    envelope = json.loads(path.read_text(encoding="utf-8"))
    if envelope.get("fixture_type") != "synthetic_external_validation":
        raise ValueError("fixture_type must identify the synthetic validation fixture")
    provenance = envelope.get("provenance", {})
    if (
        provenance.get("kind") != "synthetic"
        or provenance.get("clinical_use") != "forbidden"
    ):
        raise ValueError(
            "fixture provenance must remain synthetic and clinical-use forbidden"
        )
    rows = envelope.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("fixture rows must be a non-empty list")
    if provenance.get("row_count") != len(rows):
        raise ValueError("fixture provenance row_count does not match rows")
    return envelope, rows


def run(path: Path) -> dict[str, Any]:
    envelope, rows = load_fixture(path)
    report = validate_external_cohort(
        rows,
        cohort_name="synthetic-external-validation-engineering-fixture",
        bins=5,
        bootstrap_replicates=200,
        bootstrap_seed=int(envelope["provenance"]["seed"]),
    )
    if report.rows_evaluated != report.rows_received or report.rows_evaluated != len(
        rows
    ):
        raise RuntimeError("synthetic fixture unexpectedly excluded validation rows")
    if report.to_dict()["rows_excluded"] != 0:
        raise RuntimeError("synthetic fixture reported unexpected excluded rows")
    if report.concordance_index is None or report.concordance_ci_95 is None:
        raise RuntimeError("synthetic fixture did not produce concordance evidence")
    if report.concordance_ci_status != "emitted":
        raise RuntimeError("synthetic fixture did not emit a concordance interval")
    if report.concordance_ci_construction != "bootstrap_percentile":
        raise RuntimeError("synthetic fixture did not label bootstrap construction")
    if report.concordance_ci_valid_replicates < 100:
        raise RuntimeError(
            "synthetic fixture did not produce sufficient bootstrap support"
        )
    if (
        not report.calibration["probability_bins"]
        or not report.calibration["homeostatic_deviation_bins"]
    ):
        raise RuntimeError("synthetic fixture did not produce calibration bins")
    if set(report.subgroup_metrics["sex"]) != {"female", "male"}:
        raise RuntimeError("synthetic fixture does not cover both sex strata")
    if set(report.subgroup_metrics["age_band"]) != EXPECTED_AGE_BANDS:
        raise RuntimeError("synthetic fixture does not cover all age bands")
    if set(report.subgroup_metrics["ethnicity"]) != EXPECTED_ETHNICITIES:
        raise RuntimeError("synthetic fixture does not cover all ethnicity strata")

    invalid_rows = [dict(rows[index]) for index in (0, 1, 2)]
    invalid_rows[0]["patient_id"] = "exclusion-duration"
    invalid_rows[0]["duration"] = float("nan")
    invalid_rows[1]["patient_id"] = "exclusion-event"
    invalid_rows[1]["event"] = "not-a-boolean"
    invalid_rows[2]["patient_id"] = "exclusion-ethnicity"
    invalid_rows[2]["ethnicity"] = "synthetic-group-a"
    invalid_rows[2]["race_ethnicity"] = "synthetic-group-b"
    exclusion_report = validate_external_cohort(
        [*rows, *invalid_rows],
        cohort_name="synthetic-external-validation-exclusion-fixture",
        bins=5,
        bootstrap_replicates=200,
        bootstrap_seed=int(envelope["provenance"]["seed"]),
    )
    if exclusion_report.rows_evaluated != len(rows):
        raise RuntimeError("exclusion fixture evaluated an unexpected row count")
    if exclusion_report.to_dict()["rows_excluded"] != len(invalid_rows):
        raise RuntimeError("exclusion fixture did not report every invalid row")
    if set(exclusion_report.row_exclusion_counts) != {
        "duration must be positive and finite",
        "event must be boolean or 0/1",
        "ethnicity and race_ethnicity disagree; provide one consistent value",
    }:
        raise RuntimeError("exclusion fixture reported unexpected exclusion reasons")
    return {
        "fixture": path.as_posix(),
        "fixture_kind": envelope["provenance"]["kind"],
        "clinical_use": envelope["provenance"]["clinical_use"],
        "rows_received": report.rows_received,
        "rows_evaluated": report.rows_evaluated,
        "rows_excluded": report.to_dict()["rows_excluded"],
        "row_exclusion_counts": report.row_exclusion_counts,
        "concordance_index": report.concordance_index,
        "concordance_comparable_pairs": report.concordance_comparable_pairs,
        "concordance_ci_95": list(report.concordance_ci_95),
        "concordance_ci_status": report.concordance_ci_status,
        "concordance_ci_construction": report.concordance_ci_construction,
        "concordance_ci_valid_replicates": report.concordance_ci_valid_replicates,
        "calibration_bins": {
            "probability": len(report.calibration["probability_bins"]),
            "homeostatic_deviation": len(
                report.calibration["homeostatic_deviation_bins"]
            ),
            "biological_age": len(report.calibration["biological_age_bins"]),
        },
        "exclusion_smoke": {
            "rows_received": exclusion_report.rows_received,
            "rows_evaluated": exclusion_report.rows_evaluated,
            "rows_excluded": exclusion_report.to_dict()["rows_excluded"],
            "row_exclusion_counts": exclusion_report.row_exclusion_counts,
        },
        "status": report.status,
        "blockers": list(report.blockers),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path("examples/external_validation_synthetic.json"),
    )
    args = parser.parse_args()
    print(json.dumps(run(args.path), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
