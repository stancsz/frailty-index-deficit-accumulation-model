from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.build_token_value_receipt import build_receipt, validate_pairs


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = json.loads(
    (ROOT / "examples/frontier_token_pairs_synthetic.json").read_text(encoding="utf-8")
)


def test_synthetic_receipt_is_explicitly_not_real_value_evidence() -> None:
    receipt = build_receipt(FIXTURE)
    assert receipt["data_class"] == "synthetic_fixture"
    assert receipt["real_paired_runs"] is False
    assert receipt["record_count"] == 6
    assert receipt["paired_success_count"] == 5
    assert receipt["matched_success_metrics"]["token_savings_percent"] == 35.203366
    assert receipt["matched_success_metrics"]["bootstrap"]["status"] == (
        "mechanics_only"
    )
    assert receipt["boundary"] == {
        "prompts_emitted": False,
        "outputs_emitted": False,
        "identifiers_emitted": False,
        "credentials_emitted": False,
        "claim_status": "real_value_unverified",
    }


def test_receipt_is_deterministic() -> None:
    assert build_receipt(FIXTURE) == build_receipt(json.loads(json.dumps(FIXTURE)))


def test_schema_rejects_duplicate_and_prompt_bearing_records() -> None:
    duplicate = json.loads(json.dumps(FIXTURE))
    duplicate["records"].append(duplicate["records"][0])
    with pytest.raises(ValueError, match="duplicate task_id"):
        validate_pairs(duplicate)

    prompt_bearing = json.loads(json.dumps(FIXTURE))
    prompt_bearing["records"][0]["baseline"]["prompt"] = "secret"
    with pytest.raises(ValueError, match="unsupported fields"):
        validate_pairs(prompt_bearing)
