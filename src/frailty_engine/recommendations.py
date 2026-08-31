"""Conservative, non-diagnostic wellness suggestions derived from measured deficits."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from .fi import FIResult
from .features import PatientData


LABELS = {
    "phase_angle": "Phase Angle",
    "ecw_tbw": "ECW/TBW",
    "ffmi": "FFMI",
    "skeletal_muscle_mass": "Skeletal Muscle Mass",
    "visceral_fat": "Visceral Fat",
    "fasting_glucose": "Fasting Glucose",
    "hba1c": "HbA1c",
    "hs_crp": "hs-CRP",
    "albumin": "Albumin",
    "egfr": "eGFR",
    "grip_strength": "Grip Strength",
    "chair_rise_time": "Chair-Rise Time",
    "sleep_hours": "Sleep Hours",
    "smoking_status": "Smoking Status",
}

RECOMMENDATIONS = {
    "phase_angle": (
        "lifestyle",
        "Discuss progressive resistance training, adequate nutrition, and recovery with a qualified professional.",
    ),
    "ecw_tbw": (
        "review",
        "Review hydration context, recent illness, and measurement conditions with a qualified professional.",
    ),
    "ffmi": (
        "lifestyle",
        "Discuss a safe resistance-training and protein plan appropriate to the person’s goals and context.",
    ),
    "skeletal_muscle_mass": (
        "lifestyle",
        "Prioritize progressive strength work and adequate nutrition, subject to professional guidance.",
    ),
    "visceral_fat": (
        "lifestyle",
        "Use sustainable activity, nutrition, sleep, and waist-trend goals rather than a single reading.",
    ),
    "fasting_glucose": (
        "review",
        "Review the result and repeat or contextualize it with a qualified clinician if elevated.",
    ),
    "hba1c": (
        "review",
        "Review the result and its trend with a qualified clinician; do not infer a diagnosis from this score.",
    ),
    "hs_crp": (
        "review",
        "Consider recent infection, injury, and measurement context before acting on an isolated result.",
    ),
    "albumin": (
        "review",
        "Review nutrition, hydration, liver, kidney, and inflammatory context with a qualified clinician.",
    ),
    "egfr": (
        "review",
        "Interpret kidney markers with a qualified clinician and the person’s longitudinal trend.",
    ),
    "grip_strength": (
        "lifestyle",
        "Track functional strength over time and consider supervised strength and balance work.",
    ),
    "chair_rise_time": (
        "lifestyle",
        "Consider supervised lower-body strength, balance, and mobility work.",
    ),
    "sleep_hours": (
        "lifestyle",
        "Work toward a consistent sleep schedule and review persistent sleep concerns professionally.",
    ),
    "smoking_status": (
        "lifestyle",
        "If currently smoking, offer evidence-based cessation support and a patient-chosen next step.",
    ),
}


_PRESENTATION_DIRECTIONS = frozenset({"within_range", "below", "above", "flagged"})


def _wellness_presentation(
    item: Mapping[str, object] | None,
) -> dict[str, object]:
    """Project report context without re-deriving it from raw measurements."""

    presentation: dict[str, object] = {
        "unit": None,
        "direction": None,
        "target_range_label": None,
        "source": None,
        "z_score": None,
    }
    if item is None:
        return presentation
    unit = item.get("unit")
    if isinstance(unit, str):
        presentation["unit"] = unit
    direction = item.get("direction")
    if direction in _PRESENTATION_DIRECTIONS:
        presentation["direction"] = direction
    target_range = item.get("target_range")
    if isinstance(target_range, Mapping):
        label = target_range.get("label")
        if isinstance(label, str):
            presentation["target_range_label"] = label
    source = item.get("source")
    if isinstance(source, str):
        presentation["source"] = source
    z_score = item.get("z_score")
    if isinstance(z_score, (int, float)) and not isinstance(z_score, bool):
        presentation["z_score"] = round(float(z_score), 4)
    return presentation


def top_interventions(
    patient: PatientData,
    fi: FIResult,
    z_scores: dict[str, float],
    limit: int = 3,
    *,
    wellness_ranges: Iterable[Mapping[str, object]] | None = None,
) -> list[dict[str, object]]:
    """Return ranked actions, including measured wellness focus areas.

    FI-derived interventions retain priority. The wellness report is also
    passed in so measured features such as BMI, blood pressure, or waist
    circumference cannot disappear from this public field merely because
    they do not have a separate FI recommendation entry.
    """

    range_items = list(wellness_ranges) if wellness_ranges is not None else []
    wellness_by_feature: dict[str, Mapping[str, object]] = {}
    for item in range_items:
        name = item.get("feature")
        if isinstance(name, str):
            wellness_by_feature.setdefault(name, item)

    candidates: list[tuple[float, str, dict[str, object]]] = []
    selected: set[str] = set()
    for name, deficit in fi.deficits.items():
        if deficit <= 0 or name not in RECOMMENDATIONS:
            continue
        action_type, recommendation = RECOMMENDATIONS[name]
        wellness_item = wellness_by_feature.get(name)
        if wellness_item is not None:
            wellness_action_type = wellness_item.get("action_type")
            if wellness_action_type in {"lifestyle", "review"}:
                action_type = str(wellness_action_type)
            wellness_recommendation = wellness_item.get("recommendation")
            if (
                isinstance(wellness_recommendation, str)
                and wellness_recommendation.strip()
            ):
                recommendation = wellness_recommendation
            wellness_label = wellness_item.get("biomarker")
            if isinstance(wellness_label, str) and wellness_label.strip():
                label = wellness_label
            else:
                label = LABELS[name]
        else:
            label = LABELS[name]
        presentation = _wellness_presentation(wellness_item)
        if presentation["z_score"] is None and name in z_scores:
            presentation["z_score"] = round(z_scores[name], 4)
        candidates.append(
            (
                2.0 + deficit + abs(z_scores.get(name, 0.0)) * 0.05,
                name,
                {
                    "feature": name,
                    "biomarker": label,
                    "current_value": (
                        wellness_item.get("current_value")
                        if wellness_item is not None
                        and wellness_item.get("current_value") is not None
                        else patient.values[name]
                    ),
                    "z_score": presentation["z_score"],
                    "action_type": action_type,
                    "recommendation": recommendation,
                    **presentation,
                },
            )
        )
        selected.add(name)

    # Add only non-in-range, measured wellness items as a lower-priority
    # fallback. This keeps existing FI rankings stable while making this
    # field agree with the report's focus-area surface.
    status_priority = {
        "below_target": 0.4,
        "above_target": 0.4,
        "flagged": 0.3,
        "attention": 0.2,
    }
    if range_items:
        for index, item in enumerate(range_items):
            name = item.get("feature")
            status = item.get("status")
            recommendation = item.get("recommendation")
            if (
                not isinstance(name, str)
                or name in selected
                or status not in status_priority
                or not isinstance(recommendation, str)
                or not recommendation.strip()
                or name not in patient.values
                or patient.values[name] is None
            ):
                continue
            action_type = item.get("action_type")
            if action_type not in {"lifestyle", "review"}:
                action_type = "review"
            label = item.get("biomarker")
            if not isinstance(label, str) or not label.strip():
                label = name.replace("_", " ").title()
            presentation = _wellness_presentation(item)
            candidates.append(
                (
                    1.0 + status_priority[str(status)] - index * 0.0001,
                    name,
                    {
                        "feature": name,
                        "biomarker": label,
                        "current_value": item.get("current_value")
                        if item.get("current_value") is not None
                        else patient.values[name],
                        "z_score": presentation["z_score"],
                        "action_type": str(action_type),
                        "recommendation": recommendation,
                        **presentation,
                    },
                )
            )
            selected.add(name)

    candidates.sort(key=lambda item: (-item[0], item[1]))
    return [candidate for _, _, candidate in candidates[:limit]]
