import json
from pathlib import Path


def test_codebook_receipt_covers_all_mapped_source_families():
    receipt = json.loads(
        Path("docs/NHANES_CODEBOOK_RECEIPT_2026-09-11.json").read_text(encoding="utf-8")
    )
    assert receipt["source_count"] == len(receipt["entries"])
    assert receipt["source_count"] >= 50
    assert {entry["cycle"] for entry in receipt["entries"]} == {
        "2003_2004",
        "2009_2010",
        "2011_2012",
        "2013_2014",
        "2015_2016",
        "2017_2018",
        "2021_2023",
    }
    assert all(entry["http_status"] == 200 for entry in receipt["entries"])
    assert all(entry["bytes"] > 0 and entry["sha256"] for entry in receipt["entries"])
    assert receipt["boundary"]["measurements_emitted"] is False
