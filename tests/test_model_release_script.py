from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from frailty_engine.pipeline import MODEL_VECTOR_FEATURE_NAMES
from frailty_engine.__main__ import sample_payload
from frailty_engine.training import fit_xgb_survival
from frailty_engine.calibration import default_development_panel
from frailty_engine.model import GompertzMapper


def _load_script() -> object:
    path = Path(__file__).parents[1] / "scripts" / "validate_model_release.py"
    spec = importlib.util.spec_from_file_location("validate_model_release", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _panel(production_ready: bool, fixture_only: bool) -> dict[str, object]:
    bands = {
        feature: {
            "male": [{"min_age": 18, "max_age": 120, "mean": 1, "sd": 1}],
            "female": [{"min_age": 18, "max_age": 120, "mean": 1, "sd": 1}],
        }
        for feature in (
            "phase_angle",
            "ecw_tbw",
            "ffmi",
            "skeletal_muscle_mass",
            "visceral_fat",
        )
    }
    return {
        "panel_id": "release-panel",
        "version": "1",
        "production_ready": production_ready,
        "fixture_only": fixture_only,
        "source_note": "test panel",
        "features": bands,
    }


def test_model_release_preflight_binds_panel_and_keeps_clinical_gate_separate(
    tmp_path: Path,
) -> None:
    pytest.importorskip("xgboost")
    base = dict(sample_payload()["measurements"])
    rows = []
    for number in range(6):
        row = dict(base)
        row.update(
            {
                "patient_id": f"preflight-{number}",
                "duration": 3.0 + number,
                "event": int(number % 2 == 0),
                "age": 40 + number * 5,
                "sample_weight": float(number + 1),
            }
        )
        rows.append(row)
    model = fit_xgb_survival(
        rows, mapper=GompertzMapper(baseline_scale=0.00012, growth_rate=0.075)
    )
    model_path = model.save_model(tmp_path / "model.json")
    panel_path = tmp_path / "panel.json"
    panel_path.write_text(
        json.dumps(_panel(production_ready=False, fixture_only=True)), encoding="utf-8"
    )
    approval_path = tmp_path / "approval.json"
    approval_path.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "model_id": model.model_id,
                "artifact_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
                "feature_names": list(MODEL_VECTOR_FEATURE_NAMES),
                "reference_panel_id": "release-panel",
                "reference_panel_sha256": hashlib.sha256(
                    panel_path.read_bytes()
                ).hexdigest(),
                "uncertainty_method": "held_out_cohort_bootstrap",
                "log_hazard_se": 0.11,
                "production_ready": True,
                "uncertainty_validated": True,
                "approved_by": "test-review-board",
                "approved_at": "2026-08-27",
                "evidence_refs": ["E-005/test-approval-record"],
            }
        ),
        encoding="utf-8",
    )
    module = _load_script()
    blocked = module.validate_model_release(model_path, panel_path, approval_path)
    assert blocked["software_gate"] == "blocked"
    assert blocked["approval"]["artifact_binding_valid"] is True
    assert blocked["approval"]["reference_panel_binding_valid"] is True
    assert any("fixture_only" in item for item in blocked["blockers"])
    assert blocked["clinical_status"] == (
        "requires_e005_external_validation_and_clinical_review"
    )
    assert (
        module.main(
            [
                "--model",
                str(model_path),
                "--panel",
                str(panel_path),
                "--approval",
                str(approval_path),
            ]
        )
        == 2
    )

    panel_path.write_text(
        json.dumps(_panel(production_ready=True, fixture_only=False)), encoding="utf-8"
    )
    drifted = module.validate_model_release(model_path, panel_path, approval_path)
    assert drifted["software_gate"] == "blocked"
    assert drifted["approval"]["reference_panel_binding_valid"] is False

    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    approval["reference_panel_sha256"] = hashlib.sha256(
        panel_path.read_bytes()
    ).hexdigest()
    approval_path.write_text(json.dumps(approval), encoding="utf-8")
    ready = module.validate_model_release(model_path, panel_path, approval_path)
    assert ready["software_gate"] == "ready"
    assert ready["model"]["feature_count"] == 36
    assert ready["model"]["mapper_source"] == "supplied"
    assert ready["approval"]["reference_panel_binding_valid"] is True
    assert str(tmp_path) not in json.dumps(ready)
    assert (
        module.main(
            [
                "--model",
                str(model_path),
                "--panel",
                str(panel_path),
                "--approval",
                str(approval_path),
            ]
        )
        == 0
    )

    model.training_config.pop("survey_design")
    legacy_path = model.save_model(tmp_path / "missing-survey-design.json")
    legacy_approval = dict(approval)
    legacy_approval["artifact_sha256"] = hashlib.sha256(
        legacy_path.read_bytes()
    ).hexdigest()
    legacy_approval_path = tmp_path / "missing-survey-design-approval.json"
    legacy_approval_path.write_text(json.dumps(legacy_approval), encoding="utf-8")
    missing_design = module.validate_model_release(
        legacy_path, panel_path, legacy_approval_path
    )
    assert missing_design["software_gate"] == "blocked"
    assert any(
        "missing an explicit survey_design" in item
        for item in missing_design["blockers"]
    )


