from __future__ import annotations

import json
from pathlib import Path

from scripts.build_category_distribution_receipt import build_receipt


ROOT = Path(__file__).resolve().parents[1]
DATA = Path(r"C:\Users\stanc\AppData\Local\Temp")


FIELDS = {
    "body_composition": (
        DATA / "frailty-nhanes-2007-2008-candidate/BMX_E.XPT",
        "BMXBMI",
    ),
    "fluid_and_cellular": (
        DATA / "frailty-nhanes-2003-fluid-candidate/BIX_C.XPT",
        "BIDTBW",
    ),
    "muscle_health": (DATA / "frailty-nhanes-2007-2008-candidate/BMX_E.XPT", "BMXARMC"),
    "joint_health": (DATA / "frailty-nhanes-2007-2008-candidate/PFQ_E.XPT", "PFQ054"),
    "bone_health": (DATA / "frailty-nhanes-2005-2006-candidate/DXX_D.XPT", "DXDTOBMD"),
    "skin_health": (DATA / "frailty-nhanes-2005-2006-candidate/DEQ_D.XPT", "DEQ034C"),
    "blood_health": (DATA / "frailty-nhanes-2007-2008-candidate/CBC_E.XPT", "LBXHGB"),
    "cardiovascular_health": (
        DATA / "frailty-nhanes-2007-2008-candidate/BPX_E.XPT",
        "BPXSY1",
    ),
    "cardiorespiratory_health": (
        DATA / "frailty-nhanes-2007-2008-candidate/BPX_E.XPT",
        "BPXSY1",
    ),
    "immune_inflammatory_health": (
        DATA / "frailty-nhanes-2007-2008-candidate/CBC_E.XPT",
        "LBXWBCSI",
    ),
    "brain_cognitive_health": (
        DATA / "frailty-nhanes-2013-2014-20260911/CFQ_H.XPT",
        "CFDCCS",
    ),
    "metabolic_health": (
        DATA / "frailty-nhanes-2007-2008-candidate/GLU_E.XPT",
        "LBXGLU",
    ),
    "kidney_health": (
        DATA / "frailty-nhanes-2007-2008-candidate/ALB_CR_E.XPT",
        "URXUCR",
    ),
    "liver_health": (
        DATA / "frailty-nhanes-2007-2008-candidate/BIOPRO_E.XPT",
        "LBXSATSI",
    ),
    "sleep_and_recovery": (
        DATA / "frailty-nhanes-2007-2008-candidate/SLQ_E.XPT",
        "SLD010H",
    ),
    "lifestyle_and_function": (
        DATA / "frailty-nhanes-2007-2008-candidate/PFQ_E.XPT",
        "PFQ049",
    ),
    "mental_health_history": (
        DATA / "frailty-nhanes-2007-2008-candidate/DPQ_E.XPT",
        "DPQ010",
    ),
}


def test_all_categories_have_real_distribution_data() -> None:
    receipt = build_receipt(FIELDS)
    assert receipt["category_count"] == 17
    for summary in receipt["distributions"].values():
        assert summary["n"] > 0
        assert summary["unique_participants_with_value"] > 0
        assert summary["q05"] <= summary["median"] <= summary["q95"]
    assert receipt["boundary"]["participant_ids_emitted"] is False
    assert receipt["boundary"]["measurements_emitted"] is False


def test_distribution_receipt_matches_checked_in_artifact() -> None:
    expected = json.loads(
        (ROOT / "docs/CATEGORY_DISTRIBUTION_RECEIPT_2026-09-11.json").read_text()
    )
    assert build_receipt(FIELDS) == expected
