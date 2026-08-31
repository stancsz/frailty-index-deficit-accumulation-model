"""Biological-age mapping and optional XGBoost survival adapter."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Iterable, Literal, Mapping, Protocol, Sequence, runtime_checkable
import warnings

import numpy as np

from .exceptions import ModelUnavailableError
from .features import BIA_FEATURES, FEATURE_NAMES
from .survey_design import SurveyDesign, resolve_survey_design


_XGB_TRAINING_PARAMETERS = {
    "objective": "survival:cox",
    "eval_metric": "cox-nloglik",
    "max_depth": 3,
    "eta": 0.03,
    "subsample": 0.85,
    "colsample_bytree": 0.85,
    "lambda": 1.0,
    "seed": 42,
    "nthread": 1,
}
_XGB_NUM_BOOST_ROUNDS = 300
_LOG_FLOAT_MAX = math.log(sys.float_info.max)


def _log_expm1_positive(value: float) -> float:
    if not math.isfinite(value) or value <= 0:
        raise ValueError("exponential-minus-one input must be positive and finite")
    if value > 50:
        return value + math.log1p(-math.exp(-value))
    return math.log(math.expm1(value))


def _binary_event_array(values: Iterable[bool]) -> np.ndarray:
    """Parse survival events without Python's unsafe truthiness coercion."""

    parsed: list[bool] = []
    for value in values:
        if isinstance(value, (bool, np.bool_)):
            parsed.append(bool(value))
        elif isinstance(value, (int, float, np.integer, np.floating)):
            if not math.isfinite(float(value)) or value not in (0, 1):
                raise ValueError("events must contain only boolean or 0/1 values")
            parsed.append(bool(value))
        else:
            raise ValueError("events must contain only boolean or 0/1 values")
    return np.asarray(parsed, dtype=bool)


@dataclass(frozen=True)
class ModelPrediction:
    point_estimate: float
    ci_95: tuple[float, float] | None
    log_hazard: float
    model_id: str
    production_ready: bool
    warning: str | None = None
    uncertainty_method: str = "unvalidated_engineering_interval"
    uncertainty_validated: bool = False
    uncertainty_construction: Literal["wald_1_96_se", "none_withheld"] = "none_withheld"


_FUNCTIONAL_VECTOR_ORDER = (
    "alcohol_heavy_use",
    "sleep_hours",
    "smoking_status",
)
MODEL_VECTOR_SOURCE_FEATURE_NAMES = (
    tuple(
        name
        for name in FEATURE_NAMES
        if name not in {"smoking_status", "alcohol_heavy_use", "sleep_hours"}
    )
    + _FUNCTIONAL_VECTOR_ORDER
    + ("current_deficit_load_fi",)
)
MODEL_VECTOR_FEATURE_NAMES = tuple(
    "sex_male" if name == "sex" else f"{name}_z" if name in BIA_FEATURES else name
    for name in MODEL_VECTOR_SOURCE_FEATURE_NAMES
)
_MODEL_VECTOR_INDEX = {
    name: index for index, name in enumerate(MODEL_VECTOR_FEATURE_NAMES)
}


@runtime_checkable
class ModelAdapterProtocol(Protocol):
    """Explicit input contract required by assessment serving."""

    def predict_for_assessment(
        self, chronological_age: float, encoded_vector: Sequence[float]
    ) -> ModelPrediction:
        """Predict from the encoded assessment vector."""


