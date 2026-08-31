"""Write or verify the deterministic synthetic validation report envelope.

This command creates a reviewable software artifact from the committed
synthetic external-validation fixture.  It is deliberately not a clinical
validation report: the envelope records the fixture provenance and the
remaining E-005 requirement next to the engineering metrics.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from attestation import sha256_file, verify_sidecar, write_sidecar  # noqa: E402
from frailty_engine.validation import validate_external_cohort  # noqa: E402


FIXTURE_PATH = ROOT / "examples" / "external_validation_synthetic.json"
DEFAULT_OUTPUT = ROOT / "examples" / "external_validation_validation_report.json"
SCHEMA_VERSION = "1"
CLINICAL_STATUS = "requires_e005_external_validation_and_clinical_review"
GENERATED_BY = "scripts/run_external_validation_report.py"


def _load_fixture(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    try:
        envelope = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(
            f"unable to read synthetic validation fixture: {path}"
        ) from error
    if not isinstance(envelope, dict):
        raise ValueError("synthetic validation fixture must be a JSON object")
    if envelope.get("fixture_type") != "synthetic_external_validation":
        raise ValueError("fixture_type must identify the synthetic validation fixture")
    provenance = envelope.get("provenance")
    if not isinstance(provenance, dict):
        raise ValueError("fixture provenance must be an object")
    if provenance.get("kind") != "synthetic":
        raise ValueError("fixture provenance kind must remain synthetic")
    if provenance.get("clinical_use") != "forbidden":
        raise ValueError("fixture provenance clinical_use must remain forbidden")
    seed = provenance.get("seed")
    row_count = provenance.get("row_count")
    rows = envelope.get("rows")
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError("fixture provenance seed must be a non-negative integer")
    if isinstance(row_count, bool) or not isinstance(row_count, int) or row_count <= 0:
        raise ValueError("fixture provenance row_count must be a positive integer")
    if not isinstance(rows, list) or not rows or row_count != len(rows):
        raise ValueError("fixture provenance row_count does not match rows")
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError("fixture rows must contain JSON objects")
    return envelope, rows


def _sidecar_root(path: Path) -> Path:
    resolved = path.resolve()
    if resolved.is_relative_to(ROOT.resolve()):
        return ROOT
    return path.parent


def build_report(*, fixture_path: Path = FIXTURE_PATH) -> dict[str, Any]:
    """Build the deterministic, explicitly non-clinical report envelope."""

    fixture, rows = _load_fixture(fixture_path)
    provenance = fixture["provenance"]
    assert isinstance(provenance, dict)
    report = validate_external_cohort(
        rows,
        cohort_name="synthetic-external-validation-engineering-fixture",
        bins=5,
        bootstrap_replicates=200,
        bootstrap_seed=provenance["seed"],
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "clinical_status": CLINICAL_STATUS,
        "fixture_provenance": {
            "kind": "synthetic",
            "clinical_use": "forbidden",
            "fixture_path": fixture_path.resolve()
            .relative_to(ROOT.resolve())
            .as_posix()
            if fixture_path.resolve().is_relative_to(ROOT.resolve())
            else fixture_path.name,
            "fixture_sha256": sha256_file(fixture_path),
        },
        "generated_by": GENERATED_BY,
        "report": report.to_dict(),
    }


def _render_report(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=FIXTURE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the deterministic report and its separate SHA-256 sidecar",
    )
    args = parser.parse_args(argv)
    fixture_path = args.fixture if args.fixture.is_absolute() else ROOT / args.fixture
    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    try:
        expected = _render_report(build_report(fixture_path=fixture_path))
        if args.check:
            current = output_path.read_text(encoding="utf-8")
            if current != expected:
                raise ValueError(
                    f"validation report is not reproducible: {output_path}"
                )
            ok, message = verify_sidecar(output_path, root=_sidecar_root(output_path))
            if not ok:
                raise ValueError(message)
            print(f"synthetic validation report verified: {output_path}")
            return 0
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(expected, encoding="utf-8")
        write_sidecar(output_path, root=_sidecar_root(output_path))
        print(f"synthetic validation report written: {output_path}")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
