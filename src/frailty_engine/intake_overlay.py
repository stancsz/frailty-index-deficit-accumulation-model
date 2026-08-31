"""Load and merge the local SECA assessment-handoff contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .exceptions import InsufficientDataError, ValidationError
from .mvv import evaluate_mvv
from .seca import SecaTableViewExport

OVERLAY_FORMAT = "frailty-engine-assessment-overlay-v1"
DEFAULT_PATIENT_ID = "local-seca-overlay"
MAX_PATIENT_ID_LENGTH = 128


def load_overlay(path: str | Path) -> dict[str, Any]:
    """Read and validate the versioned JSON envelope produced by Pages."""

    try:
        with Path(path).open(encoding="utf-8") as handle:
            overlay = json.load(handle)
    except OSError as error:
        raise ValidationError(
            "overlay file could not be read",
            field_errors={"overlay": "unable to read the JSON file"},
        ) from error
    except json.JSONDecodeError as error:
        raise ValidationError(
            "overlay JSON is invalid",
            field_errors={"overlay": "expected valid JSON"},
        ) from error

    if not isinstance(overlay, dict):
        raise ValidationError(
            "overlay JSON must be an object",
            field_errors={"overlay": "expected object"},
        )
    if overlay.get("format") != OVERLAY_FORMAT:
        raise ValidationError(
            f"overlay format must be {OVERLAY_FORMAT}",
            field_errors={"format": f"expected {OVERLAY_FORMAT}"},
        )
    measurements = overlay.get("measurements")
    if not isinstance(measurements, dict):
        raise ValidationError(
            "overlay measurements must be an object",
            field_errors={"measurements": "expected object"},
        )
    return {**overlay, "measurements": dict(measurements)}


def _patient_id(overlay: dict[str, Any], override: str | None) -> str:
    value = overlay.get("patient_id")
    if value is None:
        value = override if override is not None else DEFAULT_PATIENT_ID
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(
            "patient_id must be a non-empty string",
            field_errors={"patient_id": "expected non-empty string"},
        )
    normalized = value.strip()
    if len(normalized) > MAX_PATIENT_ID_LENGTH:
        raise ValidationError(
            "patient_id must be 128 characters or fewer",
            field_errors={"patient_id": "must be 128 characters or fewer"},
        )
    return normalized


def merge_with_seca(
    overlay: dict[str, Any],
    seca_export: SecaTableViewExport,
    *,
    patient_id_override: str | None = None,
) -> dict[str, Any]:
    """Merge explicit overlay values with observed latest-scan SECA values.

    Non-null overlay values are retained. A manual overlay may not replace a
    non-null observed SECA value with a different value; this keeps the local
    handoff's source provenance explicit instead of silently changing a scan.
    """

    overlay_measurements = overlay["measurements"]
    seca_measurements = seca_export.assessment_payload_overlay()
    conflicts = {
        name: "must match the observed latest SECA value"
        for name, observed in seca_measurements.items()
        if name in overlay_measurements
        and overlay_measurements[name] is not None
        and overlay_measurements[name] != observed
    }
    if conflicts:
        raise ValidationError(
            "overlay conflicts with observed SECA values",
            field_errors=conflicts,
        )

    measurements = {
        **seca_measurements,
        **{
            name: value
            for name, value in overlay_measurements.items()
            if value is not None
        },
    }
    return {
        "patient_id": _patient_id(overlay, patient_id_override),
        "measurements": measurements,
    }


def overlay_mvv_missing(measurements: dict[str, Any]) -> list[str]:
    """Return the canonical MVV missing list for an overlay measurement map."""

    return evaluate_mvv(measurements)["missing"]


def require_overlay_mvv(measurements: dict[str, Any]) -> None:
    """Raise the same typed error as the assessment pipeline before scoring."""

    missing = overlay_mvv_missing(measurements)
    if missing:
        raise InsufficientDataError(
            "minimum viable vector not satisfied",
            missing_requirements=missing,
        )
