"""Preparation of approved survival training rows without fabricating inputs."""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any, Iterable, Mapping

import numpy as np

from .calibration import ReferencePanel
from .exceptions import ValidationError
from .model import GompertzMapper, XGBSurvivalModel
from .pipeline import MODEL_VECTOR_FEATURE_NAMES, model_vector
from .survey_design import SurveyDesign, resolve_survey_design


@dataclass(frozen=True)
class TrainingSubgroupQuality:
    """Descriptive completeness and censoring evidence for one subgroup."""

    row_count: int
    observed_event_count: int
    censored_row_count: int
    missing_counts: Mapping[str, int]
    missing_rates: Mapping[str, float]

    def to_mapping(self) -> dict[str, Any]:
        return {
            "row_count": self.row_count,
            "observed_event_count": self.observed_event_count,
            "censored_row_count": self.censored_row_count,
            "missing_counts": dict(self.missing_counts),
            "missing_rates": dict(self.missing_rates),
        }


@dataclass(frozen=True)
class TrainingQualityReport:
    """Cohort-level training completeness and censoring evidence.

    Counts are measured on the exact model matrix after canonical encoding.
    This report is descriptive: it does not approve a cohort, replace a
    subgroup analysis, or imply that native missing-value handling is unbiased.
    """

    row_count: int
    observed_event_count: int
    censored_row_count: int
    missing_counts: Mapping[str, int]
    missing_rates: Mapping[str, float]
    subgroups: Mapping[str, Mapping[str, TrainingSubgroupQuality]] = field(
        default_factory=dict
    )
    anchor_features: tuple[str, ...] = ("age", "sex_male", "bmi")
    scope: str = "cohort"
    sample_weight_mode: str = "not_provided"
    survey_design_summary: Mapping[str, Any] = field(
        default_factory=lambda: SurveyDesign().to_metadata(weighting_applied=False)
    )

    def to_mapping(self) -> dict[str, Any]:
        """Return a JSON-safe copy suitable for logs or artifact metadata."""

        return {
            "row_count": self.row_count,
            "observed_event_count": self.observed_event_count,
            "censored_row_count": self.censored_row_count,
            "missing_counts": dict(self.missing_counts),
            "missing_rates": dict(self.missing_rates),
            "subgroups": {
                dimension: {
                    label: report.to_mapping() for label, report in groups.items()
                }
                for dimension, groups in self.subgroups.items()
            },
            "anchor_features": list(self.anchor_features),
            "scope": self.scope,
            "sample_weight_mode": self.sample_weight_mode,
            "survey_design": dict(self.survey_design_summary),
        }


@dataclass(frozen=True)
class SurvivalTrainingFrame:
    """Numeric arrays and quality evidence ready for `survival:cox`."""

    feature_names: tuple[str, ...]
    x: np.ndarray
    durations: np.ndarray
    events: np.ndarray
    patient_ids: tuple[str, ...]
    weights: np.ndarray | None = None
    quality: TrainingQualityReport | None = None
    survey_design: SurveyDesign = field(default_factory=SurveyDesign)


@dataclass(frozen=True)
class SurvivalRowSplit:
    """Deterministic patient-level fit/holdout partition for review workflows."""

    train_rows: tuple[Mapping[str, Any], ...]
    holdout_rows: tuple[Mapping[str, Any], ...]
    seed: int
    holdout_fraction: float
    strategy: str = "patient_id_sha256_event_stratified"
    strata: tuple[str, ...] = ()

    @staticmethod
    def _summary(rows: tuple[Mapping[str, Any], ...]) -> dict[str, int]:
        event_count = sum(bool(value) for value in (row.get("event") for row in rows))
        return {
            "row_count": len(rows),
            "event_count": event_count,
            "censored_count": len(rows) - event_count,
        }

    def to_mapping(self) -> dict[str, Any]:
        """Return split provenance and outcome counts without patient identifiers."""

        return {
            "strategy": self.strategy,
            "strata": list(self.strata),
            "seed": self.seed,
            "holdout_fraction": self.holdout_fraction,
            "train": self._summary(self.train_rows),
            "holdout": self._summary(self.holdout_rows),
            "patient_overlap": 0,
        }


def _event_value(value: Any, row_number: int) -> bool:
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if (
        isinstance(value, (int, float, np.integer, np.floating))
        and np.isfinite(value)
        and value in (0, 1)
    ):
        return bool(value)
    raise ValidationError(
        "event must be boolean or 0/1",
        field_errors={f"row[{row_number}].event": "expected binary value"},
    )


