"""Stateless, descriptive comparison of two completed assessments.

The comparison layer is intentionally not a causal model.  It reports what
changed in two engine outputs and whether a measured wellness item moved into
or out of a development reference band.  It does not infer which action caused
the change, predict a future outcome, or estimate a treatment effect.
"""

from __future__ import annotations

from datetime import date
import math
from typing import Any, Literal, Mapping


ReadoutMovement = Literal["lower", "higher", "unchanged"]
RangeTransition = Literal[
    "unchanged",
    "moved_into_range",
    "moved_out_of_range",
    "status_changed",
    "new_measurement",
    "missing_now",
]


def _require_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an assessment mapping")
    return value


def _number(value: Any, name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be numeric") from error
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def _assessment_id(assessment: Mapping[str, Any], name: str) -> str:
    patient_id = assessment.get("patient_id")
    if not isinstance(patient_id, str) or not patient_id.strip():
        raise ValueError(f"{name}.patient_id must be a non-empty string")
    return patient_id.strip()


def _movement(delta: float) -> ReadoutMovement:
    if abs(delta) < 1e-9:
        return "unchanged"
    return "higher" if delta > 0 else "lower"


def _readout_change(metric: str, previous: Any, current: Any) -> dict[str, Any]:
    previous_number = _number(previous, f"previous.{metric}")
    current_number = _number(current, f"current.{metric}")
    delta = round(current_number - previous_number, 4)
    return {
        "metric": metric,
        "previous": previous_number,
        "current": current_number,
        "delta": delta,
        "movement": _movement(delta),
    }


def _range_transition(
    previous_status: str | None, current_status: str | None
) -> RangeTransition:
    if previous_status is None and current_status is not None:
        return "new_measurement"
    if previous_status is not None and current_status is None:
        return "missing_now"
    if previous_status == current_status:
        return "unchanged"
    if current_status == "in_range":
        return "moved_into_range"
    if previous_status == "in_range":
        return "moved_out_of_range"
    return "status_changed"


def _range_change(
    previous: Mapping[str, Any] | None,
    current: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = current or previous or {}
    previous_value = previous.get("current_value") if previous else None
    current_value = current.get("current_value") if current else None
    value_change = "not_comparable"
    delta: float | None = None
    if previous is not None and current is not None:
        if isinstance(previous_value, (int, float)) and isinstance(
            current_value, (int, float)
        ):
            delta = round(float(current_value) - float(previous_value), 4)
            value_change = _movement(delta)
        elif previous_value == current_value:
            value_change = "unchanged"
        else:
            value_change = "changed"
    elif current is not None:
        value_change = "new_measurement"
    elif previous is not None:
        value_change = "missing_now"
    return {
        "feature": source.get("feature", "unknown"),
        "biomarker": source.get("biomarker", source.get("feature", "unknown")),
        "previous_value": previous_value,
        "current_value": current_value,
        "value_delta": delta,
        "value_change": value_change,
        "previous_status": previous.get("status") if previous else None,
        "current_status": current.get("status") if current else None,
        "status_transition": _range_transition(
            previous.get("status") if previous else None,
            current.get("status") if current else None,
        ),
        "target_range": (current or previous or {}).get("target_range", {}),
        "unit": (current or previous or {}).get("unit"),
        "recommendation": (current or previous or {}).get("recommendation", ""),
    }


def build_progress_report(
    previous_assessment: Mapping[str, Any],
    current_assessment: Mapping[str, Any],
    *,
    previous_assessed_at: str,
    current_assessed_at: str,
) -> dict[str, Any]:
    """Compare two assessments for the same person without retaining inputs.

    Dates are ISO calendar dates and the current date must be later than the
    previous date.  The returned report contains derived report fields only;
    raw input payloads are deliberately excluded.
    """

    previous = _require_mapping(previous_assessment, "previous_assessment")
    current = _require_mapping(current_assessment, "current_assessment")
    previous_id = _assessment_id(previous, "previous_assessment")
    current_id = _assessment_id(current, "current_assessment")
    if previous_id != current_id:
        raise ValueError("assessments must use the same patient_id")
    try:
        previous_date = date.fromisoformat(previous_assessed_at)
        current_date = date.fromisoformat(current_assessed_at)
    except (TypeError, ValueError) as error:
        raise ValueError("assessment dates must use YYYY-MM-DD") from error
    if current_date <= previous_date:
        raise ValueError("current_assessed_at must be later than previous_assessed_at")

    current_model = _require_mapping(
        current.get("model_metadata"), "current.model_metadata"
    )
    previous_model = _require_mapping(
        previous.get("model_metadata"), "previous.model_metadata"
    )
    current_quality = _require_mapping(
        current.get("data_quality"), "current.data_quality"
    )
    previous_quality = _require_mapping(
        previous.get("data_quality"), "previous.data_quality"
    )
    if current_model.get("model_id") != previous_model.get("model_id"):
        raise ValueError("assessments must use the same model_id")
    if current_quality.get("reference_panel_id") != previous_quality.get(
        "reference_panel_id"
    ):
        raise ValueError("assessments must use the same reference_panel_id")
    previous_panel_sha256 = previous_quality.get("reference_panel_sha256")
    current_panel_sha256 = current_quality.get("reference_panel_sha256")
    if (
        previous_panel_sha256 is not None
        and current_panel_sha256 is not None
        and previous_panel_sha256 != current_panel_sha256
    ):
        raise ValueError("assessments must use the same reference_panel_sha256")

    previous_metrics = _require_mapping(previous.get("metrics"), "previous.metrics")
    current_metrics = _require_mapping(current.get("metrics"), "current.metrics")
    previous_age = _require_mapping(
        previous_metrics.get("biological_age"), "previous.metrics.biological_age"
    )
    current_age = _require_mapping(
        current_metrics.get("biological_age"), "current.metrics.biological_age"
    )
    previous_trajectory = _require_mapping(
        previous.get("trajectory"), "previous.trajectory"
    )
    current_trajectory = _require_mapping(
        current.get("trajectory"), "current.trajectory"
    )
    readout_changes = [
        _readout_change(
            "biological_age.point_estimate",
            previous_age.get("point_estimate"),
            current_age.get("point_estimate"),
        ),
        _readout_change(
            "current_deficit_load_fi",
            previous_metrics.get("current_deficit_load_fi"),
            current_metrics.get("current_deficit_load_fi"),
        ),
        _readout_change(
            "homeostatic_deviation_score",
            previous_trajectory.get("homeostatic_deviation_score"),
            current_trajectory.get("homeostatic_deviation_score"),
        ),
    ]

    previous_report = _require_mapping(
        previous.get("wellness_report"), "previous.wellness_report"
    )
    current_report = _require_mapping(
        current.get("wellness_report"), "current.wellness_report"
    )
    previous_ranges = {
        str(item.get("feature")): item
        for item in previous_report.get("ranges", [])
        if isinstance(item, Mapping) and item.get("feature")
    }
    current_ranges = {
        str(item.get("feature")): item
        for item in current_report.get("ranges", [])
        if isinstance(item, Mapping) and item.get("feature")
    }
    range_changes = [
        _range_change(previous_ranges.get(feature), current_ranges.get(feature))
        for feature in sorted(set(previous_ranges) | set(current_ranges))
    ]

    moved_into_range = [
        item["biomarker"]
        for item in range_changes
        if item["status_transition"] == "moved_into_range"
    ]
    moved_out_of_range = [
        item["biomarker"]
        for item in range_changes
        if item["status_transition"] == "moved_out_of_range"
    ]
    new_focus_areas = [
        item["biomarker"]
        for item in range_changes
        if item["previous_status"] in {None, "in_range"}
        and item["current_status"] not in {None, "in_range"}
    ]
    resolved_focus_areas = [
        item["biomarker"]
        for item in range_changes
        if item["previous_status"] not in {None, "in_range"}
        and item["current_status"] == "in_range"
    ]
    changed_ranges = [
        item["biomarker"]
        for item in range_changes
        if item["value_change"] not in {"unchanged", "not_comparable"}
        or item["status_transition"] != "unchanged"
    ]
    return {
        "format": "wellness-progress-report-v1",
        "comparison_basis": "same_model_and_reference_panel",
        "patient_id": current_id,
        "previous_assessed_at": previous_date.isoformat(),
        "current_assessed_at": current_date.isoformat(),
        "readout_changes": readout_changes,
        "range_changes": range_changes,
        "summary": {
            "changed_features": len(changed_ranges),
            "moved_into_reference_range": len(moved_into_range),
            "moved_out_of_reference_range": len(moved_out_of_range),
            "new_focus_areas": new_focus_areas,
            "resolved_focus_areas": resolved_focus_areas,
            "current_focus_areas": len(current_report.get("focus_areas", [])),
            "previous_missing_features": len(
                previous_report.get("missing_features", [])
            ),
            "current_missing_features": len(current_report.get("missing_features", [])),
            "interpretation": (
                "Descriptive change between two assessments. A change in a readout "
                "or reference-band status does not establish that an action caused "
                "it or that it will change health, biological age, or lifespan."
            ),
        },
        "current_focus_areas": list(current_report.get("focus_areas", [])),
        "model_boundary": {
            "previous_model_id": previous_model.get("model_id"),
            "current_model_id": current_model.get("model_id"),
            "previous_production_ready": bool(previous_model.get("production_ready")),
            "current_production_ready": bool(current_model.get("production_ready")),
            "previous_reference_panel_id": previous_quality.get("reference_panel_id"),
            "current_reference_panel_id": current_quality.get("reference_panel_id"),
            "previous_reference_panel_sha256": previous_panel_sha256,
            "current_reference_panel_sha256": current_panel_sha256,
        },
        "action_effect_estimated": False,
        "clinical_or_lifespan_claim": False,
        "disclaimer": (
            "This report compares measured engine outputs and development/reference "
            "bands only. It is not a treatment-effect estimate, clinical target, "
            "diagnosis, or lifespan prediction."
        ),
    }
