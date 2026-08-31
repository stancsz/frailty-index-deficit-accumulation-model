"""Conservative range-based wellness reporting for measured features.

This is a transparent interpretation layer, not a treatment planner. Ranges
are engineering/reference targets and every item carries that provenance so a
clinical reviewer can replace them without changing the API contract.
"""

from __future__ import annotations

from typing import Any

from .calibration import ReferencePanel
from .features import FEATURE_NAMES, PatientData
from .fi import FIResult


_NUMERIC_RULES: dict[str, dict[str, Any]] = {
    "bmi": {
        "label": "Body Mass Index",
        "unit": "kg/m²",
        "low": 18.5,
        "high": 24.9,
        "source": "WHO BMI classification; engineering target pending cohort review",
        "recommendation": "Discuss sustainable nutrition, activity, and body-composition goals rather than pursuing a single number.",
    },
    "systolic_bp": {
        "label": "Systolic blood pressure",
        "unit": "mmHg",
        "low": 90.0,
        "high": 129.0,
        "source": "2017 ACC/AHA adult blood pressure guideline; engineering target",
        "recommendation": "Repeat under consistent conditions and review persistent readings with a qualified clinician.",
    },
    "diastolic_bp": {
        "label": "Diastolic blood pressure",
        "unit": "mmHg",
        "low": 60.0,
        "high": 79.0,
        "source": "2017 ACC/AHA adult blood pressure guideline; engineering target",
        "recommendation": "Repeat under consistent conditions and review persistent readings with a qualified clinician.",
    },
    "resting_hr": {
        "label": "Resting heart rate",
        "unit": "bpm",
        "low": 50.0,
        "high": 90.0,
        "source": "Engineering screening band; target-cohort review required",
        "recommendation": "Compare with a consistent resting measurement and discuss persistent outliers in context.",
    },
    "waist_circumference": {
        "label": "Waist circumference",
        "unit": "cm",
        "source": "IDF metabolic-syndrome definition; sex-stratified engineering target",
        "recommendation": "Use repeatable measurement technique and focus on sustainable activity, nutrition, and sleep habits.",
    },
    "visceral_fat": {
        "label": "Visceral adipose tissue",
        "unit": "L",
        "low": 0.0,
        "high": 10.0,
        "source": "SECA reference-panel measurement; threshold approval remains external",
        "recommendation": "Track the trend under consistent scan conditions and discuss sustainable body-composition goals.",
    },
    "fasting_glucose": {
        "label": "Fasting glucose",
        "unit": "mg/dL",
        "low": 70.0,
        "high": 99.0,
        "source": "ADA diagnostic thresholds; wellness display band is not a diagnosis",
        "recommendation": "Review the result, fasting conditions, and trend with a qualified clinician if outside the display band.",
    },
    "hba1c": {
        "label": "HbA1c",
        "unit": "%",
        "low": 4.0,
        "high": 5.6,
        "source": "ADA Standards of Care; wellness display band is not a diagnosis",
        "recommendation": "Review the result and trend with a qualified clinician; do not infer a diagnosis from this report.",
    },
    "hs_crp": {
        "label": "hs-CRP",
        "unit": "mg/L",
        "low": 0.0,
        "high": 1.0,
        "source": "Cardiovascular reference band; target-cohort review required",
        "recommendation": "Consider recent infection, injury, and measurement context before acting on an isolated result.",
    },
    "albumin": {
        "label": "Albumin",
        "unit": "g/dL",
        "low": 3.5,
        "high": 5.0,
        "source": "Common clinical reference boundary; target-cohort review required",
        "recommendation": "Review nutrition, hydration, liver, kidney, and inflammatory context with a qualified clinician.",
    },
    "creatinine": {
        "label": "Creatinine",
        "unit": "mg/dL",
        "source": "Common clinical reference boundary; sex and laboratory stratification required",
        "recommendation": "Interpret alongside eGFR and longitudinal context with a qualified clinician.",
    },
    "egfr": {
        "label": "eGFR",
        "unit": "mL/min/1.73m²",
        "low": 90.0,
        "source": "KDIGO CKD G-category thresholds; wellness display is not a diagnosis",
        "recommendation": "Interpret kidney markers with a qualified clinician and the person’s longitudinal trend.",
    },
    "alp": {
        "label": "Alkaline phosphatase",
        "unit": "U/L",
        "low": 44.0,
        "high": 147.0,
        "source": "Common adult laboratory reference interval; laboratory review required",
        "recommendation": "Check the reporting laboratory's interval and review persistent differences with a qualified clinician.",
    },
    "wbc": {
        "label": "White blood cell count",
        "unit": "10⁹/L",
        "low": 4.0,
        "high": 10.0,
        "source": "Common adult laboratory reference interval; laboratory review required",
        "recommendation": "Interpret with symptoms, recent illness, medications, and the reporting laboratory's interval.",
    },
    "rdw": {
        "label": "RDW",
        "unit": "%",
        "low": 11.5,
        "high": 14.5,
        "source": "Common adult laboratory reference interval; laboratory review required",
        "recommendation": "Review alongside the complete blood count and clinical context with a qualified clinician.",
    },
    "fib_4": {
        "label": "FIB-4",
        "unit": "index",
        "low": 0.0,
        "high": 1.3,
        "source": "FIB-4 published risk thresholds; wellness display is not a diagnosis",
        "recommendation": "Review the underlying AST, ALT, platelet count, age, and trend with a qualified clinician.",
    },
    "grip_strength": {
        "label": "Grip strength",
        "unit": "kg",
        "source": "EWGSOP2 low-strength guidance; sex-stratified engineering target",
        "recommendation": "Track repeatable measurements and consider supervised strength and balance work appropriate to the person.",
    },
    "chair_rise_time": {
        "label": "Chair-rise time",
        "unit": "seconds",
        "low": 0.0,
        "high": 10.0,
        "source": "Short Physical Performance Battery convention; engineering target",
        "recommendation": "Consider supervised lower-body strength, balance, and mobility work.",
    },
    "sleep_hours": {
        "label": "Sleep duration",
        "unit": "hours",
        "low": 7.0,
        "high": 9.0,
        "source": "Engineering sleep-duration band; target-cohort review required",
        "recommendation": "Work toward a consistent sleep schedule and review persistent sleep concerns professionally.",
    },
}

