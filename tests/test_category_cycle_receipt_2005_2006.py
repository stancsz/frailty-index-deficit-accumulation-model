from __future__ import annotations

import json
from pathlib import Path

from scripts.build_category_cycle_receipt_2005_2006 import build_receipt


ROOT = Path(__file__).resolve().parents[1]
DATA = Path(r"C:\Users\stanc\AppData\Local\Temp\frailty-nhanes-2005-2006-candidate")


def test_2005_2006_receipt_has_real_fields_and_explicit_absences() -> None:
    receipt = build_receipt(DATA)
    assert receipt["cycle"] == "NHANES_2005_2006"
    assert len(receipt["categories"]) == 15
    assert len(receipt["data_sources"]) == 15
    for payload in receipt["categories"].values():
        assert payload["fields"]
        assert all(field["nonmissing_rows"] > 0 for field in payload["fields"])
        assert all(
            field["unique_participants_with_value"] > 0 for field in payload["fields"]
        )
    assert set(receipt["not_collected_in_cycle"]) == {
        "brain_cognitive_health",
        "fluid_and_cellular",
    }
    assert receipt["boundary"]["participant_ids_emitted"] is False


def test_2005_2006_receipt_matches_checked_in_artifact() -> None:
    expected = json.loads(
        (
            ROOT / "docs/REAL_DATA_INTAKE_2005_2006_CATEGORY_RECEIPT_2026-09-11.json"
        ).read_text()
    )
    assert build_receipt(DATA) == expected
