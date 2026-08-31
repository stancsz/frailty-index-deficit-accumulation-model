"""Exercise the installed package through a real loopback HTTP server."""

from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from frailty_engine.calibration import ReferencePanel
from frailty_engine.__main__ import sample_payload
from frailty_engine.model import GompertzMapper
from frailty_engine.pipeline import MODEL_VECTOR_FEATURE_NAMES
from frailty_engine.release_provenance import runtime_provenance
from frailty_engine.survey_design import SurveyDesign
from frailty_engine.training import fit_xgb_survival


_ROOT = Path(__file__).parents[1]
_MAX_RESPONSE_BYTES = 256 * 1024
_STARTUP_TIMEOUT_SECONDS = 10.0
_EXPECTED_HEADERS = {
    "cache-control": "no-store",
    "content-security-policy": "default-src 'none'; frame-ancestors 'none'",
    "permissions-policy": "camera=(), geolocation=(), microphone=()",
    "referrer-policy": "no-referrer",
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
}


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _clean_environment() -> dict[str, str]:
    environment = os.environ.copy()
    for name in (
        "FRAILTY_API_KEY",
        "FRAILTY_MAX_REQUEST_BYTES",
        "FRAILTY_MODEL_PATH",
        "FRAILTY_MODEL_APPROVAL_PATH",
        "FRAILTY_REFERENCE_PANEL_PATH",
        "FRAILTY_REQUIRE_PRODUCTION",
    ):
        environment.pop(name, None)
    return environment


def _request(
    url: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    headers: Mapping[str, str] | None = None,
) -> tuple[int, dict[str, str], bytes]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if headers:
        request_headers.update(headers)
    request = Request(
        url,
        data=body,
        headers=request_headers,
        method=method,
    )
    try:
        response = urlopen(request, timeout=5.0)
    except HTTPError as error:
        response = error
    except URLError as error:
        raise RuntimeError(f"serving smoke request failed: {error.reason}") from error
    with response:
        response_body = response.read(_MAX_RESPONSE_BYTES + 1)
        if len(response_body) > _MAX_RESPONSE_BYTES:
            raise RuntimeError("serving smoke response exceeded the size limit")
        return response.status, dict(response.headers.items()), response_body


def _wait_for_health(base_url: str, process: subprocess.Popen[bytes]) -> None:
    deadline = time.monotonic() + _STARTUP_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("uvicorn exited before the health endpoint was ready")
        try:
            status, _, _ = _request(f"{base_url}/health")
        except (RuntimeError, TimeoutError, OSError):
            time.sleep(0.1)
            continue
        if status == 200:
            return
        time.sleep(0.1)
    raise RuntimeError("uvicorn health endpoint did not become ready in time")


def _assert_headers(headers: dict[str, str], path: str) -> None:
    normalized = {name.lower(): value for name, value in headers.items()}
    for name, value in _EXPECTED_HEADERS.items():
        if normalized.get(name) != value:
            raise RuntimeError(f"{path} is missing the expected {name} header")
    if not normalized.get("x-request-id"):
        raise RuntimeError(f"{path} is missing the request ID header")


def _json_body(body: bytes, path: str) -> dict[str, Any]:
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"{path} did not return a JSON object") from error
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} did not return a JSON object")
    return payload


