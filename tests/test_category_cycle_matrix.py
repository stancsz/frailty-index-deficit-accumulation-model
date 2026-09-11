from __future__ import annotations

import json
from pathlib import Path

from scripts.build_category_cycle_matrix import build_matrix


ROOT = Path(__file__).resolve().parents[1]


def _receipt(name: str) -> dict:
    return json.loads((ROOT / "docs" / name).read_text())


def test_matrix_preserves_all_category_presence_and_declared_absence() -> None:
    matrix = build_matrix(
        {
            "PRIMARY_MULTI_CYCLE": _receipt("CATEGORY_DATA_RECEIPT_2026-09-11.json"),
            "NHANES_2013_2014": _receipt(
                "REAL_DATA_INTAKE_2013_2014_RECEIPT_2026-09-11.json"
            ),
            "NHANES_2015_2016": _receipt(
                "REAL_DATA_INTAKE_2015_2016_RECEIPT_2026-09-11.json"
            ),
            "NHANES_2005_2006": _receipt(
                "REAL_DATA_INTAKE_2005_2006_CATEGORY_RECEIPT_2026-09-11.json"
            ),
            "NHANES_2007_2008": _receipt(
                "REAL_DATA_INTAKE_2007_2008_CATEGORY_RECEIPT_2026-09-11.json"
            ),
            "NHANES_2017_2018": _receipt(
                "REAL_DATA_INTAKE_2017_2018_CATEGORY_RECEIPT_2026-09-11.json"
            ),
            "NHANES_2021_2023": _receipt(
                "REAL_DATA_INTAKE_2021_2023_CATEGORY_RECEIPT_2026-09-11.json"
            ),
        }
    )
    assert matrix["category_count"] == 17
    assert matrix["categories"] == sorted(matrix["categories"])
    primary = matrix["cycles"]["PRIMARY_MULTI_CYCLE"]
    assert all(
        row["status"] == "real_numeric_source_data_present" for row in primary.values()
    )
    for cycle in (
        "NHANES_2013_2014",
        "NHANES_2015_2016",
        "NHANES_2017_2018",
        "NHANES_2021_2023",
    ):
        present = [
            row
            for row in matrix["cycles"][cycle].values()
            if row["status"] == "real_numeric_source_data_present"
        ]
        assert present
        assert all(row["min_unique_participants"] > 0 for row in present)
    assert matrix["cycles"]["NHANES_2015_2016"]["fluid_and_cellular"]["status"] == (
        "absent_in_receipt"
    )
    assert matrix["cycles"]["NHANES_2013_2014"]["brain_cognitive_health"]["status"] == (
        "real_numeric_source_data_present"
    )
    assert matrix["boundary"]["cross_cycle_joins_performed"] is False


def test_matrix_matches_checked_in_artifact() -> None:
    receipts = {
        "PRIMARY_MULTI_CYCLE": _receipt("CATEGORY_DATA_RECEIPT_2026-09-11.json"),
        "NHANES_2013_2014": _receipt(
            "REAL_DATA_INTAKE_2013_2014_RECEIPT_2026-09-11.json"
        ),
        "NHANES_2015_2016": _receipt(
            "REAL_DATA_INTAKE_2015_2016_RECEIPT_2026-09-11.json"
        ),
        "NHANES_2005_2006": _receipt(
            "REAL_DATA_INTAKE_2005_2006_CATEGORY_RECEIPT_2026-09-11.json"
        ),
        "NHANES_2007_2008": _receipt(
            "REAL_DATA_INTAKE_2007_2008_CATEGORY_RECEIPT_2026-09-11.json"
        ),
        "NHANES_2017_2018": _receipt(
            "REAL_DATA_INTAKE_2017_2018_CATEGORY_RECEIPT_2026-09-11.json"
        ),
        "NHANES_2021_2023": _receipt(
            "REAL_DATA_INTAKE_2021_2023_CATEGORY_RECEIPT_2026-09-11.json"
        ),
    }
    expected = json.loads(
        (ROOT / "docs/CATEGORY_CYCLE_MATRIX_2026-09-11.json").read_text()
    )
    assert build_matrix(receipts) == expected