def _age_band(age: float) -> str:
    if age < 40:
        return "18-39"
    if age < 60:
        return "40-59"
    if age < 80:
        return "60-79"
    return "80+"


def _subgroup_labels(patient: Any, row: Mapping[str, Any]) -> dict[str, str]:
    raw_ethnicity = row.get("ethnicity") or row.get("race_ethnicity")
    ethnicity = (
        "unknown"
        if raw_ethnicity is None or not str(raw_ethnicity).strip()
        else str(raw_ethnicity).strip()
    )
    return {
        "sex": str(patient.values["sex"]),
        "age_band": _age_band(float(patient.values["age"])),
        "ethnicity": ethnicity,
    }


def split_survival_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    holdout_fraction: float = 0.2,
    seed: int = 42,
    strata: Iterable[str] | str | None = None,
) -> SurvivalRowSplit:
    """Create a reproducible patient-level holdout without outcome leakage.

    Patient identifiers are hashed to assign rows, and event/censor strata are
    split independently so a sufficiently large cohort keeps both outcome
    types represented in each partition. This helper only creates a review
    boundary. Optional ``strata`` values add ``sex`` and/or ``age_band`` to
    that assignment boundary. It does not select hyperparameters, establish
    external validity, or replace a prespecified analysis protocol.
    """

    if not 0.0 < holdout_fraction < 1.0:
        raise ValueError("holdout_fraction must be between 0 and 1")
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError("seed must be a non-negative integer")
    if strata is None:
        requested_strata: tuple[str, ...] = ()
    elif isinstance(strata, str):
        requested_strata = (strata,)
    else:
        try:
            requested_strata = tuple(strata)
        except TypeError as error:
            raise ValueError("strata must be an iterable of supported names") from error
    supported_strata = {"sex", "age_band"}
    if any(
        not isinstance(name, str) or name not in supported_strata
        for name in requested_strata
    ):
        raise ValueError("strata may contain only 'sex' and 'age_band'")
    if len(set(requested_strata)) != len(requested_strata):
        raise ValueError("strata values must be unique")
    source_rows = list(rows)
    if len(source_rows) < 2:
        raise ValueError("at least two rows are required for a holdout split")
    indexed: list[tuple[int, str, bool, tuple[str, ...], Mapping[str, Any]]] = []
    seen: set[str] = set()
    for row_number, row in enumerate(source_rows, start=1):
        if not isinstance(row, Mapping):
            raise ValidationError(f"training row {row_number} must be an object")
        patient_id = row.get("patient_id", f"row-{row_number}")
        if not isinstance(patient_id, str) or not patient_id.strip():
            raise ValidationError(
                "patient_id must be a non-empty string",
                field_errors={f"row[{row_number}].patient_id": "expected string"},
            )
        normalized_id = patient_id.strip()
        if normalized_id in seen:
            raise ValidationError(
                "patient_id must be unique for a patient-level split",
                field_errors={f"row[{row_number}].patient_id": "duplicate patient"},
            )
        seen.add(normalized_id)
        stratum_values: list[str] = []
        for name in requested_strata:
            if name == "sex":
                raw_sex = row.get("sex")
                stratum_values.append(
                    "unknown"
                    if raw_sex is None or not str(raw_sex).strip()
                    else str(raw_sex).strip().lower()
                )
            else:
                try:
                    age = float(row["age"])
                except (KeyError, TypeError, ValueError) as error:
                    raise ValidationError(
                        "age is required for age_band stratification",
                        field_errors={f"row[{row_number}].age": "expected numeric age"},
                    ) from error
                if not np.isfinite(age):
                    raise ValidationError(
                        "age is required for age_band stratification",
                        field_errors={f"row[{row_number}].age": "expected finite age"},
                    )
                stratum_values.append(_age_band(age))
        event = _event_value(row.get("event"), row_number)
        indexed.append((row_number, normalized_id, event, tuple(stratum_values), row))

    holdout_ids: set[str] = set()
    groups: dict[
        tuple[Any, ...],
        list[tuple[int, str, bool, tuple[str, ...], Mapping[str, Any]]],
    ] = {}
    for item in indexed:
        group_key = (item[2], *item[3])
        groups.setdefault(group_key, []).append(item)
    for group_key in sorted(groups, key=lambda key: tuple(str(value) for value in key)):
        group = groups[group_key]
        ordered = sorted(
            group,
            key=lambda item: sha256(f"{seed}:{item[1]}".encode("utf-8")).hexdigest(),
        )
        if len(ordered) > 1:
            target = max(1, int(len(ordered) * holdout_fraction + 0.5))
            target = min(target, len(ordered) - 1)
            holdout_ids.update(item[1] for item in ordered[:target])
    if not holdout_ids:
        candidate = min(
            indexed,
            key=lambda item: sha256(f"{seed}:{item[1]}".encode("utf-8")).hexdigest(),
        )
        holdout_ids.add(candidate[1])
    if len(holdout_ids) == len(indexed):
        holdout_ids.remove(next(iter(sorted(holdout_ids))))

    train_rows = tuple(
        dict(row)
        for _, patient_id, _, _, row in indexed
        if patient_id not in holdout_ids
    )
    holdout_rows = tuple(
        dict(row) for _, patient_id, _, _, row in indexed if patient_id in holdout_ids
    )
    strategy = "patient_id_sha256_event_stratified"
    if requested_strata:
        strategy = (
            "patient_id_sha256_event_" + "_".join(requested_strata) + "_stratified"
        )
    return SurvivalRowSplit(
        train_rows=train_rows,
        holdout_rows=holdout_rows,
        seed=seed,
        holdout_fraction=round(float(holdout_fraction), 6),
        strategy=strategy,
        strata=requested_strata,
    )


