"""BIA transfer calibration against age/sex-stratified reference panels."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

from .features import BIA_FEATURES, PatientData


PANEL_READINESS_STATES = (
    "development_fixture_only",
    "loaded_unapproved",
    "loaded_production_ready",
)


@dataclass(frozen=True)
class ReferenceBand:
    min_age: float
    max_age: float
    mean: float
    standard_deviation: float
    source: str

    def __post_init__(self) -> None:
        if not all(
            math.isfinite(float(value))
            for value in (
                self.min_age,
                self.max_age,
                self.mean,
                self.standard_deviation,
            )
        ):
            raise ValueError("reference bands must contain finite values")
        if self.min_age > self.max_age:
            raise ValueError("reference band age bounds are inverted")
        if self.standard_deviation <= 0:
            raise ValueError("reference band standard deviation must be positive")

    def contains(self, age: float) -> bool:
        return self.min_age <= age <= self.max_age


@dataclass(frozen=True)
class ReferencePanel:
    panel_id: str
    version: str
    production_ready: bool
    bands: dict[str, dict[str, tuple[ReferenceBand, ...]]]
    source_note: str
    source_sha256: str | None = None
    fixture_only: bool = False

    def __post_init__(self) -> None:
        if self.production_ready and self.fixture_only:
            raise ValueError(
                "a fixture-only reference panel cannot be production-ready"
            )
        if self.source_sha256 is not None:
            digest = self.source_sha256.lower()
            if len(digest) != 64 or any(
                character not in "0123456789abcdef" for character in digest
            ):
                raise ValueError(
                    "reference panel source_sha256 must be a SHA-256 digest"
                )

    def band_for(self, feature: str, sex: str, age: float) -> ReferenceBand:
        candidates = self.bands[feature][sex]
        for band in candidates:
            if band.contains(age):
                return band
        raise ValueError(f"no reference band for {feature}/{sex}/{age}")

    def coverage_for(
        self,
        sex: str,
        age: float,
        *,
        features: Iterable[str] | None = None,
    ) -> tuple[int, float]:
        """Return the deterministic BIA age-band geometry for one patient.

        Engineering metadata only. ``band_count`` is the minimum number of
        reference bands containing ``age`` across the requested BIA features,
        defaulting to all BIA features, and
        ``span_years`` is the narrowest matched-band width. Taking the
        minimum makes the result conservative when a supplied panel uses
        different age-band layouts for different features. ``age`` outside
        any requested feature's bands returns ``(0, 0.0)`` so callers can
        detect out-of-coverage patients without relying on exception control
        flow. External validation should pass only measured BIA features;
        assessment quality intentionally uses the default all-feature view.
        """

        if sex not in ("male", "female"):
            raise ValueError("sex must be 'male' or 'female'")
        if not math.isfinite(float(age)):
            raise ValueError("age must be finite")
        requested_features = tuple(BIA_FEATURES if features is None else features)
        if not requested_features or any(
            feature not in BIA_FEATURES for feature in requested_features
        ):
            raise ValueError("features must contain at least one BIA feature")
        matched_by_feature = [
            [band for band in self.bands[feature][sex] if band.contains(float(age))]
            for feature in requested_features
        ]
        if any(not matched for matched in matched_by_feature):
            return 0, 0.0
        return (
            min(len(matched) for matched in matched_by_feature),
            min(
                float(band.max_age - band.min_age)
                for matched in matched_by_feature
                for band in matched
            ),
        )

    def z_score(self, feature: str, value: float, *, sex: str, age: float) -> float:
        band = self.band_for(feature, sex, age)
        return (value - band.mean) / band.standard_deviation

    def z_scores(self, patient: PatientData) -> dict[str, float]:
        age = patient.values["age"]
        sex = patient.values["sex"]
        if age is None or sex is None:
            raise ValueError("age and sex are required before BIA calibration")
        return {
            feature: self.z_score(feature, patient.values[feature], sex=sex, age=age)
            for feature in BIA_FEATURES
            if patient.values[feature] is not None
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "ReferencePanel":
        if not data.get("panel_id"):
            raise ValueError("reference panel requires panel_id")
        if "features" not in data or not isinstance(data["features"], Mapping):
            raise ValueError("reference panel requires a features mapping")
        approval_flags = {
            name: data.get(name, False) for name in ("production_ready", "fixture_only")
        }
        for name, value in approval_flags.items():
            if not isinstance(value, bool):
                raise ValueError(f"reference panel {name} must be boolean")
        bands: dict[str, dict[str, tuple[ReferenceBand, ...]]] = {}
        for feature in BIA_FEATURES:
            if feature not in data["features"]:
                raise ValueError(f"reference panel is missing {feature}")
            feature_data = data["features"][feature]
            if not isinstance(feature_data, Mapping):
                raise ValueError(f"reference panel has invalid data for {feature}")
            bands[feature] = {}
            for sex in ("male", "female"):
                if sex not in feature_data or not feature_data[sex]:
                    raise ValueError(f"reference panel is missing {feature}/{sex}")
                try:
                    parsed_bands = tuple(
                        ReferenceBand(
                            min_age=float(item["min_age"]),
                            max_age=float(item["max_age"]),
                            mean=float(item["mean"]),
                            standard_deviation=float(item["sd"]),
                            source=str(
                                item.get(
                                    "source", data.get("source_note", "unspecified")
                                )
                            ),
                        )
                        for item in feature_data[sex]
                    )
                except (KeyError, TypeError, ValueError) as error:
                    raise ValueError(
                        f"reference panel has invalid band for {feature}/{sex}"
                    ) from error
                if any(
                    current.min_age < previous.min_age
                    or current.min_age <= previous.max_age
                    for previous, current in zip(parsed_bands, parsed_bands[1:])
                ):
                    raise ValueError(
                        f"reference panel has overlapping or unsorted bands for {feature}/{sex}"
                    )
                bands[feature][sex] = parsed_bands
        return cls(
            panel_id=str(data["panel_id"]),
            version=str(data.get("version", "unversioned")),
            production_ready=approval_flags["production_ready"],
            bands=bands,
            source_note=str(data.get("source_note", "")),
            fixture_only=approval_flags["fixture_only"],
        )

    @classmethod
    def from_json(cls, path: str | Path) -> "ReferencePanel":
        panel_path = Path(path)
        panel = cls.from_mapping(json.loads(panel_path.read_text(encoding="utf-8")))
        digest = hashlib.sha256()
        with panel_path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return replace(panel, source_sha256=digest.hexdigest())


def panel_readiness(panel: ReferencePanel) -> str:
    """Return a conservative, machine-readable runtime panel state.

    ``production_ready`` is an approval flag on the panel data, while the
    serving gate also requires an identity digest.  The public state therefore
    only reports ``loaded_production_ready`` when both are present.  A
    development fixture always wins so downstream clients do not infer that a
    synthetic panel is suitable for production from any other flag.
    """

    if panel.fixture_only:
        return "development_fixture_only"
    if panel.production_ready and panel.source_sha256:
        return "loaded_production_ready"
    return "loaded_unapproved"


def _band_value_digest(panel: ReferencePanel) -> str:
    """Return a stable digest of band values, excluding approval metadata."""

    payload = {
        feature: {
            sex: [
                {
                    "min_age": band.min_age,
                    "max_age": band.max_age,
                    "mean": band.mean,
                    "sd": band.standard_deviation,
                }
                for band in panel.bands[feature][sex]
            ]
            for sex in ("male", "female")
        }
        for feature in BIA_FEATURES
    }
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def is_development_fixture_content(panel: ReferencePanel) -> bool:
    """Return whether a panel carries the shipped synthetic band values.

    Approval flags and source labels are deliberately excluded from this
    comparison.  Copying the synthetic values into a new JSON file and
    changing only those metadata fields must not make the fixture appear
    production-ready.
    """

    expected = ReferencePanel.from_mapping(_default_development_panel_data())
    return _band_value_digest(panel) == _band_value_digest(expected)


def _canonical_panel_sha256(data: Mapping[str, Any]) -> str:
    """Hash a deterministic panel mapping used for in-memory fixtures."""

    encoded = json.dumps(
        data, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _default_development_panel_data() -> dict[str, Any]:
    """Build the canonical synthetic panel mapping used by development runs."""

    def row(mean: float, sd: float) -> list[dict[str, float | str]]:
        return [
            {
                "min_age": 18,
                "max_age": 120,
                "mean": mean,
                "sd": sd,
                "source": "synthetic-development-fixture",
            }
        ]

    data = {
        "panel_id": "seca-development-fixture",
        "version": "0.1",
        "production_ready": False,
        "fixture_only": True,
        "source_note": "Synthetic values for software tests only; replace with licensed/published panel tables before deployment.",
        "features": {
            "phase_angle": {"male": row(7.0, 1.0), "female": row(6.5, 0.9)},
            "ecw_tbw": {"male": row(0.390, 0.025), "female": row(0.400, 0.025)},
            "ffmi": {"male": row(19.0, 3.0), "female": row(16.0, 2.5)},
            "skeletal_muscle_mass": {
                "male": row(35.0, 8.0),
                "female": row(25.0, 6.0),
            },
            "visceral_fat": {"male": row(10.0, 6.0), "female": row(8.0, 5.0)},
        },
    }
    return data


def default_development_panel() -> ReferencePanel:
    """Return a synthetic fixture so the API can be run before a panel is supplied."""

    data = _default_development_panel_data()
    panel = ReferencePanel.from_mapping(data)
    # This is a canonical content digest, not a downloaded source-file hash.
    # Keeping it non-null makes reports/reconciliation identity-stable while
    # fixture_only remains an independent hard production gate.
    return replace(panel, source_sha256=_canonical_panel_sha256(data))