def _software_gate_panel_mapping() -> dict[str, Any]:
    """Build non-clinical panel data for the strict serving-path smoke only.

    This deliberately is not a shipped reference panel.  The values differ
    from the development fixture so the readiness path also exercises the
    fixture-content guard, while the release remains temporary and forbidden
    for clinical use.
    """

    def band(mean: float, standard_deviation: float) -> list[dict[str, Any]]:
        return [
            {
                "min_age": 18,
                "max_age": 120,
                "mean": mean,
                "sd": standard_deviation,
                "source": "temporary-software-gate-only",
            }
        ]

    return {
        "panel_id": "temporary-software-gate-panel",
        "version": "software-gate-smoke-v1",
        "production_ready": True,
        "fixture_only": False,
        "source_note": (
            "Temporary non-clinical values used only to exercise the strict "
            "serving gate; not a reference panel and not for patient care."
        ),
        "features": {
            "phase_angle": {"male": band(6.2, 0.9), "female": band(5.8, 0.8)},
            "ecw_tbw": {"male": band(0.385, 0.028), "female": band(0.395, 0.028)},
            "ffmi": {"male": band(18.5, 2.8), "female": band(16.5, 2.4)},
            "skeletal_muscle_mass": {
                "male": band(32.0, 7.0),
                "female": band(23.0, 5.5),
            },
            "visceral_fat": {"male": band(9.0, 5.0), "female": band(7.0, 4.5)},
        },
    }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_software_gate_release(directory: Path) -> dict[str, Path]:
    """Create an ephemeral hash-bound release for the strict software gate."""

    panel_path = directory / "temporary-reference-panel.json"
    panel_data = _software_gate_panel_mapping()
    panel_path.write_text(
        json.dumps(panel_data, ensure_ascii=False, sort_keys=True), encoding="utf-8"
    )
    panel = ReferencePanel.from_json(panel_path)

    base = dict(sample_payload()["measurements"])
    rows: list[dict[str, Any]] = []
    for number in range(8):
        age = 35 + number * 7
        sex = "male" if number % 2 == 0 else "female"
        row = dict(base)
        row.update(
            {
                "patient_id": f"software-gate-{number}",
                "duration": 2.0 + number * 0.75,
                "event": int(number % 3 != 1),
                "age": age,
                "sex": sex,
                "bmi": 22.0 + number * 0.6,
                "phase_angle": (6.0 if sex == "male" else 5.7) + number * 0.03,
                "ecw_tbw": (0.385 if sex == "male" else 0.395) + number * 0.001,
                "ffmi": (18.0 if sex == "male" else 16.0) + number * 0.2,
                "skeletal_muscle_mass": (
                    (31.0 if sex == "male" else 22.0) + number * 0.4
                ),
                "visceral_fat": (8.0 if sex == "male" else 6.5) + number * 0.3,
                "sample_weight": 1.0 + number * 0.05,
            }
        )
        rows.append(row)

    model = fit_xgb_survival(
        rows,
        reference_panel=panel,
        mapper=GompertzMapper(),
        survey_design=SurveyDesign(
            weight_name="sample_weight", weight_kind="case_weight"
        ),
    )
    model_path = model.save_model(directory / "temporary-model.json")
    approval_path = directory / "temporary-model.approval.json"
    approval_path.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "model_id": model.model_id,
                "artifact_sha256": _sha256_file(model_path),
                "feature_names": list(MODEL_VECTOR_FEATURE_NAMES),
                "reference_panel_id": panel.panel_id,
                "reference_panel_sha256": _sha256_file(panel_path),
                "uncertainty_method": "held_out_cohort_bootstrap",
                "log_hazard_se": 0.11,
                "production_ready": True,
                "uncertainty_validated": True,
                "approved_by": "software-gate-smoke",
                "approved_at": "2026-08-28",
                "evidence_refs": ["E-079/serving-software-gate-smoke-only"],
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return {
        "model": model_path,
        "approval": approval_path,
        "panel": panel_path,
    }


