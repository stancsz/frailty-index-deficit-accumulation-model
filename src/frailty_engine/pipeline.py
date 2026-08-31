"""End-to-end assessment orchestration."""

from __future__ import annotations

from typing import Any, Mapping

from .calibration import ReferencePanel, default_development_panel, panel_readiness
from .features import BIA_FEATURES, PatientData, parse_patient_data
from .fi import calculate_fi
from .model import (
    MODEL_VECTOR_FEATURE_NAMES as _MODEL_VECTOR_FEATURE_NAMES,
    MODEL_VECTOR_SOURCE_FEATURE_NAMES,
    DevelopmentPredictor,
    ModelAdapterProtocol,
    ModelPrediction,
)
from .mvv import check_mvv, check_training_requirements
from .recommendations import top_interventions
from .wellness import build_wellness_report


# Preserve the established public import path while keeping the model module as
# the single source of truth for the encoded contract.
MODEL_VECTOR_FEATURE_NAMES = _MODEL_VECTOR_FEATURE_NAMES


def _model_feature_vector(
    patient: PatientData, z_scores: dict[str, float], fi_score: float
) -> list[float]:
    """Return a stable numeric vector for a fitted model adapter."""

    # The production training manifest must define this order explicitly. The
    # source-name tuple and encoder below are the single implementation source
    # for the persisted model feature order, including the smoking encoding.
    def value_for(name: str) -> float:
        if name == "sex":
            return 1.0 if patient.values["sex"] == "male" else 0.0
        if name in BIA_FEATURES:
            return float(z_scores[name]) if name in z_scores else float("nan")
        if name == "smoking_status":
            smoking = patient.values["smoking_status"]
            return {"never": 0.0, "former": 0.5, "current": 1.0}.get(
                smoking, float("nan")
            )
        if name == "current_deficit_load_fi":
            return float(fi_score)
        value = patient.values[name]
        return float(value) if value is not None else float("nan")

    return [value_for(name) for name in MODEL_VECTOR_SOURCE_FEATURE_NAMES]


def _render_prediction(
    prediction: ModelPrediction, chronological_age: float
) -> dict[str, Any]:
    serialized_ci = (
        list(prediction.ci_95)
        if prediction.ci_95 is not None and prediction.uncertainty_validated
        else None
    )
    uncertainty_construction = "none_withheld"
    if serialized_ci is not None:
        uncertainty_construction = prediction.uncertainty_construction
        if uncertainty_construction != "wald_1_96_se":
            raise ValueError(
                "numeric assessment interval requires the wald_1_96_se construction"
            )
    return {
        "point_estimate": prediction.point_estimate,
        "ci_95": serialized_ci,
        "uncertainty_method": prediction.uncertainty_method,
        "uncertainty_construction": uncertainty_construction,
        "uncertainty_validated": prediction.uncertainty_validated,
        "interpretation": (
            "Age-equivalent wellness estimate; not a lifespan, diagnostic, "
            "or treatment-effect prediction."
        ),
    }


