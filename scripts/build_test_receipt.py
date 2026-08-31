"""Build or verify the deterministic public test-count receipt."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

from attestation import verify_sidecar, write_sidecar


RECEIPT_PATH = Path("docs/test-receipt.json")
PYTHON_COMMAND = "uv run python -m pytest --collect-only -q"
NODE_COMMAND = "node --test --test-reporter=tap tests/site_parser.test.cjs"
_PYTEST_FILE_COUNT = re.compile(r"(?m)^tests[\\/][^\r\n:]+:\s*(\d+)\s*$")
_TAP_PLAN = re.compile(r"(?m)^1\.\.(\d+)\s*$")
_TAP_SUMMARY = re.compile(r"(?m)^# tests\s+(\d+)\s*$")


def _run(command: list[str], *, root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def collect_python_count(root: Path) -> int:
    result = _run([sys.executable, "-m", "pytest", "--collect-only", "-q"], root=root)
    output = result.stdout + result.stderr
    if result.returncode:
        raise RuntimeError("pytest collection failed:\n" + output.strip())
    matches = _PYTEST_FILE_COUNT.findall(output)
    if not matches:
        raise RuntimeError(
            "could not determine pytest collection count from output:\n"
            + output.strip()
        )
    count = sum(int(value) for value in matches)
    if count <= 0:
        raise RuntimeError("pytest collection returned no tests")
    return count


def collect_node_count(root: Path) -> int:
    result = _run(
        [
            "node",
            "--test",
            "--test-reporter=tap",
            "tests/site_parser.test.cjs",
        ],
        root=root,
    )
    output = result.stdout + result.stderr
    if result.returncode:
        raise RuntimeError("Node test run failed:\n" + output.strip())
    plan_matches = _TAP_PLAN.findall(output)
    summary_matches = _TAP_SUMMARY.findall(output)
    if len(plan_matches) != 1 or len(summary_matches) != 1:
        raise RuntimeError(
            "could not determine Node test count from TAP output:\n" + output.strip()
        )
    plan_count = int(plan_matches[0])
    summary_count = int(summary_matches[0])
    if plan_count != summary_count or plan_count <= 0:
        raise RuntimeError(
            "Node TAP plan and summary counts disagree: "
            f"{plan_count} != {summary_count}"
        )
    return plan_count


def _expected_receipt(root: Path) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "generated_by": "scripts/build_test_receipt.py",
        "python_command": PYTHON_COMMAND,
        "node_command": NODE_COMMAND,
        "python_tests_collected": collect_python_count(root),
        "node_tests_collected": collect_node_count(root),
    }


def _load_receipt(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing test receipt: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid JSON in test receipt: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError("test receipt must be a JSON object")
    expected_keys = {
        "schema_version",
        "generated_by",
        "python_command",
        "node_command",
        "python_tests_collected",
        "node_tests_collected",
    }
    if set(value) != expected_keys:
        raise RuntimeError(
            "test receipt keys drifted; expected exactly: "
            + ", ".join(sorted(expected_keys))
        )
    for key in ("python_tests_collected", "node_tests_collected"):
        count = value[key]
        if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
            raise RuntimeError(f"test receipt field {key} must be a positive integer")
    if value["schema_version"] != 1:
        raise RuntimeError("unsupported test receipt schema_version")
    if value["generated_by"] != "scripts/build_test_receipt.py":
        raise RuntimeError("test receipt generated_by is not canonical")
    if (
        value["python_command"] != PYTHON_COMMAND
        or value["node_command"] != NODE_COMMAND
    ):
        raise RuntimeError("test receipt command metadata is not canonical")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the checked-in receipt instead of rewriting it",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    path = root / RECEIPT_PATH
    try:
        receipt = _expected_receipt(root)
        if args.check:
            checked_in = _load_receipt(path)
            if checked_in != receipt:
                raise RuntimeError(
                    f"stale test receipt at {path}; run scripts/build_test_receipt.py"
                )
            ok, message = verify_sidecar(path, root=root)
            if not ok:
                raise RuntimeError(message)
            print(
                "test receipt verified: "
                f"{receipt['python_tests_collected']} Python + "
                f"{receipt['node_tests_collected']} Node tests"
            )
            return 0
        path.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        write_sidecar(path, root=root)
        print(
            "test receipt written: "
            f"{receipt['python_tests_collected']} Python + "
            f"{receipt['node_tests_collected']} Node tests"
        )
        return 0
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
