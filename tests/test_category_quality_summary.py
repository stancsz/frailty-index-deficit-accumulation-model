from __future__ import annotations

import json
from pathlib import Path

from scripts.build_category_quality_summary import build_summary


ROOT = Path(__file__).resolve().parents[1]


def test_quality_summary_covers_all_categories_without_cleaning_values() -> None:
    source = json.loads(
        (ROOT / "docs/CATEGORY_QUALITY_RECEIPT_2026-09-11.json").read_text()
    )
    summary = build_summary(source)
    assert summary["category_count"] == 17
    assert len(summary["categories"]) == 17
    for payload in summary["categories"].values():
        assert payload["field_count"] > 0
        assert payload["min_source_rows"] > 0
        assert payload["min_unique_participants"] > 0
        assert 0 <= payload["min_missingness_rate"] <= 1
        assert 0 <= payload["max_missingness_rate"] <= 1
    assert summary["boundary"]["values_filtered"] is False
    assert summary["boundary"]["participant_ids_emitted"] is False
    assert summary["boundary"]["e005_status"] == "blocked"


def test_quality_summary_matches_checked_in_artifact() -> None:
    source = json.loads(
        (ROOT / "docs/CATEGORY_QUALITY_RECEIPT_2026-09-11.json").read_text()
    )
    expected = json.loads(
        (ROOT / "docs/CATEGORY_QUALITY_SUMMARY_2026-09-11.json").read_text()
    )
    assert build_summary(source) == expected
