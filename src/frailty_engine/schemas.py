"""Machine-readable public API response schemas."""

from __future__ import annotations

from typing import Any
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


AssessmentUncertaintyConstruction = Literal["wald_1_96_se", "none_withheld"]
ConcordanceUncertaintyConstruction = Literal["bootstrap_percentile", "none_withheld"]


class AssessmentRequest(BaseModel):
    """Transport-level request envelope; domain ranges remain parser-owned."""

    model_config = ConfigDict(extra="forbid", strict=True)

    patient_id: str = Field(min_length=1)
    measurements: dict[str, Any] = Field(
        description="Canonical feature measurements; missing values are not imputed."
    )


class AssessmentSnapshotRequest(BaseModel):
    """One dated assessment used by the stateless progress-comparison route."""

    model_config = ConfigDict(extra="forbid", strict=True)

    patient_id: str = Field(min_length=1)
    assessed_at: str = Field(
        min_length=10,
        max_length=10,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="ISO calendar date for the completed assessment.",
    )
    measurements: dict[str, Any] = Field(
        description="Canonical feature measurements; missing values are not imputed."
    )


class AssessmentComparisonRequest(BaseModel):
    """Two same-person snapshots; no snapshots are persisted by the API."""

    model_config = ConfigDict(extra="forbid", strict=True)

    previous: AssessmentSnapshotRequest
    current: AssessmentSnapshotRequest


class BiologicalAgeResponse(BaseModel):
    point_estimate: float
    ci_95: list[float] | None
    uncertainty_method: str
    uncertainty_construction: AssessmentUncertaintyConstruction
    uncertainty_validated: bool
    interpretation: str


class FIDetailsResponse(BaseModel):
    numerator: float
    denominator: int
    valid_variables: list[str]
    denominator_strength: Literal["low", "moderate", "high"]
    denominator_strength_caveat: str


class DataQualityResponse(BaseModel):
    variables_measured: int
    fi_variables_measured: int
    mvv_passed: bool
    blood_variables_measured: int
    history_variables_measured: int
    reference_panel_id: str
    reference_panel_sha256: str | None
    reference_panel_production_ready: bool
    reference_panel_fixture_only: bool
    reference_panel_readiness: Literal[
        "development_fixture_only", "loaded_unapproved", "loaded_production_ready"
    ]
    fi_denominator_strength: Literal["low", "moderate", "high"]
    reference_panel_band_count: int
    reference_panel_band_span_years_for_age: float


class MetricsResponse(BaseModel):
    chronological_age: float
    biological_age: BiologicalAgeResponse
    current_deficit_load_fi: float
    current_deficit_load_fi_details: FIDetailsResponse


class TrajectoryResponse(BaseModel):
    homeostatic_deviation_score: float
    score_ci_95: list[float] | None
    uncertainty_construction: AssessmentUncertaintyConstruction


class InterventionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    feature: str
    biomarker: str
    current_value: float | int | str | None
    unit: str | None = None
    z_score: float | None
    direction: Literal["within_range", "below", "above", "flagged"] | None = None
    target_range_label: str | None = None
    source: str | None = None
    action_type: str
    recommendation: str


class ModelMetadataResponse(BaseModel):
    model_id: str
    production_ready: bool


class WellnessResponseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class WellnessSummaryResponse(WellnessResponseModel):
    status: Literal["on_track", "focus_areas"]
    measured_features: int
    missing_features: int
    focus_areas: int
    interpretation: str


class TargetRangeResponse(WellnessResponseModel):
    low: float | None = None
    high: float | None = None
    label: str
    kind: str | None = None


class WellnessRangeResponse(WellnessResponseModel):
    feature: str
    biomarker: str
    current_value: float | int | str | None
    unit: str | None
    target_range: TargetRangeResponse
    status: Literal["in_range", "attention", "below_target", "above_target", "flagged"]
    direction: Literal["within_range", "below", "above", "flagged"]
    priority: Literal["maintain", "review", "priority"]
    action_type: Literal["lifestyle", "review"]
    z_score: float | None
    source: str
    recommendation: str


class WellnessFocusAreaResponse(WellnessResponseModel):
    feature: str
    focus: str
    current_value: float | int | str | None
    unit: str | None
    target_range: TargetRangeResponse
    target_range_label: str
    direction: Literal["within_range", "below", "above", "flagged"]
    action_type: Literal["lifestyle", "review"]
    z_score: float | None
    source: str
    recommendation: str


class FIContextResponse(WellnessResponseModel):
    score: float
    denominator: int
    caveat: str
    denominator_strength: Literal["low", "moderate", "high"]
    denominator_strength_caveat: str


class WellnessReportResponse(WellnessResponseModel):
    summary: WellnessSummaryResponse
    ranges: list[WellnessRangeResponse]
    focus_areas: list[WellnessFocusAreaResponse]
    missing_features: list[str]
    fi_context: FIContextResponse
    action_effect_estimated: bool
    clinical_or_lifespan_claim: bool
    disclaimer: str


class ProgressReadoutChangeResponse(WellnessResponseModel):
    metric: str
    previous: float
    current: float
    delta: float
    movement: Literal["lower", "higher", "unchanged"]


class ProgressRangeChangeResponse(WellnessResponseModel):
    feature: str
    biomarker: str
    previous_value: float | int | str | None
    current_value: float | int | str | None
    value_delta: float | None
    value_change: Literal[
        "lower",
        "higher",
        "unchanged",
        "changed",
        "new_measurement",
        "missing_now",
        "not_comparable",
    ]
    previous_status: str | None
    current_status: str | None
    status_transition: Literal[
        "unchanged",
        "moved_into_range",
        "moved_out_of_range",
        "status_changed",
        "new_measurement",
        "missing_now",
    ]
    target_range: TargetRangeResponse
    unit: str | None
    recommendation: str


class ProgressSummaryResponse(WellnessResponseModel):
    changed_features: int
    moved_into_reference_range: int
    moved_out_of_reference_range: int
    new_focus_areas: list[str]
    resolved_focus_areas: list[str]
    current_focus_areas: int
    previous_missing_features: int
    current_missing_features: int
    interpretation: str


class ProgressModelBoundaryResponse(WellnessResponseModel):
    previous_model_id: str
    current_model_id: str
    previous_production_ready: bool
    current_production_ready: bool
    previous_reference_panel_id: str
    current_reference_panel_id: str
    previous_reference_panel_sha256: str | None
    current_reference_panel_sha256: str | None


class AssessmentComparisonResponse(WellnessResponseModel):
    format: Literal["wellness-progress-report-v1"]
    comparison_basis: Literal["same_model_and_reference_panel"]
    patient_id: str
    previous_assessed_at: str
    current_assessed_at: str
    readout_changes: list[ProgressReadoutChangeResponse]
    range_changes: list[ProgressRangeChangeResponse]
    summary: ProgressSummaryResponse
    current_focus_areas: list[WellnessFocusAreaResponse]
    model_boundary: ProgressModelBoundaryResponse
    action_effect_estimated: bool
    clinical_or_lifespan_claim: bool
    disclaimer: str


class AssessmentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    patient_id: str
    data_quality: DataQualityResponse
    metrics: MetricsResponse
    trajectory: TrajectoryResponse
    top_interventions: list[InterventionResponse]
    model_metadata: ModelMetadataResponse
    wellness_report: WellnessReportResponse
    quality_notes: list[str]
