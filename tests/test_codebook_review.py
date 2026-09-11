import json
from pathlib import Path


def test_codebook_review_distinguishes_valid_ranges_from_special_codes():
    review = json.loads(
        Path("docs/NHANES_CODEBOOK_REVIEW_2026-09-11.json").read_text(encoding="utf-8")
    )
    assert review["review_boundary"]["values_removed"] is False
    assert review["review_boundary"]["all_fields_reviewed"] is False
    pax = next(entry for entry in review["entries"] if entry["field"] == "PAXVMD")
    assert "999 is within" in pax["observed_source_semantics"]["important_consequence"]
    dpq = next(entry for entry in review["entries"] if entry["field"] == "DPQ010")
    assert dpq["observed_source_semantics"]["special_codes"]["7"] == "Refused"
