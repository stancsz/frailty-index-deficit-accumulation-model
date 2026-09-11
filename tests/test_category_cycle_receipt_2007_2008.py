from __future__ import annotations

import json
from pathlib import Path

from scripts.build_category_cycle_receipt_2007_2008 import build_receipt


ROOT = Path(__file__).resolve().parents[1]
DATA = Path(r"C:\Users\stanc\AppData\Local\Temp\frailty-nhanes-2007-2008-candidate")


def test_2007_2008_receipt_has_real_fields_and_explicit_absences() -> None:
    receipt = build_receipt(DATA)
    assert receipt["cycle"] == "NHANES_2007_2008"
    assert len(receipt["categories"]) == 13
    assert len(receipt["data_sources"]) == 13
    for payload in receipt["categories"].values():
        assert payload["fields"]
        assert all(field["nonmissing_rows"] > 0 for field in payload["fields"])
    assert set(receipt["not_collected_in_cycle"]) == {
        "bone_health",
        "brain_cognitive_health",
        "fluid_and_cellular",
        "skin_health",
    }
    assert receipt["boundary"]["participant_ids_emitted"] is False


def test_2007_2008_receipt_matches_checked_in_artifact() -> None:
    expected = json.loads(
        (
            ROOT / "docs/REAL_DATA_INTAKE_2007_2008_CATEGORY_RECEIPT_2026-09-11.json"
        ).read_text()
    )
    assert build_receipt(DATA) == expected