def build_survival_frame(
    rows: Iterable[Mapping[str, Any]],
    *,
    reference_panel: ReferencePanel | None = None,
    survey_design: SurveyDesign | None = None,
) -> SurvivalTrainingFrame:
    """Convert flat NHANES-like rows into a validated model matrix.

    Each row must contain `patient_id`, `duration`, `event`, and the canonical
    measurement names. Censored observations are retained; no outcome or
    feature imputation is performed here. If survey/sample weights are
    supplied, every row must carry a positive finite value and the adapter
    passes those weights to XGBoost as DMatrix case weights. A typed survey
    declaration is retained in the frame and quality report; this is not a
    complete complex-survey variance or replicate-weight implementation.
    """

    matrix: list[list[float]] = []
    durations: list[float] = []
    events: list[bool] = []
    patient_ids: list[str] = []
    raw_weights: list[float | None] = []
    missing_counts = {name: 0 for name in MODEL_VECTOR_FEATURE_NAMES}
    subgroup_state: dict[tuple[str, str], dict[str, Any]] = {}
    for row_number, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            raise ValidationError(f"training row {row_number} must be an object")
        if "duration" not in row or "event" not in row:
            raise ValidationError(
                "training row requires duration and event",
                field_errors={f"row[{row_number}]": "missing survival target"},
            )
        try:
            duration = float(row["duration"])
        except (TypeError, ValueError) as error:
            raise ValidationError(
                "duration must be numeric",
                field_errors={f"row[{row_number}].duration": "expected number"},
            ) from error
        if not np.isfinite(duration) or duration <= 0:
            raise ValidationError(
                "duration must be a positive finite number",
                field_errors={f"row[{row_number}].duration": "expected > 0"},
            )
        event = _event_value(row["event"], row_number)
        patient_id = row.get("patient_id", f"row-{row_number}")
        if not isinstance(patient_id, str) or not patient_id.strip():
            raise ValidationError(
                "patient_id must be a non-empty string",
                field_errors={f"row[{row_number}].patient_id": "expected string"},
            )
        measurements = {name: row.get(name) for name in MODEL_MEASUREMENT_NAMES}
        patient, vector = model_vector(
            {"patient_id": patient_id, "measurements": measurements},
            reference_panel=reference_panel,
            enforce_mvv=False,
        )
        for feature_name, value in zip(MODEL_VECTOR_FEATURE_NAMES, vector):
            if np.isnan(value):
                missing_counts[feature_name] += 1
        for dimension, label in _subgroup_labels(patient, row).items():
            state = subgroup_state.setdefault(
                (dimension, label),
                {
                    "row_count": 0,
                    "observed_event_count": 0,
                    "missing_counts": {name: 0 for name in MODEL_VECTOR_FEATURE_NAMES},
                },
            )
            state["row_count"] += 1
            state["observed_event_count"] += int(event)
            for feature_name, value in zip(MODEL_VECTOR_FEATURE_NAMES, vector):
                if np.isnan(value):
                    state["missing_counts"][feature_name] += 1
        matrix.append(vector)
        durations.append(duration)
        events.append(event)
        patient_ids.append(patient_id.strip())
        raw_weight = row.get("sample_weight", row.get("weight"))
        if raw_weight is None:
            raw_weights.append(None)
        else:
            try:
                numeric_weight = float(raw_weight)
            except (TypeError, ValueError) as error:
                raise ValidationError(
                    "sample_weight must be numeric",
                    field_errors={
                        f"row[{row_number}].sample_weight": "expected number"
                    },
                ) from error
            if not np.isfinite(numeric_weight) or numeric_weight <= 0:
                raise ValidationError(
                    "sample_weight must be positive and finite",
                    field_errors={f"row[{row_number}].sample_weight": "expected > 0"},
                )
            raw_weights.append(numeric_weight)
    if not matrix:
        raise ValidationError("at least one training row is required")
    if any(weight is not None for weight in raw_weights) and any(
        weight is None for weight in raw_weights
    ):
        raise ValidationError(
            "sample_weight must be supplied for every row or omitted for every row"
        )
    has_sample_weight = bool(raw_weights and raw_weights[0] is not None)
    resolved_survey_design = resolve_survey_design(
        survey_design, has_sample_weight=has_sample_weight
    )
    row_count = len(matrix)
    quality = TrainingQualityReport(
        row_count=row_count,
        observed_event_count=sum(events),
        censored_row_count=row_count - sum(events),
        missing_counts=missing_counts,
        missing_rates={
            name: round(count / row_count, 6) for name, count in missing_counts.items()
        },
        subgroups={
            dimension: {
                label: TrainingSubgroupQuality(
                    row_count=state["row_count"],
                    observed_event_count=state["observed_event_count"],
                    censored_row_count=(
                        state["row_count"] - state["observed_event_count"]
                    ),
                    missing_counts=state["missing_counts"],
                    missing_rates={
                        name: round(
                            count / state["row_count"],
                            6,
                        )
                        for name, count in state["missing_counts"].items()
                    },
                )
                for (state_dimension, label), state in subgroup_state.items()
                if state_dimension == dimension
            }
            for dimension in sorted(
                {state_dimension for state_dimension, _ in subgroup_state}
            )
        },
        sample_weight_mode=(
            "xgboost_dmatrix_case_weight" if has_sample_weight else "not_provided"
        ),
        survey_design_summary=resolved_survey_design.to_metadata(
            weighting_applied=(
                has_sample_weight
                and resolved_survey_design.weight_kind == "case_weight"
            )
        ),
    )
    return SurvivalTrainingFrame(
        feature_names=MODEL_VECTOR_FEATURE_NAMES,
        x=np.asarray(matrix, dtype=float),
        durations=np.asarray(durations, dtype=float),
        events=np.asarray(events, dtype=bool),
        patient_ids=tuple(patient_ids),
        weights=(
            np.asarray(raw_weights, dtype=float)
            if raw_weights and raw_weights[0] is not None
            else None
        ),
        quality=quality,
        survey_design=resolved_survey_design,
    )


MODEL_MEASUREMENT_NAMES = (
    "age",
    "sex",
    "bmi",
    "systolic_bp",
    "diastolic_bp",
    "resting_hr",
    "waist_circumference",
    "phase_angle",
    "ecw_tbw",
    "ffmi",
    "skeletal_muscle_mass",
    "visceral_fat",
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
    "grip_strength",
    "chair_rise_time",
    "smoking_status",
    "alcohol_heavy_use",
    "sleep_hours",
)


def fit_xgb_survival(
    rows: Iterable[Mapping[str, Any]],
    *,
    reference_panel: ReferencePanel | None = None,
    mapper: GompertzMapper | None = None,
    survey_design: SurveyDesign | None = None,
) -> XGBSurvivalModel:
    """Build and fit the optional survival model on already-approved rows."""

    frame = build_survival_frame(
        rows, reference_panel=reference_panel, survey_design=survey_design
    )
    model = XGBSurvivalModel(frame.feature_names, mapper=mapper)
    model.fit(
        frame.x,
        frame.durations,
        frame.events,
        sample_weight=frame.weights,
        survey_design=frame.survey_design,
    )
    model.training_quality = frame.quality.to_mapping() if frame.quality else None
    return model