def test_model_release_preflight_rejects_promoted_default_fixture(
    tmp_path: Path,
) -> None:
    pytest.importorskip("xgboost")
    base = dict(sample_payload()["measurements"])
    rows = []
    for number in range(6):
        row = dict(base)
        row.update(
            {
                "patient_id": f"fixture-preflight-{number}",
                "duration": 3.0 + number,
                "event": int(number % 2 == 0),
                "age": 40 + number * 5,
            }
        )
        rows.append(row)
    model = fit_xgb_survival(rows)
    model_path = model.save_model(tmp_path / "model.json")

    source_panel = default_development_panel()
    features = {
        feature: {
            sex: [
                {
                    "min_age": band.min_age,
                    "max_age": band.max_age,
                    "mean": band.mean,
                    "sd": band.standard_deviation,
                }
                for band in source_panel.bands[feature][sex]
            ]
            for sex in ("male", "female")
        }
        for feature in source_panel.bands
    }
    panel_path = tmp_path / "promoted-fixture.json"
    panel_path.write_text(
        json.dumps(
            {
                "panel_id": source_panel.panel_id,
                "version": source_panel.version,
                "production_ready": True,
                "fixture_only": False,
                "source_note": "test promoted fixture",
                "features": features,
            }
        ),
        encoding="utf-8",
    )
    approval_path = tmp_path / "approval.json"
    approval_path.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "model_id": model.model_id,
                "artifact_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
                "feature_names": list(MODEL_VECTOR_FEATURE_NAMES),
                "reference_panel_id": source_panel.panel_id,
                "reference_panel_sha256": hashlib.sha256(
                    panel_path.read_bytes()
                ).hexdigest(),
                "uncertainty_method": "held_out_cohort_bootstrap",
                "log_hazard_se": 0.11,
                "production_ready": True,
                "uncertainty_validated": True,
                "approved_by": "test-review-board",
                "approved_at": "2026-08-27",
                "evidence_refs": ["E-005/test-approval-record"],
            }
        ),
        encoding="utf-8",
    )

    module = _load_script()
    blocked = module.validate_model_release(model_path, panel_path, approval_path)
    assert blocked["software_gate"] == "blocked"
    assert any(
        "shipped development fixture bands" in item for item in blocked["blockers"]
    )


def test_model_release_preflight_rejects_in_sample_mapper_for_production(
    tmp_path: Path,
) -> None:
    pytest.importorskip("xgboost")
    base = dict(sample_payload()["measurements"])
    rows = []
    for number in range(6):
        row = dict(base)
        row.update(
            {
                "patient_id": f"in-sample-mapper-{number}",
                "duration": 3.0 + number,
                "event": int(number % 2 == 0),
                "age": 40 + number * 5,
            }
        )
        rows.append(row)
    model = fit_xgb_survival(rows)
    model_path = model.save_model(tmp_path / "model.json")
    panel_path = tmp_path / "panel.json"
    panel_path.write_text(
        json.dumps(_panel(production_ready=True, fixture_only=False)), encoding="utf-8"
    )
    approval_path = tmp_path / "approval.json"
    approval_path.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "model_id": model.model_id,
                "artifact_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
                "feature_names": list(MODEL_VECTOR_FEATURE_NAMES),
                "reference_panel_id": "release-panel",
                "reference_panel_sha256": hashlib.sha256(
                    panel_path.read_bytes()
                ).hexdigest(),
                "uncertainty_method": "held_out_cohort_bootstrap",
                "log_hazard_se": 0.11,
                "production_ready": True,
                "uncertainty_validated": True,
                "approved_by": "test-review-board",
                "approved_at": "2026-08-27",
                "evidence_refs": ["E-005/test-approval-record"],
            }
        ),
        encoding="utf-8",
    )

    module = _load_script()
    blocked = module.validate_model_release(model_path, panel_path, approval_path)
    assert blocked["software_gate"] == "blocked"
    assert blocked["model"]["mapper_source"] == "training_cohort_in_sample"
    assert any(
        "explicit supplied Gompertz mapper provenance" in item
        for item in blocked["blockers"]
    )

    model._model.set_attr(frailty_training_config=None)
    model.training_config = None
    missing_config_model_path = tmp_path / "missing-mapper-config-model.json"
    model.save_model(missing_config_model_path)
    missing_config_approval = json.loads(approval_path.read_text(encoding="utf-8"))
    missing_config_approval["artifact_sha256"] = hashlib.sha256(
        missing_config_model_path.read_bytes()
    ).hexdigest()
    missing_config_approval_path = tmp_path / "missing-mapper-config-approval.json"
    missing_config_approval_path.write_text(
        json.dumps(missing_config_approval), encoding="utf-8"
    )
    missing = module.validate_model_release(
        missing_config_model_path,
        panel_path,
        missing_config_approval_path,
    )
    assert missing["software_gate"] == "blocked"
    assert missing["model"]["mapper_source"] == "unknown"
    assert any(
        "explicit supplied Gompertz mapper provenance" in item
        for item in missing["blockers"]
    )
