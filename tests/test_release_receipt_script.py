from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from frailty_engine.api import create_app


class _Response:
    def __init__(self, status: int, body: bytes):
        self.status = status
        self._body = body

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def read(self, _: int) -> bytes:
        return self._body


def _load_script():
    path = Path(__file__).parents[1] / "scripts" / "capture_release_receipt.py"
    spec = importlib.util.spec_from_file_location("capture_release_receipt_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_capture_script_guards_io_and_cli(tmp_path, monkeypatch, capsys) -> None:
    module = _load_script()
    health = TestClient(create_app()).get("/health").json()
    body = json.dumps(health).encode("utf-8")

    with patch.object(module, "urlopen", return_value=_Response(200, body)):
        assert module.fetch_health("http://example.test/health") == health
    with patch.object(
        module,
        "urlopen",
        side_effect=HTTPError("http://example.test/health", 503, "down", {}, None),
    ):
        with pytest.raises(module.ReceiptError):
            module.fetch_health("http://example.test/health")
    with patch.object(module, "urlopen", side_effect=URLError("offline")):
        with pytest.raises(module.ReceiptError):
            module.fetch_health("http://example.test/health")
    with patch.object(
        module,
        "urlopen",
        return_value=_Response(200, b"not-json"),
    ):
        with pytest.raises(module.ReceiptError):
            module.fetch_health("http://example.test/health")
    with patch.object(module, "urlopen", return_value=_Response(200, b"[]")):
        with pytest.raises(module.ReceiptError):
            module.fetch_health("http://example.test/health")
    with patch.object(
        module,
        "urlopen",
        return_value=_Response(200, b"x" * (module._MAX_HEALTH_BYTES + 1)),
    ):
        with pytest.raises(module.ReceiptError):
            module.fetch_health("http://example.test/health")

    monkeypatch.setattr(
        module,
        "fetch_health",
        lambda _url, timeout_seconds=10.0: health,
    )
    receipt_path = tmp_path / "release-receipt.json"
    assert module.main(["--output", str(receipt_path)]) == 0
    assert module.main(["--output", str(receipt_path)]) == 2
    assert module.main(["--output", str(receipt_path), "--force"]) == 0
    assert receipt_path.with_name("release-receipt.previous.json").is_file()

    tampered_path = tmp_path / "tampered.json"
    tampered = json.loads(receipt_path.read_text(encoding="utf-8"))
    tampered["deployment_fingerprint"] = "0" * 64
    tampered_path.write_text(json.dumps(tampered), encoding="utf-8")
    assert module.main(["--output", str(tampered_path), "--check"]) == 2
    assert "deployment_fingerprint" in capsys.readouterr().err
    current_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    blocker_tampered = json.loads(json.dumps(current_receipt))
    blocker_tampered["readiness"]["blockers"] = ["new readiness blocker"]
    mismatch = module._format_mismatch(blocker_tampered, current_receipt)
    assert "readiness.blockers" in mismatch
    assert "new readiness blocker" in mismatch
    assert module.main(["--output", str(receipt_path), "--check"]) == 0