@dataclass(frozen=True)
class ModelApproval:
    """Human-authored approval metadata bound to one artifact and panel file."""

    schema_version: str
    model_id: str
    artifact_sha256: str
    feature_names: tuple[str, ...]
    reference_panel_id: str
    reference_panel_sha256: str
    uncertainty_method: str
    log_hazard_se: float
    production_ready: bool
    uncertainty_validated: bool
    approved_by: str
    approved_at: str
    evidence_refs: tuple[str, ...]

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> "ModelApproval":
        required = {
            "schema_version",
            "model_id",
            "artifact_sha256",
            "feature_names",
            "reference_panel_id",
            "reference_panel_sha256",
            "uncertainty_method",
            "log_hazard_se",
            "production_ready",
            "uncertainty_validated",
            "approved_by",
            "approved_at",
            "evidence_refs",
        }
        if set(data) != required:
            raise ValueError("model approval manifest has an invalid field set")
        if data["schema_version"] != "1":
            raise ValueError(
                "model approval manifest has an unsupported schema version"
            )
        string_fields = (
            "model_id",
            "artifact_sha256",
            "reference_panel_id",
            "reference_panel_sha256",
            "uncertainty_method",
            "approved_by",
            "approved_at",
        )
        if any(
            not isinstance(data[field], str) or not str(data[field]).strip()
            for field in string_fields
        ):
            raise ValueError("model approval manifest has an invalid string field")
        digest = str(data["artifact_sha256"]).lower()
        if len(digest) != 64 or any(
            character not in "0123456789abcdef" for character in digest
        ):
            raise ValueError("model approval manifest has an invalid SHA-256 digest")
        panel_digest = str(data["reference_panel_sha256"]).lower()
        if len(panel_digest) != 64 or any(
            character not in "0123456789abcdef" for character in panel_digest
        ):
            raise ValueError(
                "model approval manifest has an invalid reference-panel SHA-256 digest"
            )
        raw_features = data["feature_names"]
        if (
            not isinstance(raw_features, list)
            or not raw_features
            or not all(
                isinstance(value, str) and value.strip() for value in raw_features
            )
            or len(set(raw_features)) != len(raw_features)
        ):
            raise ValueError("model approval manifest has invalid feature names")
        raw_evidence = data["evidence_refs"]
        if (
            not isinstance(raw_evidence, list)
            or not raw_evidence
            or not all(
                isinstance(value, str) and value.strip() for value in raw_evidence
            )
        ):
            raise ValueError("model approval manifest requires evidence references")
        if not isinstance(data["production_ready"], bool) or not isinstance(
            data["uncertainty_validated"], bool
        ):
            raise ValueError("model approval manifest has invalid approval flags")
        if isinstance(data["log_hazard_se"], bool):
            raise ValueError(
                "model approval manifest has an invalid uncertainty parameter"
            )
        try:
            log_hazard_se = float(data["log_hazard_se"])
        except (TypeError, ValueError) as error:
            raise ValueError(
                "model approval manifest has an invalid uncertainty parameter"
            ) from error
        if not math.isfinite(log_hazard_se) or log_hazard_se < 0:
            raise ValueError(
                "model approval manifest uncertainty parameter must be finite and non-negative"
            )
        return cls(
            schema_version="1",
            model_id=str(data["model_id"]),
            artifact_sha256=digest,
            feature_names=tuple(str(value) for value in raw_features),
            reference_panel_id=str(data["reference_panel_id"]),
            reference_panel_sha256=panel_digest,
            uncertainty_method=str(data["uncertainty_method"]),
            log_hazard_se=log_hazard_se,
            production_ready=data["production_ready"],
            uncertainty_validated=data["uncertainty_validated"],
            approved_by=str(data["approved_by"]),
            approved_at=str(data["approved_at"]),
            evidence_refs=tuple(str(value) for value in raw_evidence),
        )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class GompertzMapper:
    """Map a relative log-hazard to the age with equivalent baseline 10-year risk."""

    baseline_scale: float = 0.00008
    growth_rate: float = 0.085
    min_age: float = 18.0
    max_age: float = 110.0

    def __post_init__(self) -> None:
        values = (self.baseline_scale, self.growth_rate, self.min_age, self.max_age)
        if not all(math.isfinite(float(value)) for value in values):
            raise ValueError("Gompertz parameters must be finite")
        if self.baseline_scale <= 0 or self.growth_rate <= 0:
            raise ValueError("Gompertz scale and growth rate must be positive")
        if self.min_age < 0 or self.min_age >= self.max_age:
            raise ValueError("Gompertz age bounds must satisfy 0 <= min_age < max_age")

    def to_mapping(self) -> dict[str, float]:
        """Return the exact mapper parameters for an auditable artifact manifest."""

        return {key: float(value) for key, value in asdict(self).items()}

    @classmethod
    def from_mapping(cls, values: dict[str, float]) -> "GompertzMapper":
        """Restore mapper parameters, validating them through ``__post_init__``."""

        required = {"baseline_scale", "growth_rate", "min_age", "max_age"}
        if set(values) != required:
            raise ValueError("Gompertz mapper manifest has an invalid field set")
        return cls(**{key: float(values[key]) for key in required})

    @classmethod
    def fit_from_survival(
        cls,
        ages: Iterable[float],
        durations: Iterable[float],
        events: Iterable[bool],
        log_hazards: Iterable[float] | None = None,
        *,
        min_age: float = 18.0,
        max_age: float = 110.0,
        sample_weight: Iterable[float] | None = None,
    ) -> "GompertzMapper":
        """Fit the baseline Gompertz curve by a one-dimensional profile likelihood.

        ``log_hazards`` are Cox linear predictors.  For a fixed growth rate,
        the baseline scale has a closed-form maximum-likelihood estimate, so
        this method needs no optional optimizer.  It is a calibration primitive
        for an approved development cohort, not a substitute for external
        validation or clinical sign-off. ``sample_weight`` applies the same
        positive case weights to the profile likelihood; it is not a complex-
        survey variance estimator.
        """

        age_array = np.asarray(list(ages), dtype=float)
        duration_array = np.asarray(list(durations), dtype=float)
        event_array = _binary_event_array(events)
        if log_hazards is None:
            hazard_array = np.zeros(len(age_array), dtype=float)
        else:
            hazard_array = np.asarray(list(log_hazards), dtype=float)
        if sample_weight is None:
            weight_array = np.ones(len(age_array), dtype=float)
        else:
            weight_array = np.asarray(list(sample_weight), dtype=float)
        if not (
            len(age_array)
            == len(duration_array)
            == len(event_array)
            == len(hazard_array)
            == len(weight_array)
        ):
            raise ValueError(
                "ages, durations, events, and log_hazards must have equal length"
            )
        if len(age_array) == 0 or not np.all(np.isfinite(age_array)):
            raise ValueError("at least one finite age is required")
        if not np.all(np.isfinite(duration_array)) or np.any(duration_array <= 0):
            raise ValueError("survival durations must be positive and finite")
        if not np.all(np.isfinite(hazard_array)):
            raise ValueError("log-hazards must be finite")
        if not np.all(np.isfinite(weight_array)) or np.any(weight_array <= 0):
            raise ValueError("sample weights must be positive and finite")
        event_weight = float(np.sum(weight_array[event_array]))
        if event_weight <= 0:
            raise ValueError(
                "at least one observed event is required to fit Gompertz baseline"
            )

        def profile_log_likelihood(growth: float) -> float:
            # Work in log space so an extreme but finite development fixture
            # cannot overflow the one-dimensional calibration search.
            log_exposure = (
                hazard_array
                + growth * age_array
                + np.asarray(
                    [_log_expm1_positive(growth * value) for value in duration_array]
                )
                - math.log(growth)
                + np.log(weight_array)
            )
            if not np.all(np.isfinite(log_exposure)):
                return -math.inf
            maximum = float(np.max(log_exposure))
            log_exposure_sum = maximum + math.log(
                float(np.sum(np.exp(log_exposure - maximum)))
            )
            event_term = float(
                np.sum(
                    weight_array
                    * event_array
                    * (hazard_array + growth * (age_array + duration_array))
                )
            )
            if not math.isfinite(event_term):
                return -math.inf
            return (
                event_weight * (math.log(event_weight) - log_exposure_sum)
                + event_term
                - event_weight
            )

        # Profile likelihoods can be flat in small development samples. A
        # deterministic grid plus local refinement keeps the artifact
        # reproducible and makes boundary behavior inspectable.
        grid = np.linspace(0.01, 0.20, 191)
        scores = np.asarray([profile_log_likelihood(float(rate)) for rate in grid])
        if not np.any(np.isfinite(scores)):
            raise ValueError("Gompertz calibration produced no finite likelihood")
        best_index = int(np.argmax(scores))
        best_growth = float(grid[best_index])
        left = float(grid[max(0, best_index - 1)])
        right = float(grid[min(len(grid) - 1, best_index + 1)])
        for _ in range(32):
            first = left + (right - left) / 3.0
            second = right - (right - left) / 3.0
            if profile_log_likelihood(first) < profile_log_likelihood(second):
                left = first
            else:
                right = second
        best_growth = (left + right) / 2.0 if right > left else best_growth
        log_exposure = (
            hazard_array
            + best_growth * age_array
            + np.asarray(
                [_log_expm1_positive(best_growth * value) for value in duration_array]
            )
            - math.log(best_growth)
            + np.log(weight_array)
        )
        if not np.all(np.isfinite(log_exposure)):
            raise ValueError("Gompertz calibration produced non-finite exposure")
        maximum = float(np.max(log_exposure))
        log_exposure_sum = maximum + math.log(
            float(np.sum(np.exp(log_exposure - maximum)))
        )
        log_scale = math.log(event_weight) - log_exposure_sum
        if log_scale < math.log(sys.float_info.min) or log_scale > _LOG_FLOAT_MAX:
            raise ValueError("Gompertz calibration produced an unrepresentable scale")
        best_scale = math.exp(log_scale)
        return cls(
            baseline_scale=best_scale,
            growth_rate=best_growth,
            min_age=min_age,
            max_age=max_age,
        )

    @staticmethod
    def _log_expm1_positive(value: float) -> float:
        return _log_expm1_positive(value)

    def _log_cumulative_hazard_10y(self, age: float) -> float:
        if not math.isfinite(age):
            raise ValueError("age must be finite")
        return (
            math.log(self.baseline_scale)
            - math.log(self.growth_rate)
            + self.growth_rate * age
            + _log_expm1_positive(self.growth_rate * 10.0)
        )

    def cumulative_hazard_10y(self, age: float) -> float:
        log_hazard = self._log_cumulative_hazard_10y(age)
        if log_hazard > _LOG_FLOAT_MAX:
            return math.inf
        return math.exp(log_hazard)

    def probability_10y(self, age: float, log_hazard_ratio: float = 0.0) -> float:
        if not math.isfinite(log_hazard_ratio):
            raise ValueError("log hazard ratio must be finite")
        log_hazard = self._log_cumulative_hazard_10y(age) + log_hazard_ratio
        if math.isnan(log_hazard):
            raise ValueError("log hazard must be finite or have an overflow direction")
        if log_hazard == math.inf:
            return 1.0
        if log_hazard > 40:
            return 1.0
        if log_hazard == -math.inf:
            return 0.0
        hazard = math.exp(log_hazard)
        return -math.expm1(-hazard)

    def age_from_probability_10y(self, probability: float) -> float:
        """Invert a ten-year probability onto the configured baseline curve."""

        if not 0 <= probability < 1:
            raise ValueError("ten-year probability must be in the interval [0, 1)")
        target_hazard = -math.log1p(-probability)
        if target_hazard == 0:
            return self.min_age
        log_target_hazard = math.log(target_hazard)
        log_baseline_factor = (
            math.log(self.baseline_scale)
            - math.log(self.growth_rate)
            + _log_expm1_positive(self.growth_rate * 10.0)
        )
        age = (log_target_hazard - log_baseline_factor) / self.growth_rate
        if not math.isfinite(age):
            return self.max_age if age > 0 else self.min_age
        return min(self.max_age, max(self.min_age, age))

    def age_from_log_hazard(
        self, chronological_age: float, log_hazard_ratio: float
    ) -> float:
        if not math.isfinite(chronological_age) or not math.isfinite(log_hazard_ratio):
            raise ValueError("chronological age and log hazard ratio must be finite")
        # The inverse is algebraically exact for a multiplicative Cox hazard;
        # using it directly avoids information loss when the probability rounds
        # to 0 or 1 at floating-point extremes.
        age = chronological_age + log_hazard_ratio / self.growth_rate
        return min(self.max_age, max(self.min_age, age))


