"""Capture and reconcile a privacy-safe receipt from the running health endpoint."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from frailty_engine.release_receipt import (
    ReceiptError,
    health_to_receipt,
    receipt_matches_health,
)


_MAX_HEALTH_BYTES = 256 * 1024


def fetch_health(url: str, *, timeout_seconds: float = 10.0) -> dict[str, Any]:
    """Fetch a bounded JSON health response without sending a request body."""

    if not url.startswith(("http://", "https://")):
        raise ReceiptError("health URL must use http:// or https://")
    request = Request(url, headers={"Accept": "application/json"}, method="GET")
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            if response.status != 200:
                raise ReceiptError(f"health endpoint returned HTTP {response.status}")
            body = response.read(_MAX_HEALTH_BYTES + 1)
    except HTTPError as error:
        raise ReceiptError(f"health endpoint returned HTTP {error.code}") from error
    except URLError as error:
        raise ReceiptError(
            f"could not reach health endpoint: {error.reason}"
        ) from error
    if len(body) > _MAX_HEALTH_BYTES:
        raise ReceiptError("health response exceeds the receipt size limit")
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ReceiptError("health endpoint did not return valid UTF-8 JSON") from error
    if not isinstance(payload, Mapping):
        raise ReceiptError("health endpoint did not return a JSON object")
    return dict(payload)


def _write_receipt(
    path: Path, receipt: Mapping[str, Any], *, force: bool
) -> Path | None:
    if path.exists() and not force:
        raise ReceiptError(f"refusing to overwrite existing receipt: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    previous_path: Path | None = None
    if path.exists():
        previous_path = path.with_name(f"{path.stem}.previous{path.suffix}")
        if previous_path.exists():
            raise ReceiptError(
                "refusing to replace a receipt while its previous backup exists: "
                f"{previous_path}"
            )

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

        if previous_path is not None:
            try:
                path.replace(previous_path)
            except OSError:
                raise
        try:
            os.replace(temporary_path, path)
            temporary_path = None
        except OSError:
            if (
                previous_path is not None
                and previous_path.exists()
                and not path.exists()
            ):
                previous_path.replace(path)
            raise
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
    return previous_path


def _flatten(value: Mapping[str, Any], prefix: str = "") -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    for key, item in value.items():
        name = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(item, Mapping):
            flattened.update(_flatten(item, name))
        else:
            flattened[name] = item
    return flattened


def _format_mismatch(stored: Mapping[str, Any], live: Mapping[str, Any]) -> str:
    stored_flat = _flatten(stored)
    live_flat = _flatten(live)
    lines = ["release receipt mismatch:"]
    safe_fields = {
        "schema_version",
        "source_field_set_sha256",
        "service",
        "service_version",
        "deployment_fingerprint",
        "model.model_id",
        "model.artifact_sha256",
        "model.production_ready",
        "model.uncertainty_validated",
        "reference_panel.panel_id",
        "reference_panel.source_sha256",
        "reference_panel.production_ready",
        "reference_panel.fixture_only",
        "reference_panel.readiness",
        "approval_binding_valid",
        "readiness.status",
        "readiness.blockers",
        "operational_controls.auth_required_for_v1",
        "operational_controls.max_request_bytes",
        "operational_controls.structured_request_logging",
        "operational_controls.model_approval_manifest_configured",
        "operational_controls.model_approval_binding_valid",
        "operational_controls.reference_panel_fixture_only",
        "runtime_provenance.package_tree_sha256",
        "runtime_provenance.package_installation_mode",
        "runtime_provenance.dependency_set_sha256",
        "runtime_provenance.python_runtime.implementation",
        "runtime_provenance.python_runtime.version",
        "runtime_provenance.python_runtime.cache_tag",
        "runtime_provenance.configuration_sha256",
    }
    for field in sorted(safe_fields):
        if stored_flat.get(field) != live_flat.get(field):
            lines.append(
                f"{field}: stored={stored_flat.get(field)!r} "
                f"live={live_flat.get(field)!r}"
            )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Capture or reconcile a safe runtime release receipt"
    )
    parser.add_argument(
        "--health-url",
        default="http://127.0.0.1:8000/health",
        help="GET /health endpoint to inspect",
    )
    parser.add_argument("--output", required=True, type=Path, help="receipt JSON path")
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare an existing receipt with fresh health metadata",
    )
    parser.add_argument(
        "--force", action="store_true", help="allow replacing an existing receipt"
    )
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args(argv)
    try:
        health = fetch_health(args.health_url, timeout_seconds=args.timeout)
        if args.check:
            stored = json.loads(args.output.read_text(encoding="utf-8"))
            live_receipt = health_to_receipt(health)
            if not isinstance(stored, Mapping) or not receipt_matches_health(
                stored, health
            ):
                if isinstance(stored, Mapping):
                    print(_format_mismatch(stored, live_receipt), file=sys.stderr)
                raise ReceiptError("stored receipt does not match current health")
            print("release receipt matches current runtime health")
            return 0
        receipt = health_to_receipt(health)
        previous_path = _write_receipt(args.output, receipt, force=args.force)
        if previous_path is None:
            print(f"release receipt written: {args.output}")
        else:
            print(
                f"release receipt written: {args.output}; "
                f"previous receipt moved to {previous_path}"
            )
        return 0
    except (OSError, ReceiptError, TypeError, ValueError) as error:
        print(f"release receipt failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
