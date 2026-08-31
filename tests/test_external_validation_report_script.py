from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

SCRIPTS = Path(__file__).parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from attestation import verify_sidecar, write_sidecar  # noqa: E402
from run_external_validation_report import (  # noqa: E402
    CLINICAL_STATUS,
    DEFAULT_OUTPUT,
    build_report,
)
from verify_project import build_checks  # noqa: E402


ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "examples" / "external_validation_synthetic.json"


def test_sidecar_rejects_target_byte_drift(tmp_path: Path) -> None:
    target = tmp_path / "artifact.json"
    target.write_bytes(b'{"value": 1}\n')
    write_sidecar(target)
    ok, message = verify_sidecar(target)
    assert ok, message

    target.write_bytes(b'{"value": 2}\n')
    ok, message = verify_sidecar(target)
    assert not ok
    assert "sidecar mismatch" in message


def test_committed_report_is_deterministic_and_e005_marked() -> None:
    expected = build_report(fixture_path=FIXTURE)
    committed = json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8"))

    assert committed == expected
    assert committed["clinical_status"] == CLINICAL_STATUS
    assert committed["fixture_provenance"] == {
        "kind": "synthetic",
        "clinical_use": "forbidden",
        "fixture_path": "examples/external_validation_synthetic.json",
        "fixture_sha256": committed["fixture_provenance"]["fixture_sha256"],
    }
    serialized = json.dumps(committed)
    assert "synthetic-external-001" not in serialized
    assert '"patient_id"' not in serialized
    ok, message = verify_sidecar(DEFAULT_OUTPUT, root=ROOT)
    assert ok, message

    check_names = [check.name for check in build_checks(include_serving=False)]
    assert check_names[-1] == "documentation"
    assert build_checks(include_serving=True)[-1].name == "serving-contract-smoke"
    assert "python-tests" in check_names
    assert "pages-tests" in check_names


def test_report_refuses_non_synthetic_or_clinical_fixture(tmp_path: Path) -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    fixture["provenance"]["kind"] = "external"
    bad_kind = tmp_path / "bad-kind.json"
    bad_kind.write_text(json.dumps(fixture), encoding="utf-8")
    with pytest.raises(ValueError, match="kind must remain synthetic"):
        build_report(fixture_path=bad_kind)

    fixture["provenance"]["kind"] = "synthetic"
    fixture["provenance"]["clinical_use"] = "allowed"
    bad_use = tmp_path / "bad-use.json"
    bad_use.write_text(json.dumps(fixture), encoding="utf-8")
    with pytest.raises(ValueError, match="clinical_use must remain forbidden"):
        build_report(fixture_path=bad_use)