_HISTORY_LABELS = {
    "hypertension": "Hypertension history",
    "t2d": "Type 2 diabetes history",
    "osteoarthritis": "Osteoarthritis history",
    "sleep_apnea": "Sleep-apnea history",
    "cvd": "Cardiovascular-disease history",
    "copd": "COPD history",
    "cancer": "Cancer history",
    "depression": "Depression history",
    "alcohol_heavy_use": "Heavy alcohol-use flag",
}

_BIA_LABELS = {
    "phase_angle": "Phase Angle",
    "ecw_tbw": "ECW/TBW",
    "ffmi": "FFMI",
    "skeletal_muscle_mass": "Skeletal Muscle Mass",
}

_REVIEW_FEATURES = frozenset(
    {
        "ecw_tbw",
        "systolic_bp",
        "diastolic_bp",
        "resting_hr",
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
        "hypertension",
        "t2d",
        "osteoarthritis",
        "sleep_apnea",
        "cvd",
        "copd",
        "cancer",
        "depression",
        "alcohol_heavy_use",
    }
)


def _priority(status: str) -> str:
    return {
        "in_range": "maintain",
        "attention": "review",
        "below_target": "priority",
        "above_target": "priority",
        "flagged": "review",
    }.get(status, "review")


def _action_type(feature: str) -> str:
    return "review" if feature in _REVIEW_FEATURES else "lifestyle"


def _numeric_status(value: float, low: float | None, high: float | None) -> str:
    if low is not None and value < low:
        return "below_target"
    if high is not None and value > high:
        return "above_target"
    return "in_range"


