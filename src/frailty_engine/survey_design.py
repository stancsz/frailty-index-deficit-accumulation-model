"""Typed survey-design metadata shared by training and validation adapters.

The current XGBoost adapter can apply positive case weights, but it does not
implement complex-survey variance estimation, strata/PSU variance, or
replicate-weight estimation.  Keeping that boundary in a versioned value
object prevents a descriptive declaration from being mistaken for a complete
survey analysis.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping


SURVEY_DESIGN_SCHEMA_VERSION = "1"
SurveyWeightKind = Literal["case_weight", "replicate", "stratum", "not_provided"]
_WEIGHT_KINDS = {"case_weight", "replicate", "stratum", "not_provided"}
_FIELDS = {
    "schema_version",
    "weight_name",
    "weight_kind",
    "strata",
    "psu",
    "replicate_pattern",
}


def _optional_name(value: Any, *, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"survey design {field_name} must be a non-empty string")
    return value.strip()


def _names(values: Any, *, field_name: str) -> tuple[str, ...]:
    if not isinstance(values, (list, tuple)):
        raise ValueError(f"survey design {field_name} must be a list of strings")
    normalized = tuple(_optional_name(value, field_name=field_name) for value in values)
    if any(value is None for value in normalized):
        raise ValueError(f"survey design {field_name} must contain only strings")
    names = tuple(value for value in normalized if value is not None)
    if len(set(names)) != len(names):
        raise ValueError(f"survey design {field_name} values must be unique")
    return names


@dataclass(frozen=True)
class SurveyDesign:
    """A strict declaration of how survey-related columns should be read.

    ``weighting_applied`` is deliberately not stored here: it is an operation
    result owned by the training or validation report.  ``replicate`` and
    ``stratum`` are accepted as declarations for protocol planning, but the
    current adapter must not pass them as XGBoost case weights.
    """

    schema_version: Literal["1"] = SURVEY_DESIGN_SCHEMA_VERSION
    weight_name: str | None = None
    weight_kind: SurveyWeightKind = "not_provided"
    strata: tuple[str, ...] = ()
    psu: str | None = None
    replicate_pattern: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.schema_version != SURVEY_DESIGN_SCHEMA_VERSION:
            raise ValueError("survey design has an unsupported schema version")
        if (
            not isinstance(self.weight_kind, str)
            or self.weight_kind not in _WEIGHT_KINDS
        ):
            raise ValueError("survey design weight_kind is invalid")
        weight_name = _optional_name(self.weight_name, field_name="weight_name")
        psu = _optional_name(self.psu, field_name="psu")
        strata = _names(self.strata, field_name="strata")
        replicate_pattern = _names(
            self.replicate_pattern, field_name="replicate_pattern"
        )
        object.__setattr__(self, "weight_name", weight_name)
        object.__setattr__(self, "psu", psu)
        object.__setattr__(self, "strata", strata)
        object.__setattr__(self, "replicate_pattern", replicate_pattern)

        if self.weight_kind == "not_provided":
            if (
                weight_name is not None
                or strata
                or psu is not None
                or replicate_pattern
            ):
                raise ValueError(
                    "survey design not_provided cannot declare weight, strata, PSU, "
                    "or replicate fields"
                )
        elif weight_name is None:
            raise ValueError(f"survey design {self.weight_kind} requires weight_name")
        elif self.weight_kind == "replicate" and not replicate_pattern:
            raise ValueError("survey design replicate requires replicate_pattern")
        elif self.weight_kind == "stratum" and (not strata or psu is None):
            raise ValueError("survey design stratum requires strata and psu")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "SurveyDesign":
        """Parse the exact JSON shape persisted in an artifact or report."""

        if not isinstance(value, Mapping):
            raise ValueError("survey design metadata must be an object")
        if set(value) != _FIELDS:
            raise ValueError("survey design metadata has an invalid field set")
        if value["schema_version"] != SURVEY_DESIGN_SCHEMA_VERSION:
            raise ValueError("survey design has an unsupported schema version")
        weight_kind = value["weight_kind"]
        if not isinstance(weight_kind, str) or weight_kind not in _WEIGHT_KINDS:
            raise ValueError("survey design weight_kind is invalid")
        strata = _names(value["strata"], field_name="strata")
        replicate_pattern = _names(
            value["replicate_pattern"], field_name="replicate_pattern"
        )
        return cls(
            schema_version="1",
            weight_name=_optional_name(value["weight_name"], field_name="weight_name"),
            weight_kind=weight_kind,
            strata=strata,
            psu=_optional_name(value["psu"], field_name="psu"),
            replicate_pattern=replicate_pattern,
        )

    @classmethod
    def for_rows(cls, *, has_sample_weight: bool) -> "SurveyDesign":
        """Infer the narrow adapter declaration when callers omit metadata."""

        if has_sample_weight:
            return cls(weight_name="sample_weight", weight_kind="case_weight")
        return cls()

    def to_mapping(self) -> dict[str, Any]:
        """Return the stable JSON representation without operational flags."""

        return {
            "schema_version": self.schema_version,
            "weight_name": self.weight_name,
            "weight_kind": self.weight_kind,
            "strata": list(self.strata),
            "psu": self.psu,
            "replicate_pattern": list(self.replicate_pattern),
        }

    def to_metadata(
        self, *, weighting_applied: bool, design_reviewed: bool = False
    ) -> dict[str, Any]:
        """Return a report-safe declaration plus explicit application flags."""

        return {
            **self.to_mapping(),
            "weighting_applied": bool(weighting_applied),
            "design_reviewed": bool(design_reviewed),
        }


def resolve_survey_design(
    design: SurveyDesign | None, *, has_sample_weight: bool
) -> SurveyDesign:
    """Resolve omitted metadata and reject unsafe weight/design contradictions."""

    resolved = (
        SurveyDesign.for_rows(has_sample_weight=has_sample_weight)
        if design is None
        else design
    )
    if not isinstance(resolved, SurveyDesign):
        raise TypeError("survey_design must be a SurveyDesign instance")
    if has_sample_weight and resolved.weight_kind != "case_weight":
        raise ValueError(
            "raw sample_weight values require survey_design weight_kind=case_weight"
        )
    if not has_sample_weight and resolved.weight_kind == "case_weight":
        raise ValueError(
            "survey_design weight_kind=case_weight requires raw sample_weight values"
        )
    return resolved
