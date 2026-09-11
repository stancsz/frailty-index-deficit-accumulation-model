"""Validate redacted paired runs and build a token-value receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import re
import statistics
from typing import Any


SCHEMA_VERSION = "frontier-token-pair-v1"
RECEIPT_VERSION = "frontier-token-value-receipt-v1"
TASK_ID = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
FORBIDDEN_KEYS = {"prompt", "messages", "output", "completion", "content", "api_key"}


def _number(value: Any, name: str, *, integer: bool = False) -> float | int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    if value < 0:
        raise ValueError(f"{name} must be non-negative")
    if integer and not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    return value


def _run(raw: Any, label: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError(f"{label} must be an object")
    allowed = {
        "calls",
        "input_tokens",
        "output_tokens",
        "latency_ms",
        "success",
        "quality_score",
        "quality_pass",
        "failure_reason",
    }
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError(f"{label} has unsupported fields: {sorted(unknown)}")
    if not isinstance(raw.get("success"), bool):
        raise ValueError(f"{label}.success must be boolean")
    result = {
        "calls": _number(raw.get("calls"), f"{label}.calls", integer=True),
        "input_tokens": _number(
            raw.get("input_tokens"), f"{label}.input_tokens", integer=True
        ),
        "output_tokens": _number(
            raw.get("output_tokens"), f"{label}.output_tokens", integer=True
        ),
        "latency_ms": _number(raw.get("latency_ms"), f"{label}.latency_ms"),
        "success": raw["success"],
        "quality_score": raw.get("quality_score"),
        "quality_pass": raw.get("quality_pass"),
        "failure_reason": raw.get("failure_reason"),
    }
    if result["calls"] < 1:
        raise ValueError(f"{label}.calls must be at least 1")
    if result["quality_score"] is not None:
        score = _number(result["quality_score"], f"{label}.quality_score")
        if score > 1:
            raise ValueError(f"{label}.quality_score must be between 0 and 1")
    if result["quality_pass"] is not None and not isinstance(
        result["quality_pass"], bool
    ):
        raise ValueError(f"{label}.quality_pass must be boolean or null")
    if result["success"] and result["failure_reason"] is not None:
        raise ValueError(f"{label}.failure_reason must be null when successful")
    return result


def validate_pairs(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        raise ValueError("paired-run input must be an object")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION}")
    if payload.get("data_class") not in {"synthetic_fixture", "owner_supplied_real"}:
        raise ValueError("data_class must be synthetic_fixture or owner_supplied_real")
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("records must be a non-empty list")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"records[{index}] must be an object")
        if set(record) != {"task_id", "baseline", "candidate"}:
            raise ValueError(
                f"records[{index}] must contain only task_id, baseline, candidate"
            )
        task_id = record["task_id"]
        if not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id):
            raise ValueError(f"records[{index}].task_id is not an opaque task id")
        if task_id in seen:
            raise ValueError(f"duplicate task_id: {task_id}")
        seen.add(task_id)
        result.append(
            {
                "task_id": task_id,
                "baseline": _run(record["baseline"], f"records[{index}].baseline"),
                "candidate": _run(record["candidate"], f"records[{index}].candidate"),
            }
        )
    return result


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * weight


def _run_summary(records: list[dict[str, Any]], key: str) -> dict[str, Any]:
    runs = [record[key] for record in records]
    tokens = [run["input_tokens"] + run["output_tokens"] for run in runs]
    latencies = [float(run["latency_ms"]) for run in runs]
    successes = sum(run["success"] for run in runs)
    return {
        "tasks": len(runs),
        "successful_tasks": successes,
        "success_rate": round(successes / len(runs), 6),
        "calls": sum(run["calls"] for run in runs),
        "retries": sum(run["calls"] - 1 for run in runs),
        "input_tokens": sum(run["input_tokens"] for run in runs),
        "output_tokens": sum(run["output_tokens"] for run in runs),
        "total_tokens": sum(tokens),
        "tokens_per_successful_task": round(sum(tokens) / successes, 6)
        if successes
        else None,
        "mean_latency_ms": round(statistics.mean(latencies), 6),
        "p95_latency_ms": round(_percentile(latencies, 0.95), 6),
        "quality_pass_rate": (
            round(
                sum(run["quality_pass"] is True for run in runs)
                / sum(run["quality_pass"] is not None for run in runs),
                6,
            )
            if any(run["quality_pass"] is not None for run in runs)
            else None
        ),
    }


def build_receipt(payload: dict[str, Any]) -> dict[str, Any]:
    records = validate_pairs(payload)
    paired_success = [
        record
        for record in records
        if record["baseline"]["success"] and record["candidate"]["success"]
    ]
    baseline = _run_summary(records, "baseline")
    candidate = _run_summary(records, "candidate")
    baseline_tokens = sum(
        r["baseline"]["input_tokens"] + r["baseline"]["output_tokens"]
        for r in paired_success
    )
    candidate_tokens = sum(
        r["candidate"]["input_tokens"] + r["candidate"]["output_tokens"]
        for r in paired_success
    )
    savings = (
        round(100 * (baseline_tokens - candidate_tokens) / baseline_tokens, 6)
        if baseline_tokens
        else None
    )
    differences = [
        (r["baseline"]["input_tokens"] + r["baseline"]["output_tokens"])
        - (r["candidate"]["input_tokens"] + r["candidate"]["output_tokens"])
        for r in paired_success
    ]
    ci: dict[str, Any]
    if len(differences) < 2:
        ci = {"status": "unavailable", "reason": "fewer_than_two_paired_successes"}
    else:
        rng = random.Random(0)
        bootstraps = []
        for _ in range(2000):
            sample = [rng.choice(differences) for _ in differences]
            bootstraps.append(statistics.mean(sample))
        ci = {
            "status": "mechanics_only",
            "method": "deterministic_task_bootstrap",
            "iterations": 2000,
            "seed": 0,
            "mean_token_difference_ci95": [
                round(_percentile(bootstraps, 0.025), 6),
                round(_percentile(bootstraps, 0.975), 6),
            ],
        }
    receipt = {
        "schema_version": RECEIPT_VERSION,
        "source_schema_version": SCHEMA_VERSION,
        "data_class": payload["data_class"],
        "real_paired_runs": payload["data_class"] == "owner_supplied_real",
        "record_count": len(records),
        "paired_success_count": len(paired_success),
        "baseline": baseline,
        "candidate": candidate,
        "matched_success_metrics": {
            "baseline_total_tokens": baseline_tokens,
            "candidate_total_tokens": candidate_tokens,
            "token_savings_percent": savings,
            "bootstrap": ci,
        },
        "boundary": {
            "prompts_emitted": False,
            "outputs_emitted": False,
            "identifiers_emitted": False,
            "credentials_emitted": False,
            "claim_status": (
                "real_value_unverified"
                if payload["data_class"] != "owner_supplied_real"
                else "owner_supplied_measurement"
            ),
        },
    }
    return receipt


def _reject_forbidden_keys(value: Any) -> None:
    if isinstance(value, dict):
        if FORBIDDEN_KEYS.intersection(value):
            raise ValueError(
                "input contains a forbidden prompt/output/credential field"
            )
        for child in value.values():
            _reject_forbidden_keys(child)
    elif isinstance(value, list):
        for child in value:
            _reject_forbidden_keys(child)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        _reject_forbidden_keys(payload)
        receipt = build_receipt(payload)
        receipt["input_sha256"] = hashlib.sha256(args.input.read_bytes()).hexdigest()
        serialized = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
        if args.check:
            if args.output.read_bytes() != serialized:
                print("ERROR: token value receipt drift")
                return 3
            print(f"token value receipt verified: {args.output}")
            return 0
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(serialized)
        print(f"token value receipt written: {args.output}")
        return 0
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
