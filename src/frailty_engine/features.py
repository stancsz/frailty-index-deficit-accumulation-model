"""Canonical feature matrix and strict input normalization."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping

from .exceptions import ValidationError


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    category: str
    kind: str
    minimum: float | None = None
    maximum: float | None = None


FEATURE_SPECS: tuple[FeatureSpec, ...] = (
    FeatureSpec("age", "demographics", "numeric", 18, 120),
    FeatureSpec("sex", "demographics", "sex"),
    FeatureSpec("bmi", "demographics", "numeric", 5, 100),
    FeatureSpec("systolic_bp", "demographics", "numeric", 50, 300),
    FeatureSpec("diastolic_bp", "demographics", "numeric", 30, 200),
    FeatureSpec("resting_hr", "demographics", "numeric", 20, 250),
    FeatureSpec("waist_circumference", "demographics", "numeric", 30, 250),
    FeatureSpec("phase_angle", "bia", "numeric", 0, 20),
    FeatureSpec("ecw_tbw", "bia", "numeric", 0.1, 0.8),
    FeatureSpec("ffmi", "bia", "numeric", 5, 60),
    FeatureSpec("skeletal_muscle_mass", "bia", "numeric", 1, 150),
    FeatureSpec("visceral_fat", "bia", "numeric", 0, 100),
    FeatureSpec("fasting_glucose", "blood", "numeric", 20, 1000),
    FeatureSpec("hba1c", "blood", "numeric", 2, 30),
    FeatureSpec("hs_crp", "blood", "numeric", 0, 1000),
    FeatureSpec("albumin", "blood", "numeric", 0.1, 8),
    FeatureSpec("creatinine", "blood", "numeric", 0.1, 20),
    FeatureSpec("egfr", "blood", "numeric", 0, 250),
    FeatureSpec("alp", "blood", "numeric", 1, 2000),
    FeatureSpec("wbc", "blood", "numeric", 0.1, 200),
    FeatureSpec("rdw", "blood", "numeric", 5, 50),
    FeatureSpec("fib_4", "blood", "numeric", 0, 100),
    FeatureSpec("hypertension", "history", "binary"),
    FeatureSpec("t2d", "history", "binary"),
    FeatureSpec("osteoarthritis", "history", "binary"),
    FeatureSpec("sleep_apnea", "history", "binary"),
    FeatureSpec("cvd", "history", "binary"),
    FeatureSpec("copd", "history", "binary"),
    FeatureSpec("cancer", "history", "binary"),
    FeatureSpec("depression", "history", "binary"),
    FeatureSpec("grip_strength", "functional", "numeric", 0, 150),
    FeatureSpec("chair_rise_time", "functional", "numeric", 0.1, 300),
    FeatureSpec("smoking_status", "functional", "smoking"),
    FeatureSpec("alcohol_heavy_use", "functional", "binary"),
    FeatureSpec("sleep_hours", "functional", "numeric", 0, 30),
)

FEATURE_NAMES = tuple(spec.name for spec in FEATURE_SPECS)
# Public alias for callers that want the complete matrix definition rather than
# only its ordered names.
FEATURE_MATRIX = FEATURE_SPECS
FEATURE_BY_NAME = {spec.name: spec for spec in FEATURE_SPECS}
BIA_FEATURES = tuple(spec.name for spec in FEATURE_SPECS if spec.category == "bia")
BLOOD_FEATURES = tuple(spec.name for spec in FEATURE_SPECS if spec.category == "blood")
HISTORY_FEATURES = tuple(
    spec.name for spec in FEATURE_SPECS if spec.category == "history"
)
FI_EXCLUDED_FEATURES = frozenset({"age", "sex"})
FI_FEATURES = tuple(name for name in FEATURE_NAMES if name not in FI_EXCLUDED_FEATURES)


@dataclass(frozen=True)
class PatientData:
    """Validated patient data with all 35 canonical keys present."""

    patient_id: str
    values: dict[str, Any]

    @property
    def measured_features(self) -> tuple[str, ...]:
        return tuple(name for name in FEATURE_NAMES if self.values[name] is not None)

    @property
    def variables_measured(self) -> int:
        return len(self.measured_features)


def _coerce_binary(value: Any, name: str) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return int(value)
    if (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and value in (0, 1)
    ):
        return int(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"0", "no", "false", "n", "absent"}:
            return 0
        if normalized in {"1", "yes", "true", "y", "present"}:
            return 1
    raise ValidationError(
        f"{name} must be a boolean or 0/1", field_errors={name: "expected binary value"}
    )


def _coerce_sex(value: Any) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise ValidationError(
            "sex must be male or female", field_errors={"sex": "expected string"}
        )
    normalized = value.strip().lower()
    aliases = {
        "m": "male",
        "man": "male",
        "male": "male",
        "f": "female",
        "woman": "female",
        "female": "female",
    }
    if normalized not in aliases:
        raise ValidationError(
            "sex must be male or female for the configured sex-stratified reference panel",
            field_errors={"sex": "unsupported sex stratum"},
        )
    return aliases[normalized]


def _coerce_smoking(value: Any) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise ValidationError(
            "smoking_status must be never, former, or current",
            field_errors={"smoking_status": "expected string"},
        )
    normalized = value.strip().lower()
    aliases = {
        "never": "never",
        "non-smoker": "never",
        "nonsmoker": "never",
        "former": "former",
        "ex": "former",
        "current": "current",
        "active": "current",
    }
    if normalized not in aliases:
        raise ValidationError(
            "smoking_status must be never, former, or current",
            field_errors={"smoking_status": "unsupported value"},
        )
    return aliases[normalized]


def _coerce_numeric(value: Any, spec: FeatureSpec) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(
            f"{spec.name} must be numeric", field_errors={spec.name: "expected number"}
        )
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValidationError(
            f"{spec.name} must be finite", field_errors={spec.name: "non-finite value"}
        )
    if (
        spec.minimum is not None
        and numeric < spec.minimum
        or spec.maximum is not None
        and numeric > spec.maximum
    ):
        raise ValidationError(
            f"{spec.name} is outside the accepted engineering range",
            field_errors={spec.name: f"expected {spec.minimum}..{spec.maximum}"},
        )
    return numeric


def parse_patient_data(payload: Mapping[str, Any]) -> PatientData:
    """Validate a request and normalize it into the canonical 35-feature vector."""

    if not isinstance(payload, Mapping):
        raise ValidationError("assessment payload must be an object")
    patient_id = payload.get("patient_id")
    if not isinstance(patient_id, str) or not patient_id.strip():
        raise ValidationError(
            "patient_id is required",
            field_errors={"patient_id": "expected non-empty string"},
        )

    measurements = payload.get("measurements", payload.get("features"))
    if measurements is None:
        measurements = {
            key: value for key, value in payload.items() if key != "patient_id"
        }
    if not isinstance(measurements, Mapping):
        raise ValidationError(
            "measurements must be an object",
            field_errors={"measurements": "expected object"},
        )

    unknown = sorted(set(measurements) - set(FEATURE_NAMES))
    if unknown:
        raise ValidationError(
            "unknown feature(s) supplied",
            field_errors={name: "unknown feature" for name in unknown},
        )

    values: dict[str, Any] = {name: None for name in FEATURE_NAMES}
    errors: dict[str, str] = {}
    for spec in FEATURE_SPECS:
        raw = measurements.get(spec.name)
        try:
            if spec.kind == "numeric":
                values[spec.name] = _coerce_numeric(raw, spec)
            elif spec.kind == "binary":
                values[spec.name] = _coerce_binary(raw, spec.name)
            elif spec.kind == "sex":
                values[spec.name] = _coerce_sex(raw)
            elif spec.kind == "smoking":
                values[spec.name] = _coerce_smoking(raw)
        except ValidationError as error:
            errors.update(error.field_errors or {spec.name: str(error)})
    if errors:
        raise ValidationError(
            "one or more measurements are invalid", field_errors=errors
        )
    return PatientData(patient_id=patient_id.strip(), values=values)
