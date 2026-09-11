from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "docs/REAL_DATA_INTAKE_2015_2016_RECEIPT_2026-09-11.json"
RECEIPT_2017 = ROOT / "docs/REAL_DATA_INTAKE_2017_2018_CATEGORY_RECEIPT_2026-09-11.json"
RECEIPT_2021 = ROOT / "docs/REAL_DATA_INTAKE_2021_2023_CATEGORY_RECEIPT_2026-09-11.json"


def test_2015_2016_receipt_is_deterministic_and_bounded() -> None:
    expected = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert expected["cycle"] == "NHANES_2015_2016"
    assert expected["receipt_type"] == "nhanes-category-cycle-receipt-v1"
    assert len(expected["data_sources"]) == 15
    assert all(
        re.fullmatch(r"[0-9a-f]{64}", item["sha256"])
        for item in expected["data_sources"]
    )
    assert len(expected["categories"]) == 15
    assert expected["boundary"]["participant_ids_emitted"] is False
    assert expected["boundary"]["measurements_emitted"] is False
    assert expected["not_collected_in_cycle"]["brain_cognitive_health"]


def test_2017_2018_category_receipt_is_bounded() -> None:
    receipt = json.loads(RECEIPT_2017.read_text(encoding="utf-8"))
    assert receipt["cycle"] == "NHANES_2017_2018"
    assert len(receipt["data_sources"]) == 18
    assert len(receipt["categories"]) == 15
    assert all(
        re.fullmatch(r"[0-9a-f]{64}", item["sha256"])
        for item in receipt["data_sources"]
    )
    assert receipt["not_collected_in_cycle"]["liver_health_direct_elastography"]
    assert receipt["boundary"]["participant_ids_emitted"] is False
    lifestyle_fields = {
        field["field"]
        for field in receipt["categories"]["lifestyle_and_function"]["fields"]
    }
    assert {"PAQ605", "ALQ111", "SMQ020"}.issubset(lifestyle_fields)


def test_2021_2023_category_receipt_declares_reduced_exam_coverage() -> None:
    receipt = json.loads(RECEIPT_2021.read_text(encoding="utf-8"))
    assert receipt["cycle"] == "NHANES_2021_2023"
    assert len(receipt["data_sources"]) == 15
    assert len(receipt["categories"]) == 12
    assert receipt["not_collected_in_cycle"]["bone_health"]
    assert receipt["not_collected_in_cycle"]["cardiorespiratory_health"]
    lifestyle_fields = {
        field["field"]
        for field in receipt["categories"]["lifestyle_and_function"]["fields"]
    }
    assert {"PAD790Q", "PAD800", "ALQ111", "SMQ020"}.issubset(lifestyle_fields)
    assert receipt["boundary"]["measurements_emitted"] is False
