"""Held-out cohort evaluation utilities.

This module computes reproducible engineering metrics once an approved cohort
is supplied. It intentionally does not claim clinical validity for the
development surrogate or synthetic reference panel.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping

import numpy as np

from .calibration import ReferencePanel, default_development_panel
from .exceptions import FrailtyEngineError, ModelUnavailableError, ValidationError
from .fi import calculate_fi
from .model import (
    DevelopmentPredictor,
    GompertzMapper,
    ModelAdapterProtocol,
    ModelPrediction,
)
from .pipeline import _model_feature_vector
from .survey_design import SurveyDesign, resolve_survey_design
from .training import MODEL_MEASUREMENT_NAMES
from .features import BIA_FEATURES, parse_patient_data
from .mvv import check_mvv


@dataclass(frozen=True)
class CohortRecord:
    duration: float
    event: bool
    age: float
    sex: str
    ethnicity: str | None
    fi: float
    biological_age: float
    homeostatic_deviation_score: float
    ten_year_probability: float
    log_hazard: float


SubgroupSupportReason = Literal[
    "no_events",
    "no_comparable_pairs",
    "insufficient_valid_replicates",
]

OutcomeMetricName = Literal[
    "brier_score",
    "calibration_in_the_large",
    "calibration_slope",
    "integrated_calibration_index",
    "decision_curve_net_benefit",
]
OutcomeMetricStatus = Literal["not_implemented_pending_sap"]
OutcomeMetricConstruction = Literal["none_withheld"]


@dataclass(frozen=True)
class SubgroupSupportWarning:
    """A metric-support limitation for one observed validation subgroup.

    These reasons describe why the engineering concordance summary is
    incomplete. They intentionally do not encode a clinical sample-size
    threshold or label a subgroup as validated, fair, or safe.
    """

    dimension: str
    label: str
    reasons: tuple[SubgroupSupportReason, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "label": self.label,
            "reasons": list(self.reasons),
        }


def _pending_outcome_metric_status() -> dict[str, dict[str, Any]]:
    """Return a typed absence contract for future outcome-level metrics.

    The validation harness deliberately does not calculate these metrics from
    the synthetic fixture or an unapproved cohort. Returning an explicit
    status is safer for downstream consumers than omitting the fields or
    emitting a misleading zero.
    """

    reasons: dict[OutcomeMetricName, str] = {
        "brier_score": (
            "requires an approved survival analogue and prespecified SAP for "
            "right-censored endpoints"
        ),
        "calibration_in_the_large": (
            "requires an approved endpoint definition and prespecified "
            "censoring-aware estimator"
        ),
        "calibration_slope": (
            "requires an approved endpoint definition and prespecified "
            "recalibration estimator"
        ),
        "integrated_calibration_index": (
            "requires an approved endpoint definition and prespecified "
            "censoring-aware estimator"
        ),
        "decision_curve_net_benefit": (
            "requires a prespecified clinical decision and threshold range"
        ),
    }
    return {
        metric_name: {
            "value": None,
            "status": "not_implemented_pending_sap",
            "construction": "none_withheld",
            "reason": reason,
            "review_gate": "E-005",
        }
        for metric_name, reason in reasons.items()
    }


@dataclass(frozen=True)
class ValidationReport:
    cohort_name: str
    external: bool
    model_id: str
    model_artifact_sha256: str | None
    model_production_ready: bool
    model_uncertainty_validated: bool
    reference_panel_id: str
    reference_panel_sha256: str | None
    reference_panel_production_ready: bool
    reference_panel_fixture_only: bool
    rows_received: int
    rows_evaluated: int
    concordance_index: float | None
    calibration: dict[str, Any]
    subgroup_metrics: dict[str, dict[str, dict[str, Any]]]
    blockers: tuple[str, ...]
    subgroup_support_warnings: tuple[SubgroupSupportWarning, ...] = ()
    row_exclusion_counts: dict[str, int] = field(default_factory=dict)
    concordance_ci_status: Literal[
        "emitted",
        "withheld_no_records",
        "withheld_no_comparable_pairs",
        "withheld_insufficient_valid_replicates",
    ] = "withheld_no_records"
    concordance_ci_construction: Literal["bootstrap_percentile", "none_withheld"] = (
        "none_withheld"
    )
    concordance_comparable_pairs: int = 0
    concordance_ci_95: tuple[float, float] | None = None
    concordance_ci_valid_replicates: int = 0
    concordance_ci_requested_replicates: int = 0
    survey_design: SurveyDesign = field(default_factory=SurveyDesign)
    design_reviewed: bool = False
    weighting_applied: bool = False
    quality_flags: dict[str, bool] = field(
        default_factory=lambda: {
            "design_reviewed": False,
            "survey_design_declared": False,
            "weighting_applied": False,
        }
    )
    outcome_metric_status: dict[str, dict[str, Any]] = field(
        default_factory=_pending_outcome_metric_status
    )

    @property
    def status(self) -> str:
        return "blocked" if self.blockers else "ready_for_clinical_review"

    def to_dict(self) -> dict[str, Any]:
        return {
            "cohort_name": self.cohort_name,
            "external": self.external,
            "model_id": self.model_id,
            "model_artifact_sha256": self.model_artifact_sha256,
            "model_production_ready": self.model_production_ready,
            "model_uncertainty_validated": self.model_uncertainty_validated,
            "reference_panel_id": self.reference_panel_id,
            "reference_panel_sha256": self.reference_panel_sha256,
            "reference_panel_production_ready": self.reference_panel_production_ready,
            "reference_panel_fixture_only": self.reference_panel_fixture_only,
            "status": self.status,
            "rows_received": self.rows_received,
            "rows_evaluated": self.rows_evaluated,
            "rows_excluded": self.rows_received - self.rows_evaluated,
            "row_exclusion_counts": dict(self.row_exclusion_counts),
            "concordance_index": self.concordance_index,
            "concordance_ci_status": self.concordance_ci_status,
            "concordance_ci_construction": self.concordance_ci_construction,
            "concordance_comparable_pairs": self.concordance_comparable_pairs,
            "concordance_ci_95": (
                list(self.concordance_ci_95)
                if self.concordance_ci_95 is not None
                else None
            ),
            "concordance_ci_valid_replicates": self.concordance_ci_valid_replicates,
            "concordance_ci_requested_replicates": self.concordance_ci_requested_replicates,
            "calibration": self.calibration,
            "outcome_metric_status": self.outcome_metric_status,
            "subgroup_metrics": self.subgroup_metrics,
            "subgroup_support_warnings": [
                warning.to_dict() for warning in self.subgroup_support_warnings
            ],
            "survey_design": self.survey_design.to_metadata(
                weighting_applied=self.weighting_applied,
                design_reviewed=self.design_reviewed,
            ),
            "quality_flags": dict(self.quality_flags),
            "blockers": list(self.blockers),
        }


def _concordance(records: list[CohortRecord]) -> float | None:
    concordant, comparable = _concordance_counts(records)
    return round(concordant / comparable, 6) if comparable else None


def _concordance_counts(records: list[CohortRecord]) -> tuple[float, int]:
    concordant = 0.0
    comparable = 0
    for index, left in enumerate(records):
        for right in records[index + 1 :]:
            earlier: CohortRecord | None = None
            later: CohortRecord | None = None
            if left.event and left.duration < right.duration:
                earlier, later = left, right
            elif right.event and right.duration < left.duration:
                earlier, later = right, left
            if earlier is None or later is None:
                continue
            comparable += 1
            if earlier.log_hazard > later.log_hazard:
                concordant += 1
            elif earlier.log_hazard == later.log_hazard:
                concordant += 0.5
    return concordant, comparable


def _bootstrap_concordance(
    records: list[CohortRecord], *, replicates: int, seed: int
) -> dict[str, Any]:
    """Estimate support-aware concordance uncertainty for engineering review.

    Resampling is deterministic and row-level. Replicates with no comparable
    event pair are discarded rather than turned into a misleading value. A
    percentile interval is withheld unless at least half of the requested
    replicates (and at least 20) produce a concordance estimate. This is an
    uncertainty summary for validation review, not a clinical confidence
    interval or a substitute for a prespecified statistical analysis plan.
    """

    comparable_pairs = _concordance_counts(records)[1]
    if not records:
        return {
            "ci_95": None,
            "valid_replicates": 0,
            "requested_replicates": replicates,
            "comparable_pairs": comparable_pairs,
            "ci_95_status": "withheld_no_records",
            "ci_95_construction": "none_withheld",
        }
    if len(records) < 2 or comparable_pairs == 0 or replicates <= 0:
        return {
            "ci_95": None,
            "valid_replicates": 0,
            "requested_replicates": replicates,
            "comparable_pairs": comparable_pairs,
            "ci_95_status": "withheld_no_comparable_pairs",
            "ci_95_construction": "none_withheld",
        }
    generator = np.random.default_rng(seed)
    population = np.asarray(records, dtype=object)
    estimates: list[float] = []
    for _ in range(replicates):
        indices = generator.integers(0, len(records), size=len(records))
        estimate = _concordance(list(population[indices]))
        if estimate is not None:
            estimates.append(estimate)
    minimum_support = max(20, math.ceil(replicates * 0.5))
    interval = None
    if len(estimates) >= minimum_support:
        interval = (
            round(float(np.percentile(estimates, 2.5)), 6),
            round(float(np.percentile(estimates, 97.5)), 6),
        )
    ci_status = (
        "emitted" if interval is not None else "withheld_insufficient_valid_replicates"
    )
    return {
        "ci_95": interval,
        "valid_replicates": len(estimates),
        "requested_replicates": replicates,
        "comparable_pairs": comparable_pairs,
        "ci_95_status": ci_status,
        "ci_95_construction": (
            "bootstrap_percentile" if interval is not None else "none_withheld"
        ),
    }


def _calibration(
    records: list[CohortRecord],
    horizon_years: float,
    bins: int,
    *,
    survey_design: SurveyDesign,
) -> dict[str, Any]:
    survey_metadata = survey_design.to_metadata(weighting_applied=False)
    eligible = [
        record
        for record in records
        if record.duration >= horizon_years
        or record.event
        and record.duration <= horizon_years
    ]

    def km_event_probability(values: list[CohortRecord]) -> float | None:
        """Estimate event probability at the horizon within one bin."""

        if not values:
            return None
        at_risk = len(values)
        survival = 1.0
        for time in sorted(
            {record.duration for record in values if record.duration <= horizon_years}
        ):
            event_count = sum(
                record.event and record.duration == time for record in values
            )
            censor_count = sum(
                not record.event and record.duration == time for record in values
            )
            if event_count:
                survival *= 1.0 - (event_count / at_risk)
            at_risk -= event_count + censor_count
            if at_risk == 0 and time < horizon_years and survival > 0:
                return None
        return round(1.0 - survival, 6)

    def event_rate_fields(values: list[CohortRecord]) -> dict[str, float | None]:
        observed = [
            record.event and record.duration <= horizon_years for record in values
        ]
        return {
            "observed_event_rate": round(float(np.mean(observed)), 6),
            "censoring_adjusted_event_rate": km_event_probability(values),
        }

    probability_bins: list[dict[str, Any]] = []
    if eligible:
        probability_population = sorted(
            eligible, key=lambda record: record.ten_year_probability
        )
        for bin_index, chunk in enumerate(
            np.array_split(
                np.asarray(probability_population, dtype=object),
                min(bins, len(probability_population)),
            ),
            start=1,
        ):
            values = list(chunk)
            if not values:
                continue
            probability_bins.append(
                {
                    "bin": bin_index,
                    "n": len(values),
                    "mean_predicted_probability": round(
                        float(
                            np.mean([record.ten_year_probability for record in values])
                        ),
                        6,
                    ),
                    "survey_design": survey_metadata,
                    **event_rate_fields(values),
                }
            )
    deviation_bins: list[dict[str, Any]] = []
    if eligible:
        eligible_by_deviation = sorted(
            eligible, key=lambda record: record.homeostatic_deviation_score
        )
        for bin_index, chunk in enumerate(
            np.array_split(
                np.asarray(eligible_by_deviation, dtype=object),
                min(bins, len(eligible_by_deviation)),
            ),
            start=1,
        ):
            values = list(chunk)
            if not values:
                continue
            deviation_bins.append(
                {
                    "bin": bin_index,
                    "n": len(values),
                    "mean_predicted_homeostatic_deviation": round(
                        float(
                            np.mean(
                                [
                                    record.homeostatic_deviation_score
                                    for record in values
                                ]
                            )
                        ),
                        6,
                    ),
                    "survey_design": survey_metadata,
                    **event_rate_fields(values),
                }
            )
    age_bins: list[dict[str, Any]] = []
    if records:
        ordered_by_age = sorted(records, key=lambda record: record.age)
        for bin_index, chunk in enumerate(
            np.array_split(
                np.asarray(ordered_by_age, dtype=object),
                min(bins, len(ordered_by_age)),
            ),
            start=1,
        ):
            values = list(chunk)
            if not values:
                continue
            age_bins.append(
                {
                    "bin": bin_index,
                    "n": len(values),
                    "mean_chronological_age": round(
                        float(np.mean([record.age for record in values])), 6
                    ),
                    "mean_biological_age": round(
                        float(np.mean([record.biological_age for record in values])), 6
                    ),
                    "mean_age_delta": round(
                        float(
                            np.mean(
                                [
                                    record.biological_age - record.age
                                    for record in values
                                ]
                            )
                        ),
                        6,
                    ),
                    "survey_design": survey_metadata,
                }
            )
    return {
        "horizon_years": horizon_years,
        "eligible_rows": len(eligible),
        "calibration_rows": len(eligible),
        "censored_before_horizon_rows": sum(
            not record.event and record.duration < horizon_years for record in records
        ),
        "method": ("kaplan_meier_horizon_event_probability" if eligible else "blocked"),
        "probability_bins": probability_bins,
        "homeostatic_deviation_bins": deviation_bins,
        "biological_age_bins": age_bins,
        "survey_design": survey_metadata,
    }


def _group_metrics(
    records: list[CohortRecord],
    *,
    bootstrap_replicates: int,
    bootstrap_seed: int,
    survey_design: SurveyDesign,
) -> dict[str, Any]:
    survey_metadata = survey_design.to_metadata(weighting_applied=False)
    bootstrap = _bootstrap_concordance(
        records, replicates=bootstrap_replicates, seed=bootstrap_seed
    )
    bootstrap_interval = (
        list(bootstrap["ci_95"]) if bootstrap["ci_95"] is not None else None
    )
    if not records:
        return {
            "n": 0,
            "event_count": 0,
            "censored_count": 0,
            "event_fraction": None,
            "concordance_index": None,
            "concordance_ci_95": bootstrap_interval,
            "concordance_ci_status": bootstrap["ci_95_status"],
            "concordance_ci_construction": bootstrap["ci_95_construction"],
            "concordance_ci_valid_replicates": bootstrap["valid_replicates"],
            "concordance_ci_requested_replicates": bootstrap["requested_replicates"],
            "concordance_comparable_pairs": bootstrap["comparable_pairs"],
            "outcome_metric_status": _pending_outcome_metric_status(),
            "survey_design": survey_metadata,
        }
    _, comparable_pairs = _concordance_counts(records)
    event_count = sum(record.event for record in records)
    return {
        "n": len(records),
        "event_count": event_count,
        "censored_count": len(records) - event_count,
        "event_fraction": round(event_count / len(records), 6),
        "concordance_index": _concordance(records),
        "concordance_ci_95": bootstrap_interval,
        "concordance_ci_status": bootstrap["ci_95_status"],
        "concordance_ci_construction": bootstrap["ci_95_construction"],
        "concordance_ci_valid_replicates": bootstrap["valid_replicates"],
        "concordance_ci_requested_replicates": bootstrap["requested_replicates"],
        "concordance_comparable_pairs": comparable_pairs,
        "outcome_metric_status": _pending_outcome_metric_status(),
        "survey_design": survey_metadata,
        "mean_follow_up_years": round(
            float(np.mean([record.duration for record in records])), 6
        ),
        "mean_fi": round(float(np.mean([record.fi for record in records])), 6),
        "mean_chronological_age": round(
            float(np.mean([record.age for record in records])), 6
        ),
        "mean_biological_age": round(
            float(np.mean([record.biological_age for record in records])), 6
        ),
    }


def _subgroup_support_warning(
    dimension: str, label: str, metrics: Mapping[str, Any]
) -> SubgroupSupportWarning | None:
    """Summarize concrete support failures without inventing sample limits."""

    reasons: list[SubgroupSupportReason] = []
    if metrics.get("event_count") == 0:
        reasons.append("no_events")
    if metrics.get("concordance_comparable_pairs") == 0:
        reasons.append("no_comparable_pairs")
    if metrics.get("concordance_ci_status") == "withheld_insufficient_valid_replicates":
        reasons.append("insufficient_valid_replicates")
    if not reasons:
        return None
    return SubgroupSupportWarning(
        dimension=dimension,
        label=label,
        reasons=tuple(reasons),
    )


def _age_band(age: float) -> str:
    if age < 40:
        return "18-39"
    if age < 60:
        return "40-59"
    if age < 80:
        return "60-79"
    return "80+"


def _clean_ethnicity(value: Any) -> str | None:
    if value is None or not str(value).strip():
        return None
    return str(value).strip()


def _ethnicity_fields(row: Mapping[str, Any]) -> tuple[str | None, str | None]:
    """Return canonical and legacy ethnicity aliases after whitespace cleanup."""

    return _clean_ethnicity(row.get("ethnicity")), _clean_ethnicity(
        row.get("race_ethnicity")
    )


def _ethnicity_value(row: Mapping[str, Any]) -> str | None:
    ethnicity, race_ethnicity = _ethnicity_fields(row)
    return ethnicity or race_ethnicity


def _ethnicity_conflicts(row: Mapping[str, Any]) -> bool:
    ethnicity, race_ethnicity = _ethnicity_fields(row)
    return (
        ethnicity is not None
        and race_ethnicity is not None
        and ethnicity != race_ethnicity
    )


def _prediction(
    predictor: Any,
    patient: Any,
    vector: list[float],
) -> ModelPrediction:
    age = float(patient.values["age"])
    if not isinstance(predictor, ModelAdapterProtocol):
        raise TypeError(
            "predictor must implement predict_for_assessment(age, encoded_vector)"
        )
    return predictor.predict_for_assessment(age, vector)


def validate_external_cohort(
    rows: Iterable[Mapping[str, Any]],
    *,
    cohort_name: str,
    predictor: Any | None = None,
    reference_panel: ReferencePanel | None = None,
    survey_design: SurveyDesign | None = None,
    horizon_years: float = 10.0,
    bins: int = 5,
    bootstrap_replicates: int = 200,
    bootstrap_seed: int = 42,
) -> ValidationReport:
    """Evaluate an external held-out cohort without changing the worktree.

    ``bootstrap_replicates`` and ``bootstrap_seed`` control the deterministic
    engineering uncertainty summary for concordance. The result is intentionally
    support-aware and must be replaced or extended by the approved statistical
    analysis plan before clinical reporting.
    """

    if horizon_years <= 0 or bins < 2:
        raise ValueError("horizon_years must be positive and bins must be at least 2")
    if (
        isinstance(bootstrap_replicates, bool)
        or not isinstance(bootstrap_replicates, int)
        or bootstrap_replicates < 20
    ):
        raise ValueError("bootstrap_replicates must be an integer of at least 20")
    if (
        isinstance(bootstrap_seed, bool)
        or not isinstance(bootstrap_seed, int)
        or bootstrap_seed < 0
    ):
        raise ValueError("bootstrap_seed must be a non-negative integer")
    input_rows = list(rows)
    has_sample_weight = any(
        row.get("sample_weight", row.get("weight")) is not None for row in input_rows
    )
    design_declared = survey_design is not None
    resolved_survey_design = resolve_survey_design(
        survey_design, has_sample_weight=has_sample_weight
    )
    model = predictor or DevelopmentPredictor()
    panel = reference_panel or default_development_panel()
    blockers: list[str] = []
    row_exclusion_counts: dict[str, int] = {}
    if not getattr(model, "production_ready", False):
        blockers.append("predictor is not marked production_ready")
    if not panel.production_ready:
        blockers.append("reference panel is not marked production_ready")
    ethnicity_present = any(_ethnicity_value(row) for row in input_rows)
    if not ethnicity_present:
        blockers.append(
            "external cohort has no ethnicity field for required stratification"
        )
    elif any(_ethnicity_value(row) is None for row in input_rows):
        blockers.append("some external cohort rows are missing ethnicity")

    records: list[CohortRecord] = []
    for row_number, row in enumerate(input_rows, start=1):
        try:
            if _ethnicity_conflicts(row):
                raise ValidationError(
                    "ethnicity and race_ethnicity disagree; provide one consistent value"
                )
            duration = float(row["duration"])
            event_value = row["event"]
            if isinstance(event_value, bool):
                event = event_value
            elif isinstance(event_value, (int, float)) and event_value in (0, 1):
                event = bool(event_value)
            else:
                raise ValidationError("event must be boolean or 0/1")
            if not math.isfinite(duration) or duration <= 0:
                raise ValidationError("duration must be positive and finite")
            patient_id = str(row.get("patient_id", f"external-row-{row_number}"))
            patient = parse_patient_data(
                {
                    "patient_id": patient_id,
                    "measurements": {
                        name: row.get(name) for name in MODEL_MEASUREMENT_NAMES
                    },
                }
            )
            check_mvv(patient)
            # Pre-check panel age coverage before z-score inference so that
            # out-of-coverage rows are aggregated under a privacy-safe
            # reason rather than coerced or surfaced with row identifiers.
            measured_bia_features = tuple(
                feature
                for feature in BIA_FEATURES
                if patient.values[feature] is not None
            )
            band_count, _band_span = panel.coverage_for(
                str(patient.values["sex"]),
                float(patient.values["age"]),
                features=measured_bia_features,
            )
            if band_count == 0:
                raise ValidationError("age outside reference-panel band coverage")
            z_scores = panel.z_scores(patient)
            fi = calculate_fi(patient, z_scores)
            vector = _model_feature_vector(patient, z_scores, fi.score)
            prediction = _prediction(model, patient, vector)
            mapper = getattr(model, "mapper", GompertzMapper())
            ethnicity_value = _ethnicity_value(row)
            ten_year_probability = mapper.probability_10y(
                float(patient.values["age"]), prediction.log_hazard
            )
            records.append(
                CohortRecord(
                    duration=duration,
                    event=event,
                    age=float(patient.values["age"]),
                    sex=str(patient.values["sex"]),
                    ethnicity=ethnicity_value,
                    fi=fi.score,
                    biological_age=prediction.point_estimate,
                    homeostatic_deviation_score=(
                        prediction.point_estimate - float(patient.values["age"])
                    )
                    / max(float(patient.values["age"]), 1.0),
                    ten_year_probability=ten_year_probability,
                    log_hazard=prediction.log_hazard,
                )
            )
        except (KeyError, TypeError, ValueError, FrailtyEngineError) as error:
            reason = str(error).strip() or error.__class__.__name__
            row_exclusion_counts[reason] = row_exclusion_counts.get(reason, 0) + 1

    for reason, count in row_exclusion_counts.items():
        blockers.append(f"{count} row(s) excluded: {reason}")

    concordance_bootstrap = _bootstrap_concordance(
        records, replicates=bootstrap_replicates, seed=bootstrap_seed
    )
    subgroup_metrics: dict[str, dict[str, dict[str, Any]]] = {
        "sex": {},
        "age_band": {},
        "ethnicity": {},
    }
    for dimension_index, (group_name, group_values) in enumerate(
        (
            ("sex", {record.sex for record in records}),
            ("age_band", {_age_band(record.age) for record in records}),
            (
                "ethnicity",
                {record.ethnicity for record in records if record.ethnicity},
            ),
        )
    ):
        for value_index, value in enumerate(sorted(group_values)):
            subgroup_metrics[group_name][value] = _group_metrics(
                [
                    record
                    for record in records
                    if (
                        record.sex
                        if group_name == "sex"
                        else _age_band(record.age)
                        if group_name == "age_band"
                        else record.ethnicity
                    )
                    == value
                ],
                bootstrap_replicates=bootstrap_replicates,
                bootstrap_seed=bootstrap_seed
                + 1
                + dimension_index * 1000
                + value_index,
                survey_design=resolved_survey_design,
            )
    subgroup_support_warnings = tuple(
        warning
        for group_name in ("sex", "age_band", "ethnicity")
        for label, metrics in sorted(subgroup_metrics[group_name].items())
        if (warning := _subgroup_support_warning(group_name, label, metrics))
        is not None
    )
    concordance_index = _concordance(records)
    calibration = _calibration(
        records,
        horizon_years,
        bins,
        survey_design=resolved_survey_design,
    )
    outcome_metric_status = _pending_outcome_metric_status()
    if concordance_index is None:
        blockers.append("external cohort has no comparable event pairs for concordance")
    if calibration["eligible_rows"] == 0:
        blockers.append(
            "external cohort has no rows observable at the calibration horizon"
        )
    elif any(
        item["censoring_adjusted_event_rate"] is None
        for item in (
            calibration["probability_bins"] + calibration["homeostatic_deviation_bins"]
        )
    ):
        blockers.append(
            "one or more calibration bins lack follow-up to estimate the horizon risk"
        )
    return ValidationReport(
        cohort_name=cohort_name,
        external=True,
        model_id=str(getattr(model, "model_id", "unknown")),
        model_artifact_sha256=getattr(model, "artifact_sha256", None),
        model_production_ready=bool(getattr(model, "production_ready", False)),
        model_uncertainty_validated=bool(
            getattr(model, "uncertainty_validated", False)
        ),
        reference_panel_id=panel.panel_id,
        reference_panel_sha256=panel.source_sha256,
        reference_panel_production_ready=panel.production_ready,
        reference_panel_fixture_only=bool(getattr(panel, "fixture_only", False)),
        rows_received=len(input_rows),
        rows_evaluated=len(records),
        concordance_index=concordance_index,
        concordance_comparable_pairs=concordance_bootstrap["comparable_pairs"],
        concordance_ci_95=concordance_bootstrap["ci_95"],
        concordance_ci_status=concordance_bootstrap["ci_95_status"],
        concordance_ci_construction=concordance_bootstrap["ci_95_construction"],
        concordance_ci_valid_replicates=concordance_bootstrap["valid_replicates"],
        concordance_ci_requested_replicates=concordance_bootstrap[
            "requested_replicates"
        ],
        calibration=calibration,
        outcome_metric_status=outcome_metric_status,
        subgroup_metrics=subgroup_metrics,
        subgroup_support_warnings=subgroup_support_warnings,
        row_exclusion_counts=row_exclusion_counts,
        blockers=tuple(dict.fromkeys(blockers)),
        survey_design=resolved_survey_design,
        design_reviewed=False,
        weighting_applied=False,
        quality_flags={
            "design_reviewed": False,
            "survey_design_declared": design_declared,
            "weighting_applied": False,
        },
    )


def write_calibration_plots(
    report: ValidationReport, output_dir: str | Path
) -> dict[str, Path]:
    """Write the two required calibration plots from a validation report."""

    try:
        import matplotlib.pyplot as plt
    except ImportError as error:
        raise ModelUnavailableError(
            "matplotlib is required to render calibration plots"
        ) from error
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    deviation_bins = report.calibration["homeostatic_deviation_bins"]
    age_bins = report.calibration["biological_age_bins"]
    if not deviation_bins or not age_bins:
        raise ValueError(
            "calibration plots require non-empty deviation and biological-age bins"
        )

    def calibration_rate(item: Mapping[str, Any]) -> float:
        rate = item.get("censoring_adjusted_event_rate")
        if rate is None:
            raise ValueError(
                "calibration plot requires an estimable censoring-adjusted event rate"
            )
        return float(rate)

    figure, axis = plt.subplots(figsize=(5, 5))
    axis.plot(
        [item["mean_predicted_homeostatic_deviation"] for item in deviation_bins],
        [calibration_rate(item) for item in deviation_bins],
        marker="o",
    )
    axis.set(
        xlabel="Mean predicted homeostatic deviation",
        ylabel="Kaplan-Meier event probability at horizon",
        title="Homeostatic-deviation calibration",
    )
    figure.tight_layout()
    deviation_path = destination / "homeostatic_deviation_calibration.png"
    figure.savefig(deviation_path, dpi=150)
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(5, 5))
    chronological = [item["mean_chronological_age"] for item in age_bins]
    biological = [item["mean_biological_age"] for item in age_bins]
    axis.plot(chronological, biological, marker="o")
    identity_extent = [
        max(0.0, min(chronological + biological)),
        min(110.0, max(chronological + biological)),
    ]
    if identity_extent[0] == identity_extent[1]:
        identity_extent = [
            max(0.0, identity_extent[0] - 1.0),
            min(110.0, identity_extent[1] + 1.0),
        ]
    axis.plot(identity_extent, identity_extent, linestyle="--", color="grey")
    axis.set(
        xlabel="Mean chronological age",
        ylabel="Mean biological age",
        title="Biological-age calibration",
    )
    figure.tight_layout()
    age_path = destination / "biological_age_calibration.png"
    figure.savefig(age_path, dpi=150)
    plt.close(figure)
    return {"homeostatic_deviation": deviation_path, "biological_age": age_path}
