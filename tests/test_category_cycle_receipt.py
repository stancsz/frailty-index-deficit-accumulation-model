import json
from pathlib import Path


def test_2013_2014_receipt_covers_underrepresented_categories_without_raw_data():
    receipt = json.loads(
        Path("docs/REAL_DATA_INTAKE_2013_2014_RECEIPT_2026-09-11.json").read_text(
            encoding="utf-8"
        )
    )
    assert receipt["cycle"] == "NHANES_2013_2014"
    assert receipt["boundary"]["participant_ids_emitted"] is False
    assert receipt["boundary"]["measurements_emitted"] is False
    assert len(receipt["data_sources"]) == 17
    assert len(receipt["categories"]) == 15
    assert {
        "brain_cognitive_health",
        "mental_health_history",
        "sleep_and_recovery",
        "lifestyle_and_function",
    }.issubset(receipt["categories"])
    assert "fluid_and_cellular" not in receipt["categories"]
    assert "liver_health" not in receipt["categories"]
    for category in receipt["categories"].values():
        assert category["fields"]
        assert (
            max(field["unique_participants_with_value"] for field in category["fields"])
            > 0
        )
