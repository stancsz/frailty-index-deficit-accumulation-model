"""Deterministic Rockwood-style deficit scoring."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal

from .features import FI_FEATURES, PatientData


# These are explicit, reviewable engineering defaults. They are not a claim
# that every threshold is validated for every population or device.
CUTOFF_SOURCES = {
    "bmi": "WHO BMI classification; see docs/SOURCES.md#cutoff-boundary",
    "systolic_bp": "2017 ACC/AHA adult blood pressure guideline; see docs/SOURCES.md#cutoff-boundary",
    "diastolic_bp": "2017 ACC/AHA adult blood pressure guideline; see docs/SOURCES.md#cutoff-boundary",
    "waist_circumference": "IDF metabolic-syndrome definition; see docs/SOURCES.md#cutoff-boundary",
    "fasting_glucose": "ADA diagnostic thresholds; see docs/SOURCES.md#cutoff-boundary",
    "hba1c": "ADA diagnostic thresholds; see docs/SOURCES.md#cutoff-boundary",
    "egfr": "KDIGO CKD G-category thresholds; see docs/SOURCES.md#cutoff-boundary",
    "grip_strength": "EWGSOP2 low-strength guidance; see docs/SOURCES.md#cutoff-boundary",
    "chair_rise_time": "Short Physical Performance Battery convention; see docs/SOURCES.md#cutoff-boundary",
    "fib_4": "FIB-4 published risk thresholds; see docs/SOURCES.md#cutoff-boundary",
    "resting_hr": "Engineering screening band; validate against the target cohort before production.",
    "phase_angle": "Searle et al. 0/0.5/1 deficit coding applied to calibrated z-score bands; see docs/SOURCES.md#deficit-accumulation",
    "ecw_tbw": "Searle et al. 0/0.5/1 deficit coding applied to calibrated z-score bands; see docs/SOURCES.md#deficit-accumulation",
    "ffmi": "Searle et al. 0/0.5/1 deficit coding applied to calibrated z-score bands; see docs/SOURCES.md#deficit-accumulation",
    "skeletal_muscle_mass": "Searle et al. 0/0.5/1 deficit coding applied to calibrated z-score bands; see docs/SOURCES.md#deficit-accumulation",
    "visceral_fat": "SECA reference-panel measurement; threshold approval remains an external validation obligation.",
    "hs_crp": "Cardiovascular risk reference bands; validate in the target cohort before production.",
    "albumin": "Common clinical lower-reference boundary; validate in the target cohort before production.",
    "creatinine": "Common clinical reference boundary with sex stratification; validate in the target cohort before production.",
    "alp": "Common adult laboratory reference interval; validate by laboratory before production.",
    "wbc": "Common adult laboratory reference interval; validate by laboratory before production.",
    "rdw": "Common adult laboratory reference interval; validate by laboratory before production.",
    "hypertension": "Binary deficit coding follows Searle et al.; see docs/SOURCES.md#deficit-accumulation.",
    "t2d": "Binary deficit coding follows Searle et al.; see docs/SOURCES.md#deficit-accumulation.",
    "osteoarthritis": "Binary deficit coding follows Searle et al.; see docs/SOURCES.md#deficit-accumulation.",
    "sleep_apnea": "Binary deficit coding follows Searle et al.; see docs/SOURCES.md#deficit-accumulation.",
    "cvd": "Binary deficit coding follows Searle et al.; see docs/SOURCES.md#deficit-accumulation.",
    "copd": "Binary deficit coding follows Searle et al.; see docs/SOURCES.md#deficit-accumulation.",
    "cancer": "Binary deficit coding follows Searle et al.; see docs/SOURCES.md#deficit-accumulation.",
    "depression": "Binary deficit coding follows Searle et al.; see docs/SOURCES.md#deficit-accumulation.",
    "alcohol_heavy_use": "Binary deficit coding follows Searle et al.; see docs/SOURCES.md#deficit-accumulation.",
    "smoking_status": "Ordinal deficit coding follows Searle et al.; see docs/SOURCES.md#deficit-accumulation.",
    "sleep_hours": "Engineering sleep-duration band; validate against the target cohort before production.",
}


DenominatorStrength = Literal["low", "moderate", "high"]
FI_DENOMINATOR_TOTAL = len(FI_FEATURES)
FI_DENOMINATOR_STRENGTH_BANDS: dict[DenominatorStrength, tuple[int, int]] = {
    "low": (0, 18),
    "moderate": (19, 27),
    "high": (28, FI_DENOMINATOR_TOTAL),
}
FI_DENOMINATOR_STRENGTH_CAVEAT = (
    "Engineering label based on the count of FI-eligible items in this single "
    "assessment; it is not a clinical adequacy claim."
)


def denominator_strength(denominator: int) -> DenominatorStrength:
    """Return a count-only review label for the FI denominator.

    These bands are engineering defaults for communicating measurement support.
    They are not validated completeness thresholds or medical recommendations.
    """

    if denominator <= FI_DENOMINATOR_STRENGTH_BANDS["low"][1]:
        return "low"
    if denominator <= FI_DENOMINATOR_STRENGTH_BANDS["moderate"][1]:
        return "moderate"
    return "high"


@dataclass(frozen=True)
class FIResult:
    score: float
    numerator: float
    denominator: int
    deficits: dict[str, float]
    valid_variables: tuple[str, ...]

    @property
    def caveat(self) -> str:
        return "FI denominator is the count of valid FI-eligible health variables; missing values are not imputed."

    @property
    def denominator_strength(self) -> DenominatorStrength:
        return denominator_strength(self.denominator)

    @property
    def denominator_strength_caveat(self) -> str:
        return FI_DENOMINATOR_STRENGTH_CAVEAT


def _three_level(
    value: float,
    healthy: Callable[[float], bool],
    intermediate: Callable[[float], bool],
) -> float:
    if healthy(value):
        return 0.0
    if intermediate(value):
        return 0.5
    return 1.0


def _range_score(
    value: float,
    low: float,
    high: float,
    outer_low: float | None = None,
    outer_high: float | None = None,
) -> float:
    if low <= value <= high:
        return 0.0
    if outer_low is None:
        outer_low = low
    if outer_high is None:
        outer_high = high
    if outer_low <= value < low or high < value <= outer_high:
        return 0.5
    return 1.0


def _score_feature(
    name: str, value: object, sex: str, z_scores: dict[str, float]
) -> float | None:
    if value is None:
        return None
    number = float(value) if isinstance(value, (int, float)) else None
    if name == "bmi":
        return _three_level(number, lambda x: 18.5 <= x < 25, lambda x: 17 <= x < 30)
    if name == "systolic_bp":
        return _three_level(number, lambda x: x < 130, lambda x: x < 140)
    if name == "diastolic_bp":
        return _three_level(number, lambda x: x < 80, lambda x: x < 90)
    if name == "resting_hr":
        return _range_score(number, 50, 90, 40, 100)
    if name == "waist_circumference":
        low, high = (94, 102) if sex == "male" else (80, 88)
        return _three_level(number, lambda x: x < low, lambda x: x <= high)
    if name in {"phase_angle", "ffmi", "skeletal_muscle_mass"}:
        z = z_scores.get(name)
        if z is None:
            return None
        return _three_level(z, lambda x: x >= -1, lambda x: x >= -2)
    if name == "ecw_tbw":
        z = z_scores.get(name)
        if z is None:
            return None
        return _three_level(z, lambda x: x <= 1, lambda x: x <= 2)
    if name == "visceral_fat":
        return _three_level(number, lambda x: x < 10, lambda x: x < 15)
    if name == "fasting_glucose":
        return _three_level(number, lambda x: x < 100, lambda x: x < 126)
    if name == "hba1c":
        return _three_level(number, lambda x: x < 5.7, lambda x: x < 6.5)
    if name == "hs_crp":
        return _three_level(number, lambda x: x < 1, lambda x: x <= 3)
    if name == "albumin":
        return _three_level(number, lambda x: x >= 3.5, lambda x: x >= 3.0)
    if name == "creatinine":
        upper = 1.2 if sex == "male" else 1.0
        return _three_level(number, lambda x: x <= upper, lambda x: x <= upper * 1.35)
    if name == "egfr":
        return _three_level(number, lambda x: x >= 90, lambda x: x >= 60)
    if name == "alp":
        return _three_level(number, lambda x: 44 <= x <= 147, lambda x: 30 <= x <= 200)
    if name == "wbc":
        return _range_score(number, 4, 10, 3, 12)
    if name == "rdw":
        return _three_level(number, lambda x: x <= 14.5, lambda x: x <= 16)
    if name == "fib_4":
        return _three_level(number, lambda x: x < 1.3, lambda x: x < 2.67)
    if name in {
        "hypertension",
        "t2d",
        "osteoarthritis",
        "sleep_apnea",
        "cvd",
        "copd",
        "cancer",
        "depression",
        "alcohol_heavy_use",
    }:
        return float(number)
    if name == "grip_strength":
        healthy, intermediate = (30, 20) if sex == "male" else (20, 15)
        return _three_level(number, lambda x: x >= healthy, lambda x: x >= intermediate)
    if name == "chair_rise_time":
        return _three_level(number, lambda x: x <= 10, lambda x: x <= 15)
    if name == "smoking_status":
        return {"never": 0.0, "former": 0.5, "current": 1.0}[str(value)]
    if name == "sleep_hours":
        return _range_score(number, 7, 9, 6, 10)
    raise KeyError(name)


def calculate_fi(patient: PatientData, z_scores: dict[str, float]) -> FIResult:
    deficits: dict[str, float] = {}
    for name in FI_FEATURES:
        score = _score_feature(
            name, patient.values[name], patient.values["sex"], z_scores
        )
        if score is not None:
            deficits[name] = round(score, 4)
    numerator = round(sum(deficits.values()), 4)
    denominator = len(deficits)
    score = round(numerator / denominator, 4) if denominator else 0.0
    return FIResult(
        score=score,
        numerator=numerator,
        denominator=denominator,
        deficits=deficits,
        valid_variables=tuple(deficits),
    )
