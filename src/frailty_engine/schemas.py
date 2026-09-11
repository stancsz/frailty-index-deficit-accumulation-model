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
    artifact_sha256: str | None


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


class CategoryMeasurementResponse(WellnessResponseModel):
    feature: str
    label: str
    current_value: float | int | str | None
    unit: str | None
    status: Literal["in_range", "attention", "below_target", "above_target", "flagged"]
    direction: Literal["within_range", "below", "above", "flagged"]
    target_range: TargetRangeResponse
    target_range_label: str
    source: str
    measurement_source: str
    measured_at: str | None
    protocol: str | None
    reference_source: str | None


class CategoryReferenceInterpretationResponse(WellnessResponseModel):
    status: Literal["within_reference", "attention", "mixed", "not_available"]
    basis: str
    direction: str


class ChronologicalAgeContextResponse(WellnessResponseModel):
    value: float
    unit: Literal["years"]
    source: str
    reference_date: str | None
    precision: str
    status: Literal["supplied_not_recomputed"]


class CategoryAgeReportResponse(WellnessResponseModel):
    status: Literal["withheld_unvalidated", "not_available"]
    label: str
    point_estimate: float | None
    delta_from_chronological_age: float | None
    ci_95: list[float] | None
    interval: list[float] | None
    interval_type: str | None
    model_id: str | None
    reference_panel_id: str | None
    method: str
    uncertainty_validated: bool
    interpretation: str


class CategoryDistributionEvidenceResponse(WellnessResponseModel):
    status: Literal["real_distribution_receipt"]
    receipt: str
    source_file: str
    field: str
    interpretation: str


class CategorySourceDataResponse(WellnessResponseModel):
    status: Literal["real_source_available"]
    directness: str
    observed_source_rows: int
    observed_source_participants: int
    source_files: list[str]
    fields: list[str]
    coverage_receipt: str
    interpretation: str
    distribution_evidence: CategoryDistributionEvidenceResponse


class CategoryReportResponse(WellnessResponseModel):
    system: str
    display_name: str
    category: str
    label: str
    source_data: CategorySourceDataResponse
    chronological_age_context: ChronologicalAgeContextResponse
    status: Literal["complete", "partial", "not_available"]
    reference_status: Literal["within_reference", "attention", "mixed", "not_available"]
    measured_count: int
    expected_count: int
    measurements: list[CategoryMeasurementResponse]
    measurement_profile: list[CategoryMeasurementResponse]
    missing_measurements: list[str]
    reference_interpretation: CategoryReferenceInterpretationResponse
    age_report: CategoryAgeReportResponse
    interpretation: str
    next_step: str
    action_effect_estimated: bool
    clinical_or_lifespan_claim: bool


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
    aggregate_readouts_comparable: bool
    interpretation: str


class ProgressModelBoundaryResponse(WellnessResponseModel):
    previous_model_id: str
    current_model_id: str
    previous_production_ready: bool
    current_production_ready: bool
    previous_model_artifact_sha256: str | None
    current_model_artifact_sha256: str | None
    previous_reference_panel_id: str
    current_reference_panel_id: str
    previous_reference_panel_sha256: str | None
    current_reference_panel_sha256: str | None


class ComparisonEligibilityResponse(WellnessResponseModel):
    status: Literal["eligible", "withheld"]
    basis: Literal["aggregate_readouts", "matched_items_only"]
    blockers: list[str]
    previous_fi_features: list[str]
    current_fi_features: list[str]
    matched_fi_features: list[str]
    added_fi_features: list[str]
    removed_fi_features: list[str]
    changed_units: list[str]
    changed_protocols: list[str]


class AssessmentComparisonResponse(WellnessResponseModel):
    format: Literal["wellness-progress-report-v1"]
    comparison_basis: Literal["same_model_and_reference_panel", "matched_items_only"]
    patient_id: str
    previous_assessed_at: str
    current_assessed_at: str
    readout_changes: list[ProgressReadoutChangeResponse]
    range_changes: list[ProgressRangeChangeResponse]
    summary: ProgressSummaryResponse
    current_focus_areas: list[WellnessFocusAreaResponse]
    model_boundary: ProgressModelBoundaryResponse
    comparison_eligibility: ComparisonEligibilityResponse
    action_effect_estimated: bool
    clinical_or_lifespan_claim: bool
    disclaimer: str


class ComparisonContextResponse(WellnessResponseModel):
    schema_version: str
    feature_contract_version: str
    measurement_protocol_version: str
    measured_features: list[str]
    fi_valid_features: list[str]
    feature_units: dict[str, str]
    feature_protocols: dict[str, str]
    fi_coding_version: str
    fi_cutoff_set_id: str
    model_id: str
    model_artifact_sha256: str | None
    reference_panel_id: str
    reference_panel_sha256: str | None


class AssessmentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    patient_id: str
    data_quality: DataQualityResponse
    metrics: MetricsResponse
    trajectory: TrajectoryResponse
    top_interventions: list[InterventionResponse]
    model_metadata: ModelMetadataResponse
    comparison_context: ComparisonContextResponse
    wellness_report: WellnessReportResponse
    category_reports: list[CategoryReportResponse]
    quality_notes: list[str]
