"""FastAPI gateway enforcing the MVV before assessment."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
from pathlib import Path
import re
from threading import Lock
import time
from typing import Any, Mapping
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .calibration import (
    ReferencePanel,
    default_development_panel,
    is_development_fixture_content,
    panel_readiness,
)
from .exceptions import (
    FrailtyEngineError,
    InsufficientDataError,
    ModelUnavailableError,
    PredictionFailure,
    ValidationError,
)
from .model import DevelopmentPredictor, XGBSurvivalModel
from .pipeline import MODEL_VECTOR_FEATURE_NAMES, assess
from .progress import build_progress_report
from .release_provenance import (
    provenance_is_ready_for_strict_admission,
    provenance_is_well_formed,
    runtime_provenance,
)
from .schemas import (
    AssessmentComparisonRequest,
    AssessmentComparisonResponse,
    AssessmentRequest,
    AssessmentResponse,
)

logger = logging.getLogger("frailty_engine.api")
_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_DEFAULT_MAX_REQUEST_BYTES = 64 * 1024
_SERVICE_VERSION = "0.1.0"
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)
_SECURITY_RESPONSE_HEADERS = {
    "Cache-Control": "no-store",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
    "Permissions-Policy": "camera=(), geolocation=(), microphone=()",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
}


class _RequestTooLargeError(Exception):
    """Internal signal raised before a request body reaches FastAPI parsing."""


class _RequestMetrics:
    """Bounded process-local request metrics that never retain request labels."""

    _STATUS_CLASSES = ("2xx", "3xx", "4xx", "5xx", "other")

    def __init__(self) -> None:
        self._lock = Lock()
        self._requests_total = 0
        self._responses_by_status_class = dict.fromkeys(self._STATUS_CLASSES, 0)
        self._duration_ms_total = 0.0
        self._duration_ms_max = 0.0
        self._oversize_rejections = 0

    @staticmethod
    def _status_class(status_code: int) -> str:
        if 200 <= status_code < 300:
            return "2xx"
        if 300 <= status_code < 400:
            return "3xx"
        if 400 <= status_code < 500:
            return "4xx"
        if 500 <= status_code < 600:
            return "5xx"
        return "other"

    def record(
        self, status_code: int, duration_ms: float, *, oversize_rejection: bool = False
    ) -> None:
        with self._lock:
            self._requests_total += 1
            status_class = self._status_class(status_code)
            self._responses_by_status_class[status_class] += 1
            self._duration_ms_total += duration_ms
            self._duration_ms_max = max(self._duration_ms_max, duration_ms)
            if oversize_rejection:
                self._oversize_rejections += 1

    def snapshot(self) -> dict[str, Any]:
        """Return a JSON-safe snapshot without route or caller identifiers."""

        with self._lock:
            return {
                "format": "clinical-healthspan-metrics-v1",
                "process_local": True,
                "requests_total": self._requests_total,
                "responses_by_status_class": dict(self._responses_by_status_class),
                "duration_ms": {
                    "observed_requests": self._requests_total,
                    "total": round(self._duration_ms_total, 3),
                    "max": round(self._duration_ms_max, 3),
                },
                "request_size_rejections": self._oversize_rejections,
            }


def _configured_panel() -> ReferencePanel:
    path = os.getenv("FRAILTY_REFERENCE_PANEL_PATH")
    return ReferencePanel.from_json(Path(path)) if path else default_development_panel()


def _configured_predictor() -> Any:
    path = os.getenv("FRAILTY_MODEL_PATH")
    approval_manifest = os.getenv("FRAILTY_MODEL_APPROVAL_PATH")
    if approval_manifest and not path:
        raise ValueError("FRAILTY_MODEL_APPROVAL_PATH requires FRAILTY_MODEL_PATH")
    return (
        XGBSurvivalModel.load_model(
            path,
            MODEL_VECTOR_FEATURE_NAMES,
            approval_manifest=approval_manifest,
        )
        if path
        else DevelopmentPredictor()
    )


def _configured_max_request_bytes() -> int:
    raw_value = os.getenv("FRAILTY_MAX_REQUEST_BYTES", str(_DEFAULT_MAX_REQUEST_BYTES))
    try:
        value = int(raw_value)
    except ValueError as error:
        raise ValueError("FRAILTY_MAX_REQUEST_BYTES must be an integer") from error
    if value <= 0:
        raise ValueError("FRAILTY_MAX_REQUEST_BYTES must be positive")
    return value


def _configured_bool(name: str, default: bool = False) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    normalized = raw_value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be a boolean value")


def _is_sha256_digest(value: Any) -> bool:
    """Return whether a runtime identity is a complete SHA-256 digest."""

    return isinstance(value, str) and _SHA256_PATTERN.fullmatch(value) is not None


def _readiness_blockers(
    predictor: Any,
    panel: ReferencePanel,
    api_key: str | None,
    process_provenance: Mapping[str, Any],
    require_production: bool,
) -> list[str]:
    blockers: list[str] = []
    if not provenance_is_well_formed(process_provenance):
        blockers.append(
            "runtime provenance is incomplete; admit traffic only from a verified installed package"
        )
    elif require_production and not provenance_is_ready_for_strict_admission(
        process_provenance
    ):
        blockers.append(
            "production admission requires a complete installed-distribution provenance identity"
        )
    if not getattr(predictor, "production_ready", False):
        blockers.append(
            "predictor is not marked production_ready; load an approved model artifact"
        )
    if not getattr(predictor, "uncertainty_validated", False):
        blockers.append(
            "predictor uncertainty is not marked validated; supply cohort-reviewed uncertainty"
        )
    if getattr(predictor, "production_ready", False) and not _is_sha256_digest(
        getattr(predictor, "artifact_sha256", None)
    ):
        blockers.append(
            "production-ready predictor has no valid artifact SHA-256; configure an immutable hashed model artifact"
        )
    if not panel.production_ready:
        blockers.append(
            "reference panel is not marked production_ready; configure an approved panel"
        )
    if getattr(panel, "fixture_only", False):
        blockers.append(
            "reference panel is a development fixture; configure an approved panel"
        )
    elif panel.production_ready and is_development_fixture_content(panel):
        blockers.append(
            "reference panel contains the shipped development fixture bands; replace it with an approved panel"
        )
    if panel.production_ready and not _is_sha256_digest(
        getattr(panel, "source_sha256", None)
    ):
        blockers.append(
            "production-ready reference panel has no valid source SHA-256; load the frozen panel file"
        )
    if api_key is None:
        blockers.append(
            "FRAILTY_API_KEY is not configured; configure it before admitting traffic"
        )
    if getattr(predictor, "requires_approval_manifest", False):
        if not getattr(predictor, "approval_manifest_path", None):
            blockers.append(
                "predictor approval manifest is not configured; provide a hash-bound approval manifest"
            )
        approved_panel_id = getattr(predictor, "approved_reference_panel_id", None)
        if approved_panel_id and approved_panel_id != panel.panel_id:
            blockers.append(
                "approved model reference panel does not match the configured panel"
            )
        approved_panel_sha256 = getattr(
            predictor, "approved_reference_panel_sha256", None
        )
        if approved_panel_sha256:
            configured_panel_sha256 = getattr(panel, "source_sha256", None)
            if configured_panel_sha256 is None:
                blockers.append(
                    "configured reference panel has no source SHA-256 for approval binding"
                )
            elif approved_panel_sha256 != configured_panel_sha256:
                blockers.append(
                    "approved model reference panel hash does not match the configured panel"
                )
    return blockers


def _approval_binding_is_valid(predictor: Any, panel: ReferencePanel) -> bool:
    """Report whether a manifest-required model is bound to this panel."""

    if not getattr(predictor, "requires_approval_manifest", False):
        return True
    if not getattr(predictor, "approval_manifest_path", None):
        return False
    approved_panel_id = getattr(predictor, "approved_reference_panel_id", None)
    approved_panel_sha256 = getattr(predictor, "approved_reference_panel_sha256", None)
    configured_panel_sha256 = getattr(panel, "source_sha256", None)
    return bool(
        approved_panel_id
        and approved_panel_sha256
        and configured_panel_sha256
        and approved_panel_id == panel.panel_id
        and approved_panel_sha256 == configured_panel_sha256
    )


def _runtime_identity(
    predictor: Any,
    panel: ReferencePanel,
    *,
    configured_api_key: str | None,
    max_request_bytes: int,
    process_provenance: Mapping[str, Any],
) -> dict[str, Any]:
    """Return a non-secret identity for the currently served configuration."""

    artifact_sha256 = getattr(predictor, "artifact_sha256", None)
    panel_sha256 = getattr(panel, "source_sha256", None)
    approval_binding_valid = _approval_binding_is_valid(predictor, panel)
    identity = {
        "service_version": _SERVICE_VERSION,
        "model_id": getattr(predictor, "model_id", "unknown"),
        "model_artifact_sha256": artifact_sha256,
        "reference_panel_id": panel.panel_id,
        "reference_panel_sha256": panel_sha256,
        "approval_binding_valid": approval_binding_valid,
        "api_key_required": configured_api_key is not None,
        "max_request_bytes": max_request_bytes,
        "runtime_provenance": dict(process_provenance),
    }
    encoded = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return {
        **identity,
        "deployment_fingerprint": hashlib.sha256(encoded).hexdigest(),
    }


def _request_id(request: Request) -> str:
    candidate = request.headers.get("x-request-id", "")
    return candidate if _REQUEST_ID_PATTERN.fullmatch(candidate) else uuid4().hex


def _provided_api_key(request: Request) -> str | None:
    direct = request.headers.get("x-api-key")
    if direct:
        return direct
    authorization = request.headers.get("authorization", "")
    scheme, _, value = authorization.partition(" ")
    return value if scheme.lower() == "bearer" and value else None


_PREDICTION_FAILURE_CAUSES = (
    ModelUnavailableError,
    RuntimeError,
    TypeError,
    ValueError,
)


def _run_assessment_safely(
    payload: dict[str, Any],
    *,
    predictor: Any,
    reference_panel: ReferencePanel,
) -> dict[str, Any]:
    """Invoke ``assess`` and map non-domain predictor failures to ``PredictionFailure``.

    The HTTP layer returns a generic 500 envelope without echoing the underlying
    exception text or caller-supplied data. The original exception is chained
    for bounded server-side diagnostics and ``__cause__`` inspection.
    """

    try:
        return assess(
            payload,
            predictor=predictor,
            reference_panel=reference_panel,
        )
    except (InsufficientDataError, ValidationError):
        raise
    except _PREDICTION_FAILURE_CAUSES as error:
        raise PredictionFailure("prediction failed") from error


def create_app(
    *, predictor: Any | None = None, reference_panel: ReferencePanel | None = None
) -> FastAPI:
    """Create a serving app with injectable dependencies and env-based defaults.

    ``FRAILTY_MODEL_PATH`` and ``FRAILTY_REFERENCE_PANEL_PATH`` are optional
    deployment settings. When absent, the app intentionally uses development
    fixtures and exposes their non-production status in every assessment.
    """

    runtime_predictor = predictor if predictor is not None else _configured_predictor()
    runtime_panel = (
        reference_panel if reference_panel is not None else _configured_panel()
    )
    configured_api_key = os.getenv("FRAILTY_API_KEY") or None
    max_request_bytes = _configured_max_request_bytes()
    require_production = _configured_bool("FRAILTY_REQUIRE_PRODUCTION")
    process_provenance = runtime_provenance()
    startup_blockers = _readiness_blockers(
        runtime_predictor,
        runtime_panel,
        configured_api_key,
        process_provenance,
        require_production,
    )
    if require_production and startup_blockers:
        raise RuntimeError(
            "FRAILTY_REQUIRE_PRODUCTION is enabled but readiness is blocked: "
            + "; ".join(startup_blockers)
        )
    request_metrics = _RequestMetrics()

    def current_readiness_blockers() -> list[str]:
        """Re-evaluate mutable runtime state for every health/readiness probe."""

        return _readiness_blockers(
            runtime_predictor,
            runtime_panel,
            configured_api_key,
            process_provenance,
            require_production,
        )

    app = FastAPI(title="Clinical Healthspan Engine", version=_SERVICE_VERSION)

    @app.middleware("http")
    async def operational_controls(request: Request, call_next: Any) -> Any:
        started = time.perf_counter()
        request_id = _request_id(request)
        original_receive = request.receive
        received_bytes = 0
        oversize_rejection = False

        async def limited_receive() -> dict[str, Any]:
            nonlocal received_bytes
            message = await original_receive()
            if message["type"] == "http.request":
                received_bytes += len(message.get("body", b""))
                if received_bytes > max_request_bytes:
                    raise _RequestTooLargeError
            return message

        request._receive = limited_receive

        if (
            request.url.path.startswith("/v1/") or request.url.path == "/metrics"
        ) and configured_api_key is not None:
            provided_api_key = _provided_api_key(request)
            if provided_api_key is None or not hmac.compare_digest(
                provided_api_key, configured_api_key
            ):
                response = JSONResponse(
                    status_code=401,
                    content={
                        "error": {
                            "code": "AuthenticationRequired",
                            "message": "configure a valid API key for this endpoint",
                        }
                    },
                    headers={"WWW-Authenticate": "Bearer"},
                )
                response.headers["X-Request-ID"] = request_id
                response.headers["Connection"] = "close"
                request_metrics.record(401, (time.perf_counter() - started) * 1000)
                return response

        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                declared_length = int(content_length)
            except ValueError:
                response = JSONResponse(
                    status_code=400,
                    content={
                        "error": {
                            "code": "InvalidContentLength",
                            "message": "content-length must be an integer",
                        }
                    },
                )
                response.headers["X-Request-ID"] = request_id
                response.headers["Connection"] = "close"
                response.headers["Retry-After"] = "1"
                request_metrics.record(400, (time.perf_counter() - started) * 1000)
                return response
            if declared_length < 0 or declared_length > max_request_bytes:
                response = JSONResponse(
                    status_code=413,
                    content={
                        "error": {
                            "code": "RequestTooLarge",
                            "message": (
                                "request body exceeds the configured limit of "
                                f"{max_request_bytes} bytes"
                            ),
                        }
                    },
                )
                response.headers["X-Request-ID"] = request_id
                response.headers["Connection"] = "close"
                response.headers["Retry-After"] = "1"
                request_metrics.record(
                    413,
                    (time.perf_counter() - started) * 1000,
                    oversize_rejection=True,
                )
                return response

        if request.method in {"POST", "PUT", "PATCH"}:
            try:
                await request.body()
            except _RequestTooLargeError:
                status_code = 413
                response = JSONResponse(
                    status_code=status_code,
                    content={
                        "error": {
                            "code": "RequestTooLarge",
                            "message": (
                                "request body exceeds the configured limit of "
                                f"{max_request_bytes} bytes"
                            ),
                        }
                    },
                )
                response.headers["X-Request-ID"] = request_id
                response.headers["Connection"] = "close"
                response.headers["Retry-After"] = "1"
                logger.info(
                    json.dumps(
                        {
                            "event": "http_request",
                            "method": request.method,
                            "path": request.url.path,
                            "request_id": request_id,
                            "status_code": status_code,
                            "duration_ms": round(
                                (time.perf_counter() - started) * 1000, 3
                            ),
                        },
                        sort_keys=True,
                    )
                )
                request_metrics.record(
                    status_code,
                    (time.perf_counter() - started) * 1000,
                    oversize_rejection=True,
                )
                return response

        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Request-ID"] = request_id
            return response
        except _RequestTooLargeError:
            status_code = 413
            oversize_rejection = True
            response = JSONResponse(
                status_code=status_code,
                content={
                    "error": {
                        "code": "RequestTooLarge",
                        "message": (
                            "request body exceeds the configured limit of "
                            f"{max_request_bytes} bytes"
                        ),
                    }
                },
            )
            response.headers["X-Request-ID"] = request_id
            response.headers["Connection"] = "close"
            response.headers["Retry-After"] = "1"
            return response
        finally:
            request_metrics.record(
                status_code,
                (time.perf_counter() - started) * 1000,
                oversize_rejection=oversize_rejection,
            )
            logger.info(
                json.dumps(
                    {
                        "event": "http_request",
                        "method": request.method,
                        "path": request.url.path,
                        "request_id": request_id,
                        "status_code": status_code,
                        "duration_ms": round((time.perf_counter() - started) * 1000, 3),
                    },
                    sort_keys=True,
                )
            )

    @app.middleware("http")
    async def security_response_headers(request: Request, call_next: Any) -> Any:
        """Prevent caching and browser reinterpretation of API responses."""

        response = await call_next(request)
        for name, value in _SECURITY_RESPONSE_HEADERS.items():
            response.headers[name] = value
        return response

    @app.exception_handler(InsufficientDataError)
    async def insufficient_data_handler(
        _: Request, error: InsufficientDataError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "InsufficientDataError",
                    "message": str(error),
                    "missing_requirements": error.missing_requirements,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        _: Request, error: RequestValidationError
    ) -> JSONResponse:
        field_errors = {
            ".".join(str(part) for part in item.get("loc", ()) if part != "body"): str(
                item.get("msg", "invalid request")
            )
            for item in error.errors()
        }
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "RequestValidationError",
                    "message": "request envelope is invalid",
                    "field_errors": field_errors,
                }
            },
        )

    @app.exception_handler(ValidationError)
    async def validation_handler(_: Request, error: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "ValidationError",
                    "message": str(error),
                    "field_errors": error.field_errors,
                }
            },
        )

    @app.exception_handler(FrailtyEngineError)
    async def engine_handler(_: Request, error: FrailtyEngineError) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"error": {"code": type(error).__name__, "message": str(error)}},
        )

    @app.exception_handler(PredictionFailure)
    async def prediction_failure_handler(
        _: Request, error: PredictionFailure
    ) -> JSONResponse:
        # Generic envelope: never echo or log the chained exception text, request
        # data, patient identifiers, model paths, or stack traces. The exception
        # class is enough to route a bounded server-side diagnostic.
        cause = error.__cause__
        cause_type = type(cause).__name__ if cause is not None else "unknown"
        logger.error("prediction failure error_type=%s", cause_type)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "PredictionFailure",
                    "message": "prediction failed",
                }
            },
        )

    @app.get("/metrics")
    async def metrics() -> dict[str, Any]:
        """Return bounded process-local metrics for operational diagnostics."""

        return request_metrics.snapshot()

    @app.get("/health")
    async def health() -> dict[str, Any]:
        readiness_blockers = current_readiness_blockers()
        runtime_identity = _runtime_identity(
            runtime_predictor,
            runtime_panel,
            configured_api_key=configured_api_key,
            max_request_bytes=max_request_bytes,
            process_provenance=process_provenance,
        )
        return {
            "status": "ok",
            "service": "clinical-healthspan-engine",
            "service_version": runtime_identity["service_version"],
            "deployment_fingerprint": runtime_identity["deployment_fingerprint"],
            "runtime_provenance": runtime_identity["runtime_provenance"],
            "model_id": runtime_identity["model_id"],
            "model_artifact_sha256": runtime_identity["model_artifact_sha256"],
            "model_production_ready": bool(
                getattr(runtime_predictor, "production_ready", False)
            ),
            "model_uncertainty_validated": bool(
                getattr(runtime_predictor, "uncertainty_validated", False)
            ),
            "reference_panel_id": runtime_panel.panel_id,
            "reference_panel_sha256": runtime_identity["reference_panel_sha256"],
            "reference_panel_production_ready": runtime_panel.production_ready,
            "reference_panel_fixture_only": bool(
                getattr(runtime_panel, "fixture_only", False)
            ),
            "reference_panel_readiness": panel_readiness(runtime_panel),
            "approval_binding_valid": runtime_identity["approval_binding_valid"],
            "readiness": {
                "status": "ready" if not readiness_blockers else "not_ready",
                "blockers": readiness_blockers,
            },
            "operational_controls": {
                "api_key_required_for_v1": configured_api_key is not None,
                "max_request_bytes": max_request_bytes,
                "structured_request_logging": True,
                "model_approval_manifest_configured": bool(
                    getattr(runtime_predictor, "approval_manifest_path", None)
                ),
                "model_approval_binding_valid": _approval_binding_is_valid(
                    runtime_predictor, runtime_panel
                ),
                "reference_panel_fixture_only": bool(
                    getattr(runtime_panel, "fixture_only", False)
                ),
            },
        }

    @app.get("/readyz")
    async def ready() -> JSONResponse:
        """Return deployment readiness separately from process liveness."""

        readiness_blockers = current_readiness_blockers()
        runtime_identity = _runtime_identity(
            runtime_predictor,
            runtime_panel,
            configured_api_key=configured_api_key,
            max_request_bytes=max_request_bytes,
            process_provenance=process_provenance,
        )
        # Keep non-secret release identity on both probes so a readiness
        # transition can be reconciled with the liveness receipt without
        # logging request data or exposing credentials.
        identity_content = {
            "model_id": runtime_identity["model_id"],
            "model_artifact_sha256": runtime_identity["model_artifact_sha256"],
            "model_production_ready": bool(
                getattr(runtime_predictor, "production_ready", False)
            ),
            "model_uncertainty_validated": bool(
                getattr(runtime_predictor, "uncertainty_validated", False)
            ),
            "reference_panel_id": runtime_identity["reference_panel_id"],
            "reference_panel_sha256": runtime_identity["reference_panel_sha256"],
            "reference_panel_production_ready": runtime_panel.production_ready,
            "reference_panel_fixture_only": bool(
                getattr(runtime_panel, "fixture_only", False)
            ),
            "reference_panel_readiness": panel_readiness(runtime_panel),
            "approval_binding_valid": runtime_identity["approval_binding_valid"],
            "runtime_provenance": runtime_identity["runtime_provenance"],
        }

        if readiness_blockers:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "not_ready",
                    "service": "clinical-healthspan-engine",
                    "service_version": runtime_identity["service_version"],
                    "deployment_fingerprint": runtime_identity[
                        "deployment_fingerprint"
                    ],
                    "blockers": readiness_blockers,
                    **identity_content,
                },
            )
        return JSONResponse(
            status_code=200,
            content={
                "status": "ready",
                "service": "clinical-healthspan-engine",
                "service_version": runtime_identity["service_version"],
                "deployment_fingerprint": runtime_identity["deployment_fingerprint"],
                "blockers": [],
                **identity_content,
            },
        )

    @app.post("/v1/assessments", response_model=AssessmentResponse)
    async def create_assessment(payload: AssessmentRequest) -> AssessmentResponse:
        return _run_assessment_safely(
            payload.model_dump(),
            predictor=runtime_predictor,
            reference_panel=runtime_panel,
        )

    @app.post(
        "/v1/assessment-comparisons",
        response_model=AssessmentComparisonResponse,
    )
    async def create_assessment_comparison(
        payload: AssessmentComparisonRequest,
    ) -> AssessmentComparisonResponse:
        previous = _run_assessment_safely(
            {
                "patient_id": payload.previous.patient_id,
                "measurements": payload.previous.measurements,
            },
            predictor=runtime_predictor,
            reference_panel=runtime_panel,
        )
        current = _run_assessment_safely(
            {
                "patient_id": payload.current.patient_id,
                "measurements": payload.current.measurements,
            },
            predictor=runtime_predictor,
            reference_panel=runtime_panel,
        )
        try:
            return build_progress_report(
                previous,
                current,
                previous_assessed_at=payload.previous.assessed_at,
                current_assessed_at=payload.current.assessed_at,
            )
        except ValueError as error:
            raise ValidationError(
                str(error), field_errors={"snapshots": str(error)}
            ) from error

    return app


app = create_app()
