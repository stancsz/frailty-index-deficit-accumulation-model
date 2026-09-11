"""Validate the non-approving shape of a system-age model manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


REQUIRED_SECTIONS = (
    "construct",
    "target",
    "measurement_protocol",
    "measurements",
    "missingness",
    "reference_panel",
    "model",
    "uncertainty",
    "age_output",
    "validation",
    "subgroup_support",
    "approval",
)
REQUIRED_TEXT_FIELDS = {
    "construct": ("label", "definition"),
    "target": ("name", "horizon", "outcome_definition", "incremental_value_question"),
    "measurement_protocol": (
        "protocol_id",
        "device_and_software",
        "unit_rules",
        "measurement_date_rule",
        "repeatability_plan",
        "operator_training",
    ),
    "missingness": ("policy", "minimum_complete_profile"),
    "reference_panel": (
        "panel_id",
        "population",
        "age_sex_strata",
        "device_protocol_match",
        "source_and_license",
        "sha256",
    ),
    "model": (
        "model_id",
        "algorithm_and_version",
        "training_cohort",
        "patient_level_split",
        "artifact_sha256",
    ),
    "uncertainty": ("method", "interval_type"),
}


def _require_object(
    data: dict[str, Any], key: str, failures: list[str]
) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        failures.append(f"{key} must be an object")
        return {}
    return value


def _require_text_fields(
    section: str, value: dict[str, Any], fields: tuple[str, ...], failures: list[str]
) -> None:
    for field in fields:
        if not isinstance(value.get(field), str) or not value[field].strip():
            failures.append(f"{section}.{field} must be a non-empty string")


def validate_manifest(path: Path) -> list[str]:
    """Return all contract failures; never approve a numeric age output."""

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return [f"could not read valid JSON: {error}"]
    if not isinstance(data, dict):
        return ["manifest root must be an object"]

    failures: list[str] = []
    for key in (
        "manifest_version",
        "status",
        "system",
        "display_name",
        *REQUIRED_SECTIONS,
    ):
        if key not in data:
            failures.append(f"missing top-level field: {key}")
    if data.get("manifest_version") != "1":
        failures.append("manifest_version must be '1'")
    if data.get("status") != "template":
        failures.append("status must be 'template'")
    for key in ("system", "display_name"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            failures.append(f"{key} must be a non-empty string")

    for section, fields in REQUIRED_TEXT_FIELDS.items():
        value = _require_object(data, section, failures)
        _require_text_fields(section, value, fields, failures)

    construct = _require_object(data, "construct", failures)
    for field in ("not_a_diagnosis", "not_a_lifespan_or_treatment_effect_estimate"):
        if construct.get(field) is not True:
            failures.append(f"construct.{field} must be true")

    measurements = data.get("measurements")
    if not isinstance(measurements, list) or not measurements:
        failures.append("measurements must be a non-empty list")
        measurements = []
    names: set[str] = set()
    for index, measurement in enumerate(measurements):
        if not isinstance(measurement, dict):
            failures.append(f"measurements[{index}] must be an object")
            continue
        name = measurement.get("name")
        if not isinstance(name, str) or not name.strip():
            failures.append(f"measurements[{index}].name must be a non-empty string")
        elif name in names:
            failures.append(f"measurements[{index}].name must be unique")
        else:
            names.add(name)
        for field in ("unit", "modality", "source_and_license", "quality_rule"):
            if (
                not isinstance(measurement.get(field), str)
                or not measurement[field].strip()
            ):
                failures.append(
                    f"measurements[{index}].{field} must be a non-empty string"
                )
        if not isinstance(measurement.get("required"), bool):
            failures.append(f"measurements[{index}].required must be boolean")

    missingness = _require_object(data, "missingness", failures)
    if not isinstance(missingness.get("sensitivity_analyses"), list):
        failures.append("missingness.sensitivity_analyses must be a list")

    model = _require_object(data, "model", failures)
    if (
        not isinstance(model.get("feature_names_and_order"), list)
        or not model["feature_names_and_order"]
    ):
        failures.append("model.feature_names_and_order must be a non-empty list")

    uncertainty = _require_object(data, "uncertainty", failures)
    if uncertainty.get("validated") is not False:
        failures.append("uncertainty.validated must be false")
    if not isinstance(uncertainty.get("measurement_error_included"), bool):
        failures.append("uncertainty.measurement_error_included must be boolean")

    age_output = _require_object(data, "age_output", failures)
    if age_output.get("label") != "system_specific_age_equivalent":
        failures.append("age_output.label must be system_specific_age_equivalent")
    if age_output.get("unit") != "years":
        failures.append("age_output.unit must be years")
    if age_output.get("numeric_allowed") is not False:
        failures.append("age_output.numeric_allowed must be false")
    for field in ("point_estimate", "interval"):
        if age_output.get(field) is not None:
            failures.append(f"age_output.{field} must be null in a template")
    if (
        not isinstance(age_output.get("withheld_reason"), str)
        or not age_output["withheld_reason"].strip()
    ):
        failures.append("age_output.withheld_reason must be a non-empty string")

    subgroup = _require_object(data, "subgroup_support", failures)
    if not isinstance(subgroup.get("dimensions"), list) or not subgroup["dimensions"]:
        failures.append("subgroup_support.dimensions must be a non-empty list")
    for field in ("support_definition", "missingness_sensitivity"):
        if not isinstance(subgroup.get(field), str) or not subgroup[field].strip():
            failures.append(f"subgroup_support.{field} must be a non-empty string")

    approval = _require_object(data, "approval", failures)
    if approval.get("status") != "not_submitted":
        failures.append("approval.status must be not_submitted")
    if approval.get("production_ready") is not False:
        failures.append("approval.production_ready must be false")
    if approval.get("clinical_or_lifespan_claim") is not False:
        failures.append("approval.clinical_or_lifespan_claim must be false")
    if (
        approval.get("approved_by") is not None
        or approval.get("approved_at") is not None
    ):
        failures.append("approval approver and timestamp must be null in a template")
    if approval.get("evidence_refs") != []:
        failures.append("approval.evidence_refs must be empty in a template")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    failures = validate_manifest(args.path)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    print(f"system-age manifest shape passed: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
