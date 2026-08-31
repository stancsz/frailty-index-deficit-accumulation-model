"""Run the repository's canonical non-writing software verification suite.

This command composes the existing checks so an operator or agent can verify
the documented software contract from one entry point. It reports software
evidence only; a green run never clears E-005 or establishes clinical validity.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
MAX_CHECK_SECONDS = 180


@dataclass(frozen=True)
class Check:
    name: str
    command: tuple[str, ...]


def _python(*arguments: str) -> tuple[str, ...]:
    return (sys.executable, *arguments)


def build_checks(*, include_serving: bool) -> tuple[Check, ...]:
    """Return checks in the order used by local and agent verification."""

    checks = [
        Check("locked-resolution", ("uv", "lock", "--check")),
        Check("ruff", _python("-m", "ruff", "check", "src", "tests", "scripts")),
        Check(
            "ruff-format",
            _python("-m", "ruff", "format", "--check", "src", "tests", "scripts"),
        ),
        Check(
            "compile",
            _python("scripts/verify_project.py", "--syntax"),
        ),
        Check("python-tests", _python("-m", "pytest", "-q")),
        Check("pages-seca-syntax", ("node", "--check", "docs/seca-parser.js")),
        Check("pages-intake-syntax", ("node", "--check", "docs/intake-form.js")),
        Check("pages-site-syntax", ("node", "--check", "docs/site.js")),
        Check("pages-tests", ("node", "--test", "tests/site_parser.test.cjs")),
        Check(
            "test-receipt",
            _python("scripts/build_test_receipt.py", "--check"),
        ),
        Check("demo-artifact", _python("scripts/build_demo_data.py", "--check")),
        Check(
            "external-fixture",
            _python(
                "scripts/build_external_validation_fixture.py",
                "--output",
                "examples/external_validation_synthetic.json",
                "--check",
            ),
        ),
        Check(
            "external-report",
            _python("scripts/run_external_validation_report.py", "--check"),
        ),
        Check(
            "training-manifest",
            _python(
                "scripts/validate_training_manifest.py",
                "docs/TRAINING_MANIFEST_TEMPLATE.json",
            ),
        ),
        Check(
            "training-split-smoke",
            _python("scripts/run_training_split_smoke.py"),
        ),
        Check(
            "external-validation-smoke",
            _python("scripts/run_external_validation_smoke.py"),
        ),
        Check("documentation", _python("scripts/verify_docs.py")),
    ]
    if include_serving:
        checks.append(
            Check(
                "serving-contract-smoke",
                _python("scripts/run_serving_contract_smoke.py"),
            )
        )
    return tuple(checks)


def _executable_available(command: str) -> bool:
    if Path(command).name == command:
        return shutil.which(command) is not None
    return Path(command).is_file()


def _compile_python_sources() -> int:
    """Compile project Python in memory without creating bytecode files."""

    try:
        for directory in ("src", "scripts", "tests"):
            for path in (ROOT / directory).rglob("*.py"):
                compile(path.read_text(encoding="utf-8"), str(path), "exec")
    except (OSError, SyntaxError) as error:
        print(f"python syntax check failed: {error}", file=sys.stderr)
        return 1
    return 0


def _run_check(check: Check) -> dict[str, object]:
    started = time.monotonic()
    if not _executable_available(check.command[0]):
        return {
            "name": check.name,
            "status": "failed",
            "duration_ms": 0,
            "error": f"executable not found: {check.command[0]}",
        }
    try:
        result = subprocess.run(
            check.command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=MAX_CHECK_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        return {
            "name": check.name,
            "status": "failed",
            "duration_ms": round((time.monotonic() - started) * 1000, 3),
            "error": f"timed out after {MAX_CHECK_SECONDS} seconds",
            "stdout_tail": (error.stdout or "")[-4000:],
            "stderr_tail": (error.stderr or "")[-4000:],
        }
    except OSError as error:
        return {
            "name": check.name,
            "status": "failed",
            "duration_ms": round((time.monotonic() - started) * 1000, 3),
            "error": str(error),
        }
    outcome: dict[str, object] = {
        "name": check.name,
        "status": "passed" if result.returncode == 0 else "failed",
        "duration_ms": round((time.monotonic() - started) * 1000, 3),
        "returncode": result.returncode,
    }
    if result.returncode:
        outcome["stdout_tail"] = result.stdout[-4000:]
        outcome["stderr_tail"] = result.stderr[-4000:]
    return outcome


def _render_human(
    results: Sequence[dict[str, object]], *, include_serving: bool
) -> None:
    passed = sum(result["status"] == "passed" for result in results)
    total = len(results)
    print("Frailty Engine software verification")
    for result in results:
        print(
            f"[{str(result['status']).upper()}] {result['name']} "
            f"({float(result['duration_ms']) / 1000:.2f}s)"
        )
        if result["status"] != "passed":
            if result.get("error"):
                print(f"  error: {result['error']}")
            if result.get("stdout_tail"):
                print(f"  stdout:\n{result['stdout_tail']}")
            if result.get("stderr_tail"):
                print(f"  stderr:\n{result['stderr_tail']}")
    mode = "including serving" if include_serving else "without serving"
    print(f"Summary: {passed}/{total} checks passed ({mode}).")
    print(
        "Clinical gate: E-005 remains separate and blocked pending approved evidence."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-serving",
        action="store_true",
        help="skip the real loopback serving smoke",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit a machine-readable result instead of human-readable progress",
    )
    parser.add_argument("--syntax", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.syntax:
        return _compile_python_sources()
    include_serving = not args.skip_serving
    results = tuple(
        _run_check(check) for check in build_checks(include_serving=include_serving)
    )
    passed = all(result["status"] == "passed" for result in results)
    if args.json:
        print(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "passed" if passed else "failed",
                    "clinical_gate": "E-005 blocked",
                    "include_serving": include_serving,
                    "checks": list(results),
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        _render_human(results, include_serving=include_serving)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
