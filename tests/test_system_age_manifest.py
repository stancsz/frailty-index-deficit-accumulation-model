from __future__ import annotations

import json
import importlib.util
from pathlib import Path


def _validator():
    path = Path(__file__).parents[1] / "scripts" / "validate_system_age_manifest.py"
    spec = importlib.util.spec_from_file_location("validate_system_age_manifest", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_system_age_manifest_template_is_explicitly_non_approving() -> None:
    path = (
        Path(__file__).parents[1] / "docs" / "SYSTEM_AGE_MODEL_MANIFEST_TEMPLATE.json"
    )
    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["manifest_version"] == "1"
    assert data["status"] == "template"
    assert data["system"] == "musculoskeletal"
    for key in (
        "construct",
        "target",
        "measurement_protocol",
        "measurements",
        "missingness",
        "reference_panel",
        "model",
        "uncertainty",
        "age_output",
        "validation",
        "subgroup_support",
        "approval",
    ):
        assert key in data

    assert data["age_output"]["numeric_allowed"] is False
    assert data["age_output"]["point_estimate"] is None
    assert data["age_output"]["interval"] is None
    assert data["uncertainty"]["validated"] is False
    assert data["approval"]["status"] == "not_submitted"
    assert data["approval"]["production_ready"] is False
    assert data["construct"]["not_a_diagnosis"] is True
    assert data["construct"]["not_a_lifespan_or_treatment_effect_estimate"] is True

    measurements = data["measurements"]
    assert measurements
    assert len({item["name"] for item in measurements}) == len(measurements)
    assert all(item["required"] is True for item in measurements)
    assert all(item["unit"] and item["modality"] for item in measurements)
    assert _validator().validate_manifest(path) == []


def test_system_age_manifest_rejects_numeric_or_production_flags(tmp_path) -> None:
    path = (
        Path(__file__).parents[1] / "docs" / "SYSTEM_AGE_MODEL_MANIFEST_TEMPLATE.json"
    )
    data = json.loads(path.read_text(encoding="utf-8"))
    data["age_output"]["numeric_allowed"] = True
    data["approval"]["production_ready"] = True
    invalid_path = tmp_path / "invalid-system-age-manifest.json"
    invalid_path.write_text(json.dumps(data), encoding="utf-8")

    failures = _validator().validate_manifest(invalid_path)

    assert "age_output.numeric_allowed must be false" in failures
    assert "approval.production_ready must be false" in failures
