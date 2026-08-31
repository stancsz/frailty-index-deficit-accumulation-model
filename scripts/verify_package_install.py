"""Smoke-test the installed wheel path, not the repository's ``src`` path."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Awaitable, Callable

from frailty_engine.__main__ import sample_payload
from frailty_engine.api import create_app
from frailty_engine.release_provenance import runtime_provenance
from frailty_engine.seca import read_seca_tableview_csv


ASGIApp = Callable[
    [
        dict[str, Any],
        Callable[[], Awaitable[dict[str, Any]]],
        Callable[[dict[str, Any]], Awaitable[None]],
    ],
    Awaitable[None],
]


async def _request(app: ASGIApp, method: str, path: str, payload: Any = None) -> int:
    body = b"" if payload is None else json.dumps(payload).encode("utf-8")
    messages = [{"type": "http.request", "body": body, "more_body": False}]
    sent: list[dict[str, Any]] = []

    async def receive() -> dict[str, Any]:
        return messages.pop(0) if messages else {"type": "http.disconnect"}

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    await app(
        {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1",
            "method": method,
            "scheme": "http",
            "path": path,
            "raw_path": path.encode("ascii"),
            "query_string": b"",
            "headers": [
                (b"host", b"smoke"),
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode("ascii")),
            ],
            "client": ("127.0.0.1", 1),
            "server": ("smoke", 80),
            "root_path": "",
        },
        receive,
        send,
    )
    return next(
        message["status"]
        for message in sent
        if message["type"] == "http.response.start"
    )


async def _smoke() -> tuple[int, int, int, int, int]:
    app = create_app()
    sample = sample_payload()
    comparison = {
        "previous": {
            "patient_id": "package-progress",
            "assessed_at": "2026-01-01",
            "measurements": sample["measurements"],
        },
        "current": {
            "patient_id": "package-progress",
            "assessed_at": "2026-03-01",
            "measurements": sample["measurements"],
        },
    }
    return (
        await _request(app, "GET", "/health"),
        await _request(app, "GET", "/metrics"),
        await _request(app, "POST", "/v1/assessments", sample),
        await _request(
            app,
            "POST",
            "/v1/assessments",
            {"patient_id": "package-smoke", "measurements": {}},
        ),
        await _request(app, "POST", "/v1/assessment-comparisons", comparison),
    )


def _seca_smoke() -> tuple[bool, int, int]:
    """Exercise the installed wheel's local SECA import path as well."""

    fixture = Path(__file__).parents[1] / "examples" / "seca_tableview_fixture.csv"
    export = read_seca_tableview_csv(fixture)
    readiness = export.assessment_readiness
    return (
        bool(readiness["assessment_ready"]),
        len(export.latest_measurements()),
        len(export.latest.segmental_skeletal_muscle_mass),
    )


def main() -> int:
    (
        health_status,
        metrics_status,
        assessment_status,
        invalid_status,
        comparison_status,
    ) = asyncio.run(_smoke())
    seca_ready, seca_fields, seca_segments = _seca_smoke()
    provenance = runtime_provenance()
    if provenance.get("package_installation_mode") != "installed_distribution":
        raise RuntimeError("installed wheel provenance is not from distribution files")
    if not provenance.get("package_tree_sha256"):
        raise RuntimeError(
            "installed wheel provenance is missing a package-tree digest"
        )
    if health_status != 200:
        raise RuntimeError(f"wheel health smoke failed: {health_status}")
    if metrics_status != 200:
        raise RuntimeError(f"wheel metrics smoke failed: {metrics_status}")
    if assessment_status != 200:
        raise RuntimeError(f"wheel assessment smoke failed: {assessment_status}")
    if invalid_status != 422:
        raise RuntimeError(f"wheel validation smoke failed: {invalid_status}")
    if comparison_status != 200:
        raise RuntimeError(f"wheel comparison smoke failed: {comparison_status}")
    if seca_ready or seca_fields != 4 or seca_segments != 5:
        raise RuntimeError(
            "wheel SECA smoke failed: "
            f"ready={seca_ready} canonical={seca_fields} segments={seca_segments}"
        )
    entry_point = Path(sys.executable).with_name(
        "frailty-engine.exe" if os.name == "nt" else "frailty-engine"
    )
    entry_help = subprocess.run(
        [str(entry_point), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    if entry_help.returncode or "Clinical healthspan engine" not in entry_help.stdout:
        raise RuntimeError("installed wheel entry point smoke failed")
    print(
        "installed wheel smoke passed: "
        f"health={health_status} metrics={metrics_status} assessment={assessment_status} "
        f"invalid={invalid_status} comparison={comparison_status} seca_ready={seca_ready} "
        f"seca_canonical={seca_fields} seca_segments={seca_segments}"
        f" package_tree_sha256={provenance['package_tree_sha256']}"
        f" dependency_set_sha256={provenance['dependency_set_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
