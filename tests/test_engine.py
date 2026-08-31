from __future__ import annotations

from io import StringIO
import subprocess
import json
from dataclasses import replace
import hashlib
import math
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
import numpy as np

from frailty_engine.calibration import (
    ReferencePanel,
    default_development_panel,
    is_development_fixture_content,
    panel_readiness,
)
from frailty_engine.exceptions import (
    InsufficientDataError,
    ModelUnavailableError,
    PredictionFailure,
    ValidationError,
)
from frailty_engine.derived import calculate_fib_4
from frailty_engine.features import FI_FEATURES, FEATURE_NAMES, parse_patient_data
from frailty_engine.fi import CUTOFF_SOURCES, calculate_fi, denominator_strength
from frailty_engine.model import (
    DevelopmentPredictor,
    GompertzMapper,
    ModelPrediction,
    XGBSurvivalModel,
)
from frailty_engine.mvv import evaluate_mvv
from frailty_engine.intake_overlay import (
    OVERLAY_FORMAT,
    merge_with_seca,
    overlay_mvv_missing,
)
from frailty_engine.pipeline import assess, model_vector
from frailty_engine.pipeline import MODEL_VECTOR_FEATURE_NAMES
from frailty_engine.progress import build_progress_report
from frailty_engine.training import (
    build_survival_frame,
    fit_xgb_survival,
    split_survival_rows,
)
from frailty_engine.validation import validate_external_cohort, write_calibration_plots
from frailty_engine.__main__ import main, sample_payload
from frailty_engine.api import app, create_app
import frailty_engine.api as api_module
from frailty_engine.schemas import (
    AssessmentComparisonResponse,
    AssessmentResponse,
    WellnessRangeResponse,
)
from frailty_engine.nhanes import (
    NHANESColumnMap,
    build_nhanes_rows,
    cycle_resource,
    read_public_use_mortality,
)
from frailty_engine.seca import read_seca_tableview_csv
from frailty_engine.survey_design import SurveyDesign
from frailty_engine.release_receipt import (
    ReceiptError,
    health_to_receipt,
    receipt_matches_health,
)
from frailty_engine.release_provenance import (
    provenance_is_ready_for_strict_admission,
    provenance_is_well_formed,
    runtime_provenance,
)


