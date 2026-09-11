"""Category-level body measurement reports.

The current engine has one validated overall biological-age interface, not a
separate age model for every body system.  This module therefore groups the
measurements already in the canonical contract, reports coverage and reference
band status, and withholds a numeric category age until a category-specific
model, panel, uncertainty method, and review record exist.
"""

from __future__ import annotations

from typing import Any, Mapping

from .category_data import category_source_for
from .features import PatientData


_CATEGORY_SPECS: tuple[tuple[str, str, tuple[str, ...], str], ...] = (
    (
        "body_composition",
        "Body composition",
        ("bmi", "waist_circumference", "visceral_fat"),
        "Body-size and adiposity measurements are descriptive reference-band signals.",
    ),
    (
        "fluid_and_cellular",
        "Fluid and cellular health",
        ("phase_angle", "ecw_tbw"),
        "BIA hydration and cellular measurements are interpreted only against the configured panel.",
    ),
    (
        "muscle_health",
        "Muscle health",
        ("ffmi", "skeletal_muscle_mass", "grip_strength", "chair_rise_time"),
        "Muscle and function measurements are not a diagnosis of sarcopenia or physical capability.",
    ),
    (
        "joint_health",
        "Joint health",
        ("osteoarthritis", "chair_rise_time"),
        "Joint-function measurement profile only; the current 35-feature contract includes only an osteoarthritis history flag and a chair-rise timing proxy, so a numeric joint age is withheld until a joint-specific protocol, reference panel, model, and approval exist.",
    ),
    (
        "bone_health",
        "Bone health",
        (),
        "Bone density and bone-turnover measurements are not in the current 35-feature contract.",
    ),
    (
        "skin_health",
        "Skin health",
        (),
        "Skin hydration, elasticity, pigmentation, and lesion measurements are not in the current contract.",
    ),
    (
        "blood_health",
        "Blood health",
        (
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
        ),
        "Blood values are displayed with engineering/reference bands and require clinical context.",
    ),
    (
        "cardiovascular_health",
        "Cardiovascular health",
        ("systolic_bp", "diastolic_bp", "resting_hr", "hs_crp", "hypertension", "cvd"),
        "Cardiovascular measurements are not a diagnosis or a cardiovascular-risk estimate.",
    ),
    (
        "cardiorespiratory_health",
        "Cardiorespiratory health",
        ("systolic_bp", "diastolic_bp", "resting_hr"),
        "Heart-rate and blood-pressure context is shown without a VO2-max measurement or fitness-age claim.",
    ),
    (
        "immune_inflammatory_health",
        "Immune and inflammatory health",
        ("hs_crp", "wbc", "rdw"),
        "Inflammatory and blood-count markers are nonspecific and require clinical context; they are not an immune-age estimate.",
    ),
    (
        "brain_cognitive_health",
        "Brain and cognitive health",
        (),
        "Standardized cognitive testing and governed neuroimaging are not in the current 35-feature contract.",
    ),
    (
        "metabolic_health",
        "Metabolic health",
        (
            "bmi",
            "waist_circumference",
            "visceral_fat",
            "fasting_glucose",
            "hba1c",
            "t2d",
        ),
        "Metabolic measurements are descriptive and do not establish a diagnosis or treatment target.",
    ),
    (
        "kidney_health",
        "Kidney health",
        ("creatinine", "egfr"),
        "Kidney markers require laboratory and clinical context; this report is not a diagnosis.",
    ),
    (
        "liver_health",
        "Liver health",
        ("albumin", "alp", "fib_4"),
        "Liver-related markers are descriptive and do not diagnose liver disease.",
    ),
    (
        "sleep_and_recovery",
        "Sleep and recovery",
        ("sleep_hours", "sleep_apnea"),
        "Sleep fields are self-reported or historical and are not a sleep-disorder assessment.",
    ),
    (
        "lifestyle_and_function",
        "Lifestyle and function",
        (
            "grip_strength",
            "chair_rise_time",
            "smoking_status",
            "alcohol_heavy_use",
            "sleep_hours",
        ),
        "Lifestyle and function fields support discussion and trend review, not an intervention-effect estimate.",
    ),
    (
        "mental_health_history",
        "Mental-health history",
        ("depression",),
        "This is a reported history field and not a mental-health screening or diagnosis.",
    ),
)


