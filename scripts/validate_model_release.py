"""Validate a model, reference panel, and approval sidecar as one release unit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from frailty_engine.calibration import (
    ReferencePanel,
    is_development_fixture_content,
)
from frailty_engine.exceptions import ModelUnavailableError
from frailty_engine.model import XGBSurvivalModel
from frailty_engine.pipeline import MODEL_VECTOR_FEATURE_NAMES
from frailty_engine.survey_design import SurveyDesign


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _binding_is_valid(model: XGBSurvivalModel, panel: ReferencePanel) -> bool:
    return bool(
        model.approval_manifest_path
        and model.approved_reference_panel_id == panel.panel_id
        and model.approved_reference_panel_sha256
        and panel.source_sha256
        and model.approved_reference_panel_sha256 == panel.source_sha256
    )


def validate_model_release(
    model_path: str | Path,
    panel_path: str | Path,
    approval_path: str | Path,
) -> dict[str, Any]:
    """Return a safe, deterministic software-gate report for a release unit.

    Loading verifies the artifact bytes, persisted feature manifest, model id,
    and sidecar artifact binding. This report adds the panel-file binding and
    production flags. It never turns a passing software gate into clinical
    approval; E-005 remains a separate external evidence obligation.
    """

    artifact = Path(model_path)
    panel_file = Path(panel_path)
    approval = Path(approval_path)
    model = XGBSurvivalModel.load_model(
        artifact,
        MODEL_VECTOR_FEATURE_NAMES,
        approval_manifest=approval,
    )
    panel = ReferencePanel.from_json(panel_file)
    binding_valid = _binding_is_valid(model, panel)
    blockers: list[str] = []
    if not model.production_ready:
        blockers.append(
            "model approval sidecar does not mark the model production_ready"
        )
    if not model.uncertainty_validated:
        blockers.append("model approval sidecar does not mark uncertainty as validated")
    mapper_source = (
        model.training_config.get("mapper_source")
        if model.training_config is not None
        else None
    )
    if model.production_ready and mapper_source != "supplied":
        blockers.append(
            "production-ready model requires explicit supplied Gompertz mapper provenance"
        )
    training_config = model.training_config or {}
    if model.production_ready:
        if "survey_design" not in training_config:
            blockers.append(
                "production-ready model is missing an explicit survey_design declaration"
            )
        else:
            try:
                survey_design = SurveyDesign.from_mapping(
                    training_config["survey_design"]
                )
            except (TypeError, ValueError):
                blockers.append(
                    "production-ready model has invalid survey_design metadata"
                )
            else:
                if survey_design.weight_kind == "not_provided":
                    blockers.append(
                        "production-ready model cannot use survey_design.weight_kind=not_provided"
                    )
                elif survey_design.weight_kind in {"replicate", "stratum"}:
                    blockers.append(
                        "production-ready model declares a survey-design weight kind "
                        "unsupported by this adapter"
                    )
    if not panel.production_ready:
        blockers.append("reference panel is not marked production_ready")
    if panel.fixture_only:
        blockers.append("reference panel is marked fixture_only")
    elif panel.production_ready and is_development_fixture_content(panel):
        blockers.append(
            "reference panel contains the shipped development fixture bands"
        )
    if not binding_valid:
        blockers.append(
            "approval sidecar reference-panel id or SHA-256 does not match the panel file"
        )
    return {
        "schema_version": "1",
        "report_type": "healthspan-model-release-preflight",
        "software_gate": "ready" if not blockers else "blocked",
        "clinical_status": "requires_e005_external_validation_and_clinical_review",
        "model": {
            "model_id": model.model_id,
            "artifact_sha256": model.artifact_sha256,
            "feature_count": len(model.feature_names),
            "production_ready": model.production_ready,
            "uncertainty_validated": model.uncertainty_validated,
            "uncertainty_method": model.uncertainty_method,
            "mapper_source": (
                mapper_source if isinstance(mapper_source, str) else "unknown"
            ),
            "survey_design": (
                training_config.get("survey_design")
                if isinstance(training_config.get("survey_design"), dict)
                else None
            ),
        },
        "reference_panel": {
            "panel_id": panel.panel_id,
            "version": panel.version,
            "source_sha256": panel.source_sha256,
            "production_ready": panel.production_ready,
            "fixture_only": panel.fixture_only,
        },
        "approval": {
            "manifest_sha256": _sha256_file(approval),
            "artifact_binding_valid": True,
            "reference_panel_binding_valid": binding_valid,
        },
        "blockers": blockers,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate one XGBoost artifact, reference-panel file, and approval "
            "sidecar as a release unit."
        )
    )
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--panel", required=True, type=Path)
    parser.add_argument("--approval", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        report = validate_model_release(args.model, args.panel, args.approval)
    except (ModelUnavailableError, OSError, TypeError, ValueError, KeyError) as error:
        print(f"model release preflight failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["software_gate"] == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