def _item(
    *,
    feature: str,
    label: str,
    value: object,
    unit: str | None,
    status: str,
    target_range: dict[str, Any],
    source: str,
    recommendation: str,
    z_score: float | None = None,
    direction: str | None = None,
) -> dict[str, Any]:
    return {
        "feature": feature,
        "biomarker": label,
        "current_value": value,
        "unit": unit,
        "target_range": target_range,
        "status": status,
        "direction": direction
        or {
            "below_target": "below",
            "above_target": "above",
            "attention": "flagged",
            "flagged": "flagged",
        }.get(status, "within_range"),
        "priority": _priority(status),
        "action_type": _action_type(feature),
        "z_score": round(z_score, 4) if z_score is not None else None,
        "source": source,
        "recommendation": recommendation,
    }


def _bia_item(
    patient: PatientData,
    panel: ReferencePanel,
    feature: str,
    z_scores: dict[str, float],
) -> dict[str, Any] | None:
    value = patient.values[feature]
    z = z_scores.get(feature)
    if value is None or z is None:
        return None
    band = panel.band_for(
        feature, str(patient.values["sex"]), float(patient.values["age"])
    )
    if z < -2.0:
        status = "below_target"
    elif z > 2.0:
        status = "above_target"
    elif z < -1.0 or z > 1.0:
        status = "attention"
    else:
        status = "in_range"
    direction = "below" if z < -1.0 else "above" if z > 1.0 else "within_range"
    recommendation = {
        "phase_angle": "Discuss progressive resistance training, adequate nutrition, and recovery with a qualified professional.",
        "ecw_tbw": "Review hydration context, recent illness, and measurement conditions with a qualified professional.",
        "ffmi": "Discuss a safe resistance-training and nutrition plan appropriate to the person's goals and context.",
        "skeletal_muscle_mass": "Track the trend under consistent scan conditions and discuss progressive strength work.",
    }[feature]
    return _item(
        feature=feature,
        label=_BIA_LABELS[feature],
        value=value,
        unit={
            "phase_angle": "degrees",
            "ecw_tbw": "ratio",
            "ffmi": "kg/m²",
            "skeletal_muscle_mass": "kg",
        }[feature],
        status=status,
        target_range={
            "low": round(band.mean - band.standard_deviation, 4),
            "high": round(band.mean + band.standard_deviation, 4),
            "label": "within ±1 development reference SD",
            "kind": "development_reference_band",
        },
        source=f"{band.source}; development reference band, not a clinical cutoff",
        recommendation=recommendation,
        z_score=z,
        direction=direction,
    )


