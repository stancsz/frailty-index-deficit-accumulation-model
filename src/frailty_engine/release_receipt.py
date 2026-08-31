"""Allow-listed, privacy-safe projection of runtime release identity."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


RECEIPT_SCHEMA_VERSION = "1"
RECEIPT_TYPE = "clinical-healthspan-runtime"


class ReceiptError(ValueError):
    """Raised when a health response cannot become a safe release receipt."""


def _required_text(data: Mapping[str, Any], field: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ReceiptError(f"health response has an invalid {field}")
    return value


def _optional_sha256(data: Mapping[str, Any], field: str) -> str | None:
    value = data.get(field)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ReceiptError(f"health response has an invalid {field}")
    digest = value.lower()
    if len(digest) != 64 or any(
        character not in "0123456789abcdef" for character in digest
    ):
        raise ReceiptError(f"health response has an invalid {field}")
    return digest


def _required_sha256(data: Mapping[str, Any], field: str) -> str:
    value = _optional_sha256(data, field)
    if value is None:
        raise ReceiptError(f"health response has an invalid {field}")
    return value


def _required_bool(data: Mapping[str, Any], field: str) -> bool:
    value = data.get(field)
    if not isinstance(value, bool):
        raise ReceiptError(f"health response has an invalid {field}")
    return value


def _readiness_receipt(data: Mapping[str, Any]) -> dict[str, Any]:
    readiness = data.get("readiness")
    if not isinstance(readiness, Mapping):
        raise ReceiptError("health response is missing readiness metadata")
    status = readiness.get("status")
    blockers = readiness.get("blockers")
    if status not in {"ready", "not_ready"} or not isinstance(blockers, list):
        raise ReceiptError("health response has invalid readiness metadata")
    if not all(isinstance(blocker, str) and blocker.strip() for blocker in blockers):
        raise ReceiptError("health response has invalid readiness blockers")
    if status == "ready" and blockers:
        raise ReceiptError("ready health response must not contain readiness blockers")
    if status == "not_ready" and not blockers:
        raise ReceiptError(
            "not_ready health response must contain at least one readiness blocker"
        )
    return {"status": status, "blockers": list(blockers)}


def _runtime_provenance_receipt(data: Mapping[str, Any]) -> dict[str, Any]:
    """Project build identity without retaining paths or credentials."""

    if not isinstance(data, Mapping):
        raise ReceiptError("health response is missing runtime provenance")
    python_runtime = data.get("python_runtime")
    if not isinstance(python_runtime, Mapping):
        raise ReceiptError("health response has invalid python runtime provenance")
    python_values: dict[str, str] = {}
    for field in ("implementation", "version", "cache_tag"):
        value = python_runtime.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ReceiptError(f"health response has an invalid python runtime {field}")
        python_values[field] = value
    installation_mode = data.get("package_installation_mode")
    if installation_mode not in {"installed_distribution", "source_tree"}:
        raise ReceiptError("health response has an invalid package installation mode")
    return {
        "package_tree_sha256": _optional_sha256(data, "package_tree_sha256"),
        "package_installation_mode": installation_mode,
        "dependency_set_sha256": _required_sha256(data, "dependency_set_sha256"),
        "python_runtime": python_values,
        "configuration_sha256": _required_sha256(data, "configuration_sha256"),
    }


def _source_field_set_sha256(health: Mapping[str, Any]) -> str:
    """Hash the receipt-relevant health schema, including nested field sets."""

    def nested_field_set(value: Any) -> list[str] | None:
        if not isinstance(value, Mapping):
            return None
        return sorted(str(field) for field in value)

    field_set = {
        "top_level": sorted(str(field) for field in health),
        "operational_controls": nested_field_set(health.get("operational_controls")),
        "readiness": nested_field_set(health.get("readiness")),
        "runtime_provenance": {
            "top_level": nested_field_set(health.get("runtime_provenance")),
            "python_runtime": nested_field_set(
                health.get("runtime_provenance", {}).get("python_runtime")
                if isinstance(health.get("runtime_provenance"), Mapping)
                else None
            ),
        },
    }
    encoded = json.dumps(field_set, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()


def health_to_receipt(health: Mapping[str, Any]) -> dict[str, Any]:
    """Project `/health` onto an explicit, non-secret release receipt schema.

    The projection is deliberately allow-listed. Future health fields are not
    copied automatically, so a request body, credential, patient identifier,
    or other accidental addition cannot become part of a persisted receipt.
    """

    if not isinstance(health, Mapping) or health.get("status") != "ok":
        raise ReceiptError("health response is not a successful liveness response")
    fingerprint = _required_text(health, "deployment_fingerprint").lower()
    if len(fingerprint) != 64 or any(
        character not in "0123456789abcdef" for character in fingerprint
    ):
        raise ReceiptError("health response has an invalid deployment_fingerprint")
    controls = health.get("operational_controls")
    if not isinstance(controls, Mapping):
        raise ReceiptError("health response is missing operational controls")

    safe_controls = {
        "auth_required_for_v1": _required_bool(controls, "api_key_required_for_v1"),
        "max_request_bytes": controls.get("max_request_bytes"),
        "structured_request_logging": _required_bool(
            controls, "structured_request_logging"
        ),
        "model_approval_manifest_configured": _required_bool(
            controls, "model_approval_manifest_configured"
        ),
        "model_approval_binding_valid": _required_bool(
            controls, "model_approval_binding_valid"
        ),
        "reference_panel_fixture_only": _required_bool(
            controls, "reference_panel_fixture_only"
        ),
    }
    if (
        isinstance(safe_controls["max_request_bytes"], bool)
        or not isinstance(safe_controls["max_request_bytes"], int)
        or safe_controls["max_request_bytes"] <= 0
    ):
        raise ReceiptError("health response has an invalid max_request_bytes")

    model_artifact_sha256 = _optional_sha256(health, "model_artifact_sha256")
    reference_panel_sha256 = _optional_sha256(health, "reference_panel_sha256")
    runtime_provenance = _runtime_provenance_receipt(health.get("runtime_provenance"))
    readiness_receipt = _readiness_receipt(health)
    model_production_ready = _required_bool(health, "model_production_ready")
    model_uncertainty_validated = _required_bool(health, "model_uncertainty_validated")
    reference_panel_production_ready = _required_bool(
        health, "reference_panel_production_ready"
    )
    reference_panel_fixture_only = _required_bool(
        health, "reference_panel_fixture_only"
    )
    reference_panel_readiness = _required_text(health, "reference_panel_readiness")
    expected_panel_readiness = (
        "development_fixture_only"
        if reference_panel_fixture_only
        else (
            "loaded_production_ready"
            if reference_panel_production_ready and reference_panel_sha256 is not None
            else "loaded_unapproved"
        )
    )
    if reference_panel_readiness != expected_panel_readiness:
        raise ReceiptError(
            "health response has inconsistent reference-panel readiness state"
        )
    if reference_panel_fixture_only != safe_controls["reference_panel_fixture_only"]:
        raise ReceiptError(
            "health response has inconsistent reference-panel fixture-only state"
        )
    if reference_panel_production_ready and reference_panel_fixture_only:
        raise ReceiptError(
            "health response cannot mark a reference panel both production-ready and fixture-only"
        )
    if readiness_receipt["status"] == "ready" and (
        model_artifact_sha256 is None or reference_panel_sha256 is None
    ):
        raise ReceiptError(
            "ready health response must include model and reference-panel SHA-256 identities"
        )
    if readiness_receipt["status"] == "ready":
        if not model_production_ready:
            raise ReceiptError(
                "ready health response requires a production-ready model"
            )
        if not model_uncertainty_validated:
            raise ReceiptError(
                "ready health response requires validated model uncertainty"
            )
        if not reference_panel_production_ready or reference_panel_fixture_only:
            raise ReceiptError(
                "ready health response requires a non-fixture production-ready reference panel"
            )
        if not safe_controls["auth_required_for_v1"]:
            raise ReceiptError(
                "ready health response requires API-key protection for v1 endpoints"
            )
        if runtime_provenance["package_tree_sha256"] is None:
            raise ReceiptError(
                "ready health response requires an installed package-tree SHA-256 identity"
            )

    return {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "receipt_type": RECEIPT_TYPE,
        "captured_from": "GET /health",
        "source_field_set_sha256": _source_field_set_sha256(health),
        "service": _required_text(health, "service"),
        "service_version": _required_text(health, "service_version"),
        "deployment_fingerprint": fingerprint,
        "model": {
            "model_id": _required_text(health, "model_id"),
            "artifact_sha256": model_artifact_sha256,
            "production_ready": model_production_ready,
            "uncertainty_validated": model_uncertainty_validated,
        },
        "reference_panel": {
            "panel_id": _required_text(health, "reference_panel_id"),
            "source_sha256": reference_panel_sha256,
            "production_ready": reference_panel_production_ready,
            "fixture_only": reference_panel_fixture_only,
            "readiness": reference_panel_readiness,
        },
        "runtime_provenance": runtime_provenance,
        "approval_binding_valid": _required_bool(
            controls, "model_approval_binding_valid"
        ),
        "readiness": readiness_receipt,
        "operational_controls": safe_controls,
    }


def receipt_matches_health(
    receipt: Mapping[str, Any], health: Mapping[str, Any]
) -> bool:
    """Return whether a stored receipt exactly matches fresh health metadata."""

    try:
        if receipt.get("schema_version") != RECEIPT_SCHEMA_VERSION:
            return False
        if receipt.get("source_field_set_sha256") != _source_field_set_sha256(health):
            return False
        return dict(receipt) == health_to_receipt(health)
    except ReceiptError:
        return False