class DevelopmentPredictor:
    """Deterministic integration fixture; not a trained mortality model."""

    model_id = "development-surrogate-v1"
    production_ready = False

    def __init__(self, mapper: GompertzMapper | None = None):
        self.mapper = mapper or GompertzMapper()

    def predict(
        self, chronological_age: float, fi_score: float, z_scores: dict[str, float]
    ) -> ModelPrediction:
        warnings.warn(
            "DevelopmentPredictor.predict(...) is deprecated; use "
            "predict_for_assessment(...) with the encoded vector",
            DeprecationWarning,
            stacklevel=2,
        )
        oriented = [
            -z if name in {"phase_angle", "ffmi", "skeletal_muscle_mass"} else z
            for name, z in z_scores.items()
        ]
        return self._predict_from_components(chronological_age, fi_score, oriented)

    def _predict_from_components(
        self, chronological_age: float, fi_score: float, oriented: Sequence[float]
    ) -> ModelPrediction:
        mean_bia_deviation = float(np.mean(oriented)) if oriented else 0.0
        log_hazard = 1.2 * (fi_score - 0.15) + 0.10 * mean_bia_deviation
        point = self.mapper.age_from_log_hazard(chronological_age, log_hazard)
        return ModelPrediction(
            point_estimate=round(point, 1),
            ci_95=None,
            log_hazard=log_hazard,
            model_id=self.model_id,
            production_ready=False,
            warning=(
                "Development surrogate only; no approved trained model was supplied. "
                "Uncertainty is not validated; ci_95 is intentionally null rather "
                "than a calibrated clinical confidence interval."
            ),
            uncertainty_method="fixed_log_hazard_sensitivity",
            uncertainty_validated=False,
        )

    def predict_for_assessment(
        self, chronological_age: float, encoded_vector: Sequence[float]
    ) -> ModelPrediction:
        """Use the same encoded vector contract as fitted model adapters."""

        if len(encoded_vector) != len(MODEL_VECTOR_FEATURE_NAMES):
            raise ValueError(
                "encoded assessment vector must contain exactly "
                f"{len(MODEL_VECTOR_FEATURE_NAMES)} values"
            )
        fi_score = float(encoded_vector[_MODEL_VECTOR_INDEX["current_deficit_load_fi"]])
        if not math.isfinite(fi_score):
            raise ValueError("encoded assessment FI value must be finite")
        oriented: list[float] = []
        for feature in BIA_FEATURES:
            value = float(encoded_vector[_MODEL_VECTOR_INDEX[f"{feature}_z"]])
            if math.isfinite(value):
                oriented.append(
                    -value
                    if feature in {"phase_angle", "ffmi", "skeletal_muscle_mass"}
                    else value
                )
        return self._predict_from_components(chronological_age, fi_score, oriented)


