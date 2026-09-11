"""Validate the non-approving IR4 public-data manifest shape."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read manifest: {exc}"]

    required = {
        "schema_version",
        "manifest_version",
        "status",
        "protocol_id",
        "research_boundary",
        "population",
        "construct",
        "access",
        "source_files",
        "variables",
        "survey_design",
        "planned_analysis",
        "review",
    }
    errors.extend(
        f"missing top-level field: {name}" for name in sorted(required - payload.keys())
    )
    if payload.get("status") != "planning_unpopulated":
        errors.append("manifest status must remain planning_unpopulated")
    boundary = payload.get("research_boundary", {})
    for field in (
        "clinical_use",
        "patient_facing_use",
        "numeric_system_age_authorized",
        "model_fitting_authorized",
    ):
        if boundary.get(field) is not False:
            errors.append(f"research boundary must keep {field}=false")
    if boundary.get("e005_status") != "blocked":
        errors.append("research boundary must keep e005_status=blocked")
    construct = payload.get("construct", {})
    for field in ("id", "target", "formula"):
        if not construct.get(field):
            errors.append(f"construct is missing {field}")
    if construct.get("numeric_age_equivalent") is not None:
        errors.append("construct numeric_age_equivalent must be null")
    sources = payload.get("source_files", [])
    if not isinstance(sources, list) or not sources:
        errors.append("source_files must be a non-empty list")
    else:
        for index, source in enumerate(sources):
            for field in (
                "id",
                "role",
                "filename",
                "cycle",
                "data_url",
                "documentation_url",
                "sha256",
                "retrieved_at",
            ):
                if field not in source:
                    errors.append(f"source_files[{index}] is missing {field}")
            if source.get("sha256") is not None:
                errors.append(
                    f"source_files[{index}] sha256 must remain null until retrieval"
                )
            if source.get("retrieved_at") is not None:
                errors.append(
                    f"source_files[{index}] retrieved_at must remain null until retrieval"
                )
    variables = payload.get("variables", {})
    if not isinstance(variables, dict) or not variables:
        errors.append("variables must be a non-empty object")
    else:
        for name, variable in variables.items():
            for field in ("name", "source", "unit", "sentinels", "sentinel_status"):
                if field not in variable:
                    errors.append(f"variables.{name} is missing {field}")
    design = payload.get("survey_design", {})
    if (
        not design.get("weight_name")
        or not design.get("strata_name")
        or not design.get("psu_name")
    ):
        errors.append("survey_design must name planned weight, strata, and PSU fields")
    if design.get("variance_method") is not None:
        errors.append("survey_design variance_method must remain null before review")
    review = payload.get("review", {})
    if review.get("approval_status") != "not_submitted":
        errors.append("review approval_status must remain not_submitted")
    if (
        review.get("clinical_data_reviewer") is not None
        or review.get("statistical_reviewer") is not None
    ):
        errors.append("reviewer identities must remain unset until assigned")
    return errors


def main() -> int:
    path = (
        Path(sys.argv[1])
        if len(sys.argv) == 2
        else Path("docs/IR4_PUBLIC_DATA_MANIFEST_2026-09-10.json")
    )
    errors = validate(path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"IR4 manifest shape passed: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