def _run_software_gate_contract() -> dict[str, Any]:
    """Exercise strict readiness and authentication over real loopback HTTP.

    The temporary release is a software integration fixture.  Passing this
    function proves serving behavior only; it is not clinical approval.
    """

    with tempfile.TemporaryDirectory(prefix="frailty-serving-gate-") as raw_dir:
        release = _write_software_gate_release(Path(raw_dir))
        environment = _clean_environment()
        environment.update(
            {
                "FRAILTY_API_KEY": "software-gate-smoke-secret",
                "FRAILTY_MODEL_PATH": str(release["model"]),
                "FRAILTY_MODEL_APPROVAL_PATH": str(release["approval"]),
                "FRAILTY_REFERENCE_PANEL_PATH": str(release["panel"]),
                "FRAILTY_REQUIRE_PRODUCTION": "true",
            }
        )
        port = _free_port()
        base_url = f"http://127.0.0.1:{port}"
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "frailty_engine.api:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--log-level",
                "warning",
            ],
            cwd=_ROOT,
            env=environment,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        api_headers = {"X-API-Key": environment["FRAILTY_API_KEY"]}
        try:
            _wait_for_health(base_url, process)
            checks = {
                "/health": _request(f"{base_url}/health"),
                "/readyz": _request(f"{base_url}/readyz"),
                "/metrics-unauthenticated": _request(f"{base_url}/metrics"),
                "/metrics": _request(f"{base_url}/metrics", headers=api_headers),
                "/assessment-unauthenticated": _request(
                    f"{base_url}/v1/assessments",
                    method="POST",
                    payload=sample_payload(),
                ),
                "/assessment": _request(
                    f"{base_url}/v1/assessments",
                    method="POST",
                    payload=sample_payload(),
                    headers=api_headers,
                ),
                "/assessment-invalid": _request(
                    f"{base_url}/v1/assessments",
                    method="POST",
                    payload={"patient_id": "contract-smoke", "measurements": {}},
                    headers=api_headers,
                ),
            }
            for path, (_, headers, _) in checks.items():
                _assert_headers(headers, path)

            health_status, _, health_body = checks["/health"]
            ready_status, _, ready_body = checks["/readyz"]
            missing_metrics_status, _, _ = checks["/metrics-unauthenticated"]
            metrics_status, _, metrics_body = checks["/metrics"]
            missing_assessment_status, _, _ = checks["/assessment-unauthenticated"]
            assessment_status, _, assessment_body = checks["/assessment"]
            invalid_status, _, invalid_body = checks["/assessment-invalid"]
            health = _json_body(health_body, "/health")
            ready = _json_body(ready_body, "/readyz")
            metrics = _json_body(metrics_body, "/metrics")
            assessment = _json_body(assessment_body, "/assessment")
            invalid = _json_body(invalid_body, "/assessment-invalid")
            expected_provenance = runtime_provenance(environment=environment)
            if health.get("runtime_provenance") != expected_provenance:
                raise RuntimeError(
                    "production health provenance does not match the configured process"
                )
            if ready.get("runtime_provenance") != expected_provenance:
                raise RuntimeError(
                    "production readyz provenance does not match the configured process"
                )
            if (
                expected_provenance["package_installation_mode"]
                != "installed_distribution"
            ):
                raise RuntimeError(
                    "strict serving smoke did not run from an installed distribution"
                )
            if (
                health_status != 200
                or health.get("readiness", {}).get("status") != "ready"
                or health.get("reference_panel_readiness") != "loaded_production_ready"
                or health.get("model_production_ready") is not True
                or health.get("model_uncertainty_validated") is not True
                or health.get("approval_binding_valid") is not True
            ):
                raise RuntimeError(
                    "production health contract did not report the strict software gate as ready"
                )
            if (
                ready_status != 200
                or ready.get("status") != "ready"
                or ready.get("reference_panel_readiness") != "loaded_production_ready"
            ):
                raise RuntimeError("production readyz contract did not report ready")
            if missing_metrics_status != 401 or missing_assessment_status != 401:
                raise RuntimeError("configured API-key gate did not fail closed")
            if metrics_status != 200 or "requests_total" not in metrics:
                raise RuntimeError("authenticated metrics contract was not bounded")
            if (
                assessment_status != 200
                or "metrics" not in assessment
                or b"contract-smoke" in assessment_body
            ):
                raise RuntimeError(
                    "authenticated production assessment contract was not typed and privacy-safe"
                )
            if (
                invalid_status != 422
                or invalid.get("error", {}).get("code") != "InsufficientDataError"
                or b"contract-smoke" in invalid_body
            ):
                raise RuntimeError("authenticated invalid assessment contract failed")
            return {
                "health": health_status,
                "readyz": ready_status,
                "metrics_unauthenticated": missing_metrics_status,
                "metrics": metrics_status,
                "assessment_unauthenticated": missing_assessment_status,
                "assessment": assessment_status,
                "invalid_assessment": invalid_status,
                "headers_checked": len(checks),
                "api_key_gate": "observed",
                "production_software_gate": "observed",
                "clinical_use": "forbidden",
            }
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)