def assess(
    payload: Mapping[str, Any],
    *,
    reference_panel: ReferencePanel | None = None,
    predictor: Any | None = None,
) -> dict[str, Any]:
    """Validate, calibrate, score, and return the public wellness response."""

    patient = parse_patient_data(payload)
    check_mvv(patient)
    panel = reference_panel or default_development_panel()
    z_scores = panel.z_scores(patient)
    fi = calculate_fi(patient, z_scores)
    wellness_report = build_wellness_report(patient, fi, z_scores, panel)
    model = predictor or DevelopmentPredictor()
    chronological_age = float(patient.values["age"])
    vector = _model_feature_vector(patient, z_scores, fi.score)
    if not isinstance(model, ModelAdapterProtocol):
        raise TypeError(
            "predictor must implement predict_for_assessment(age, encoded_vector)"
        )
    prediction = model.predict_for_assessment(chronological_age, vector)
    deviation = round(
        (prediction.point_estimate - float(patient.values["age"]))
        / max(float(patient.values["age"]), 1.0),
        4,
    )
    score_ci_95 = None
    if prediction.ci_95 is not None and prediction.uncertainty_validated:
        low, high = prediction.ci_95
        score_ci_95 = [
            round(
                (low - float(patient.values["age"]))
                / max(float(patient.values["age"]), 1.0),
                4,
            ),
            round(
                (high - float(patient.values["age"]))
                / max(float(patient.values["age"]), 1.0),
                4,
            ),
        ]
    rendered_prediction = _render_prediction(prediction, float(patient.values["age"]))
    score_uncertainty_construction = (
        rendered_prediction["uncertainty_construction"]
        if score_ci_95 is not None
        else "none_withheld"
    )
    blood_count = sum(
        patient.values[name] is not None
        for name in (
            "fasting_glucose",
            "hba1c",
            "hs_crp",
            "albumin",
            "creatinine",
            "egfr",
            "alp",
            "wbc",
            "rdw",
            "fib_4",
        )
    )
    history_count = sum(
        patient.values[name] is not None
        for name in (
            "hypertension",
            "t2d",
            "osteoarthritis",
            "sleep_apnea",
            "cvd",
            "copd",
            "cancer",
            "depression",
        )
    )
    sex_value = str(patient.values["sex"])
    band_count, band_span = panel.coverage_for(sex_value, chronological_age)
    return {
        "patient_id": patient.patient_id,
        "data_quality": {
            "variables_measured": patient.variables_measured,
            "fi_variables_measured": fi.denominator,
            "mvv_passed": True,
            "blood_variables_measured": blood_count,
            "history_variables_measured": history_count,
            "reference_panel_id": panel.panel_id,
            "reference_panel_sha256": getattr(panel, "source_sha256", None),
            "reference_panel_production_ready": panel.production_ready,
            "reference_panel_fixture_only": bool(getattr(panel, "fixture_only", False)),
            "reference_panel_readiness": panel_readiness(panel),
            "fi_denominator_strength": fi.denominator_strength,
            "reference_panel_band_count": band_count,
            "reference_panel_band_span_years_for_age": band_span,
        },
        "metrics": {
            "chronological_age": chronological_age,
            "biological_age": rendered_prediction,
            "current_deficit_load_fi": fi.score,
            "current_deficit_load_fi_details": {
                "numerator": fi.numerator,
                "denominator": fi.denominator,
                "valid_variables": list(fi.valid_variables),
                "denominator_strength": fi.denominator_strength,
                "denominator_strength_caveat": fi.denominator_strength_caveat,
            },
        },
        "trajectory": {
            "homeostatic_deviation_score": deviation,
            "score_ci_95": score_ci_95,
            "uncertainty_construction": score_uncertainty_construction,
        },
        "top_interventions": top_interventions(
            patient,
            fi,
            z_scores,
            wellness_ranges=wellness_report["ranges"],
        ),
        "wellness_report": wellness_report,
        "model_metadata": {
            "model_id": prediction.model_id,
            "production_ready": prediction.production_ready,
        },
        "quality_notes": [
            fi.caveat,
            "No missing value was fabricated; XGBoost may receive NaN for absent features.",
            "homeostatic_deviation_score is normalized as (biological age - chronological age) / chronological age; it is not a hazard ratio.",
            *(
                [panel.source_note]
                if not panel.production_ready and panel.source_note
                else []
            ),
            *([prediction.warning] if prediction.warning else []),
        ],
    }


def model_vector(
    payload: Mapping[str, Any],
    *,
    reference_panel: ReferencePanel | None = None,
    enforce_mvv: bool = True,
) -> tuple[PatientData, list[float]]:
    """Expose a stable model vector with assessment or training validation.

    `enforce_mvv=True` is the public assessment contract. Training callers
    set it to false so optional blood/history missingness is retained for
    XGBoost rather than converted into complete-case selection.
    """

    patient = parse_patient_data(payload)
    if enforce_mvv:
        check_mvv(patient)
    else:
        check_training_requirements(patient)
    panel = reference_panel or default_development_panel()
    z_scores = panel.z_scores(patient)
    fi = calculate_fi(patient, z_scores)
    return patient, _model_feature_vector(patient, z_scores, fi.score)