def build_wellness_report(
    patient: PatientData,
    fi: FIResult,
    z_scores: dict[str, float],
    panel: ReferencePanel,
) -> dict[str, Any]:
    """Build an auditable improvement report from the measured values only."""

    items: list[dict[str, Any]] = []
    missing: list[str] = []
    for feature in FEATURE_NAMES:
        if feature in {"age", "sex"}:
            continue
        value = patient.values[feature]
        if value is None:
            missing.append(feature)
            continue
        if feature in {"phase_angle", "ecw_tbw", "ffmi", "skeletal_muscle_mass"}:
            bia_item = _bia_item(patient, panel, feature, z_scores)
            if bia_item is not None:
                items.append(bia_item)
            continue
        if feature == "waist_circumference":
            male = patient.values["sex"] == "male"
            low, high = (0.0, 94.0) if male else (0.0, 80.0)
            rule = _NUMERIC_RULES[feature]
            items.append(
                _item(
                    feature=feature,
                    label=rule["label"],
                    value=value,
                    unit=rule["unit"],
                    status=_numeric_status(float(value), low, high),
                    target_range={"low": low, "high": high, "label": f"< {high:g}"},
                    source=rule["source"],
                    recommendation=rule["recommendation"],
                )
            )
            continue
        if feature == "creatinine":
            high = 1.2 if patient.values["sex"] == "male" else 1.0
            rule = _NUMERIC_RULES[feature]
            items.append(
                _item(
                    feature=feature,
                    label=rule["label"],
                    value=value,
                    unit=rule["unit"],
                    status=_numeric_status(float(value), 0.0, high),
                    target_range={"low": 0.0, "high": high, "label": f"≤ {high:g}"},
                    source=rule["source"],
                    recommendation=rule["recommendation"],
                )
            )
            continue
        if feature in _HISTORY_LABELS:
            items.append(
                _item(
                    feature=feature,
                    label=_HISTORY_LABELS[feature],
                    value=value,
                    unit=None,
                    status="in_range" if int(value) == 0 else "flagged",
                    target_range={
                        "low": 0,
                        "high": 0,
                        "label": "0 = no reported history",
                    },
                    source="Binary history field; not independently verified",
                    recommendation="Discuss the reported history and routine follow-up with the person's care team; this report does not diagnose or clear a condition.",
                )
            )
            continue
        rule = _NUMERIC_RULES.get(feature)
        if rule is None:
            if feature == "smoking_status":
                status = {
                    "never": "in_range",
                    "former": "attention",
                    "current": "flagged",
                }[str(value)]
                items.append(
                    _item(
                        feature=feature,
                        label="Smoking status",
                        value=value,
                        unit=None,
                        status=status,
                        target_range={
                            "label": "never / former",
                            "kind": "wellness_target",
                        },
                        source="Ordinal lifestyle field; self-reported",
                        recommendation="If currently smoking, offer evidence-based cessation support and a patient-chosen next step.",
                    )
                )
            continue
        low = rule.get("low")
        high = rule.get("high")
        if feature == "grip_strength":
            low = 30.0 if patient.values["sex"] == "male" else 20.0
            high = None
        status = _numeric_status(float(value), low, high)
        label = rule["label"]
        if feature == "chair_rise_time":
            status = _numeric_status(float(value), None, high)
        items.append(
            _item(
                feature=feature,
                label=label,
                value=value,
                unit=rule["unit"],
                status=status,
                target_range={
                    key: val
                    for key, val in {
                        "low": low,
                        "high": high,
                        "label": (
                            f"{low:g}–{high:g}"
                            if low is not None and high is not None
                            else (f"≥ {low:g}" if low is not None else f"≤ {high:g}")
                        ),
                    }.items()
                    if val is not None
                },
                source=rule["source"],
                recommendation=rule["recommendation"],
            )
        )

    rank = {"priority": 0, "review": 1, "maintain": 2}
    focus = sorted(items, key=lambda item: (rank[item["priority"]], item["biomarker"]))
    focus = [item for item in focus if item["status"] != "in_range"]
    focus_areas = [
        {
            "feature": item["feature"],
            "focus": item["biomarker"],
            "current_value": item["current_value"],
            "unit": item["unit"],
            "target_range": item["target_range"],
            "target_range_label": item["target_range"]["label"],
            "direction": item["direction"],
            "action_type": item["action_type"],
            "z_score": item["z_score"],
            "source": item["source"],
            "recommendation": item["recommendation"],
        }
        for item in focus
    ]
    return {
        "summary": {
            "status": "on_track" if not focus else "focus_areas",
            "measured_features": len(items),
            "missing_features": len(missing),
            "focus_areas": len(focus),
            "interpretation": "This is a development wellness view of measured values. It does not estimate the effect of an action on biological age.",
        },
        "ranges": items,
        "focus_areas": focus_areas,
        "missing_features": missing,
        "fi_context": {
            "score": fi.score,
            "denominator": fi.denominator,
            "caveat": fi.caveat,
            "denominator_strength": fi.denominator_strength,
            "denominator_strength_caveat": fi.denominator_strength_caveat,
        },
        "action_effect_estimated": False,
        "clinical_or_lifespan_claim": False,
        "disclaimer": "Ranges are engineering or development reference bands, not individualized medical targets. Discuss persistent or concerning results with a qualified professional.",
    }
