"""Versioned provenance metadata for descriptive assessment comparisons."""

from __future__ import annotations

from typing import Any

from .features import FEATURE_NAMES, FEATURE_SPECS, PatientData
from .fi import FIResult


COMPARISON_CONTEXT_SCHEMA_VERSION = "comparison-context-v1"
FEATURE_CONTRACT_VERSION = "canonical-feature-contract-v1"
MEASUREMENT_PROTOCOL_VERSION = "canonical-feature-protocol-v1"
FI_CODING_VERSION = "rockwood-deficit-coding-v1"
FI_CUTOFF_SET_ID = "engineering-cutoff-set-v1"


# These are the canonical transport units accepted by the current feature
# parser. They describe the input contract, not a claim that any device,
# laboratory, or reference interval has been clinically harmonized.
FEATURE_UNITS: dict[str, str] = {
    "age": "years",
    "sex": "category",
    "bmi": "kg/m²",
    "systolic_bp": "mmHg",
    "diastolic_bp": "mmHg",
    "resting_hr": "bpm",
    "waist_circumference": "cm",
    "phase_angle": "degrees",
    "ecw_tbw": "ratio",
    "ffmi": "kg/m²",
    "skeletal_muscle_mass": "kg",
    "visceral_fat": "L",
    "fasting_glucose": "mg/dL",
    "hba1c": "%",
    "hs_crp": "mg/L",
    "albumin": "g/dL",
    "creatinine": "mg/dL",
    "egfr": "mL/min/1.73m²",
    "alp": "U/L",
    "wbc": "10⁹/L",
    "rdw": "%",
    "fib_4": "index",
    "hypertension": "binary",
    "t2d": "binary",
    "osteoarthritis": "binary",
    "sleep_apnea": "binary",
    "cvd": "binary",
    "copd": "binary",
    "cancer": "binary",
    "depression": "binary",
    "grip_strength": "kg",
    "chair_rise_time": "seconds",
    "smoking_status": "category",
    "alcohol_heavy_use": "binary",
    "sleep_hours": "hours",
}


def _feature_protocols() -> dict[str, str]:
    return {spec.name: MEASUREMENT_PROTOCOL_VERSION for spec in FEATURE_SPECS}


FEATURE_PROTOCOLS = _feature_protocols()


def build_comparison_context(
    patient: PatientData,
    fi: FIResult,
    *,
    predictor: Any,
    panel: Any,
) -> dict[str, Any]:
    """Return non-sensitive identity needed before comparing two outputs.

    The context contains feature names and contract identities only. It never
    carries raw measurements. An absent model artifact hash is intentional for
    the development surrogate and must make aggregate comparison ineligible.
    """

    measured_features = list(patient.measured_features)
    return {
        "schema_version": COMPARISON_CONTEXT_SCHEMA_VERSION,
        "feature_contract_version": FEATURE_CONTRACT_VERSION,
        "measurement_protocol_version": MEASUREMENT_PROTOCOL_VERSION,
        "measured_features": measured_features,
        "fi_valid_features": list(fi.valid_variables),
        "feature_units": {
            feature: FEATURE_UNITS[feature] for feature in measured_features
        },
        "feature_protocols": {
            feature: FEATURE_PROTOCOLS[feature] for feature in measured_features
        },
        "fi_coding_version": FI_CODING_VERSION,
        "fi_cutoff_set_id": FI_CUTOFF_SET_ID,
        "model_id": getattr(predictor, "model_id", "unknown"),
        "model_artifact_sha256": getattr(predictor, "artifact_sha256", None),
        "reference_panel_id": panel.panel_id,
        "reference_panel_sha256": getattr(panel, "source_sha256", None),
    }


def comparison_context_feature_names(context: dict[str, Any]) -> tuple[str, ...]:
    """Return a validated, deterministic measured-feature sequence."""

    raw = context.get("measured_features")
    if not isinstance(raw, list) or any(
        not isinstance(feature, str) or feature not in FEATURE_NAMES for feature in raw
    ):
        return ()
    return tuple(dict.fromkeys(raw))