def _category_measurement(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "feature": item["feature"],
        "label": item["biomarker"],
        "current_value": item["current_value"],
        "unit": item["unit"],
        "status": item["status"],
        "direction": item["direction"],
        "target_range": item["target_range"],
        "target_range_label": item["target_range"]["label"],
        "source": item["source"],
        "measurement_source": "assessment_payload",
        "measured_at": None,
        "protocol": "canonical_feature_contract",
        "reference_source": item["source"],
    }


def build_category_reports(
    patient: PatientData,
    wellness_ranges: list[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Return deterministic full-body category coverage and age-report shells."""

    by_feature = {str(item["feature"]): item for item in wellness_ranges}
    chronological_age_context = {
        "value": float(patient.values["age"]),
        "unit": "years",
        "source": "assessment_payload",
        "reference_date": None,
        "precision": "supplied_age_field",
        "status": "supplied_not_recomputed",
    }
    reports: list[dict[str, Any]] = []
    for category_id, label, features, interpretation in _CATEGORY_SPECS:
        measured = [
            feature
            for feature in features
            if patient.values.get(feature) is not None and feature in by_feature
        ]
        missing = [
            feature for feature in features if patient.values.get(feature) is None
        ]
        measurements = [
            _category_measurement(by_feature[feature]) for feature in measured
        ]
        if not features:
            status = "not_available"
            reference_status = "not_available"
            missing = ["no supported measurements in current feature contract"]
            age_status = "not_available"
            age_method = "no_supported_measurements"
            age_interpretation = "No category age report is available because this category is not measured by the current engine."
        else:
            status = (
                "complete"
                if not missing
                else ("partial" if measured else "not_available")
            )
            statuses = {item["status"] for item in measurements}
            if not measurements:
                reference_status = "not_available"
            elif statuses == {"in_range"}:
                reference_status = "within_reference"
            elif "in_range" in statuses:
                reference_status = "mixed"
            else:
                reference_status = "attention"
            age_status = "withheld_unvalidated" if measured else "not_available"
            age_method = "category_specific_model_not_available"
            age_interpretation = (
                "A numeric category age is withheld: the repository has no validated category-specific model, mapper, or uncertainty method."
                if measured
                else "No category age report is available until a supported measurement is supplied."
            )
        reports.append(
            {
                "system": category_id,
                "display_name": label,
                "category": category_id,
                "label": label,
                "source_data": category_source_for(category_id),
                "chronological_age_context": chronological_age_context,
                "status": status,
                "reference_status": reference_status,
                "measured_count": len(measured),
                "expected_count": len(features),
                "measurements": measurements,
                "measurement_profile": measurements,
                "missing_measurements": missing,
                "reference_interpretation": {
                    "status": reference_status,
                    "basis": (
                        "development_reference_band"
                        if measurements
                        else "not_available"
                    ),
                    "direction": (
                        "within_reference_band"
                        if reference_status == "within_reference"
                        else (
                            "not_available"
                            if reference_status == "not_available"
                            else "mixed_or_requires_context"
                        )
                    ),
                },
                "age_report": {
                    "status": age_status,
                    "label": "system_specific_age_equivalent",
                    "point_estimate": None,
                    "delta_from_chronological_age": None,
                    "ci_95": None,
                    "interval": None,
                    "interval_type": None,
                    "model_id": None,
                    "reference_panel_id": None,
                    "method": age_method,
                    "uncertainty_validated": False,
                    "interpretation": age_interpretation,
                },
                "interpretation": interpretation,
                "next_step": (
                    "Discuss the measured pattern, reference context, and missing inputs with a qualified professional."
                    if measured
                    else "Collect the domain measurements with an appropriate protocol before interpreting this system."
                ),
                "action_effect_estimated": False,
                "clinical_or_lifespan_claim": False,
            }
        )
    return reports
