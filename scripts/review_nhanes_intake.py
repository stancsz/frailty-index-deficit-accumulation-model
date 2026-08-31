"""Audit the local, aggregate shape of an explicit NHANES intake.

This command is a provenance and shape check for the existing non-imputing
NHANES adapters.  It is deliberately not a downloader, trainer, clinical
validator, or production-readiness gate.  Receipts contain file digests and
aggregate counts only; they never contain SEQN values, patient identifiers,
measurement values, or local paths.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from frailty_engine.exceptions import (  # noqa: E402
    FrailtyEngineError,
    ModelUnavailableError,
)
from frailty_engine.features import FEATURE_NAMES  # noqa: E402
from frailty_engine.nhanes import (  # noqa: E402
    NHANES_BIA_CYCLES,
    NHANESColumnMap,
    build_nhanes_rows,
    merge_xpt_files,
    read_public_use_mortality,
)


SCHEMA_VERSION = 1
RECEIPT_TYPE = "nhanes-intake-review-v1"
MAX_INPUT_BYTES = 512 * 1024 * 1024
REVIEWER_OBLIGATIONS = [
    "review the cycle-specific column map against the official codebooks",
    "review laboratory and questionnaire missing-value sentinels",
    "review BIA fit-quality and measurement acceptance rules",
    "review survey weights, variance, disclosure control, and linkage policy",
    "keep the approved cohort, reference panel, clinical cutoffs, and production sign-off as separate gates",
]


class IntakeReviewError(Exception):
    """Expected, privacy-safe failure while creating an intake receipt."""

    def __init__(self, blocker: str, *, role: str | None = None):
        super().__init__(blocker)
        self.blocker = blocker
        self.role = role


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cycle",
        required=True,
        help="supported NHANES BIA cycle (for example, 2003-2004)",
    )
    parser.add_argument(
        "--xpt",
        action="append",
        required=True,
        type=Path,
        help="local SAS transport component; repeat for each component",
    )
    parser.add_argument(
        "--mortality",
        required=True,
        type=Path,
        help="local CDC public-use linked-mortality fixed-width .dat file",
    )
    parser.add_argument(
        "--column-map",
        required=True,
        type=Path,
        help="explicit JSON map for this cycle's raw columns",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="write the deterministic receipt here instead of stdout",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare the generated receipt with --output without rewriting it",
    )
    return parser


def _file_digest(path: Path, role: str) -> dict[str, Any]:
    try:
        stat = path.stat()
    except OSError as error:
        raise IntakeReviewError(f"{role} input could not be read", role=role) from error
    if not path.is_file():
        raise IntakeReviewError(f"{role} input must be a regular file", role=role)
    if stat.st_size > MAX_INPUT_BYTES:
        raise IntakeReviewError(f"{role} input exceeds the local size limit", role=role)
    digest = hashlib.sha256()
    try:
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as error:
        raise IntakeReviewError(f"{role} input could not be read", role=role) from error
    return {"role": role, "size_bytes": stat.st_size, "sha256": digest.hexdigest()}


def _load_column_map(path: Path) -> NHANESColumnMap:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise IntakeReviewError(
            "column-map JSON could not be read", role="column_map"
        ) from error
    if not isinstance(data, dict) or not isinstance(data.get("columns"), dict):
        raise IntakeReviewError(
            "column-map JSON must contain an object named columns", role="column_map"
        )
    if "duration_unit" not in data or "missing_values" not in data:
        raise IntakeReviewError(
            "column-map JSON must explicitly define duration_unit and missing_values",
            role="column_map",
        )
    columns = data["columns"]
    if any(
        not isinstance(key, str) or not isinstance(value, str)
        for key, value in columns.items()
    ):
        raise IntakeReviewError(
            "column-map keys and values must be strings", role="column_map"
        )
    required = {"seqn", "age", "sex", "bmi"}
    missing = sorted(required - set(columns))
    if missing:
        raise IntakeReviewError(
            "column-map must explicitly map seqn, age, sex, and bmi",
            role="column_map",
        )
    duration_unit = data["duration_unit"]
    missing_values = data["missing_values"]
    if not isinstance(duration_unit, str) or not isinstance(missing_values, list):
        raise IntakeReviewError(
            "column-map duration_unit and missing_values have invalid types",
            role="column_map",
        )
    try:
        frozen_missing_values = frozenset(missing_values)
        normalized_columns = {
            key: value.strip().upper() for key, value in columns.items()
        }
        return NHANESColumnMap(
            columns=normalized_columns,
            duration_unit=duration_unit,
            missing_values=frozen_missing_values,
        )
    except (TypeError, ValueError) as error:
        raise IntakeReviewError(
            "column-map values are not a valid NHANES map", role="column_map"
        ) from error


def _frame_columns(frame: Any) -> list[str]:
    try:
        return sorted({str(column).upper() for column in frame.columns})
    except (AttributeError, TypeError) as error:
        raise IntakeReviewError(
            "XPT components did not return tabular columns", role="xpt"
        ) from error


def _frame_records(frame: Any) -> list[Mapping[str, Any]]:
    try:
        records = frame.to_dict(orient="records")
    except (AttributeError, TypeError, ValueError) as error:
        raise IntakeReviewError(
            "XPT components did not return tabular rows", role="xpt"
        ) from error
    if not isinstance(records, list) or any(
        not isinstance(row, Mapping) for row in records
    ):
        raise IntakeReviewError("XPT components did not return object rows", role="xpt")
    return records


def _present(value: Any) -> bool:
    if value is None:
        return False
    try:
        if value == "":
            return False
    except (TypeError, ValueError):
        pass
    try:
        return not bool(value != value)
    except (TypeError, ValueError):
        return True


def _seqn_key(value: Any) -> int | str | None:
    if not _present(value):
        return None
    try:
        number = float(value)
        if math.isfinite(number) and number.is_integer():
            return int(number)
    except (TypeError, ValueError):
        pass
    return str(value)


def _duplicate_count(records: Sequence[Mapping[str, Any]], source: str) -> int:
    seen: set[int | str] = set()
    duplicates = 0
    for record in records:
        key = _seqn_key(record.get(source))
        if key is None:
            continue
        if key in seen:
            duplicates += 1
        seen.add(key)
    return duplicates


def _canonical_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "rows_after_map": len(rows),
        "anchor_presence": {
            name: sum(1 for row in rows if _present(row.get(name)))
            for name in ("age", "sex", "bmi")
        },
        "feature_presence": {
            name: sum(1 for row in rows if _present(row.get(name)))
            for name in FEATURE_NAMES
        },
        "derived_signal_presence": {
            name: sum(1 for row in rows if _present(row.get(name)))
            for name in ("phase_angle", "ecw_tbw", "ffmi", "fib_4")
        },
    }


def _mortality_summary(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "rows_seen": len(records),
        "eligible_rows": sum(1 for record in records if record.get("eligstat") == 1),
        "ineligible_or_unknown_rows": sum(
            1 for record in records if record.get("eligstat") != 1
        ),
        "event_rows": sum(1 for record in records if record.get("event") is True),
        "censored_rows": sum(1 for record in records if record.get("event") is False),
        "rows_without_duration": sum(
            1 for record in records if record.get("duration") is None
        ),
        "duration_unit": "years",
        "parser": "CDC fixed-width public-use .dat; no header row assumed",
    }


def _base_receipt(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": RECEIPT_TYPE,
        "tool": "nhanes-intake-review",
        "reviewer_note": (
            "Local aggregate intake-shape audit only; this receipt is not "
            "clinical validation, a training result, or a production approval."
        ),
        "cycle": args.cycle,
        "inputs": [],
        "xpt_summary": {},
        "mortality_summary": {},
        "canonical_row_summary": {},
        "checks": {},
        "reviewer_obligations": REVIEWER_OBLIGATIONS,
        "outcome": {"status": "failed", "blockers": []},
    }


def _failure_receipt(
    args: argparse.Namespace,
    blocker: str,
    *,
    inputs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    receipt = _base_receipt(args)
    receipt["inputs"] = inputs or []
    receipt["outcome"] = {"status": "failed", "blockers": [blocker]}
    return receipt


def run_review(args: argparse.Namespace) -> dict[str, Any]:
    """Run the mechanical review and return a path-free deterministic receipt."""

    inputs: list[dict[str, Any]] = []
    try:
        if args.cycle not in NHANES_BIA_CYCLES:
            raise IntakeReviewError("cycle is not in the supported NHANES BIA manifest")
        for path in args.xpt:
            inputs.append(_file_digest(path, "xpt"))
        inputs.append(_file_digest(args.mortality, "mortality"))
        inputs.append(_file_digest(args.column_map, "column_map"))
        column_map = _load_column_map(args.column_map)
        if column_map.duration_unit != "years":
            raise IntakeReviewError(
                "column-map duration_unit must be years when linked mortality is supplied",
                role="column_map",
            )

        frame = merge_xpt_files(args.xpt)
        columns = _frame_columns(frame)
        source_rows = _frame_records(frame)
        duplicate_seqn_rows = _duplicate_count(source_rows, "SEQN")
        missing_seqn_rows = sum(
            1 for row in source_rows if not _present(row.get("SEQN"))
        )
        if "SEQN" not in columns:
            raise IntakeReviewError(
                "XPT components are missing the SEQN join key", role="xpt"
            )
        if set(column_map.columns.values()) - set(columns):
            raise IntakeReviewError(
                "column-map references a source column missing from the XPT intake",
                role="column_map",
            )
        if missing_seqn_rows:
            raise IntakeReviewError(
                "XPT components contain rows without SEQN", role="xpt"
            )
        if duplicate_seqn_rows:
            raise IntakeReviewError(
                "XPT components contain duplicate SEQN rows", role="xpt"
            )

        mortality_records = read_public_use_mortality(
            args.mortality, require_eligible=False
        )
        eligible_mortality = [
            record for record in mortality_records if record.get("eligstat") == 1
        ]
        if not eligible_mortality:
            raise IntakeReviewError(
                "mortality file contains no eligible rows", role="mortality"
            )
        invalid_duration = False
        for record in eligible_mortality:
            try:
                duration = float(record.get("duration"))
            except (TypeError, ValueError):
                invalid_duration = True
                break
            if not math.isfinite(duration) or duration <= 0:
                invalid_duration = True
                break
        if invalid_duration:
            raise IntakeReviewError(
                "eligible mortality rows contain non-positive or missing follow-up duration",
                role="mortality",
            )
        source_seqns = {
            _seqn_key(row.get("SEQN"))
            for row in source_rows
            if _present(row.get("SEQN"))
        }
        matched_eligible_rows = sum(
            1
            for record in eligible_mortality
            if _seqn_key(record.get("seqn")) in source_seqns
        )
        if matched_eligible_rows == 0:
            raise IntakeReviewError(
                "no eligible mortality rows matched the XPT intake", role="mortality"
            )
        canonical_rows = build_nhanes_rows(
            source_rows,
            column_map=column_map,
            mortality_records=eligible_mortality,
        )
    except IntakeReviewError as error:
        return _failure_receipt(args, error.blocker, inputs=inputs)
    except ModelUnavailableError:
        return _failure_receipt(
            args,
            "pandas is required for XPT ingestion; install the [data] extra",
            inputs=inputs,
        )
    except (FrailtyEngineError, TypeError, ValueError, OSError):
        return _failure_receipt(
            args,
            "NHANES intake could not be parsed or mapped; inspect the local inputs and explicit column map",
            inputs=inputs,
        )

    receipt = _base_receipt(args)
    receipt["inputs"] = sorted(inputs, key=lambda item: (item["role"], item["sha256"]))
    receipt["xpt_summary"] = {
        "component_count": len(args.xpt),
        "row_count": len(source_rows),
        "column_count": len(columns),
        "columns": columns,
        "seqn_column_present": True,
        "rows_without_seqn": missing_seqn_rows,
        "duplicate_seqn_rows": duplicate_seqn_rows,
    }
    receipt["mortality_summary"] = _mortality_summary(mortality_records)
    receipt["mortality_summary"]["eligible_rows_matched_to_xpt"] = matched_eligible_rows
    receipt["mortality_summary"]["eligible_rows_without_xpt"] = (
        receipt["mortality_summary"]["eligible_rows"] - matched_eligible_rows
    )
    receipt["canonical_row_summary"] = _canonical_summary(canonical_rows)
    receipt["checks"] = {
        "supported_cycle": True,
        "xpt_components_read": True,
        "seqn_join_key_present": True,
        "duplicate_seqn_rejected": duplicate_seqn_rows == 0,
        "mortality_fixed_width_parsed": True,
        "mortality_duration_canonical_years": True,
        "explicit_anchor_map_present": True,
        "no_imputation": True,
        "cycle_specific_column_map_reviewed": False,
        "missing_value_sentinels_reviewed": False,
        "bia_fit_quality_reviewed": False,
        "survey_design_reviewed": False,
        "clinical_or_production_approval": False,
    }
    receipt["outcome"] = {"status": "passed", "blockers": []}
    return receipt


def _json_bytes(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.check and args.output is None:
        parser.error("--check requires --output")

    receipt = run_review(args)
    serialized = _json_bytes(receipt)
    if args.check:
        try:
            checked = args.output.read_bytes()
        except OSError:
            print("ERROR: stored intake receipt could not be read", file=sys.stderr)
            return 3
        if checked != serialized:
            print(
                "ERROR: stored intake receipt does not match generated output",
                file=sys.stderr,
            )
            return 3
        print(f"NHANES intake receipt verified: {args.output}")
    elif args.output is not None:
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(serialized)
        except OSError:
            print("ERROR: intake receipt could not be written", file=sys.stderr)
            return 1
        print(f"NHANES intake receipt written: {args.output}")
    else:
        sys.stdout.buffer.write(serialized)
    return 0 if receipt["outcome"]["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
