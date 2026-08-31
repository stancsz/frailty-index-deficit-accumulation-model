"""Validate the reproducibility shape of a training-manifest JSON file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse


EXPECTED_CYCLES = {"1999-2000", "2001-2002", "2003-2004"}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PLACEHOLDER_SHA = "RECORD_AFTER_DOWNLOAD"
PLACEHOLDER_DATE = "YYYY-MM-DD"


def validate_manifest(path: Path) -> list[str]:
    failures: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return [f"could not read valid JSON: {error}"]
    if not isinstance(data, dict):
        return ["manifest root must be an object"]

    for key in (
        "manifest_version",
        "status",
        "population",
        "sources",
        "linkage",
        "eligibility",
        "measurement_and_derivation",
        "survey_design",
        "training_recipe",
        "split_and_sensitivity",
        "reference_panel",
        "approval",
    ):
        if key not in data:
            failures.append(f"missing top-level field: {key}")
    if data.get("manifest_version") != "1":
        failures.append("manifest_version must be '1'")
    if data.get("status") not in {"template", "frozen"}:
        failures.append("status must be 'template' or 'frozen'")

    sources = data.get("sources")
    if not isinstance(sources, list) or len(sources) != 6:
        failures.append("sources must contain the three BIA and three mortality files")
        sources = []
    source_cycles: set[str] = set()
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            failures.append(f"sources[{index}] must be an object")
            continue
        cycle = source.get("cycle")
        if isinstance(cycle, str):
            source_cycles.add(cycle)
        parsed = urlparse(str(source.get("url", "")))
        if parsed.scheme != "https" or not parsed.netloc:
            failures.append(f"sources[{index}].url must be an https URL")
        sha = source.get("sha256")
        retrieved = source.get("retrieved_at")
        if data.get("status") == "frozen":
            if not isinstance(sha, str) or not SHA256.fullmatch(sha):
                failures.append(
                    f"sources[{index}].sha256 must be a lowercase SHA-256 digest when frozen"
                )
            if not isinstance(retrieved, str) or not ISO_DATE.fullmatch(retrieved):
                failures.append(
                    f"sources[{index}].retrieved_at must be YYYY-MM-DD when frozen"
                )
        elif sha != PLACEHOLDER_SHA or retrieved != PLACEHOLDER_DATE:
            failures.append(
                f"sources[{index}] template placeholders must remain explicit"
            )
    if source_cycles != EXPECTED_CYCLES:
        failures.append("sources must cover exactly the supported NHANES cycles")

    population = data.get("population")
    if (
        not isinstance(population, dict)
        or set(population.get("cycles", [])) != EXPECTED_CYCLES
    ):
        failures.append("population.cycles must match the supported NHANES cycles")
    linkage = data.get("linkage")
    if not isinstance(linkage, dict):
        failures.append("linkage must be an object")
    else:
        for key, expected in (
            ("join_key", "SEQN"),
            ("eligibility_field", "ELIGSTAT"),
            ("vital_status_field", "MORTSTAT"),
            ("duration_source_field", "PERMTH_EXM"),
        ):
            if linkage.get(key) != expected:
                failures.append(f"linkage.{key} must be {expected}")
        if linkage.get("eligible_value") != 1 or linkage.get("event_mapping") != {
            "1": 1,
            "0": 0,
        }:
            failures.append("linkage eligibility and event mapping must be explicit")

    eligibility = data.get("eligibility")
    if not isinstance(eligibility, dict) or eligibility.get(
        "training_anchor_features"
    ) != ["age", "sex", "bmi"]:
        failures.append(
            "eligibility must preserve the age/sex/bmi training anchor contract"
        )
    measurement = data.get("measurement_and_derivation")
    if (
        not isinstance(measurement, dict)
        or not measurement.get("column_map_policy")
        or not measurement.get("missing_value_policy")
    ):
        failures.append("measurement mapping and missing-value policy must be recorded")
    bia_quality = (
        measurement.get("bia_quality", {}) if isinstance(measurement, dict) else {}
    )
    if (
        bia_quality.get("accepted_codes") is not None
        or bia_quality.get("decision_status")
        != "REVIEW_AND_RECORD_CYCLE_SPECIFIC_CODES"
    ):
        failures.append(
            "BIA fit-quality acceptance must remain an explicit review decision"
        )

    recipe = data.get("training_recipe")
    if (
        not isinstance(recipe, dict)
        or recipe.get("model") != "xgboost survival:cox"
        or recipe.get("feature_count") != 36
        or recipe.get("num_boost_round") != 300
    ):
        failures.append(
            "training recipe must identify the guarded 36-column, 300-round survival adapter"
        )
    survey = data.get("survey_design")
    if (
        not isinstance(survey, dict)
        or survey.get("schema_version") != "1"
        or survey.get("weight_kind")
        not in {"case_weight", "replicate", "stratum", "not_provided"}
        or not isinstance(survey.get("strata_field"), (str, type(None)))
        or not isinstance(survey.get("psu_field"), (str, type(None)))
        or not isinstance(survey.get("replicate_pattern"), list)
        or not isinstance(survey.get("design_reviewed"), bool)
        or survey.get("variance_method") != "NOT_IMPLEMENTED_BY_THIS_ADAPTER"
    ):
        failures.append(
            "survey design must use the versioned shape and state that complex-survey variance is not implemented here"
        )

    approval = data.get("approval")
    if (
        not isinstance(approval, dict)
        or approval.get("production_ready") is not False
        or approval.get("status") != "not_submitted"
    ):
        failures.append(
            "template approval state must be explicitly not_submitted and production_ready=false"
        )
    panel = data.get("reference_panel")
    if not isinstance(panel, dict) or panel.get("production_ready") is not False:
        failures.append("reference panel must remain development-only in the template")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    failures = validate_manifest(args.path)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    print(f"training manifest shape passed: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
