"""Minimum viable vector enforcement."""

from typing import Any, Mapping, TypedDict

from .exceptions import InsufficientDataError
from .features import BLOOD_FEATURES, HISTORY_FEATURES, PatientData


class MvvStatus(TypedDict):
    """JSON-safe result from evaluating the assessment minimum viable vector."""

    ok: bool
    missing: list[str]


def evaluate_mvv(values: Mapping[str, Any]) -> MvvStatus:
    """Return the assessment MVV status without raising.

    This is the non-throwing form of the assessment gate. Keeping the rule
    expressions here lets intake, diagnostics, and the raising pipeline use
    the same explicit requirements while preserving missing values as missing.
    """

    missing: list[str] = []
    for feature in ("age", "sex", "bmi", "phase_angle", "ecw_tbw"):
        if values.get(feature) is None:
            missing.append(f"{feature} is mandatory")

    blood_measured = [name for name in BLOOD_FEATURES if values.get(name) is not None]
    if len(blood_measured) < 6:
        missing.append(
            f"at least 6 blood variables are required (received {len(blood_measured)})"
        )
    if values.get("fasting_glucose") is None and values.get("hba1c") is None:
        missing.append("fasting_glucose or hba1c is required")

    history_measured = [
        name for name in HISTORY_FEATURES if values.get(name) is not None
    ]
    if len(history_measured) < 4:
        missing.append(
            f"at least 4 history variables are required (received {len(history_measured)})"
        )

    return {"ok": not missing, "missing": missing}


def check_mvv(patient: PatientData) -> None:
    """Raise a structured error unless the goal's MVV is satisfied."""

    status = evaluate_mvv(patient.values)
    if not status["ok"]:
        raise InsufficientDataError(
            "minimum viable vector not satisfied",
            missing_requirements=status["missing"],
        )


def check_training_requirements(patient: PatientData) -> None:
    """Require only model anchors when preparing a survival-training row.

    The assessment MVV intentionally requires enough blood and history values
    for a usable clinic readout. Applying those optional-field thresholds to
    training would select participants based on measurement completeness and
    undermine the native-missingness design. Training still requires the
    demographic anchor, BMI, and sex-stratified reference inputs.
    """

    missing = [
        f"{feature} is required for training"
        for feature in ("age", "sex", "bmi")
        if patient.values[feature] is None
    ]
    if missing:
        raise InsufficientDataError(
            "training model anchors not satisfied",
            missing_requirements=missing,
        )