def _non_fixture_panel(
    *,
    panel_id: str = "test-approved-panel",
    production_ready: bool,
    source_sha256: str | None,
) -> ReferencePanel:
    features = {
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
    panel = ReferencePanel.from_mapping(
        {
            "panel_id": panel_id,
            "version": "test",
            "production_ready": production_ready,
            "fixture_only": False,
            "source_note": "test-approved-panel",
            "features": features,
        }
    )
    return replace(panel, source_sha256=source_sha256)


def test_feature_matrix_has_exactly_35_canonical_variables() -> None:
    assert len(FEATURE_NAMES) == 35
    assert len(set(FEATURE_NAMES)) == 35


def test_every_fi_feature_has_a_visible_cutoff_or_coding_source_reference() -> None:
    assert set(FI_FEATURES).issubset(CUTOFF_SOURCES)


def test_api_openapi_declares_the_public_assessment_response_model() -> None:
    operation = app.openapi()["paths"]["/v1/assessments"]["post"]
    assert operation["responses"]["200"]["content"]["application/json"]["schema"][
        "$ref"
    ].endswith("/AssessmentResponse")
    assert operation["requestBody"]["content"]["application/json"]["schema"][
        "$ref"
    ].endswith("/AssessmentRequest")
    comparison_operation = app.openapi()["paths"]["/v1/assessment-comparisons"]["post"]
    assert comparison_operation["responses"]["200"]["content"]["application/json"][
        "schema"
    ]["$ref"].endswith("/AssessmentComparisonResponse")


def test_metrics_endpoint_is_bounded_and_protected_when_api_key_is_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FRAILTY_API_KEY", "metrics-secret")
    monkeypatch.setenv("FRAILTY_MAX_REQUEST_BYTES", "8")
    client = TestClient(create_app())

    unauthorized = client.get("/metrics")
    assert unauthorized.status_code == 401
    assert unauthorized.json()["error"]["code"] == "AuthenticationRequired"

    oversized = client.post(
        "/v1/assessments",
        headers={"x-api-key": "metrics-secret"},
        content=b"123456789",
    )
    assert oversized.status_code == 413

    health = client.get("/health")
    assert health.status_code == 200
    response = client.get("/metrics", headers={"x-api-key": "metrics-secret"})
    assert response.status_code == 200
    metrics = response.json()
    assert metrics["format"] == "clinical-healthspan-metrics-v1"
    assert metrics["process_local"] is True
    assert metrics["requests_total"] == 3
    assert metrics["responses_by_status_class"]["2xx"] == 1
    assert metrics["responses_by_status_class"]["4xx"] == 2
    assert metrics["duration_ms"]["observed_requests"] == 3
    assert metrics["request_size_rejections"] == 1
    assert not {"path", "method", "request_id", "patient_id"}.intersection(metrics)


def test_metrics_endpoint_remains_aggregate_only_without_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("FRAILTY_API_KEY", raising=False)
    client = TestClient(create_app())

    assert client.get("/health").status_code == 200
    response = client.get("/metrics")

    assert response.status_code == 200
    metrics = response.json()
    assert set(metrics) == {
        "format",
        "process_local",
        "requests_total",
        "responses_by_status_class",
        "duration_ms",
        "request_size_rejections",
    }
    assert metrics["requests_total"] == 1
    assert metrics["responses_by_status_class"]["2xx"] == 1


def test_api_request_envelope_is_typed_and_returns_pii_safe_errors() -> None:
    client = TestClient(create_app())
    missing_measurements = client.post(
        "/v1/assessments", json={"patient_id": "request-envelope-test"}
    )
    assert missing_measurements.status_code == 422
    assert missing_measurements.json()["error"]["code"] == "RequestValidationError"
    assert "measurements" in missing_measurements.json()["error"]["field_errors"]

    extra_field = dict(sample_payload(), unexpected_top_level="do-not-accept")
    response = client.post("/v1/assessments", json=extra_field)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "RequestValidationError"
    assert "unexpected_top_level" in str(response.json())

    for malformed_measurements in ([], "not-a-map"):
        malformed = client.post(
            "/v1/assessments",
            json={
                "patient_id": "request-envelope-test",
                "measurements": malformed_measurements,
            },
        )
        assert malformed.status_code == 422
        assert malformed.json()["error"]["code"] == "RequestValidationError"
        assert "measurements" in malformed.json()["error"]["field_errors"]


def test_api_success_response_matches_the_declared_response_schema() -> None:
    response = TestClient(create_app()).post("/v1/assessments", json=sample_payload())
    assert response.status_code == 200
    parsed = AssessmentResponse.model_validate(response.json())
    assert parsed.wellness_report.ranges
    assert parsed.metrics.biological_age.uncertainty_validated is False
    assert parsed.metrics.biological_age.ci_95 is None
    assert parsed.metrics.biological_age.uncertainty_construction == "none_withheld"
    assert parsed.trajectory.score_ci_95 is None
    assert parsed.trajectory.uncertainty_construction == "none_withheld"
    assert parsed.data_quality.reference_panel_fixture_only is True
    assert len(parsed.data_quality.reference_panel_sha256) == 64
    assert parsed.data_quality.reference_panel_readiness == "development_fixture_only"
    assert parsed.data_quality.fi_denominator_strength in {"low", "moderate", "high"}
    assert (
        parsed.metrics.current_deficit_load_fi_details.denominator_strength
        == parsed.data_quality.fi_denominator_strength
    )
    assert parsed.wellness_report.fi_context.denominator_strength_caveat


def test_assessment_carries_reference_panel_digest_into_typed_quality() -> None:
    panel = replace(default_development_panel(), source_sha256="a" * 64)
    result = assess(sample_payload(), reference_panel=panel)
    assert result["data_quality"]["reference_panel_sha256"] == "a" * 64
    assert (
        result["metrics"]["current_deficit_load_fi_details"]["denominator_strength"]
        == result["data_quality"]["fi_denominator_strength"]
    )


def test_progress_report_compares_reference_status_without_claiming_causality() -> None:
    previous_payload = sample_payload()
    previous_payload["patient_id"] = "progress-test"
    previous_payload["measurements"].update(
        {
            "bmi": 31.2,
            "phase_angle": 4.8,
            "ecw_tbw": 0.46,
            "systolic_bp": 146,
            "diastolic_bp": 92,
        }
    )
    current_payload = sample_payload()
    current_payload["patient_id"] = "progress-test"
    previous = assess(previous_payload)
    current = assess(current_payload)

    report = build_progress_report(
        previous,
        current,
        previous_assessed_at="2026-01-01",
        current_assessed_at="2026-03-01",
    )

    assert report["format"] == "wellness-progress-report-v1"
    assert report["summary"]["moved_into_reference_range"] >= 1
    bmi_change = next(
        item for item in report["range_changes"] if item["feature"] == "bmi"
    )
    assert bmi_change["status_transition"] == "moved_into_range"
    assert bmi_change["value_change"] == "lower"
    assert "measurements" not in json.dumps(report)
    assert report["action_effect_estimated"] is False
    assert report["clinical_or_lifespan_claim"] is False
    assert len(report["model_boundary"]["previous_reference_panel_sha256"]) == 64
    assert len(report["model_boundary"]["current_reference_panel_sha256"]) == 64

    changed_model = json.loads(json.dumps(current))
    changed_model["model_metadata"]["model_id"] = "different-development-model"
    with pytest.raises(ValueError, match="same model_id"):
        build_progress_report(
            previous,
            changed_model,
            previous_assessed_at="2026-01-01",
            current_assessed_at="2026-03-01",
        )


def test_progress_report_rejects_reference_panel_sha256_mismatch() -> None:
    previous_payload = sample_payload()
    previous_payload["patient_id"] = "progress-digest-test"
    current_payload = json.loads(json.dumps(previous_payload))
    panel_a = replace(default_development_panel(), source_sha256="a" * 64)
    panel_b = replace(default_development_panel(), source_sha256="b" * 64)
    previous = assess(previous_payload, reference_panel=panel_a)
    current = assess(current_payload, reference_panel=panel_b)

    with pytest.raises(ValueError, match="same reference_panel_sha256"):
        build_progress_report(
            previous,
            current,
            previous_assessed_at="2026-01-01",
            current_assessed_at="2026-03-01",
        )


def test_progress_report_accepts_null_digest_when_panel_ids_match() -> None:
    payload = sample_payload()
    payload["patient_id"] = "progress-null-digest-test"
    panel = replace(default_development_panel(), source_sha256=None)
    previous = assess(payload, reference_panel=panel)
    current = assess(json.loads(json.dumps(payload)), reference_panel=panel)
    report = build_progress_report(
        previous,
        current,
        previous_assessed_at="2026-01-01",
        current_assessed_at="2026-03-01",
    )
    assert report["model_boundary"]["previous_reference_panel_sha256"] is None
    assert report["model_boundary"]["current_reference_panel_sha256"] is None


def test_reference_panel_readiness_is_explicit_and_conservative() -> None:
    panel = default_development_panel()
    assert panel_readiness(panel) == "development_fixture_only"
    assert panel_readiness(replace(panel, fixture_only=False)) == "loaded_unapproved"
    assert (
        panel_readiness(replace(panel, production_ready=True, fixture_only=False))
        == "loaded_production_ready"
    )


def test_api_rejects_promoted_development_fixture_content(monkeypatch) -> None:
    class ReadyPredictor:
        model_id = "promoted-fixture-test-model"
        production_ready = True
        uncertainty_validated = True
        artifact_sha256 = "c" * 64

    panel = replace(
        default_development_panel(),
        production_ready=True,
        fixture_only=False,
        source_sha256="d" * 64,
    )
    assert is_development_fixture_content(panel) is True
    monkeypatch.setenv("FRAILTY_API_KEY", "promoted-fixture-secret")
    client = TestClient(create_app(predictor=ReadyPredictor(), reference_panel=panel))
    response = client.get("/readyz")
    assert response.status_code == 503
    assert any(
        "shipped development fixture bands" in item
        for item in response.json()["blockers"]
    )


def test_api_comparison_is_typed_and_rejects_different_people() -> None:
    previous = sample_payload()
    previous["patient_id"] = "comparison-api"
    current = json.loads(json.dumps(previous))
    current["assessed_at"] = "2026-03-01"
    request = {
        "previous": {**previous, "assessed_at": "2026-01-01"},
        "current": current,
    }
    client = TestClient(create_app())
    response = client.post("/v1/assessment-comparisons", json=request)
    assert response.status_code == 200
    parsed = AssessmentComparisonResponse.model_validate(response.json())
    assert parsed.format == "wellness-progress-report-v1"
    assert parsed.comparison_basis == "same_model_and_reference_panel"
    assert parsed.action_effect_estimated is False
    assert parsed.current_focus_areas == []
    assert "measurements" not in json.dumps(response.json())

    different_person = json.loads(json.dumps(request))
    different_person["current"]["patient_id"] = "another-person"
    mismatch = client.post("/v1/assessment-comparisons", json=different_person)
    assert mismatch.status_code == 422
    assert mismatch.json()["error"]["code"] == "ValidationError"

    non_chronological = json.loads(json.dumps(request))
    non_chronological["current"]["assessed_at"] = "2025-12-31"
    chronology_error = client.post("/v1/assessment-comparisons", json=non_chronological)
    assert chronology_error.status_code == 422
    assert chronology_error.json()["error"]["code"] == "ValidationError"


def test_api_app_factory_injects_runtime_model_and_panel_into_health_metadata() -> None:
    class RuntimePredictor:
        model_id = "runtime-test-model"
        production_ready = False

    response = TestClient(
        create_app(
            predictor=RuntimePredictor(), reference_panel=default_development_panel()
        )
    ).get("/health")
    assert response.status_code == 200
    assert response.json()["model_id"] == "runtime-test-model"
    assert response.json()["reference_panel_id"] == "seca-development-fixture"
    assert response.json()["reference_panel_fixture_only"] is True
    assert response.json()["operational_controls"]["max_request_bytes"] == 65536
    assert response.json()["readiness"]["status"] == "not_ready"
    assert any(
        "development fixture" in blocker
        for blocker in response.json()["readiness"]["blockers"]
    )
    assert (
        TestClient(
            create_app(
                predictor=RuntimePredictor(),
                reference_panel=default_development_panel(),
            )
        )
        .get("/readyz")
        .status_code
        == 503
    )


def test_health_exposes_non_secret_runtime_release_identity() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["service_version"] == "0.1.0"
    assert body["model_artifact_sha256"] is None
    assert len(body["reference_panel_sha256"]) == 64
    assert body["reference_panel_readiness"] == "development_fixture_only"
    provenance = body["runtime_provenance"]
    assert len(provenance["dependency_set_sha256"]) == 64
    assert len(provenance["configuration_sha256"]) == 64
    assert set(provenance["python_runtime"]) == {
        "implementation",
        "version",
        "cache_tag",
    }
    assert "api_key" not in json.dumps(provenance).lower()
    fingerprint = body["deployment_fingerprint"]
    assert len(fingerprint) == 64
    assert all(character in "0123456789abcdef" for character in fingerprint)
    assert "api_key" not in fingerprint

    readiness = client.get("/readyz")
    assert readiness.status_code == 503
    assert readiness.json()["deployment_fingerprint"] == fingerprint

    class ArtifactPredictor:
        model_id = "artifact-test-model"
        artifact_sha256 = "b" * 64
        production_ready = False
        uncertainty_validated = False

    hashed_panel = replace(default_development_panel(), source_sha256="a" * 64)
    hashed_body = (
        TestClient(
            create_app(predictor=ArtifactPredictor(), reference_panel=hashed_panel)
        )
        .get("/health")
        .json()
    )
    assert hashed_body["model_artifact_sha256"] == "b" * 64
    assert hashed_body["reference_panel_sha256"] == "a" * 64
    assert hashed_body["deployment_fingerprint"] != fingerprint

    class MutableReadyPredictor:
        model_id = "mutable-ready-test-model"
        production_ready = True
        uncertainty_validated = True

    mutable_panel = default_development_panel()
    mutable_client = TestClient(
        create_app(predictor=MutableReadyPredictor(), reference_panel=mutable_panel)
    )
    object.__setattr__(mutable_panel, "production_ready", True)
    mutated_health = mutable_client.get("/health").json()
    assert mutated_health["readiness"]["status"] == "not_ready"
    assert any(
        "development fixture" in blocker
        for blocker in mutated_health["readiness"]["blockers"]
    )


def test_runtime_provenance_is_deterministic_and_secret_safe() -> None:
    environment = {
        "FRAILTY_MAX_REQUEST_BYTES": "65536",
        "FRAILTY_API_KEY": "runtime-secret",
    }
    first = runtime_provenance(environment=environment)
    second = runtime_provenance(environment=dict(environment))
    assert first == second
    assert (
        first["configuration_sha256"]
        != runtime_provenance(
            environment={**environment, "FRAILTY_MAX_REQUEST_BYTES": "65537"}
        )["configuration_sha256"]
    )
    assert "runtime-secret" not in json.dumps(first)
    assert (
        first["package_tree_sha256"] is None or len(first["package_tree_sha256"]) == 64
    )


def test_runtime_provenance_well_formed_vs_strict_admission() -> None:
    base = {
        "package_tree_sha256": "a" * 64,
        "dependency_set_sha256": "b" * 64,
        "configuration_sha256": "c" * 64,
        "python_runtime": {
            "implementation": "cpython",
            "version": "3.13.11",
            "cache_tag": "cpython-313",
        },
    }
    source_tree = {**base, "package_installation_mode": "source_tree"}
    installed = {**base, "package_installation_mode": "installed_distribution"}

    assert provenance_is_well_formed(source_tree) is True
    assert provenance_is_ready_for_strict_admission(source_tree) is False
    assert provenance_is_well_formed(installed) is True
    assert provenance_is_ready_for_strict_admission(installed) is True


def test_api_responses_have_restrictive_cache_and_browser_headers(monkeypatch) -> None:
    client = TestClient(create_app())
    responses = [client.get("/health"), client.post("/v1/assessments", json={})]

    monkeypatch.setenv("FRAILTY_API_KEY", "test-key")
    responses.append(TestClient(create_app()).post("/v1/assessments", json={}))

    monkeypatch.delenv("FRAILTY_API_KEY")
    monkeypatch.setenv("FRAILTY_MAX_REQUEST_BYTES", "1")
    responses.append(TestClient(create_app()).post("/v1/assessments", json={}))

    expected = {
        "cache-control": "no-store",
        "content-security-policy": "default-src 'none'; frame-ancestors 'none'",
        "permissions-policy": "camera=(), geolocation=(), microphone=()",
        "referrer-policy": "no-referrer",
        "x-content-type-options": "nosniff",
        "x-frame-options": "DENY",
    }
    assert [response.status_code for response in responses] == [200, 422, 401, 413]
    for response in responses:
        assert response.headers["x-request-id"]
        for name, value in expected.items():
            assert response.headers[name] == value


def test_runtime_release_receipt_is_allowlisted_and_reconcilable() -> None:
    health = TestClient(create_app()).get("/health").json()
    receipt = health_to_receipt(health)
    serialized = json.dumps(receipt, sort_keys=True)

    assert receipt["receipt_type"] == "clinical-healthspan-runtime"
    assert receipt["deployment_fingerprint"] == health["deployment_fingerprint"]
    assert receipt_matches_health(receipt, health)
    assert "api_key" not in serialized
    assert "patient_id" not in serialized
    assert "request_body" not in serialized

    health_with_sensitive_extras = {
        **health,
        "api_key": "do-not-persist",
        "patient_id": "patient-do-not-persist",
        "request_body": {"measurements": {"age": 45}},
    }
    safe_receipt = health_to_receipt(health_with_sensitive_extras)
    safe_serialized = json.dumps(safe_receipt, sort_keys=True)
    assert "do-not-persist" not in safe_serialized
    assert "patient-do-not-persist" not in safe_serialized
    assert "request_body" not in safe_serialized

    tampered = json.loads(serialized)
    tampered["deployment_fingerprint"] = "0" * 64
    assert not receipt_matches_health(tampered, health)

    nested_drift = json.loads(json.dumps(health))
    nested_drift["operational_controls"]["new_schema_field"] = False
    assert not receipt_matches_health(receipt, nested_drift)
    provenance_drift = json.loads(json.dumps(health))
    provenance_drift["runtime_provenance"]["python_runtime"]["new_field"] = "drift"
    assert not receipt_matches_health(receipt, provenance_drift)

    ready_without_hashes = {
        **health,
        "model_production_ready": True,
        "model_uncertainty_validated": True,
        "reference_panel_production_ready": True,
        "reference_panel_fixture_only": False,
        "reference_panel_sha256": None,
        "reference_panel_readiness": "loaded_unapproved",
        "readiness": {"status": "ready", "blockers": []},
        "operational_controls": {
            **health["operational_controls"],
            "api_key_required_for_v1": True,
            "reference_panel_fixture_only": False,
        },
    }
    with pytest.raises(ReceiptError, match="SHA-256 identities"):
        health_to_receipt(ready_without_hashes)


def test_runtime_release_receipt_rejects_inconsistent_ready_metadata() -> None:
    health = TestClient(create_app()).get("/health").json()
    contradictory = json.loads(json.dumps(health))
    contradictory["model_artifact_sha256"] = "a" * 64
    contradictory["reference_panel_sha256"] = "b" * 64
    contradictory["model_production_ready"] = True
    contradictory["model_uncertainty_validated"] = True
    contradictory["reference_panel_production_ready"] = True
    contradictory["reference_panel_fixture_only"] = True
    contradictory["readiness"] = {"status": "ready", "blockers": []}
    contradictory["operational_controls"]["api_key_required_for_v1"] = True
    contradictory["operational_controls"]["reference_panel_fixture_only"] = True
    contradictory["operational_controls"]["model_approval_binding_valid"] = True
    with pytest.raises(ReceiptError, match="both production-ready and fixture-only"):
        health_to_receipt(contradictory)

    inconsistent_status = json.loads(json.dumps(health))
    inconsistent_status["readiness"] = {"status": "ready", "blockers": ["stale"]}
    with pytest.raises(ReceiptError, match="must not contain readiness blockers"):
        health_to_receipt(inconsistent_status)


def test_api_production_readiness_can_fail_closed_and_report_ready(monkeypatch) -> None:
    class ReadyPredictor:
        model_id = "approved-test-model"
        production_ready = True
        uncertainty_validated = True

    ready_panel = _non_fixture_panel(production_ready=True, source_sha256=None)
    client = TestClient(
        create_app(predictor=ReadyPredictor(), reference_panel=ready_panel)
    )
    assert client.get("/readyz").status_code == 503
    assert "FRAILTY_API_KEY" in client.get("/readyz").json()["blockers"][-1]

    monkeypatch.setenv("FRAILTY_API_KEY", "ready-secret")
    ready_client = TestClient(
        create_app(predictor=ReadyPredictor(), reference_panel=ready_panel)
    )
    missing_identity = ready_client.get("/readyz")
    assert missing_identity.status_code == 503
    assert any(
        "artifact SHA-256" in item for item in missing_identity.json()["blockers"]
    )
    assert any("source SHA-256" in item for item in missing_identity.json()["blockers"])

    ReadyPredictor.artifact_sha256 = "c" * 64
    ready_panel = replace(ready_panel, source_sha256="d" * 64)
    ready_client = TestClient(
        create_app(predictor=ReadyPredictor(), reference_panel=ready_panel)
    )
    assert ready_client.get("/readyz").status_code == 200
    assert ready_client.get("/health").json()["readiness"]["status"] == "ready"


def test_api_production_requirement_fails_closed(monkeypatch) -> None:
    monkeypatch.setenv("FRAILTY_REQUIRE_PRODUCTION", "true")
    with pytest.raises(RuntimeError, match="readiness is blocked"):
        create_app()


def test_strict_production_rejects_source_only_runtime_provenance(monkeypatch) -> None:
    complete_source_provenance = {
        "package_tree_sha256": "a" * 64,
        "package_installation_mode": "source_tree",
        "dependency_set_sha256": "b" * 64,
        "configuration_sha256": "c" * 64,
        "python_runtime": {
            "implementation": "cpython",
            "version": "3.13.11",
            "cache_tag": "cpython-313",
        },
    }
    monkeypatch.setenv("FRAILTY_REQUIRE_PRODUCTION", "true")
    monkeypatch.setattr(
        api_module, "runtime_provenance", lambda: complete_source_provenance
    )
    with pytest.raises(
        RuntimeError, match="installed-distribution provenance identity"
    ):
        create_app()


def test_api_optional_key_and_request_size_controls_are_explicit(monkeypatch) -> None:
    monkeypatch.setenv("FRAILTY_API_KEY", "test-secret")
    monkeypatch.setenv("FRAILTY_MAX_REQUEST_BYTES", "2048")
    client = TestClient(create_app())

    unauthenticated = client.post("/v1/assessments", json=sample_payload())
    assert unauthenticated.status_code == 401
    assert unauthenticated.headers["x-request-id"]
    assert unauthenticated.headers["connection"] == "close"

    authenticated = client.post(
        "/v1/assessments", json=sample_payload(), headers={"X-API-Key": "test-secret"}
    )
    assert authenticated.status_code == 200

    oversized = client.post(
        "/v1/assessments",
        content=b"{}" * 2000,
        headers={"X-API-Key": "test-secret", "Content-Type": "application/json"},
    )
    assert oversized.status_code == 413
    assert oversized.headers["connection"] == "close"
    assert oversized.headers["retry-after"] == "1"

    oversized_chunked = client.post(
        "/v1/assessments",
        content=iter([b"{}" * 2000]),
        headers={"X-API-Key": "test-secret", "Content-Type": "application/json"},
    )
    assert oversized_chunked.status_code == 413
    assert oversized_chunked.headers["connection"] == "close"
    assert oversized_chunked.headers["retry-after"] == "1"

    monkeypatch.delenv("FRAILTY_API_KEY")
    monkeypatch.delenv("FRAILTY_MAX_REQUEST_BYTES")


def test_predictor_runtime_failure_returns_generic_500_envelope() -> None:
    sentinel = "sentinel-predictor-leak-7f3c9b"

    class ExplodingPredictor:
        production_ready = False
        uncertainty_validated = False

        def predict_for_assessment(
            self, chronological_age: float, encoded_vector: list[float]
        ) -> ModelPrediction:
            raise RuntimeError(f"model exploded with {sentinel} token")

    client = TestClient(
        create_app(
            predictor=ExplodingPredictor(),
            reference_panel=default_development_panel(),
        )
    )

    assessment = client.post("/v1/assessments", json=sample_payload())
    assert assessment.status_code == 500
    assessment_body = assessment.json()
    assert assessment_body == {
        "error": {
            "code": "PredictionFailure",
            "message": "prediction failed",
        }
    }
    serialized = json.dumps(assessment_body)
    assert sentinel not in serialized
    assert "Traceback" not in serialized
    assert "patient_id" not in serialized

    previous = sample_payload()
    previous["patient_id"] = "comparison-predictor-failure"
    current = json.loads(json.dumps(previous))
    current["assessed_at"] = "2026-03-01"
    comparison_request = {
        "previous": {**previous, "assessed_at": "2026-01-01"},
        "current": current,
    }
    comparison = client.post("/v1/assessment-comparisons", json=comparison_request)
    assert comparison.status_code == 500
    comparison_body = comparison.json()
    assert comparison_body == {
        "error": {
            "code": "PredictionFailure",
            "message": "prediction failed",
        }
    }
    comparison_serialized = json.dumps(comparison_body)
    assert sentinel not in comparison_serialized
    assert "Traceback" not in comparison_serialized
    assert "comparison-predictor-failure" not in comparison_serialized

    invalid = client.post(
        "/v1/assessments",
        json={"patient_id": "still-invalid-after-hardening"},
    )
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "RequestValidationError"


def test_predictor_runtime_failure_preserves_chained_exception(caplog) -> None:
    sentinel = "chained-cause-leak-2c8d4e"

    class ExplodingPredictor:
        production_ready = False
        uncertainty_validated = False

        def predict_for_assessment(
            self, chronological_age: float, encoded_vector: list[float]
        ) -> ModelPrediction:
            raise RuntimeError(f"underlying crash {sentinel}")

    client = TestClient(
        create_app(
            predictor=ExplodingPredictor(),
            reference_panel=default_development_panel(),
        )
    )
    response = client.post("/v1/assessments", json=sample_payload())
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "PredictionFailure"
    assert sentinel not in json.dumps(response.json())
    assert sentinel not in caplog.text

    with pytest.raises(PredictionFailure) as raised:
        from frailty_engine.api import _run_assessment_safely

        _run_assessment_safely(
            sample_payload(),
            predictor=ExplodingPredictor(),
            reference_panel=default_development_panel(),
        )
    assert isinstance(raised.value.__cause__, RuntimeError)
    assert sentinel in str(raised.value.__cause__)


def test_prediction_failure_handler_covers_narrow_non_domain_causes() -> None:
    sentinel = "model-unavailable-leak-91a0ff"

    class UnavailablePredictor:
        production_ready = False
        uncertainty_validated = False

        def predict_for_assessment(
            self, chronological_age: float, encoded_vector: list[float]
        ) -> ModelPrediction:
            raise ModelUnavailableError(f"missing artifact {sentinel}")

    client = TestClient(
        create_app(
            predictor=UnavailablePredictor(),
            reference_panel=default_development_panel(),
        )
    )
    response = client.post("/v1/assessments", json=sample_payload())
    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "PredictionFailure"
    assert sentinel not in json.dumps(body)

    comparison_failure = client.post(
        "/v1/assessment-comparisons",
        json={
            "previous": {
                "patient_id": "same-person",
                "assessed_at": "2026-01-01",
                "measurements": sample_payload()["measurements"],
            },
            "current": {
                "patient_id": "same-person",
                "assessed_at": "2026-03-01",
                "measurements": sample_payload()["measurements"],
            },
        },
    )
    assert comparison_failure.status_code == 500
    assert comparison_failure.json()["error"]["code"] == "PredictionFailure"
    assert sentinel not in json.dumps(comparison_failure.json())


def test_mvv_accepts_minimum_vector_and_output_uses_neutral_trajectory_name() -> None:
    result = assess(sample_payload())
    assert result["data_quality"]["mvv_passed"] is True
    assert result["metrics"]["current_deficit_load_fi"] >= 0
    assert (
        result["metrics"]["current_deficit_load_fi_details"]["denominator"]
        == result["data_quality"]["fi_variables_measured"]
    )
    assert "homeostatic_deviation_score" in result["trajectory"]
    assert "relative_aging_velocity" not in result["trajectory"]
    assert result["model_metadata"]["production_ready"] is False
    assert "mortality" not in str(result).lower()
    assert result["metrics"]["biological_age"]["uncertainty_validated"] is False
    assert result["metrics"]["biological_age"]["ci_95"] is None
    assert (
        result["metrics"]["biological_age"]["uncertainty_construction"]
        == "none_withheld"
    )
    assert result["trajectory"]["score_ci_95"] is None
    assert result["trajectory"]["uncertainty_construction"] == "none_withheld"
    assert result["metrics"]["biological_age"]["uncertainty_method"] == (
        "fixed_log_hazard_sensitivity"
    )


def test_assessment_includes_range_based_wellness_report_without_clinical_claims() -> (
    None
):
    report = assess(sample_payload())["wellness_report"]
    assert report["summary"]["measured_features"] >= 10
    assert report["summary"]["missing_features"] > 0
    assert report["ranges"]
    assert report["action_effect_estimated"] is False
    assert report["clinical_or_lifespan_claim"] is False
    biological_age = assess(sample_payload())["metrics"]["biological_age"]
    assert "not a lifespan" in biological_age["interpretation"]
    bmi = next(item for item in report["ranges"] if item["feature"] == "bmi")
    assert bmi["target_range"]["label"] == "18.5–24.9"
    assert bmi["action_type"] == "lifestyle"
    assert bmi["recommendation"]
    ecw_tbw = next(item for item in report["ranges"] if item["feature"] == "ecw_tbw")
    assert ecw_tbw["biomarker"] == "ECW/TBW"
    assert "mortality" not in str(report).lower()
    support_report = assess(
        {
            "patient_id": "support-direction",
            "measurements": {
                **sample_payload()["measurements"],
                "phase_angle": 5.2,
                "ecw_tbw": 0.46,
            },
        }
    )["wellness_report"]
    phase_angle = next(
        item for item in support_report["ranges"] if item["feature"] == "phase_angle"
    )
    assert phase_angle["status"] == "attention"
    assert phase_angle["direction"] == "below"
    assert (
        next(
            item
            for item in support_report["focus_areas"]
            if item["focus"] == "Phase Angle"
        )["direction"]
        == "below"
    )


def test_wellness_report_lists_every_measured_non_in_range_focus_item() -> None:
    report = assess(sample_payload())["wellness_report"]
    summary_count = report["summary"]["focus_areas"]
    focus_list = report["focus_areas"]
    assert summary_count == len(focus_list)
    assert summary_count == sum(
        1 for item in report["ranges"] if item["status"] != "in_range"
    )
    non_in_range_features = {
        item["biomarker"] for item in report["ranges"] if item["status"] != "in_range"
    }
    listed_features = {item["focus"] for item in focus_list}
    assert listed_features == non_in_range_features
    priorities = []
    for item in focus_list:
        match = next(
            range_item
            for range_item in report["ranges"]
            if range_item["biomarker"] == item["focus"]
        )
        priorities.append(match["priority"])
    assert priorities == sorted(
        priorities,
        key=lambda value: {"priority": 0, "review": 1, "maintain": 2}[value],
    )
    listed_after_priority = [
        item["focus"]
        for item in focus_list
        if next(
            range_item
            for range_item in report["ranges"]
            if range_item["biomarker"] == item["focus"]
        )["priority"]
        == "priority"
    ]
    listed_after_review = [
        item["focus"]
        for item in focus_list
        if next(
            range_item
            for range_item in report["ranges"]
            if range_item["biomarker"] == item["focus"]
        )["priority"]
        == "review"
    ]
    assert listed_after_priority == sorted(listed_after_priority)
    assert listed_after_review == sorted(listed_after_review)


def test_wellness_report_focus_list_preserves_complete_api_contract() -> None:
    payload = sample_payload()
    payload["measurements"] = {
        **payload["measurements"],
        "phase_angle": 5.2,
        "ecw_tbw": 0.46,
    }
    result = assess(payload)
    parsed = AssessmentResponse.model_validate(result)
    assert parsed.wellness_report.summary.focus_areas == len(
        parsed.wellness_report.focus_areas
    )
    assert parsed.wellness_report.summary.focus_areas >= 1
    assert all(
        hasattr(item, "focus")
        and hasattr(item, "current_value")
        and hasattr(item, "target_range")
        and hasattr(item, "direction")
        and hasattr(item, "action_type")
        and hasattr(item, "recommendation")
        for item in parsed.wellness_report.focus_areas
    )
    # A larger out-of-range payload also stays in agreement so the static
    # Pages demo's "support" example (which exposes 20+ focus items) cannot
    # silently disagree with the API.
    rich = {
        **sample_payload()["measurements"],
        "age": 62,
        "sex": "male",
        "bmi": 31.2,
        "systolic_bp": 146,
        "diastolic_bp": 92,
        "resting_hr": 96,
        "waist_circumference": 107,
        "phase_angle": 4.8,
        "ecw_tbw": 0.46,
        "ffmi": 16.5,
        "skeletal_muscle_mass": 30.0,
        "visceral_fat": 18.0,
        "fasting_glucose": 128,
        "hba1c": 6.8,
        "hs_crp": 4.0,
        "albumin": 3.4,
        "creatinine": 1.3,
        "egfr": 55,
        "alp": 180,
        "wbc": 11,
        "rdw": 16.8,
        "fib_4": 2.8,
        "hypertension": 1,
        "t2d": 1,
        "osteoarthritis": 1,
        "sleep_apnea": 1,
        "grip_strength": 21,
        "chair_rise_time": 16,
        "smoking_status": "current",
        "alcohol_heavy_use": 1,
        "sleep_hours": 5.5,
    }
    rich_report = assess({"patient_id": "support-rich", "measurements": rich})[
        "wellness_report"
    ]
    assert rich_report["summary"]["focus_areas"] == len(rich_report["focus_areas"])
    assert rich_report["summary"]["focus_areas"] >= 5


def test_top_interventions_include_wellness_focus_without_fi_recommendation() -> None:
    payload = sample_payload()
    payload["measurements"] = {
        **payload["measurements"],
        "bmi": 31.2,
    }
    result = assess(payload)
    bmi = next(
        item for item in result["wellness_report"]["ranges"] if item["feature"] == "bmi"
    )
    assert bmi["status"] == "above_target"
    intervention = next(
        item
        for item in result["top_interventions"]
        if item["biomarker"] == "Body Mass Index"
    )
    assert intervention["action_type"] == "lifestyle"
    assert intervention["recommendation"] == bmi["recommendation"]


def test_top_interventions_share_wellness_context_and_provenance() -> None:
    payload = sample_payload()
    payload["measurements"] = {
        **payload["measurements"],
        "bmi": 31.2,
        "phase_angle": 5.2,
    }
    result = assess(payload)
    ranges = {item["feature"]: item for item in result["wellness_report"]["ranges"]}
    interventions = {item["biomarker"]: item for item in result["top_interventions"]}

    for feature in ("bmi", "phase_angle"):
        wellness_item = ranges[feature]
        intervention = interventions[wellness_item["biomarker"]]
        assert intervention["feature"] == feature
        assert intervention["current_value"] == wellness_item["current_value"]
        assert intervention["unit"] == wellness_item["unit"]
        assert intervention["direction"] == wellness_item["direction"]
        assert (
            intervention["target_range_label"] == wellness_item["target_range"]["label"]
        )
        assert intervention["source"] == wellness_item["source"]
        assert intervention["recommendation"] == wellness_item["recommendation"]
        assert intervention["action_type"] == wellness_item["action_type"]

    parsed = AssessmentResponse.model_validate(result)
    assert parsed.top_interventions[0].unit is not None


def test_wellness_focus_items_expose_their_range_provenance() -> None:
    result = assess(
        {
            **sample_payload(),
            "measurements": {
                **sample_payload()["measurements"],
                "bmi": 31.2,
            },
        }
    )
    ranges = {item["feature"]: item for item in result["wellness_report"]["ranges"]}
    bmi = next(
        item
        for item in result["wellness_report"]["focus_areas"]
        if item["feature"] == "bmi"
    )
    assert bmi["unit"] == ranges["bmi"]["unit"]
    assert bmi["target_range_label"] == ranges["bmi"]["target_range"]["label"]
    assert bmi["source"] == ranges["bmi"]["source"]
    assert bmi["z_score"] == ranges["bmi"]["z_score"]
    parsed = AssessmentResponse.model_validate(result)
    assert parsed.wellness_report.focus_areas[0].feature


def test_assessment_explains_homeostatic_deviation_normalization() -> None:
    result = assess(sample_payload())
    assert any(
        "normalized as (biological age - chronological age) / chronological age" in note
        for note in result["quality_notes"]
    )


def test_wellness_schema_rejects_unknown_status_and_extra_fields() -> None:
    with pytest.raises(ValueError):
        WellnessRangeResponse(
            feature="bmi",
            biomarker="Body Mass Index",
            current_value=23.4,
            unit="kg/m²",
            target_range={"label": "18.5–24.9"},
            status="not_a_status",
            direction="within_range",
            priority="maintain",
            action_type="lifestyle",
            z_score=None,
            source="test",
            recommendation="test",
        )
    with pytest.raises(ValueError):
        WellnessRangeResponse(
            feature="bmi",
            biomarker="Body Mass Index",
            current_value=23.4,
            unit="kg/m²",
            target_range={"label": "18.5–24.9"},
            status="in_range",
            direction="within_range",
            priority="maintain",
            action_type="lifestyle",
            z_score=None,
            source="test",
            recommendation="test",
            unexpected="reject-me",
        )


def test_static_demo_artifact_matches_the_python_assessment_pipeline() -> None:
    script = Path(__file__).parents[1] / "scripts" / "build_demo_data.py"
    subprocess.run(
        [sys.executable, str(script), "--check"],
        check=True,
        capture_output=True,
    )
    data = json.loads(
        (Path(__file__).parents[1] / "docs" / "demo-data.json").read_text(
            encoding="utf-8"
        )
    )
    assert data["privacy_note"].startswith("Synthetic")
    assert len(data["examples"]) >= 2
    for example in data["examples"]:
        payload = example["payload"]
        assert payload["patient_id"].startswith("demo-")
        expected = assess(payload)
        assert example["result"]["metrics"] == expected["metrics"]
        assert example["result"]["wellness_report"] == expected["wellness_report"]


def test_mvv_reports_both_blood_and_history_requirements() -> None:
    payload = {
        "patient_id": "p",
        "measurements": {
            "age": 45,
            "sex": "female",
            "bmi": 22,
            "phase_angle": 6,
            "ecw_tbw": 0.4,
        },
    }
    with pytest.raises(InsufficientDataError) as raised:
        assess(payload)
    assert any("blood" in item for item in raised.value.missing_requirements)
    assert any("history" in item for item in raised.value.missing_requirements)
    assert any(
        "fasting_glucose or hba1c" in item for item in raised.value.missing_requirements
    )


def test_evaluate_mvv_reports_missing_requirements_without_raising() -> None:
    status = evaluate_mvv(
        {
            "age": 45,
            "sex": "female",
            "bmi": 22,
            "phase_angle": 6,
            "ecw_tbw": 0.4,
        }
    )
    assert status["ok"] is False
    assert status["missing"] == [
        "at least 6 blood variables are required (received 0)",
        "fasting_glucose or hba1c is required",
        "at least 4 history variables are required (received 0)",
    ]


def test_evaluate_mvv_accepts_the_complete_sample_payload() -> None:
    assert evaluate_mvv(sample_payload()["measurements"]) == {"ok": True, "missing": []}


def test_missing_fi_items_change_denominator_without_imputation() -> None:
    patient = parse_patient_data(sample_payload())
    z_scores = default_development_panel().z_scores(patient)
    complete = calculate_fi(patient, z_scores)
    reduced_values = dict(patient.values)
    for name in ("fasting_glucose", "hs_crp", "albumin"):
        reduced_values[name] = None
    reduced = calculate_fi(type(patient)(patient.patient_id, reduced_values), z_scores)
    assert complete.denominator > reduced.denominator
    assert "fasting_glucose" not in reduced.valid_variables
    assert "fasting_glucose" not in reduced.deficits


def test_fi_denominator_strength_is_count_only_and_engineering_caveated() -> None:
    assert denominator_strength(0) == "low"
    assert denominator_strength(18) == "low"
    assert denominator_strength(19) == "moderate"
    assert denominator_strength(27) == "moderate"
    assert denominator_strength(28) == "high"
    assert denominator_strength(33) == "high"

    patient = parse_patient_data(sample_payload())
    result = calculate_fi(patient, default_development_panel().z_scores(patient))
    assert result.denominator_strength in {"low", "moderate", "high"}
    assert "not a clinical adequacy claim" in result.denominator_strength_caveat


def test_sex_stratified_panel_changes_the_same_phase_angle_z_score() -> None:
    panel = default_development_panel()
    male = panel.z_score("phase_angle", 6.5, sex="male", age=45)
    female = panel.z_score("phase_angle", 6.5, sex="female", age=45)
    assert male != female


def test_reference_panel_rejects_missing_or_nonpositive_normative_bands() -> None:
    with pytest.raises(ValueError, match="panel_id"):
        ReferencePanel.from_mapping({})
    with pytest.raises(ValueError, match="invalid band"):
        ReferencePanel.from_mapping(
            {
                "panel_id": "bad",
                "features": {
                    feature: {
                        "male": [{"min_age": 18, "max_age": 120, "mean": 1, "sd": 0}],
                        "female": [{"min_age": 18, "max_age": 120, "mean": 1, "sd": 1}],
                    }
                    for feature in (
                        "phase_angle",
                        "ecw_tbw",
                        "ffmi",
                        "skeletal_muscle_mass",
                        "visceral_fat",
                    )
                },
            }
        )
    valid_features = {
        feature: {
            "male": [
                {"min_age": 18, "max_age": 39, "mean": 1, "sd": 1},
                {"min_age": 40, "max_age": 120, "mean": 1, "sd": 1},
            ],
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
    valid_features["phase_angle"]["male"][1]["min_age"] = 39
    with pytest.raises(ValueError, match="overlapping"):
        ReferencePanel.from_mapping({"panel_id": "overlap", "features": valid_features})
    unsorted_features = json.loads(json.dumps(valid_features))
    unsorted_features["phase_angle"]["male"] = [
        {"min_age": 40, "max_age": 120, "mean": 1, "sd": 1},
        {"min_age": 18, "max_age": 39, "mean": 1, "sd": 1},
    ]
    with pytest.raises(ValueError, match="unsorted"):
        ReferencePanel.from_mapping(
            {"panel_id": "unsorted", "features": unsorted_features}
        )
    fixture_features = json.loads(json.dumps(valid_features))
    fixture_features["phase_angle"]["male"][1]["min_age"] = 40
    with pytest.raises(ValueError, match="fixture-only"):
        ReferencePanel.from_mapping(
            {
                "panel_id": "fixture",
                "production_ready": True,
                "fixture_only": True,
                "features": fixture_features,
            }
        )
    with pytest.raises(ValueError, match="production_ready must be boolean"):
        ReferencePanel.from_mapping(
            {
                "panel_id": "string-approval",
                "production_ready": "false",
                "features": valid_features,
            }
        )
    with pytest.raises(ValueError, match="fixture_only must be boolean"):
        ReferencePanel.from_mapping(
            {
                "panel_id": "string-fixture",
                "fixture_only": "false",
                "features": valid_features,
            }
        )


def test_parser_rejects_unknown_and_invalid_values() -> None:
    payload = sample_payload()
    payload["measurements"]["not_a_feature"] = 1
    with pytest.raises(ValidationError):
        parse_patient_data(payload)
    payload = sample_payload()
    payload["measurements"]["bmi"] = 300
    with pytest.raises(ValidationError):
        parse_patient_data(payload)


def test_model_vector_is_stable_and_keeps_missing_values_as_nan() -> None:
    payload = sample_payload()
    patient, vector = model_vector(payload)
    assert len(vector) == 36
    assert patient.values["waist_circumference"] is None
    assert vector[0] == 45.0
    assert vector[1] == 0.0
    assert vector[2] == 23.4
    assert vector[6] != vector[6]  # NaN, intentionally not fabricated.
    assert len(MODEL_VECTOR_FEATURE_NAMES) == len(vector) == 36
    assert MODEL_VECTOR_FEATURE_NAMES == (
        "age",
        "sex_male",
        "bmi",
        "systolic_bp",
        "diastolic_bp",
        "resting_hr",
        "waist_circumference",
        "phase_angle_z",
        "ecw_tbw_z",
        "ffmi_z",
        "skeletal_muscle_mass_z",
        "visceral_fat_z",
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
        "alcohol_heavy_use",
        "sleep_hours",
        "smoking_status",
        "current_deficit_load_fi",
    )


def test_training_frame_preserves_censoring_and_reuses_the_same_vector_contract() -> (
    None
):
    first = dict(sample_payload()["measurements"])
    first.update({"patient_id": "p1", "duration": 10, "event": 1})
    second = dict(first)
    second.update({"patient_id": "p2", "duration": 12, "event": 0, "phase_angle": None})
    frame = build_survival_frame([first, second])
    assert frame.x.shape == (2, 36)
    assert frame.events.tolist() == [True, False]
    assert frame.durations.tolist() == [10.0, 12.0]
    assert frame.quality is not None
    assert frame.quality.row_count == 2
    assert frame.quality.observed_event_count == 1
    assert frame.quality.censored_row_count == 1
    assert frame.quality.missing_counts["phase_angle_z"] == 1
    assert frame.quality.missing_rates["phase_angle_z"] == 0.5
    assert frame.quality.subgroups["sex"]["female"].row_count == 2
    assert frame.quality.subgroups["age_band"]["40-59"].censored_row_count == 1
    assert (
        frame.quality.subgroups["ethnicity"]["unknown"].missing_counts["phase_angle_z"]
        == 1
    )
    weighted = build_survival_frame(
        [dict(first, sample_weight=2.0), dict(second, sample_weight=3.0)]
    )
    assert weighted.weights is not None
    assert weighted.weights.tolist() == [2.0, 3.0]
    assert weighted.quality is not None
    assert weighted.quality.sample_weight_mode == "xgboost_dmatrix_case_weight"
    assert frame.quality.sample_weight_mode == "not_provided"
    numpy_event = build_survival_frame([dict(first, event=np.bool_(True))])
    assert numpy_event.events.tolist() == [True]
    with pytest.raises(ValidationError, match="every row or omitted"):
        build_survival_frame([dict(first, sample_weight=2.0), second])


def test_survey_design_contract_is_versioned_and_rejects_weight_conflicts() -> None:
    base = dict(sample_payload()["measurements"])
    first = dict(base, patient_id="survey-1", duration=10, event=1)
    second = dict(base, patient_id="survey-2", duration=12, event=0)
    case_weight = SurveyDesign(weight_name="sample_weight", weight_kind="case_weight")
    weighted = build_survival_frame(
        [dict(first, sample_weight=2.0), dict(second, sample_weight=3.0)],
        survey_design=case_weight,
    )
    assert weighted.survey_design == case_weight
    assert weighted.quality is not None
    assert weighted.quality.to_mapping()["survey_design"] == {
        **case_weight.to_mapping(),
        "weighting_applied": True,
        "design_reviewed": False,
    }
    assert SurveyDesign.from_mapping(case_weight.to_mapping()) == case_weight

    with pytest.raises(ValueError, match="invalid field set"):
        SurveyDesign.from_mapping({**case_weight.to_mapping(), "unexpected": True})
    with pytest.raises(ValueError, match="case_weight requires"):
        build_survival_frame([first, second], survey_design=case_weight)
    with pytest.raises(ValueError, match="raw sample_weight values require"):
        build_survival_frame(
            [dict(first, sample_weight=2.0), dict(second, sample_weight=3.0)],
            survey_design=SurveyDesign(
                weight_name="replicate_weight",
                weight_kind="replicate",
                replicate_pattern=("replicate_*",),
            ),
        )

    planned_replicates = SurveyDesign(
        weight_name="WTMEC2YR",
        weight_kind="replicate",
        replicate_pattern=("WTMEC2YR_REP{}",),
    )
    metadata_only = build_survival_frame(
        [first, second], survey_design=planned_replicates
    )
    assert metadata_only.weights is None
    assert metadata_only.survey_design == planned_replicates
    assert metadata_only.quality is not None
    assert (
        metadata_only.quality.to_mapping()["survey_design"]["weighting_applied"]
        is False
    )


def test_training_frame_retains_optional_missingness_without_assessment_mvv() -> None:
    row = dict(sample_payload()["measurements"])
    row.update({"patient_id": "sparse-training-row", "duration": 8, "event": 0})
    for name in (
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
    ):
        row[name] = None
    frame = build_survival_frame([row])
    assert frame.x.shape == (1, 36)
    assert np.isnan(frame.x[0, MODEL_VECTOR_FEATURE_NAMES.index("hba1c")])
    assert np.isnan(frame.x[0, MODEL_VECTOR_FEATURE_NAMES.index("hypertension")])
    assert frame.quality is not None
    assert frame.quality.missing_counts["hba1c"] == 1
    assert frame.quality.missing_rates["hba1c"] == 1.0
    assert frame.quality.subgroups["ethnicity"]["unknown"].row_count == 1
    assert frame.quality.subgroups["ethnicity"]["unknown"].missing_rates["hba1c"] == 1.0
    assert frame.quality.to_mapping()["scope"] == "cohort"


def test_external_validation_surfaces_survey_design_without_claiming_weighted_metrics() -> (
    None
):
    base = dict(sample_payload()["measurements"])
    rows = []
    for number, (age, event) in enumerate(((45, 1), (55, 0), (65, 1)), start=1):
        row = dict(base)
        row.update(
            {
                "patient_id": f"survey-validation-{number}",
                "age": age,
                "duration": 8 + number,
                "event": event,
                "ethnicity": "group-a",
                "sample_weight": float(number),
            }
        )
        rows.append(row)
    design = SurveyDesign(weight_name="WTMEC2YR", weight_kind="case_weight")
    report = validate_external_cohort(
        rows,
        cohort_name="survey-design-validation-fixture",
        survey_design=design,
        bins=3,
        bootstrap_replicates=20,
    )
    output = report.to_dict()
    expected_design = design.to_metadata(weighting_applied=False)
    assert output["survey_design"] == expected_design
    assert output["quality_flags"] == {
        "design_reviewed": False,
        "survey_design_declared": True,
        "weighting_applied": False,
    }
    assert output["calibration"]["survey_design"] == expected_design
    for bins in (
        output["calibration"]["probability_bins"],
        output["calibration"]["homeostatic_deviation_bins"],
        output["calibration"]["biological_age_bins"],
    ):
        assert all(item["survey_design"] == expected_design for item in bins)
    for groups in output["subgroup_metrics"].values():
        assert all(item["survey_design"] == expected_design for item in groups.values())


def test_gompertz_mapping_is_monotonic_and_zero_hazard_delta_preserves_age() -> None:
    mapper = GompertzMapper()
    assert mapper.age_from_log_hazard(45, 0) == pytest.approx(45)
    assert mapper.age_from_log_hazard(45, 0.5) > 45
    assert mapper.age_from_log_hazard(45, -0.5) < 45
    probability = mapper.probability_10y(45, 0.3)
    assert mapper.age_from_probability_10y(probability) == pytest.approx(
        mapper.age_from_log_hazard(45, 0.3)
    )
    assert GompertzMapper.from_mapping(mapper.to_mapping()) == mapper
    with pytest.raises(ValueError, match="age bounds"):
        GompertzMapper(min_age=80, max_age=80)


def test_gompertz_baseline_fit_is_deterministic_and_positive() -> None:
    mapper = GompertzMapper.fit_from_survival(
        [40, 45, 50, 55, 60, 65],
        [4, 5, 6, 7, 8, 9],
        [False, True, False, True, False, True],
        [0.1, 0.2, -0.1, 0.3, 0.0, 0.4],
    )
    repeat = GompertzMapper.fit_from_survival(
        [40, 45, 50, 55, 60, 65],
        [4, 5, 6, 7, 8, 9],
        [False, True, False, True, False, True],
        [0.1, 0.2, -0.1, 0.3, 0.0, 0.4],
    )
    assert mapper == repeat
    assert mapper.baseline_scale > 0
    assert mapper.growth_rate > 0


def test_gompertz_mapping_stays_finite_at_extreme_risk_inputs() -> None:
    mapper = GompertzMapper()
    assert mapper.probability_10y(110, 10_000) == 1.0
    assert mapper.age_from_log_hazard(45, 10_000) == mapper.max_age
    with pytest.raises(ValueError, match="finite"):
        mapper.probability_10y(float("inf"))


def test_development_predictor_withholds_unvalidated_ci() -> None:
    with pytest.warns(DeprecationWarning, match="predict_for_assessment"):
        prediction = DevelopmentPredictor().predict(
            45, 0.14, {"phase_angle": -1, "ecw_tbw": 1}
        )
    assert prediction.ci_95 is None
    assert prediction.uncertainty_validated is False
    assert prediction.model_id == "development-surrogate-v1"


def test_development_predictor_encoded_contract_preserves_legacy_semantics() -> None:
    payload = sample_payload()
    patient = parse_patient_data(payload)
    panel = default_development_panel()
    z_scores = panel.z_scores(patient)
    fi = calculate_fi(patient, z_scores)
    predictor = DevelopmentPredictor()

    with pytest.warns(DeprecationWarning, match="predict_for_assessment"):
        legacy = predictor.predict(float(patient.values["age"]), fi.score, z_scores)
    _, vector = model_vector(payload)
    encoded = predictor.predict_for_assessment(float(patient.values["age"]), vector)

    assert encoded.log_hazard == pytest.approx(legacy.log_hazard)
    assert encoded.point_estimate == legacy.point_estimate
    assert encoded.model_id == legacy.model_id
    with pytest.raises(ValueError, match="exactly 36"):
        predictor.predict_for_assessment(float(patient.values["age"]), [0.0] * 35)


def test_assessment_rejects_predictors_without_the_explicit_adapter_contract() -> None:
    class LegacyPredictor:
        def predict(
            self, chronological_age: float, fi_score: float, z_scores: dict[str, float]
        ) -> ModelPrediction:
            return DevelopmentPredictor().predict(chronological_age, fi_score, z_scores)

    with pytest.raises(TypeError, match="predict_for_assessment"):
        assess(sample_payload(), predictor=LegacyPredictor())


@pytest.mark.parametrize(
    ("model_ready", "panel_ready", "panel_fixture", "key_configured"),
    [
        (model_ready, panel_ready, panel_fixture, key_configured)
        for model_ready in (False, True)
        for panel_ready in (False, True)
        for panel_fixture in (False, True)
        for key_configured in (False, True)
    ],
)
def test_readiness_matrix_consistent_with_health_receipt(
    model_ready: bool,
    panel_ready: bool,
    panel_fixture: bool,
    key_configured: bool,
    monkeypatch,
) -> None:
    class MatrixPredictor:
        model_id = "readiness-matrix-model"
        requires_approval_manifest = False

        def __init__(self) -> None:
            self.production_ready = model_ready
            self.uncertainty_validated = model_ready
            self.artifact_sha256 = "a" * 64 if model_ready else None

        def predict_for_assessment(
            self, chronological_age: float, encoded_vector: list[float]
        ) -> ModelPrediction:
            raise AssertionError("readiness checks must not run inference")

    for variable in (
        "FRAILTY_MODEL_PATH",
        "FRAILTY_MODEL_APPROVAL_PATH",
        "FRAILTY_REFERENCE_PANEL_PATH",
        "FRAILTY_REQUIRE_PRODUCTION",
    ):
        monkeypatch.delenv(variable, raising=False)
    if key_configured:
        monkeypatch.setenv("FRAILTY_API_KEY", "readiness-matrix-secret")
    else:
        monkeypatch.delenv("FRAILTY_API_KEY", raising=False)

    panel = (
        _non_fixture_panel(production_ready=True, source_sha256="b" * 64)
        if panel_ready and not panel_fixture
        else replace(
            default_development_panel(),
            production_ready=panel_ready,
            fixture_only=panel_fixture and not panel_ready,
            source_sha256="b" * 64 if panel_ready else None,
        )
    )
    if panel_ready and panel_fixture:
        # Exercise the health/receipt invariant after construction; the frozen
        # panel normally prevents this contradictory state from being created.
        object.__setattr__(panel, "fixture_only", True)

    client = TestClient(create_app(predictor=MatrixPredictor(), reference_panel=panel))
    expected_ready = (
        model_ready and panel_ready and not panel_fixture and key_configured
    )
    ready_response = client.get("/readyz")
    health_response = client.get("/health")
    assert ready_response.status_code == (200 if expected_ready else 503)
    health = health_response.json()
    ready_body = ready_response.json()
    for field in (
        "model_id",
        "model_artifact_sha256",
        "model_production_ready",
        "model_uncertainty_validated",
        "reference_panel_id",
        "reference_panel_sha256",
        "reference_panel_production_ready",
        "reference_panel_fixture_only",
        "reference_panel_readiness",
        "approval_binding_valid",
        "runtime_provenance",
    ):
        assert ready_body[field] == health[field]
    assert ready_body["status"] == health["readiness"]["status"]
    assert ready_body["blockers"] == health["readiness"]["blockers"]
    assert health["readiness"]["status"] == ("ready" if expected_ready else "not_ready")
    if panel_ready and panel_fixture:
        with pytest.raises(
            ReceiptError, match="both production-ready and fixture-only"
        ):
            health_to_receipt(health)
    else:
        receipt = health_to_receipt(health)
        assert receipt_matches_health(receipt, health)


def test_fib4_derivation_is_explicit_and_validates_units_as_positive_values() -> None:
    assert calculate_fib_4(45, 35, 40, 250) == pytest.approx(0.996117)
    with pytest.raises(ValidationError):
        calculate_fib_4(45, 35, 0, 250)


def test_external_validation_harness_reports_subgroups_calibration_and_development_blockers() -> (
    None
):
    base = dict(sample_payload()["measurements"])
    rows = []
    for number, age, event, sex, ethnicity in (
        (1, 45, 1, "female", "group-a"),
        (2, 55, 0, "male", "group-b"),
        (3, 65, 1, "female", "group-a"),
    ):
        row = dict(base)
        row.update(
            {
                "patient_id": f"p{number}",
                "age": age,
                "sex": sex,
                "duration": 8 + number,
                "event": event,
                "ethnicity": ethnicity,
            }
        )
        rows.append(row)
    report = validate_external_cohort(
        rows, cohort_name="synthetic-external-fixture", bins=3
    )
    assert report.rows_evaluated == 3
    assert report.model_id == "development-surrogate-v1"
    assert report.model_artifact_sha256 is None
    assert report.model_production_ready is False
    assert report.model_uncertainty_validated is False
    assert report.reference_panel_id == "seca-development-fixture"
    assert len(report.reference_panel_sha256) == 64
    assert report.reference_panel_production_ready is False
    assert report.reference_panel_fixture_only is True
    report_payload = report.to_dict()
    expected_outcome_metrics = {
        "brier_score",
        "calibration_in_the_large",
        "calibration_slope",
        "integrated_calibration_index",
        "decision_curve_net_benefit",
    }
    assert set(report_payload["outcome_metric_status"]) == expected_outcome_metrics
    assert all(
        metric["value"] is None
        and metric["status"] == "not_implemented_pending_sap"
        and metric["construction"] == "none_withheld"
        and metric["review_gate"] == "E-005"
        for metric in report_payload["outcome_metric_status"].values()
    )
    assert all(
        set(metrics["outcome_metric_status"]) == expected_outcome_metrics
        for groups in report_payload["subgroup_metrics"].values()
        for metrics in groups.values()
    )
    assert report_payload["model_id"] == report.model_id
    assert report_payload["reference_panel_fixture_only"] is True
    assert report_payload["rows_excluded"] == 0
    assert report_payload["row_exclusion_counts"] == {}
    assert report_payload["concordance_ci_construction"] == "bootstrap_percentile"
    assert report.concordance_index is not None
    assert report.concordance_ci_status == "emitted"
    assert report.concordance_ci_construction == "bootstrap_percentile"
    assert report.concordance_comparable_pairs == 2
    assert report.concordance_ci_95 is not None
    assert report.concordance_ci_valid_replicates >= 100
    assert report.concordance_ci_requested_replicates == 200
    assert set(report.subgroup_metrics["sex"]) == {"female", "male"}
    assert set(report.subgroup_metrics["ethnicity"]) == {"group-a", "group-b"}
    assert report.subgroup_metrics["sex"]["female"]["event_count"] == 2
    assert report.subgroup_metrics["sex"]["female"]["censored_count"] == 0
    assert report.subgroup_metrics["sex"]["male"]["event_fraction"] == 0.0
    assert report.subgroup_metrics["sex"]["male"]["concordance_ci_95"] is None
    assert (
        report.subgroup_metrics["sex"]["male"]["concordance_ci_status"]
        == "withheld_no_comparable_pairs"
    )
    assert (
        report.subgroup_metrics["sex"]["male"]["concordance_ci_construction"]
        == "none_withheld"
    )
    assert report.subgroup_metrics["sex"]["male"]["concordance_comparable_pairs"] == 0
    assert report.subgroup_metrics["sex"]["female"]["concordance_comparable_pairs"] == 1
    support_warnings = {
        (item["dimension"], item["label"]): item["reasons"]
        for item in report.to_dict()["subgroup_support_warnings"]
    }
    assert support_warnings[("sex", "male")] == [
        "no_events",
        "no_comparable_pairs",
    ]
    assert support_warnings[("sex", "female")] == [
        "insufficient_valid_replicates",
    ]
    assert report.subgroup_metrics["age_band"]["40-59"]["mean_follow_up_years"] == 9.5
    assert report.calibration["probability_bins"]
    assert report.calibration["method"] == "kaplan_meier_horizon_event_probability"
    assert all(
        item["censoring_adjusted_event_rate"] is not None
        for item in report.calibration["probability_bins"]
        + report.calibration["homeostatic_deviation_bins"]
    )
    assert report.status == "blocked"
    assert any("production_ready" in blocker for blocker in report.blockers)

    class ApprovedMetadataPredictor(DevelopmentPredictor):
        model_id = "approved-metadata-test-model"
        artifact_sha256 = "b" * 64
        production_ready = True
        uncertainty_validated = True

    approved_panel = replace(
        default_development_panel(),
        production_ready=True,
        fixture_only=False,
        source_sha256="a" * 64,
    )
    identified_report = validate_external_cohort(
        rows,
        cohort_name="identified-external-fixture",
        predictor=ApprovedMetadataPredictor(),
        reference_panel=approved_panel,
        bins=3,
        bootstrap_replicates=20,
    )
    assert identified_report.model_id == "approved-metadata-test-model"
    assert identified_report.model_artifact_sha256 == "b" * 64
    assert identified_report.model_production_ready is True
    assert identified_report.model_uncertainty_validated is True
    assert identified_report.reference_panel_id == approved_panel.panel_id
    assert identified_report.reference_panel_sha256 == "a" * 64
    assert identified_report.reference_panel_production_ready is True
    assert identified_report.reference_panel_fixture_only is False
    assert identified_report.to_dict()["model_artifact_sha256"] == "b" * 64


def test_external_validation_aggregates_row_exclusions_without_row_identifiers() -> (
    None
):
    base = dict(sample_payload()["measurements"])
    rows = []
    for number in (1, 2):
        row = dict(base)
        row.update(
            {
                "patient_id": f"excluded-{number}",
                "duration": 10,
                "event": "not-a-boolean",
                "ethnicity": "group-a",
            }
        )
        rows.append(row)

    report = validate_external_cohort(
        rows,
        cohort_name="excluded-row-fixture",
        bootstrap_replicates=20,
    )

    assert report.rows_received == 2
    assert report.rows_evaluated == 0
    assert report.to_dict()["rows_excluded"] == 2
    assert report.row_exclusion_counts == {"event must be boolean or 0/1": 2}
    assert report.to_dict()["row_exclusion_counts"] == {
        "event must be boolean or 0/1": 2
    }
    assert "excluded-1" not in json.dumps(report.to_dict())
    assert "2 row(s) excluded: event must be boolean or 0/1" in report.blockers
    assert report.concordance_ci_status == "withheld_no_records"
    assert report.to_dict()["concordance_ci_status"] == "withheld_no_records"


def test_external_validation_accepts_legacy_ethnicity_alias_and_rejects_conflicts() -> (
    None
):
    base = dict(sample_payload()["measurements"])
    alias_rows = []
    for number, ethnicity in enumerate(("group-a", "group-b"), start=1):
        row = dict(base)
        row.update(
            {
                "patient_id": f"alias-{number}",
                "duration": 8 + number,
                "event": number % 2,
                "race_ethnicity": ethnicity,
            }
        )
        alias_rows.append(row)
    alias_report = validate_external_cohort(
        alias_rows, cohort_name="legacy-ethnicity-alias", bootstrap_replicates=20
    )
    assert alias_report.rows_evaluated == 2
    assert not any("missing ethnicity" in blocker for blocker in alias_report.blockers)
    assert set(alias_report.subgroup_metrics["ethnicity"]) == {"group-a", "group-b"}

    conflicting = dict(alias_rows[0])
    conflicting["ethnicity"] = "group-a"
    conflicting["race_ethnicity"] = "group-b"
    report = validate_external_cohort(
        [alias_rows[0], conflicting],
        cohort_name="conflicting-ethnicity-alias",
        bootstrap_replicates=20,
    )
    assert report.rows_received == 2
    assert report.rows_evaluated == 1
    assert report.to_dict()["rows_excluded"] == 1
    assert report.row_exclusion_counts == {
        "ethnicity and race_ethnicity disagree; provide one consistent value": 1
    }
    assert "conflicting-1" not in json.dumps(report.to_dict())


def test_external_validation_concordance_bootstrap_is_deterministic_and_json_safe() -> (
    None
):
    base = dict(sample_payload()["measurements"])
    rows = []
    for number, (age, duration, event) in enumerate(
        ((35, 4, 1), (45, 8, 0), (55, 12, 1), (65, 16, 0), (75, 20, 1)),
        start=1,
    ):
        row = dict(base)
        row.update(
            {
                "patient_id": f"bootstrap-{number}",
                "age": age,
                "duration": duration,
                "event": event,
                "ethnicity": "group-a",
            }
        )
        rows.append(row)
    first = validate_external_cohort(
        rows,
        cohort_name="bootstrap-fixture",
        bins=3,
        bootstrap_replicates=80,
        bootstrap_seed=7,
    )
    second = validate_external_cohort(
        rows,
        cohort_name="bootstrap-fixture",
        bins=3,
        bootstrap_replicates=80,
        bootstrap_seed=7,
    )
    assert first.concordance_ci_95 == second.concordance_ci_95
    assert first.concordance_ci_status == "emitted"
    assert first.concordance_comparable_pairs == 6
    assert (
        first.concordance_ci_valid_replicates == second.concordance_ci_valid_replicates
    )
    assert first.to_dict()["concordance_ci_95"] == list(first.concordance_ci_95)
    json.dumps(first.to_dict())
    assert isinstance(
        first.to_dict()["subgroup_metrics"]["sex"]["female"]["concordance_ci_95"],
        list,
    )
    assert (
        first.to_dict()["subgroup_metrics"]["sex"]["female"]["concordance_ci_status"]
        == "emitted"
    )
    assert first.concordance_ci_valid_replicates >= 40
    with pytest.raises(ValueError, match="bootstrap_replicates"):
        validate_external_cohort(
            rows, cohort_name="bootstrap-fixture", bootstrap_replicates=19
        )


def test_external_validation_does_not_treat_equal_event_times_as_ordered() -> None:
    base = dict(sample_payload()["measurements"])
    rows = []
    for number, event in enumerate((1, 1, 0), start=1):
        row = dict(base)
        row.update(
            {
                "patient_id": f"tie-{number}",
                "age": 40 + number * 5,
                "duration": 5 if event else 10,
                "event": event,
                "ethnicity": "group-a",
            }
        )
        rows.append(row)
    report = validate_external_cohort(rows, cohort_name="tie-fixture")
    assert report.concordance_comparable_pairs == 2


def test_committed_synthetic_external_fixture_runs_end_to_end() -> None:
    fixture = json.loads(
        (
            Path(__file__).parents[1]
            / "examples"
            / "external_validation_synthetic.json"
        ).read_text(encoding="utf-8")
    )
    assert fixture["provenance"]["kind"] == "synthetic"
    assert fixture["provenance"]["clinical_use"] == "forbidden"
    rows = fixture["rows"]
    report = validate_external_cohort(
        rows,
        cohort_name="committed-synthetic-external-fixture",
        bins=5,
        bootstrap_replicates=60,
        bootstrap_seed=fixture["provenance"]["seed"],
    )
    assert report.rows_evaluated == report.rows_received == 300
    assert report.concordance_index is not None
    assert report.concordance_ci_95 is not None
    assert report.calibration["probability_bins"]
    assert set(report.subgroup_metrics["age_band"]) == {
        "18-39",
        "40-59",
        "60-79",
        "80+",
    }
    assert set(report.subgroup_metrics["ethnicity"]) == {
        "synthetic-group-a",
        "synthetic-group-b",
        "synthetic-group-c",
    }


def test_survival_split_is_deterministic_patient_level_and_event_stratified() -> None:
    base = dict(sample_payload()["measurements"])
    rows = []
    for number in range(20):
        row = dict(base)
        row.update(
            {
                "patient_id": f"split-{number}",
                "duration": float(number + 1),
                "event": number % 2 == 0,
            }
        )
        rows.append(row)
    first = split_survival_rows(rows, holdout_fraction=0.2, seed=13)
    second = split_survival_rows(rows, holdout_fraction=0.2, seed=13)
    first_train_ids = {row["patient_id"] for row in first.train_rows}
    first_holdout_ids = {row["patient_id"] for row in first.holdout_rows}
    assert not first_train_ids & first_holdout_ids
    assert first_train_ids == {row["patient_id"] for row in second.train_rows}
    assert first_holdout_ids == {row["patient_id"] for row in second.holdout_rows}
    assert first.to_mapping()["patient_overlap"] == 0
    assert first.to_mapping()["train"]["event_count"] > 0
    assert first.to_mapping()["holdout"]["event_count"] > 0
    assert first.to_mapping()["train"]["censored_count"] > 0
    assert first.to_mapping()["holdout"]["censored_count"] > 0
    duplicate = [dict(rows[0]), dict(rows[0])]
    with pytest.raises(ValidationError, match="unique"):
        split_survival_rows(duplicate)
    with pytest.raises(ValueError, match="holdout_fraction"):
        split_survival_rows(rows, holdout_fraction=1.0)


def test_survival_split_can_preserve_sex_and_age_band_strata() -> None:
    base = dict(sample_payload()["measurements"])
    rows = []
    for sex in ("female", "male"):
        for age in (25, 45, 65, 85):
            for event in (False, True):
                for repeat in range(2):
                    row = dict(base)
                    row.update(
                        {
                            "patient_id": f"strata-{sex}-{age}-{event}-{repeat}",
                            "age": age,
                            "sex": sex,
                            "event": event,
                            "duration": 5 + repeat,
                        }
                    )
                    rows.append(row)
    split = split_survival_rows(
        rows,
        holdout_fraction=0.25,
        seed=7,
        strata=("sex", "age_band"),
    )
    assert split.strategy == "patient_id_sha256_event_sex_age_band_stratified"
    assert split.to_mapping()["strata"] == ["sex", "age_band"]
    assert {row["sex"] for row in split.train_rows} == {"female", "male"}
    assert {row["sex"] for row in split.holdout_rows} == {"female", "male"}
    assert {
        "18-39"
        if row["age"] < 40
        else "40-59"
        if row["age"] < 60
        else "60-79"
        if row["age"] < 80
        else "80+"
        for row in split.train_rows
    } == {"18-39", "40-59", "60-79", "80+"}
    assert {
        "18-39"
        if row["age"] < 40
        else "40-59"
        if row["age"] < 60
        else "60-79"
        if row["age"] < 80
        else "80+"
        for row in split.holdout_rows
    } == {"18-39", "40-59", "60-79", "80+"}
    with pytest.raises(ValueError, match="only 'sex' and 'age_band'"):
        split_survival_rows(rows, strata=("ethnicity",))


def test_calibration_excludes_early_censored_rows_from_horizon_bins() -> None:
    base = dict(sample_payload()["measurements"])
    rows = []
    for number, (age, duration, event) in enumerate(
        ((30, 5, 0), (45, 8, 1), (60, 12, 0), (75, 15, 1)), start=1
    ):
        row = dict(base)
        row.update(
            {
                "patient_id": f"km-{number}",
                "age": age,
                "duration": duration,
                "event": event,
                "ethnicity": "group-a",
            }
        )
        rows.append(row)
    report = validate_external_cohort(rows, cohort_name="km-fixture", bins=4)
    assert report.calibration["method"] == "kaplan_meier_horizon_event_probability"
    assert report.calibration["censored_before_horizon_rows"] == 1
    assert report.calibration["calibration_rows"] == 3
    assert sum(item["n"] for item in report.calibration["probability_bins"]) == 3
    assert not any("lack follow-up" in blocker for blocker in report.blockers)


def test_horizon_calibration_excludes_early_censored_rows_from_bins() -> None:
    base = dict(sample_payload()["measurements"])
    rows = []
    for number, (age, duration, event) in enumerate(
        ((30, 5, 0), (45, 10, 0), (60, 12, 1), (75, 15, 0)), start=1
    ):
        row = dict(base)
        row.update(
            {
                "patient_id": f"km-eligible-{number}",
                "age": age,
                "duration": duration,
                "event": event,
                "ethnicity": "group-a",
            }
        )
        rows.append(row)

    report = validate_external_cohort(rows, cohort_name="km-eligible-fixture", bins=4)

    assert report.calibration["eligible_rows"] == 3
    assert report.calibration["calibration_rows"] == 3
    assert sum(item["n"] for item in report.calibration["probability_bins"]) == 3
    assert (
        sum(item["n"] for item in report.calibration["homeostatic_deviation_bins"]) == 3
    )
    assert report.calibration["censored_before_horizon_rows"] == 1


def test_assessment_passes_the_full_vector_to_a_vector_based_predictor() -> None:
    class VectorPredictor:
        production_ready = False

        def __init__(self) -> None:
            self.vector = None

        def predict_for_assessment(
            self, age: float, vector: list[float]
        ) -> ModelPrediction:
            self.vector = vector
            return ModelPrediction(45.0, (43.0, 47.0), 0.0, "test-vector-model", False)

    predictor = VectorPredictor()
    result = assess(sample_payload(), predictor=predictor)
    assert len(predictor.vector) == 36
    assert result["model_metadata"]["model_id"] == "test-vector-model"
    assert result["metrics"]["biological_age"]["uncertainty_construction"] == (
        "none_withheld"
    )

    class ValidatedWithoutInterval:
        production_ready = True
        uncertainty_validated = True

        def predict_for_assessment(
            self, age: float, vector: list[float]
        ) -> ModelPrediction:
            return ModelPrediction(
                45.0,
                None,
                0.0,
                "validated-without-interval",
                True,
                uncertainty_validated=True,
            )

    no_interval = assess(sample_payload(), predictor=ValidatedWithoutInterval())
    assert no_interval["metrics"]["biological_age"]["ci_95"] is None
    assert (
        no_interval["metrics"]["biological_age"]["uncertainty_construction"]
        == "none_withheld"
    )
    assert no_interval["trajectory"]["score_ci_95"] is None
    assert no_interval["trajectory"]["uncertainty_construction"] == "none_withheld"

    class InvalidAssessmentConstruction:
        production_ready = True
        uncertainty_validated = True

        def predict_for_assessment(
            self, age: float, vector: list[float]
        ) -> ModelPrediction:
            return ModelPrediction(
                45.0,
                (44.0, 46.0),
                0.0,
                "invalid-construction",
                True,
                uncertainty_validated=True,
                uncertainty_construction="bootstrap_percentile",  # type: ignore[arg-type]
            )

    with pytest.raises(ValueError, match="wald_1_96_se"):
        assess(sample_payload(), predictor=InvalidAssessmentConstruction())


def test_xgb_adapter_requests_linear_predictor_for_log_hazard_mapping() -> None:
    class FakeXGB:
        def __init__(self) -> None:
            self.output_margin = None

        def predict(self, values, output_margin=False):
            self.output_margin = output_margin
            return [0.0]

    model = XGBSurvivalModel(MODEL_VECTOR_FEATURE_NAMES)
    model._model = FakeXGB()
    prediction = model.predict(45, [0.0] * 36)
    assert model._model.output_margin is True
    assert prediction.point_estimate == 45.0
    assert prediction.uncertainty_validated is False
    assert prediction.ci_95 is None
    with pytest.raises(ValueError):
        model.predict(45, [0.0] * 35)
    with pytest.raises(ValueError, match="standard error"):
        model.predict(45, [0.0] * 36, log_hazard_se=-1)


def test_native_xgb_model_round_trips_an_artifact_when_optional_dependency_is_available(
    tmp_path,
) -> None:
    pytest.importorskip("xgboost")
    base = dict(sample_payload()["measurements"])
    rows = []
    for number in range(6):
        row = dict(base)
        row.update(
            {
                "patient_id": f"artifact-{number}",
                "duration": 3.0 + number,
                "event": int(number % 2 == 0),
                "age": 40 + number * 5,
                "phase_angle": 6.8 - number * 0.15,
            }
        )
        rows.append(row)
    model = fit_xgb_survival(rows)
    assert model.training_quality is not None
    assert model.training_quality["row_count"] == 6
    import xgboost as xgb

    inference = xgb.DMatrix(
        np.asarray([[0.0] * len(MODEL_VECTOR_FEATURE_NAMES)], dtype=float),
        feature_names=list(MODEL_VECTOR_FEATURE_NAMES),
        missing=np.nan,
    )
    hazard_ratio = float(model._model.predict(inference)[0])
    raw_margin = float(model._model.predict(inference, output_margin=True)[0])
    assert hazard_ratio == pytest.approx(np.exp(raw_margin))
    assert raw_margin == pytest.approx(float(np.log(hazard_ratio)))
    path = model.save_model(tmp_path / "model.json")
    loaded = XGBSurvivalModel.load_model(path, MODEL_VECTOR_FEATURE_NAMES)
    assert loaded.training_quality == model.training_quality
    assert loaded.training_config == model.training_config
    assert loaded.training_config is not None
    assert loaded.training_config["num_boost_round"] == 300
    assert loaded.training_config["mapper_source"] == "training_cohort_in_sample"
    assert loaded.survey_design == model.survey_design
    assert loaded.training_config["survey_design"] == model.survey_design.to_mapping()
    prediction = loaded.predict(55, [0.0] * 36)
    assessment = assess(
        {"patient_id": "artifact-inference", "measurements": dict(base)},
        predictor=loaded,
    )
    assert path.exists()
    assert prediction.ci_95 is None
    assert assessment["model_metadata"]["model_id"] == "xgb-survival-cox-v1"


def test_native_xgb_artifact_restores_the_persisted_gompertz_mapper(
    tmp_path,
) -> None:
    pytest.importorskip("xgboost")
    base = dict(sample_payload()["measurements"])
    rows = []
    for number in range(6):
        row = dict(base)
        row.update(
            {
                "patient_id": f"mapper-{number}",
                "duration": 3.0 + number,
                "event": int(number % 2 == 0),
                "age": 40 + number * 5,
            }
        )
        rows.append(row)
    mapper = GompertzMapper(baseline_scale=0.00012, growth_rate=0.075)
    model = XGBSurvivalModel(MODEL_VECTOR_FEATURE_NAMES, mapper=mapper).fit(
        build_survival_frame(rows).x,
        [row["duration"] for row in rows],
        [row["event"] for row in rows],
    )
    path = model.save_model(tmp_path / "mapper-model.json")
    loaded = XGBSurvivalModel.load_model(path, MODEL_VECTOR_FEATURE_NAMES)
    assert loaded.mapper == mapper
    with pytest.raises(ValueError, match="does not match the persisted mapper"):
        XGBSurvivalModel.load_model(
            path,
            MODEL_VECTOR_FEATURE_NAMES,
            mapper=GompertzMapper(baseline_scale=0.0002, growth_rate=0.06),
        )


def test_native_xgb_fit_rejects_non_binary_events_and_infinite_features() -> None:
    pytest.importorskip("xgboost")
    model = XGBSurvivalModel(("age",))
    x = np.asarray([[45.0], [55.0]])
    with pytest.raises(ValueError, match="boolean or 0/1"):
        model.fit(x, [3.0, 4.0], ["0", True])
    with pytest.raises(ValueError, match="boolean or 0/1"):
        model.fit(x, [3.0, 4.0], [2, 1])
    with pytest.raises(ValueError, match="infinite"):
        model.fit(np.asarray([[45.0], [float("inf")]]), [3.0, 4.0], [1, 0])


def test_model_approval_sidecar_binds_hash_features_and_readiness(
    tmp_path, monkeypatch
) -> None:
    pytest.importorskip("xgboost")
    base = dict(sample_payload()["measurements"])
    rows = []
    for number in range(6):
        row = dict(base)
        row.update(
            {
                "patient_id": f"approval-{number}",
                "duration": 3.0 + number,
                "event": int(number % 2 == 0),
                "age": 40 + number * 5,
            }
        )
        rows.append(row)
    model = fit_xgb_survival(rows)
    artifact_path = model.save_model(tmp_path / "approved-model.json")
    approval_path = tmp_path / "approved-model.approval.json"
    panel_sha256 = "a" * 64
    approval_path.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "model_id": model.model_id,
                "artifact_sha256": hashlib.sha256(
                    artifact_path.read_bytes()
                ).hexdigest(),
                "feature_names": list(MODEL_VECTOR_FEATURE_NAMES),
                "reference_panel_id": "seca-development-fixture",
                "reference_panel_sha256": panel_sha256,
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
    approved = XGBSurvivalModel.load_model(
        artifact_path,
        MODEL_VECTOR_FEATURE_NAMES,
        approval_manifest=approval_path,
    )
    assert approved.production_ready is True
    assert approved.uncertainty_validated is True
    assert approved.approved_reference_panel_id == "seca-development-fixture"
    assert approved.approved_reference_panel_sha256 == panel_sha256
    assert approved.approved_log_hazard_se == pytest.approx(0.11)
    approved_prediction = approved.predict(55, [0.0] * 36)
    assert approved_prediction.warning is None
    assert approved_prediction.ci_95 is not None
    assert (
        approved_prediction.ci_95[0]
        <= approved_prediction.point_estimate
        <= approved_prediction.ci_95[1]
    )
    approved.production_ready = False
    with pytest.raises(ValueError, match="bound by its approval"):
        approved.predict(55, [0.0] * 36, log_hazard_se=0.12)
    approved.production_ready = True
    with pytest.raises(ValueError, match="bound by its approval"):
        approved.predict(55, [0.0] * 36, log_hazard_se=0.12)

    monkeypatch.setenv("FRAILTY_API_KEY", "approval-secret")
    ready_panel = _non_fixture_panel(
        panel_id="seca-development-fixture",
        production_ready=True,
        source_sha256=panel_sha256,
    )
    client = TestClient(
        create_app(
            predictor=approved,
            reference_panel=ready_panel,
        )
    )
    assert client.get("/readyz").status_code == 200
    assert (
        client.get("/health").json()["operational_controls"][
            "model_approval_manifest_configured"
        ]
        is True
    )
    assert (
        client.get("/health").json()["operational_controls"][
            "model_approval_binding_valid"
        ]
        is True
    )
    approved_assessment = client.post(
        "/v1/assessments",
        json=sample_payload(),
        headers={"x-api-key": "approval-secret"},
    )
    assert approved_assessment.status_code == 200
    approved_response = AssessmentResponse.model_validate(approved_assessment.json())
    assert approved_response.metrics.biological_age.ci_95 is not None
    assert (
        approved_response.metrics.biological_age.uncertainty_construction
        == "wald_1_96_se"
    )
    assert approved_response.trajectory.score_ci_95 is not None
    assert approved_response.trajectory.uncertainty_construction == "wald_1_96_se"
    mismatch_client = TestClient(
        create_app(
            predictor=approved,
            reference_panel=replace(ready_panel, source_sha256="b" * 64),
        )
    )
    assert mismatch_client.get("/readyz").status_code == 503
    assert (
        "hash does not match" in mismatch_client.get("/readyz").json()["blockers"][-1]
    )
    assert (
        mismatch_client.get("/health").json()["operational_controls"][
            "model_approval_binding_valid"
        ]
        is False
    )

    refit_probe = XGBSurvivalModel.load_model(
        artifact_path,
        MODEL_VECTOR_FEATURE_NAMES,
        approval_manifest=approval_path,
    )
    probe_frame = build_survival_frame(rows)
    refit_probe.fit(probe_frame.x, probe_frame.durations, probe_frame.events)
    assert refit_probe.production_ready is False
    assert refit_probe.approved_reference_panel_id is None
    assert refit_probe.approved_reference_panel_sha256 is None
    assert refit_probe.approval_manifest_path is None
    assert refit_probe.approved_log_hazard_se is None
    assert refit_probe.artifact_sha256 is None
    assert refit_probe.uncertainty_method == "fixed_log_hazard_standard_error"

    bad_approval = dict(
        json.loads(approval_path.read_text(encoding="utf-8")),
        artifact_sha256="0" * 64,
    )
    approval_path.write_text(json.dumps(bad_approval), encoding="utf-8")
    with pytest.raises(ValueError, match="SHA-256"):
        XGBSurvivalModel.load_model(
            artifact_path,
            MODEL_VECTOR_FEATURE_NAMES,
            approval_manifest=approval_path,
        )


def test_api_rejects_an_orphaned_model_approval_manifest(monkeypatch) -> None:
    monkeypatch.delenv("FRAILTY_MODEL_PATH", raising=False)
    monkeypatch.setenv("FRAILTY_MODEL_APPROVAL_PATH", "orphan.approval.json")
    with pytest.raises(ValueError, match="requires FRAILTY_MODEL_PATH"):
        create_app()


def test_validation_report_renders_both_calibration_plot_artifacts(tmp_path) -> None:
    base = dict(sample_payload()["measurements"])
    rows = []
    for number, (age, event) in enumerate(((62, 1), (35, 0), (50, 1)), start=1):
        row = dict(base)
        row.update(
            {
                "patient_id": f"plot-{number}",
                "duration": 8 + number,
                "event": event,
                "age": age,
                "ethnicity": "group-a",
            }
        )
        rows.append(row)
    report = validate_external_cohort(rows, cohort_name="plot-fixture", bins=3)
    ages = [
        item["mean_chronological_age"]
        for item in report.calibration["biological_age_bins"]
    ]
    assert ages == sorted(ages)
    paths = write_calibration_plots(report, tmp_path)
    assert paths["homeostatic_deviation"].exists()
    assert paths["biological_age"].exists()


def test_public_nhanes_mortality_reader_uses_mec_follow_up_and_filters_ineligible(
    tmp_path,
) -> None:
    def record(
        seqn: int, eligstat: int, mortstat: int, interview_months: int, exam_months: int
    ) -> bytes:
        values = [" "] * 61
        values[0:6] = f"{seqn:06d}"
        values[14] = str(eligstat)
        values[15] = str(mortstat)
        values[16:19] = "010"
        values[42:45] = f"{interview_months:03d}"
        values[45:48] = f"{exam_months:03d}"
        return "".join(values).encode("ascii")

    path = tmp_path / "NHANES_2003_2004_MORT_2019_PUBLIC.dat"
    path.write_bytes(record(123, 1, 0, 110, 100) + b"\n" + record(124, 2, 0, 110, 100))
    rows = read_public_use_mortality(path)
    assert len(rows) == 1
    assert rows[0]["seqn"] == 123
    assert rows[0]["duration_months"] == 100
    assert rows[0]["duration"] == pytest.approx(100 / 12)
    assert rows[0]["event"] is False


def test_nhanes_column_map_keeps_missingness_and_derives_bia_and_fib4() -> None:
    mapping = NHANESColumnMap(
        {
            "age": "AGE",
            "sex": "SEX",
            "bmi": "BMI",
            "phase_angle": "PHASE",
            "ecw_tbw": "ECW_TBW",
            "ffmi": "FFMI",
            "bia_resistance_50k": "R50",
            "bia_reactance_50k": "X50",
            "bia_ecf": "ECF",
            "bia_tbw": "TBW",
            "bia_fat_free_mass": "FFM",
            "height_cm": "HEIGHT",
            "ast": "AST",
            "alt": "ALT",
            "platelets": "PLT",
            "ethnicity": "RACE",
        },
        missing_values=frozenset({7, 9}),
    )
    raw = {
        "SEQN": 123,
        "AGE": 45,
        "SEX": "female",
        "BMI": 23.4,
        "PHASE": None,
        "ECW_TBW": None,
        "FFMI": None,
        "R50": 500,
        "X50": 50,
        "ECF": 12,
        "TBW": 30,
        "FFM": 54,
        "HEIGHT": 165,
        "AST": 35,
        "ALT": 40,
        "PLT": 250,
        "RACE": "group-a",
    }
    rows = build_nhanes_rows(
        [raw],
        column_map=mapping,
        mortality_records=[
            {
                "seqn": 123,
                "patient_id": "nhanes-seqn-000123",
                "duration": 10.0,
                "event": True,
            }
        ],
    )
    assert len(rows) == 1
    assert rows[0]["phase_angle"] == pytest.approx(5.710593)
    assert rows[0]["ecw_tbw"] == pytest.approx(0.4)
    assert rows[0]["ffmi"] == pytest.approx(19.834711)
    assert rows[0]["fib_4"] == pytest.approx(calculate_fib_4(45, 35, 40, 250))
    assert rows[0]["skeletal_muscle_mass"] is None
    assert rows[0]["ethnicity"] == "group-a"


def test_nhanes_mortality_duration_unit_cannot_double_convert_normalized_years() -> (
    None
):
    raw = {"SEQN": 123, "AGE": 45, "SEX": "female", "BMI": 23.4}
    mapping = NHANESColumnMap(
        {"age": "AGE", "sex": "SEX", "bmi": "BMI"}, duration_unit="months"
    )
    with pytest.raises(ValueError, match="already normalized to years"):
        build_nhanes_rows(
            [raw],
            column_map=mapping,
            mortality_records=[{"seqn": 123, "duration": 24.0, "event": False}],
        )

    years_mapping = NHANESColumnMap(
        {"age": "AGE", "sex": "SEX", "bmi": "BMI"}, duration_unit="years"
    )
    rows = build_nhanes_rows(
        [raw],
        column_map=years_mapping,
        mortality_records=[{"seqn": 123, "duration": 24.0, "event": False}],
    )
    assert rows[0]["duration"] == 24.0


def test_nhanes_resource_manifest_is_explicit_for_the_three_bia_cycles() -> None:
    assert cycle_resource("1999-2000").bia_url.endswith("/BIX.XPT")
    assert cycle_resource("2003-2004").mortality_url.endswith(
        "NHANES_2003_2004_MORT_2019_PUBLIC.dat"
    )
    with pytest.raises(ValueError, match="unsupported BIA cycle"):
        cycle_resource("2019-2020")


def test_seca_tableview_import_maps_latest_scan_derives_ffmi_and_preserves_trend() -> (
    None
):
    csv_text = """"Value","Unit","Jan 2, 2025, 8:00 AM","Dec 2, 2024, 8:00 AM"
"Body Mass Index","kg/m²","25.8","26.4"
"Weight","kg","76.2","78.1"
"Skeletal Muscle Mass","kg","28.8","28.6"
"Fat Mass","kg","19.4","21.0"
"Visceral Adipose Tissue","Liters","3.1","3.8"
"Segmental Skeletal Muscle Mass","","",""
"Torso","kg","13.4","13.2"
"Left Arm","kg","1.74","1.70"
"Left Leg","kg","5.46","5.41"
"Right Arm","kg","1.72","1.68"
"Right Leg","kg","5.48","5.43"
"""
    export = read_seca_tableview_csv(csv_text)
    assert len(export.scans) == 2
    assert export.latest_measurements()["bmi"] == 25.8
    assert export.latest_measurements()["skeletal_muscle_mass"] == 28.8
    assert export.latest_measurements()["ffmi"] == pytest.approx(19.23, abs=0.02)
    assert export.latest_all_measurements()["weight_kg"] == 76.2
    assert export.latest_all_measurements()["fat_free_mass_kg"] == pytest.approx(56.8)
    assert export.latest.segmental_skeletal_muscle_mass["Left Leg"] == 5.46
    assert export.trend()["bmi"] == pytest.approx(-0.6)
    assert export.segmental_trend()["Left Leg"] == pytest.approx(0.05)
    assert export.segmental_trend()["Right Arm"] == pytest.approx(0.04)
    assert export.trend_available is True
    assert export.trend_note == "Latest minus previous dated scan."
    assert "age" not in export.latest_measurements()
    assert export.latest.derivations
    assert "estimated_height_cm" in export.latest_all_measurements()
    assert "estimated_height_cm" not in export.latest_measurements()
    readiness = export.assessment_readiness
    assert readiness["assessment_ready"] is False
    assert "age and sex" in readiness["missing_requirements"][0]
    assert any("blood-panel" in item for item in readiness["missing_requirements"])
    assert "not an assessment" in readiness["note"]

    single_scan = read_seca_tableview_csv(
        'Value,Unit,"Jan 2, 2025, 8:00 AM"\nBody Mass Index,kg/m²,25.8\n'
    )
    assert single_scan.trend() == {}
    assert single_scan.segmental_trend() == {}
    assert single_scan.trend_available is False
    assert "two dated scans" in single_scan.trend_note


def test_seca_tableview_import_matches_browser_safety_contract() -> None:
    unicode_minus = 'Value,Unit,"Jan 2, 2025, 8:00 AM"\nBody Mass Index,kg/m²,−25.8\n'
    assert read_seca_tableview_csv(unicode_minus).latest_measurements()["bmi"] == -25.8
    bom_csv = "\ufeff" + unicode_minus
    assert (
        read_seca_tableview_csv(StringIO(bom_csv)).latest_measurements()["bmi"] == -25.8
    )
    with pytest.raises(ValueError, match="parseable dates"):
        read_seca_tableview_csv("Value,Unit,2025-01-02\nBody Mass Index,kg/m²,25.8\n")
    with pytest.raises(ValueError, match="extra non-empty columns"):
        read_seca_tableview_csv(
            'Value,Unit,"Jan 2, 2025, 8:00 AM"\nBody Mass Index,kg/m²,25.8,unexpected\n'
        )


def test_seca_assessment_payload_overlay_returns_only_canonical_fields() -> None:
    export = read_seca_tableview_csv(
        'Value,Unit,"Jan 2, 2025, 8:00 AM"\n'
        "Body Mass Index,kg/m²,25.8\n"
        "Weight,kg,76.2\n"
        "Skeletal Muscle Mass,kg,28.8\n"
        "Fat Mass,kg,19.4\n"
        "Visceral Adipose Tissue,Liters,3.1\n"
    )
    overlay = export.assessment_payload_overlay()
    assert set(overlay) == {
        "bmi",
        "ffmi",
        "skeletal_muscle_mass",
        "visceral_fat",
    }
    assert overlay["bmi"] == 25.8
    assert "weight_kg" not in overlay
    assert "estimated_height_cm" not in overlay


def test_assess_overlay_cli_merges_seca_values_with_a_complete_overlay(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fixture = Path(__file__).parents[1] / "examples" / "seca_tableview_fixture.csv"
    overlay_path = tmp_path / "overlay.json"
    overlay_path.write_text(
        json.dumps(
            {
                "format": OVERLAY_FORMAT,
                "patient_id": "local-overlay",
                "measurements": {
                    "age": 45,
                    "sex": "female",
                    "phase_angle": 6.1,
                    "ecw_tbw": 0.39,
                    "fasting_glucose": 92,
                    "hba1c": 5.3,
                    "hs_crp": 0.7,
                    "albumin": 4.2,
                    "egfr": 98,
                    "wbc": 6.0,
                    "hypertension": 0,
                    "t2d": 0,
                    "osteoarthritis": 0,
                    "sleep_apnea": 0,
                },
            }
        ),
        encoding="utf-8",
    )
    assert (
        main(
            [
                "assess-overlay",
                str(fixture),
                "--overlay",
                str(overlay_path),
            ]
        )
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["patient_id"] == "local-overlay"
    assert result["data_quality"]["mvv_passed"] is True
    assert result["metrics"]["current_deficit_load_fi"] >= 0
    assert result["metrics"]["biological_age"]["ci_95"] is None


def test_cli_prints_research_use_only_e005_boundary(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["sample"]) == 0
    assert (
        "research-use-only development artifact - not for clinical use - "
        "does not satisfy E-005"
    ) in capsys.readouterr().err


def test_assess_overlay_cli_reports_structured_mvv_and_validation_errors(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fixture = Path(__file__).parents[1] / "examples" / "seca_tableview_fixture.csv"

    def run_overlay(
        measurements: dict[str, object], *, format: str = OVERLAY_FORMAT
    ) -> tuple[int, dict[str, object]]:
        path = tmp_path / f"overlay-{len(list(tmp_path.iterdir()))}.json"
        path.write_text(
            json.dumps(
                {
                    "format": format,
                    "patient_id": "cli-error-test",
                    "measurements": measurements,
                }
            ),
            encoding="utf-8",
        )
        result = main(["assess-overlay", str(fixture), "--overlay", str(path)])
        captured = capsys.readouterr()
        assert captured.out == ""
        return result, json.loads(captured.err)

    incomplete = {
        "age": 45,
        "sex": "female",
        "phase_angle": 6.1,
        "ecw_tbw": 0.39,
    }
    result, error = run_overlay(incomplete)
    assert result == 2
    assert error["error"]["code"] == "InsufficientDataError"
    assert "missing_requirements" in error["error"]
    assert (
        "fasting_glucose or hba1c is required" in error["error"]["missing_requirements"]
    )
    assert overlay_mvv_missing(incomplete | {"bmi": 25.8})

    complete = {
        "age": 45,
        "sex": "female",
        "phase_angle": 6.1,
        "ecw_tbw": 0.39,
        "fasting_glucose": 92,
        "hba1c": 5.3,
        "hs_crp": 0.7,
        "albumin": 4.2,
        "egfr": 98,
        "wbc": 6.0,
        "hypertension": 0,
        "t2d": 0,
        "osteoarthritis": 0,
        "sleep_apnea": 0,
    }
    result, error = run_overlay({**complete, "foobar": 1})
    assert result == 3
    assert error["error"]["code"] == "ValidationError"
    assert error["error"]["field_errors"]["foobar"] == "unknown feature"

    result, error = run_overlay({**complete, "phase_angle": 99})
    assert result == 3
    assert error["error"]["code"] == "ValidationError"
    assert "phase_angle" in error["error"]["field_errors"]

    result, error = run_overlay(complete, format="wrong-version")
    assert result == 3
    assert error["error"]["code"] == "ValidationError"
    assert error["error"]["field_errors"]["format"] == f"expected {OVERLAY_FORMAT}"

    bad_seca = tmp_path / "bad-seca.csv"
    bad_seca.write_text(
        '"Value","Unit","not-a-date"\n"Body Mass Index","kg/m²","25.8"\n',
        encoding="utf-8",
    )
    valid_overlay = tmp_path / "valid-overlay.json"
    valid_overlay.write_text(
        json.dumps(
            {
                "format": OVERLAY_FORMAT,
                "measurements": {
                    "age": 45,
                    "sex": "female",
                    "phase_angle": 6.1,
                    "ecw_tbw": 0.39,
                    "fasting_glucose": 92,
                    "hs_crp": 0.7,
                    "albumin": 4.2,
                    "creatinine": 0.9,
                    "egfr": 98,
                    "wbc": 6.0,
                    "hypertension": 0,
                    "t2d": 0,
                    "osteoarthritis": 0,
                    "sleep_apnea": 0,
                },
            }
        ),
        encoding="utf-8",
    )
    assert (
        main(
            [
                "assess-overlay",
                str(bad_seca),
                "--overlay",
                str(valid_overlay),
            ]
        )
        == 3
    )
    bad_seca_error = json.loads(capsys.readouterr().err)
    assert bad_seca_error == {
        "error": {
            "code": "ValidationError",
            "message": "SECA input validation failed",
            "field_errors": {"seca": "unable to read or parse the TableView CSV"},
        }
    }


def test_assess_overlay_cli_preserves_patient_id_and_rejects_seca_conflicts(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fixture = Path(__file__).parents[1] / "examples" / "seca_tableview_fixture.csv"
    complete = {
        "age": 45,
        "sex": "female",
        "phase_angle": 6.1,
        "ecw_tbw": 0.39,
        "fasting_glucose": 92,
        "hba1c": 5.3,
        "hs_crp": 0.7,
        "albumin": 4.2,
        "egfr": 98,
        "wbc": 6.0,
        "hypertension": 0,
        "t2d": 0,
        "osteoarthritis": 0,
        "sleep_apnea": 0,
    }

    missing_id_path = tmp_path / "missing-id.json"
    missing_id_path.write_text(
        json.dumps({"format": OVERLAY_FORMAT, "measurements": complete}),
        encoding="utf-8",
    )
    assert (
        main(
            [
                "assess-overlay",
                str(fixture),
                "--overlay",
                str(missing_id_path),
                "--patient-id",
                "clinic-abc",
            ]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out)["patient_id"] == "clinic-abc"

    existing_id_path = tmp_path / "existing-id.json"
    existing_id_path.write_text(
        json.dumps(
            {
                "format": OVERLAY_FORMAT,
                "patient_id": "alice",
                "measurements": complete,
            }
        ),
        encoding="utf-8",
    )
    assert (
        main(
            [
                "assess-overlay",
                str(fixture),
                "--overlay",
                str(existing_id_path),
                "--patient-id",
                "clinic-abc",
            ]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out)["patient_id"] == "alice"

    conflict_path = tmp_path / "conflict.json"
    conflict_path.write_text(
        json.dumps(
            {
                "format": OVERLAY_FORMAT,
                "patient_id": "conflict-test",
                "measurements": {**complete, "bmi": 99},
            }
        ),
        encoding="utf-8",
    )
    assert main(["assess-overlay", str(fixture), "--overlay", str(conflict_path)]) == 3
    error = json.loads(capsys.readouterr().err)
    assert error["error"]["code"] == "ValidationError"
    assert error["error"]["field_errors"]["bmi"] == (
        "must match the observed latest SECA value"
    )

    export = read_seca_tableview_csv(fixture)
    merged = merge_with_seca(
        {"format": OVERLAY_FORMAT, "measurements": complete}, export
    )
    assert merged["patient_id"] == "local-seca-overlay"

    long_id_path = tmp_path / "long-id.json"
    long_id_path.write_text(
        json.dumps({"format": OVERLAY_FORMAT, "measurements": complete}),
        encoding="utf-8",
    )
    assert (
        main(
            [
                "assess-overlay",
                str(fixture),
                "--overlay",
                str(long_id_path),
                "--patient-id",
                "x" * 129,
            ]
        )
        == 3
    )
    long_id_error = json.loads(capsys.readouterr().err)
    assert long_id_error["error"]["field_errors"]["patient_id"] == (
        "must be 128 characters or fewer"
    )


def test_seca_readiness_keeps_available_mvv_fields_and_never_infers_context() -> None:
    export = read_seca_tableview_csv(
        'Value,Unit,"Jan 2, 2025, 8:00 AM"\n'
        "Body Mass Index,kg/m²,25.8\n"
        "Phase Angle,degrees,6.0\n"
        "ECW/TBW,ratio,0.40\n"
    )
    readiness = export.assessment_readiness
    assert readiness["assessment_ready"] is False
    requirements = readiness["missing_requirements"]
    assert requirements == (
        "age and sex (not available in this SECA export; never inferred)",
        "at least 6 blood-panel values, including fasting_glucose or hba1c",
        "at least 4 clinical-history values",
    )


def test_seca_cli_surfaces_assessment_readiness(
    capsys: pytest.CaptureFixture[str],
) -> None:
    fixture = Path(__file__).parents[1] / "examples" / "seca_tableview_fixture.csv"
    assert main(["seca", str(fixture)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["assessment_readiness"]["assessment_ready"] is False
    assert (
        "at least 4 clinical-history values"
        in output["assessment_readiness"]["missing_requirements"]
    )
    assert output["segmental_trend_latest_minus_previous"]["Left Leg"] == pytest.approx(
        0.05
    )


def test_reference_panel_coverage_helper_reports_band_count_and_span() -> None:
    fixture = default_development_panel()
    band_count, span = fixture.coverage_for("female", 45)
    assert isinstance(band_count, int)
    assert band_count == 1
    assert math.isfinite(span)
    assert span > 0
    assert span == pytest.approx(102.0)

    male_count, male_span = fixture.coverage_for("male", 70)
    assert male_count == 1
    assert male_span == pytest.approx(102.0)

    out_of_range, out_span = fixture.coverage_for("female", 150)
    assert out_of_range == 0
    assert out_span == 0.0

    with pytest.raises(ValueError, match="male"):
        fixture.coverage_for("unknown", 45)
    with pytest.raises(ValueError, match="finite"):
        fixture.coverage_for("female", float("inf"))
    with pytest.raises(ValueError, match="at least one BIA feature"):
        fixture.coverage_for("female", 45, features=())
    with pytest.raises(ValueError, match="at least one BIA feature"):
        fixture.coverage_for("female", 45, features=("age",))


def test_assessment_exposes_reference_panel_band_geometry_for_current_patient() -> None:
    result = assess(sample_payload())
    parsed = AssessmentResponse.model_validate(result)
    assert isinstance(parsed.data_quality.reference_panel_band_count, int)
    assert parsed.data_quality.reference_panel_band_count >= 1
    assert isinstance(
        parsed.data_quality.reference_panel_band_span_years_for_age, float
    )
    assert math.isfinite(parsed.data_quality.reference_panel_band_span_years_for_age)
    assert parsed.data_quality.reference_panel_band_span_years_for_age > 0
    assert (
        result["data_quality"]["reference_panel_band_count"]
        == parsed.data_quality.reference_panel_band_count
    )
    assert (
        result["data_quality"]["reference_panel_band_span_years_for_age"]
        == parsed.data_quality.reference_panel_band_span_years_for_age
    )

    banded_panel = ReferencePanel.from_mapping(
        {
            "panel_id": "multi-band-fixture",
            "version": "test",
            "production_ready": False,
            "fixture_only": True,
            "source_note": "test multi-band coverage",
            "features": {
                "phase_angle": {
                    "male": [
                        {"min_age": 18, "max_age": 39, "mean": 1, "sd": 1},
                        {"min_age": 40, "max_age": 120, "mean": 1, "sd": 1},
                    ],
                    "female": [{"min_age": 18, "max_age": 120, "mean": 1, "sd": 1}],
                },
                "ecw_tbw": {
                    "male": [
                        {"min_age": 18, "max_age": 39, "mean": 1, "sd": 1},
                        {"min_age": 40, "max_age": 120, "mean": 1, "sd": 1},
                    ],
                    "female": [{"min_age": 18, "max_age": 120, "mean": 1, "sd": 1}],
                },
                "ffmi": {
                    "male": [
                        {"min_age": 18, "max_age": 39, "mean": 1, "sd": 1},
                        {"min_age": 40, "max_age": 120, "mean": 1, "sd": 1},
                    ],
                    "female": [{"min_age": 18, "max_age": 120, "mean": 1, "sd": 1}],
                },
                "skeletal_muscle_mass": {
                    "male": [
                        {"min_age": 18, "max_age": 39, "mean": 1, "sd": 1},
                        {"min_age": 40, "max_age": 120, "mean": 1, "sd": 1},
                    ],
                    "female": [{"min_age": 18, "max_age": 120, "mean": 1, "sd": 1}],
                },
                "visceral_fat": {
                    "male": [
                        {"min_age": 18, "max_age": 39, "mean": 1, "sd": 1},
                        {"min_age": 40, "max_age": 120, "mean": 1, "sd": 1},
                    ],
                    "female": [{"min_age": 18, "max_age": 120, "mean": 1, "sd": 1}],
                },
            },
        }
    )
    payload = sample_payload()
    payload["patient_id"] = "banded-coverage"
    payload["measurements"]["sex"] = "male"
    payload["measurements"]["age"] = 25
    young = assess(payload, reference_panel=banded_panel)
    assert young["data_quality"]["reference_panel_band_count"] == 1
    assert young["data_quality"][
        "reference_panel_band_span_years_for_age"
    ] == pytest.approx(21.0)

    payload["measurements"]["age"] = 50
    old = assess(payload, reference_panel=banded_panel)
    assert old["data_quality"]["reference_panel_band_count"] == 1
    assert old["data_quality"][
        "reference_panel_band_span_years_for_age"
    ] == pytest.approx(80.0)


def test_validate_external_cohort_pre_checks_panel_age_coverage_and_aggregates_out_of_coverage_rows() -> (
    None
):
    base = dict(sample_payload()["measurements"])
    banded_panel = ReferencePanel.from_mapping(
        {
            "panel_id": "narrow-band-coverage",
            "version": "test",
            "production_ready": False,
            "fixture_only": True,
            "source_note": "narrow-band test",
            "features": {
                "phase_angle": {
                    "male": [{"min_age": 40, "max_age": 64, "mean": 1, "sd": 1}],
                    "female": [{"min_age": 40, "max_age": 64, "mean": 1, "sd": 1}],
                },
                "ecw_tbw": {
                    "male": [{"min_age": 40, "max_age": 64, "mean": 1, "sd": 1}],
                    "female": [{"min_age": 40, "max_age": 64, "mean": 1, "sd": 1}],
                },
                "ffmi": {
                    "male": [{"min_age": 40, "max_age": 64, "mean": 1, "sd": 1}],
                    "female": [{"min_age": 40, "max_age": 64, "mean": 1, "sd": 1}],
                },
                "skeletal_muscle_mass": {
                    "male": [{"min_age": 40, "max_age": 64, "mean": 1, "sd": 1}],
                    "female": [{"min_age": 40, "max_age": 64, "mean": 1, "sd": 1}],
                },
                "visceral_fat": {
                    "male": [{"min_age": 40, "max_age": 64, "mean": 1, "sd": 1}],
                    "female": [{"min_age": 40, "max_age": 64, "mean": 1, "sd": 1}],
                },
            },
        }
    )

    covered = dict(base)
    covered.update(
        {
            "patient_id": "covered-row",
            "age": 50,
            "sex": "female",
            "ffmi": None,
            "duration": 10,
            "event": 1,
            "ethnicity": "group-a",
        }
    )
    out_of_band = dict(base)
    out_of_band.update(
        {
            "patient_id": "out-of-band-row",
            "age": 65,
            "sex": "male",
            "duration": 11,
            "event": 0,
            "ethnicity": "group-b",
        }
    )
    below_band = dict(base)
    below_band.update(
        {
            "patient_id": "below-band-row",
            "age": 30,
            "sex": "male",
            "duration": 12,
            "event": 1,
            "ethnicity": "group-a",
        }
    )

    report = validate_external_cohort(
        [covered, out_of_band, below_band],
        cohort_name="coverage-fixture",
        reference_panel=banded_panel,
        bins=2,
        bootstrap_replicates=20,
    )

    assert report.rows_received == 3
    assert report.rows_evaluated == 1
    assert report.to_dict()["rows_excluded"] == 2
    assert report.row_exclusion_counts == {
        "age outside reference-panel band coverage": 2
    }
    serialized = json.dumps(report.to_dict())
    assert "out-of-band-row" not in serialized
    assert "below-band-row" not in serialized
    assert any(
        "age outside reference-panel band coverage" in blocker
        for blocker in report.blockers
    )
