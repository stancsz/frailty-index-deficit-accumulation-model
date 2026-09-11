from __future__ import annotations

import json
from pathlib import Path

from scripts.build_category_numeric_coverage_receipt import build_receipt


ROOT = Path(__file__).resolve().parents[1]


def test_all_17_categories_have_real_numeric_coverage() -> None:
    source = json.loads(
        (ROOT / "docs/CATEGORY_DATA_RECEIPT_2026-09-11.json").read_text()
    )
    receipt = build_receipt(source)
    assert receipt["category_count"] == 17
    assert len(receipt["categories"]) == 17
    for payload in receipt["categories"].values():
        assert payload["status"] == "real_numeric_source_data_present"
        assert payload["field_count"] > 0
        assert payload["min_nonmissing_rows_across_fields"] > 0
        assert payload["min_unique_participants_across_fields"] > 0
    assert receipt["boundary"]["participant_ids_emitted"] is False
    assert receipt["boundary"]["measurements_emitted"] is False
    assert receipt["boundary"]["e005_status"] == "blocked"


def test_receipt_matches_checked_in_artifact() -> None:
    source = json.loads(
        (ROOT / "docs/CATEGORY_DATA_RECEIPT_2026-09-11.json").read_text()
    )
    expected = json.loads(
        (ROOT / "docs/CATEGORY_NUMERIC_COVERAGE_RECEIPT_2026-09-11.json").read_text()
    )
    assert build_receipt(source) == expected
