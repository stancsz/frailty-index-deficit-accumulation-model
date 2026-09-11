import json
from pathlib import Path


def test_2017_2018_liver_receipt_is_direct_and_privacy_safe():
    receipt = json.loads(
        Path("docs/REAL_DATA_INTAKE_2017_2018_LIVER_RECEIPT_2026-09-11.json").read_text(
            encoding="utf-8"
        )
    )
    assert receipt["cycle"] == "NHANES_2017_2018"
    assert receipt["category"]["name"] == "liver_health"
    assert receipt["category"]["status"].startswith("real_direct")
    assert receipt["boundary"]["participant_ids_emitted"] is False
    assert receipt["data_sources"][0]["rows"] == 6401
    assert (
        max(
            field["unique_participants_with_value"]
            for field in receipt["category"]["fields"]
        )
        > 0
    )