def _run() -> dict[str, Any]:
    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "frailty_engine.api:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "warning",
        ],
        cwd=_ROOT,
        env=_clean_environment(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _wait_for_health(base_url, process)
        checks = {
            "/health": _request(f"{base_url}/health"),
            "/readyz": _request(f"{base_url}/readyz"),
            "/metrics": _request(f"{base_url}/metrics"),
            "/v1/assessments": _request(
                f"{base_url}/v1/assessments",
                method="POST",
                payload=sample_payload(),
            ),
            "/v1/assessments-invalid": _request(
                f"{base_url}/v1/assessments",
                method="POST",
                payload={"patient_id": "contract-smoke", "measurements": {}},
            ),
        }
        for path, (_, headers, _) in checks.items():
            _assert_headers(headers, path)

        health_status, _, health_body = checks["/health"]
        ready_status, _, ready_body = checks["/readyz"]
        metrics_status, _, metrics_body = checks["/metrics"]
        assessment_status, _, assessment_body = checks["/v1/assessments"]
        invalid_status, _, invalid_body = checks["/v1/assessments-invalid"]
        health = _json_body(health_body, "/health")
        ready = _json_body(ready_body, "/readyz")
        metrics = _json_body(metrics_body, "/metrics")
        assessment = _json_body(assessment_body, "/v1/assessments")
        invalid = _json_body(invalid_body, "/v1/assessments-invalid")
        expected_provenance = runtime_provenance(environment=_clean_environment())
        if health.get("runtime_provenance") != expected_provenance:
            raise RuntimeError(
                "health runtime provenance does not match the installed process"
            )
        if ready.get("runtime_provenance") != expected_provenance:
            raise RuntimeError(
                "readyz runtime provenance does not match the installed process"
            )
        if expected_provenance["package_installation_mode"] != "installed_distribution":
            raise RuntimeError(
                "serving smoke did not run from an installed distribution"
            )
        if (
            health_status != 200
            or health.get("readiness", {}).get("status") != "not_ready"
        ):
            raise RuntimeError(
                "health contract did not expose the development boundary"
            )
        if ready_status != 503 or ready.get("status") != "not_ready":
            raise RuntimeError(
                "readyz contract did not fail closed for the development fixture"
            )
        if metrics_status != 200 or "requests_total" not in metrics:
            raise RuntimeError("metrics contract did not return bounded diagnostics")
        if assessment_status != 200 or "metrics" not in assessment:
            raise RuntimeError("assessment contract did not return a typed response")
        if (
            invalid_status != 422
            or invalid.get("error", {}).get("code") != "InsufficientDataError"
        ):
            raise RuntimeError(
                "invalid assessment contract did not return the typed 422"
            )
        if b"contract-smoke" in assessment_body or b"contract-smoke" in invalid_body:
            raise RuntimeError(
                "assessment response echoed the smoke patient identifier"
            )
        production = _run_software_gate_contract()
        return {
            "health": health_status,
            "readyz": ready_status,
            "metrics": metrics_status,
            "assessment": assessment_status,
            "invalid_assessment": invalid_status,
            "headers_checked": len(checks),
            "clinical_use": "forbidden",
            "package_tree_sha256": expected_provenance["package_tree_sha256"],
            "package_installation_mode": expected_provenance[
                "package_installation_mode"
            ],
            "dependency_set_sha256": expected_provenance["dependency_set_sha256"],
            "production": production,
        }
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def main() -> int:
    result = _run()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