class XGBSurvivalModel:
    """Thin optional adapter for an XGBoost `survival:cox` model."""

    def __init__(
        self,
        feature_names: Sequence[str],
        *,
        model_id: str = "xgb-survival-cox-v1",
        mapper: GompertzMapper | None = None,
    ):
        self.feature_names = tuple(feature_names)
        if not self.feature_names or len(set(self.feature_names)) != len(
            self.feature_names
        ):
            raise ValueError("feature_names must be non-empty and unique")
        if mapper is None and self.feature_names[0] != "age":
            raise ValueError(
                "automatic Gompertz baseline fitting requires age as the first feature"
            )
        self.model_id = model_id
        self.mapper = mapper or GompertzMapper()
        self._mapper_supplied = mapper is not None
        self._model = None
        self._uses_native_booster = False
        self.production_ready = False
        self.uncertainty_validated = False
        self.uncertainty_method = "fixed_log_hazard_standard_error"
        self.requires_approval_manifest = True
        self.approved_reference_panel_id: str | None = None
        self.approved_reference_panel_sha256: str | None = None
        self.approval_manifest_path: str | None = None
        self.artifact_sha256: str | None = None
        self.approved_log_hazard_se: float | None = None
        self.training_quality: dict[str, object] | None = None
        self.training_config: dict[str, object] | None = None
        self.survey_design = SurveyDesign()

    def fit(
        self,
        x: np.ndarray,
        durations: Iterable[float],
        events: Iterable[bool],
        *,
        sample_weight: Iterable[float] | None = None,
        survey_design: SurveyDesign | None = None,
    ) -> "XGBSurvivalModel":
        try:
            import xgboost as xgb
        except ImportError as error:
            raise ModelUnavailableError(
                "xgboost is optional; install the [ml] extra to train the survival adapter"
            ) from error
        durations_array = np.asarray(list(durations), dtype=float)
        events_array = _binary_event_array(events)
        if len(x) != len(durations_array) or len(x) != len(events_array):
            raise ValueError("x, durations, and events must have equal length")
        if not np.all(np.isfinite(durations_array)) or np.any(durations_array <= 0):
            raise ValueError("survival durations must be positive and finite")
        if not np.any(events_array):
            raise ValueError("at least one observed event is required")
        labels = np.where(events_array, durations_array, -durations_array)
        matrix = np.asarray(x, dtype=float)
        if matrix.ndim != 2 or matrix.shape[1] != len(self.feature_names):
            raise ValueError("x must be a 2-D matrix matching feature_names")
        if np.any(np.isinf(matrix)):
            raise ValueError("x must not contain infinite feature values")
        if not self._mapper_supplied and self.feature_names[0] != "age":
            raise ValueError(
                "automatic Gompertz baseline fitting requires age as the first feature"
            )
        self.production_ready = False
        self.uncertainty_validated = False
        self.approved_reference_panel_id = None
        self.approved_reference_panel_sha256 = None
        self.approval_manifest_path = None
        self.approved_log_hazard_se = None
        self.uncertainty_method = "fixed_log_hazard_standard_error"
        self.training_quality = None
        self.training_config = None
        self.artifact_sha256 = None
        weights_array = None
        if sample_weight is not None:
            weights_array = np.asarray(list(sample_weight), dtype=float)
            if len(weights_array) != len(matrix):
                raise ValueError("sample_weight must have one value per training row")
            if not np.all(np.isfinite(weights_array)) or np.any(weights_array <= 0):
                raise ValueError("sample_weight values must be positive and finite")
        resolved_survey_design = resolve_survey_design(
            survey_design, has_sample_weight=weights_array is not None
        )
        self.survey_design = resolved_survey_design
        training_matrix = xgb.DMatrix(
            matrix,
            label=labels,
            weight=(
                weights_array
                if resolved_survey_design.weight_kind == "case_weight"
                else None
            ),
            feature_names=list(self.feature_names),
            missing=np.nan,
        )
        self._model = xgb.train(
            _XGB_TRAINING_PARAMETERS,
            training_matrix,
            num_boost_round=_XGB_NUM_BOOST_ROUNDS,
        )
        if not self._mapper_supplied:
            training_margin = self._model.predict(training_matrix, output_margin=True)
            # Keep the baseline calibration's case-weight semantics aligned
            # with the weighted Cox fit. This remains a development estimate,
            # not a full complex-survey baseline-hazard estimator.
            self.mapper = GompertzMapper.fit_from_survival(
                matrix[:, 0],
                durations_array,
                events_array,
                training_margin,
                sample_weight=weights_array,
            )
        self._model.set_attr(
            frailty_feature_manifest=json.dumps(
                list(self.feature_names), separators=(",", ":")
            ),
            frailty_mapper=json.dumps(self.mapper.to_mapping(), separators=(",", ":")),
            frailty_model_id=self.model_id,
        )
        self.training_config = {
            "schema_version": "1",
            "xgboost_version": str(xgb.__version__),
            "num_boost_round": _XGB_NUM_BOOST_ROUNDS,
            "parameters": dict(_XGB_TRAINING_PARAMETERS),
            "mapper_source": (
                "supplied" if self._mapper_supplied else "training_cohort_in_sample"
            ),
            "mapper_weight_mode": (
                "xgboost_dmatrix_case_weight"
                if weights_array is not None
                else "not_provided"
            ),
            "survey_design": resolved_survey_design.to_mapping(),
        }
        self._model.set_attr(
            frailty_training_config=json.dumps(
                self.training_config, separators=(",", ":")
            )
        )
        self._uses_native_booster = True
        return self

    def predict(
        self,
        chronological_age: float,
        x: Sequence[float],
        *,
        log_hazard_se: float | None = None,
    ) -> ModelPrediction:
        if self._model is None:
            raise ModelUnavailableError(
                "the XGBoost survival model has not been fitted"
            )
        if len(x) != len(self.feature_names):
            raise ValueError("x must contain exactly the fitted feature count")
        # For survival:cox, the default prediction is the exponentiated
        # hazard-ratio scale. output_margin=True requests the raw linear
        # predictor (log-risk), which is the value required by the mapper.
        if self._uses_native_booster:
            try:
                import xgboost as xgb
            except ImportError as error:
                raise ModelUnavailableError(
                    "xgboost is required to read the fitted survival model"
                ) from error
            inference_matrix = xgb.DMatrix(
                np.asarray([x], dtype=float),
                feature_names=list(self.feature_names),
                missing=np.nan,
            )
            raw_prediction = self._model.predict(inference_matrix, output_margin=True)
        else:
            # This path keeps the class easy to unit-test with a narrow fake
            # booster without importing the optional dependency.
            raw_prediction = self._model.predict(
                np.asarray([x], dtype=float), output_margin=True
            )
        log_hazard = float(raw_prediction[0])
        if not math.isfinite(log_hazard):
            raise ValueError("XGBoost returned a non-finite log-hazard")
        effective_log_hazard_se = (
            self.approved_log_hazard_se
            if log_hazard_se is None and self.approved_log_hazard_se is not None
            else 0.18
            if log_hazard_se is None
            else log_hazard_se
        )
        if (
            self.approval_manifest_path is not None
            and self.approved_log_hazard_se is not None
            and log_hazard_se is not None
            and not math.isclose(
                log_hazard_se, self.approved_log_hazard_se, rel_tol=0, abs_tol=1e-12
            )
        ):
            raise ValueError(
                "model uncertainty parameter is bound by its approval manifest"
            )
        if not math.isfinite(effective_log_hazard_se) or effective_log_hazard_se < 0:
            raise ValueError(
                "log_hazard standard error must be finite and non-negative"
            )
        point = self.mapper.age_from_log_hazard(chronological_age, log_hazard)
        ci_95 = None
        if self.production_ready and self.uncertainty_validated:
            low = self.mapper.age_from_log_hazard(
                chronological_age, log_hazard - 1.96 * effective_log_hazard_se
            )
            high = self.mapper.age_from_log_hazard(
                chronological_age, log_hazard + 1.96 * effective_log_hazard_se
            )
            ci_95 = (round(low, 1), round(high, 1))
        return ModelPrediction(
            point_estimate=round(point, 1),
            ci_95=ci_95,
            log_hazard=log_hazard,
            model_id=self.model_id,
            production_ready=self.production_ready,
            warning=(
                None
                if self.production_ready and self.uncertainty_validated
                else (
                    "External cohort calibration and uncertainty validation are still "
                    "required. ci_95 is withheld rather than presented as a calibrated "
                    "clinical confidence interval."
                )
            ),
            uncertainty_method=self.uncertainty_method,
            uncertainty_validated=self.uncertainty_validated,
            uncertainty_construction=(
                "wald_1_96_se" if ci_95 is not None else "none_withheld"
            ),
        )

    def predict_for_assessment(
        self,
        chronological_age: float,
        model_vector: Sequence[float],
        *,
        log_hazard_se: float | None = None,
    ) -> ModelPrediction:
        """Use the same vector contract as `pipeline.assess`."""

        return self.predict(
            chronological_age, model_vector, log_hazard_se=log_hazard_se
        )

    def save_model(self, path: str | Path) -> Path:
        """Persist a fitted native booster; validation status is not persisted as approval."""

        if self._model is None or not self._uses_native_booster:
            raise ModelUnavailableError(
                "only a fitted native XGBoost booster can be saved"
            )
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if self.training_quality is not None:
            self._model.set_attr(
                frailty_training_quality=json.dumps(
                    self.training_quality, separators=(",", ":")
                )
            )
        if self.training_config is not None:
            self._model.set_attr(
                frailty_training_config=json.dumps(
                    self.training_config, separators=(",", ":")
                )
            )
        self._model.save_model(str(destination))
        self.artifact_sha256 = _sha256_file(destination)
        return destination

    def _apply_approval_manifest(
        self, artifact_path: Path, approval_manifest_path: str | Path
    ) -> None:
        manifest_path = Path(approval_manifest_path)
        try:
            raw = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
            raise ValueError("could not read model approval manifest") from error
        if not isinstance(raw, Mapping):
            raise ValueError("model approval manifest must be a JSON object")
        approval = ModelApproval.from_mapping(raw)
        actual_digest = _sha256_file(artifact_path)
        if approval.artifact_sha256 != actual_digest:
            raise ValueError("model approval manifest does not match artifact SHA-256")
        if approval.model_id != self.model_id:
            raise ValueError("model approval manifest model_id does not match artifact")
        if approval.feature_names != self.feature_names:
            raise ValueError("model approval manifest features do not match artifact")
        self.production_ready = approval.production_ready
        self.uncertainty_validated = approval.uncertainty_validated
        self.uncertainty_method = approval.uncertainty_method
        self.approved_log_hazard_se = approval.log_hazard_se
        self.approved_reference_panel_id = approval.reference_panel_id
        self.approved_reference_panel_sha256 = approval.reference_panel_sha256
        self.approval_manifest_path = str(manifest_path)

    @classmethod
    def load_model(
        cls,
        path: str | Path,
        feature_names: Sequence[str],
        *,
        model_id: str = "xgb-survival-cox-v1",
        mapper: GompertzMapper | None = None,
        approval_manifest: str | Path | None = None,
    ) -> "XGBSurvivalModel":
        """Load an artifact and optionally verify a hash-bound approval sidecar."""

        try:
            import xgboost as xgb
        except ImportError as error:
            raise ModelUnavailableError(
                "xgboost is required to load the fitted survival model"
            ) from error
        model = cls(feature_names, model_id=model_id, mapper=mapper)
        booster = xgb.Booster()
        booster.load_model(str(path))
        stored_names = getattr(booster, "feature_names", None)
        if not stored_names:
            raise ValueError("model artifact is missing persisted feature names")
        if tuple(stored_names) != tuple(feature_names):
            raise ValueError(
                "model artifact feature names do not match the supplied manifest"
            )
        stored_manifest = booster.attr("frailty_feature_manifest")
        if not stored_manifest:
            raise ValueError("model artifact is missing its feature manifest")
        try:
            manifest_names = tuple(json.loads(stored_manifest))
        except (TypeError, ValueError, json.JSONDecodeError) as error:
            raise ValueError(
                "model artifact has an invalid feature manifest"
            ) from error
        if manifest_names != tuple(feature_names):
            raise ValueError(
                "model artifact manifest does not match the supplied feature names"
            )
        restored_mapper = mapper
        stored_mapper = booster.attr("frailty_mapper")
        persisted_mapper = None
        if stored_mapper:
            try:
                persisted_mapper = GompertzMapper.from_mapping(
                    json.loads(stored_mapper)
                )
            except (TypeError, ValueError, json.JSONDecodeError) as error:
                raise ValueError(
                    "model artifact has an invalid Gompertz mapper"
                ) from error
        if restored_mapper is not None and persisted_mapper is not None:
            if restored_mapper != persisted_mapper:
                raise ValueError(
                    "supplied Gompertz mapper does not match the persisted mapper"
                )
        restored_mapper = restored_mapper or persisted_mapper
        model.mapper = restored_mapper or GompertzMapper()
        stored_quality = booster.attr("frailty_training_quality")
        if stored_quality:
            try:
                parsed_quality = json.loads(stored_quality)
            except (TypeError, ValueError, json.JSONDecodeError) as error:
                raise ValueError(
                    "model artifact has invalid training quality metadata"
                ) from error
            if not isinstance(parsed_quality, Mapping):
                raise ValueError(
                    "model artifact training quality metadata must be an object"
                )
            model.training_quality = dict(parsed_quality)
        stored_config = booster.attr("frailty_training_config")
        if stored_config:
            try:
                parsed_config = json.loads(stored_config)
            except (TypeError, ValueError, json.JSONDecodeError) as error:
                raise ValueError(
                    "model artifact has invalid training configuration metadata"
                ) from error
            if not isinstance(parsed_config, Mapping):
                raise ValueError(
                    "model artifact training configuration metadata must be an object"
                )
            model.training_config = dict(parsed_config)
            stored_survey_design = model.training_config.get("survey_design")
            if stored_survey_design is not None:
                try:
                    model.survey_design = SurveyDesign.from_mapping(
                        stored_survey_design
                    )
                except (TypeError, ValueError) as error:
                    raise ValueError(
                        "model artifact has invalid survey design metadata"
                    ) from error
        mapper_source = (
            model.training_config.get("mapper_source")
            if model.training_config is not None
            else None
        )
        if mapper_source is not None and mapper_source not in {
            "supplied",
            "training_cohort_in_sample",
        }:
            raise ValueError("model artifact has invalid mapper provenance")
        model._mapper_supplied = (
            mapper_source == "supplied"
            if mapper_source is not None
            else restored_mapper is not None
        )
        stored_model_id = booster.attr("frailty_model_id")
        if not stored_model_id:
            raise ValueError("model artifact is missing its model id")
        if model_id == "xgb-survival-cox-v1":
            model.model_id = stored_model_id
        elif stored_model_id != model_id:
            raise ValueError("model artifact model id does not match the supplied id")
        model._model = booster
        model._uses_native_booster = True
        model.artifact_sha256 = _sha256_file(Path(path))
        if approval_manifest is not None:
            model._apply_approval_manifest(Path(path), approval_manifest)
        return model
