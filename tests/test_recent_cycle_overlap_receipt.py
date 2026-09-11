from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "docs/RECENT_CATEGORY_OVERLAP_RECEIPT_2026-09-11.json"


def test_recent_overlap_receipt_is_privacy_safe_and_cycle_specific() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert set(receipt["cycles"]) == {
        "NHANES_2013_2014",
        "NHANES_2015_2016",
        "NHANES_2017_2018",
        "NHANES_2021_2023",
    }
    assert receipt["privacy_boundary"] == {
        "participant_ids_emitted": False,
        "raw_rows_emitted": False,
        "measurements_emitted": False,
        "cross_cycle_joins_performed": False,
    }
    assert receipt["cycles"]["NHANES_2013_2014"]["category_count"] == 15
    assert receipt["cycles"]["NHANES_2015_2016"]["category_count"] == 15
    assert receipt["cycles"]["NHANES_2017_2018"]["category_count"] == 15
    assert receipt["cycles"]["NHANES_2021_2023"]["category_count"] == 12
    assert (
        receipt["cycles"]["NHANES_2013_2014"][
            "all_mapped_categories_intersection_unique_participants"
        ]
        == 0
    )
    assert (
        receipt["cycles"]["NHANES_2013_2014"]["pairwise_overlap_unique_participants"][
            "blood_health__body_composition"
        ]
        > 0
    )
    assert (
        receipt["cycles"]["NHANES_2015_2016"][
            "all_mapped_categories_intersection_unique_participants"
        ]
        > 0
    )
    assert (
        receipt["cycles"]["NHANES_2017_2018"][
            "all_mapped_categories_intersection_unique_participants"
        ]
        > 0
    )
