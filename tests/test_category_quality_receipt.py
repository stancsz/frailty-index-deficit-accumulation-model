import json
from pathlib import Path


def test_category_quality_receipt_covers_all_categories_without_cleaning_values():
    receipt = json.loads(
        Path("docs/CATEGORY_QUALITY_RECEIPT_2026-09-11.json").read_text(
            encoding="utf-8"
        )
    )
    assert receipt["receipt_type"] == "nhanes-category-quality-audit-v1"
    assert len(receipt["categories"]) == 17
    assert receipt["boundary"] == {
        "clinical_use": False,
        "e005_status": "blocked",
        "measurements_emitted": False,
        "participant_ids_emitted": False,
        "raw_rows_emitted": False,
        "values_removed": False,
    }
    for category in receipt["categories"].values():
        assert (
            category["quality_status"]
            == "candidate_special_codes_audited_no_cleaning_applied"
        )
        assert category["fields"]
        assert all(
            field["source_rows"] >= field["nonmissing_rows"]
            for field in category["fields"]
        )


def test_cycle_quality_receipts_cover_new_real_sources():
    cycle = json.loads(
        Path("docs/CATEGORY_QUALITY_RECEIPT_2013_2014_2026-09-11.json").read_text(
            encoding="utf-8"
        )
    )
    liver = json.loads(
        Path("docs/CATEGORY_QUALITY_RECEIPT_2017_2018_LIVER_2026-09-11.json").read_text(
            encoding="utf-8"
        )
    )
    assert cycle["scope"] == "2013_2014"
    assert len(cycle["categories"]) == 15
    assert liver["scope"] == "2017_2018_liver"
    assert set(liver["categories"]) == {"liver_health"}
    for receipt in (cycle, liver):
        assert receipt["boundary"]["values_removed"] is False
        assert all(
            category["quality_status"]
            == "candidate_special_codes_audited_no_cleaning_applied"
            for category in receipt["categories"].values()
        )
