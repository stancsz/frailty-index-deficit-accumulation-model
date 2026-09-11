import json
from pathlib import Path


def test_category_overlap_receipt_is_privacy_safe_and_covers_cycles():
    path = Path("docs/CATEGORY_OVERLAP_RECEIPT_2026-09-11.json")
    receipt = json.loads(path.read_text(encoding="utf-8"))
    assert receipt["receipt_type"] == "nhanes-category-participant-overlap-v1"
    assert receipt["privacy_boundary"] == {
        "cross_cycle_joins_performed": False,
        "measurements_emitted": False,
        "participant_ids_emitted": False,
        "raw_rows_emitted": False,
    }
    assert set(receipt["cycles"]) == {
        "NHANES_1991_1994",
        "NHANES_2003_2004",
        "NHANES_2009_2010",
        "NHANES_2011_2012",
        "NHANES_2017_MARCH_2020_PREPANDEMIC",
    }
    assert receipt["cycles"]["NHANES_2011_2012"]["category_count"] == 16
    current = receipt["cycles"]["NHANES_2011_2012"]
    assert current["reference_population"]["source"] == "DEMO_G.XPT"
    assert current["reference_population"]["unique_participants"] > 9000
    assert current["all_mapped_categories_intersection_unique_participants"] >= 0
    assert set(current["category_reference_coverage"]) == set(current["categories"])
    for cycle in receipt["cycles"].values():
        for count in cycle["categories"].values():
            assert count["unique_participants_with_any_mapped_field"] > 0
        assert all(
            value >= 0
            for value in cycle["pairwise_overlap_unique_participants"].values()
        )
