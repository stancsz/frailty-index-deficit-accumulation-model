"""Prove the Pages verification path observes an isolated test failure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = ROOT / "docs" / "publication-failure-demo-2026-09-10.json"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "pages.yml"


def _load_receipt() -> dict[str, Any]:
    try:
        value = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"invalid publication-failure receipt: {error}") from error
    if not isinstance(value, dict):
        raise RuntimeError("publication-failure receipt must be an object")
    expected = {
        "schema_version",
        "receipt_type",
        "evidence_class",
        "status",
        "deliberate_test_returncode",
        "publication_step_reached",
        "workflow_dependency",
        "remote_verified",
    }
    if set(value) != expected:
        raise RuntimeError(
            "publication-failure receipt keys drifted; expected exactly: "
            + ", ".join(sorted(expected))
        )
    if value["schema_version"] != 1:
        raise RuntimeError("unsupported publication-failure receipt schema")
    if value["receipt_type"] != "isolated-publication-failure-demo":
        raise RuntimeError("unexpected publication-failure receipt type")
    if value["evidence_class"] != "local-harness":
        raise RuntimeError("publication-failure receipt evidence class is unsafe")
    if value["status"] != "passed":
        raise RuntimeError("publication-failure receipt is not marked passed")
    if value["deliberate_test_returncode"] != 1:
        raise RuntimeError("publication-failure receipt must record pytest exit 1")
    if value["publication_step_reached"] is not False:
        raise RuntimeError("publication step must be recorded as not reached")
    if value["workflow_dependency"] != "deploy.needs: verify":
        raise RuntimeError("publication dependency metadata drifted")
    if value["remote_verified"] is not False:
        raise RuntimeError("local failure demo cannot claim remote verification")
    return value


def _verify_workflow_shape() -> None:
    try:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise RuntimeError(f"could not read Pages workflow: {error}") from error
    for marker in (
        "uv run python -m pytest -q",
        "needs: verify",
        "actions/upload-pages-artifact@v4",
        "actions/deploy-pages@v4",
    ):
        if marker not in workflow:
            raise RuntimeError(f"Pages workflow is missing guard: {marker}")


def _run_isolated_failure() -> int:
    with tempfile.TemporaryDirectory(prefix="frailty-pages-failure-") as raw:
        directory = Path(raw)
        test_path = directory / "test_deliberate_failure.py"
        test_path.write_text(
            "def test_deliberate_failure():\n    assert False\n",
            encoding="utf-8",
            newline="\n",
        )
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", str(test_path)],
            cwd=directory,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        output = result.stdout + result.stderr
        if result.returncode != 1 or "1 failed" not in output:
            raise RuntimeError(
                "isolated deliberate failure did not produce the expected pytest "
                f"exit 1 and failure summary: returncode={result.returncode}"
            )
        return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the retained receipt and Pages workflow shape",
    )
    parser.parse_args()
    try:
        receipt = _load_receipt()
        _verify_workflow_shape()
        returncode = _run_isolated_failure()
    except RuntimeError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(
        "publication failure demo passed: "
        f"pytest_returncode={returncode} publication_step_reached="
        f"{receipt['publication_step_reached']} remote_verified="
        f"{receipt['remote_verified']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
