from __future__ import annotations

import json
from pathlib import Path

from frailty_engine.body_reports import build_category_reports
from frailty_engine.category_data import category_source_catalog
from frailty_engine.features import parse_patient_data


def test_every_current_category_has_a_real_source_entry() -> None:
    catalog = category_source_catalog()
    assert len(catalog) == 17
    for entry in catalog.values():
        assert entry["status"] == "real_source_available"
        assert entry["observed_source_rows"] > 0
        assert entry["observed_source_participants"] > 0
        assert entry["source_files"]
        assert entry["fields"]
        assert entry["coverage_receipt"] == "CATEGORY_DATA_RECEIPT_2026-09-11"
        assert entry["distribution_evidence"]["status"] == "real_distribution_receipt"
        assert entry["distribution_evidence"]["receipt"] == (
            "CATEGORY_DISTRIBUTION_RECEIPT_2026-09-11"
        )
        assert entry["distribution_evidence"]["field"]
    assert "PFQ_G.XPT" in catalog["joint_health"]["source_files"]
    assert "xr.dat" in catalog["joint_health"]["source_files"]
    assert "ARX_F.XPT" in catalog["joint_health"]["source_files"]
    assert "ARQ_F.XPT" in catalog["joint_health"]["source_files"]
    assert {"ARQ010", "ARQ040", "ARQ110", "ARD125A"}.issubset(
        catalog["joint_health"]["fields"]
    )
    assert {"ARXO2WD", "ARDDINEX", "ARDLFTL"}.issubset(
        catalog["joint_health"]["fields"]
    )
    assert {"XRPKLR", "XRPKLL", "XRPOMFR", "XRPJRL"}.issubset(
        catalog["joint_health"]["fields"]
    )
    assert {"MCQ160N", "MCQ180A", "MCQ180N", "PFQ054", "PFQ059", "PFQ061T"}.issubset(
        catalog["joint_health"]["fields"]
    )
    assert {"DED031", "DEQ034C", "DEQ038Q", "DED125"}.issubset(
        catalog["skin_health"]["fields"]
    )
    assert {"BMXWT", "BMXBMI", "BMXWAIST", "BMXARMC"}.issubset(
        catalog["body_composition"]["fields"]
    )
    assert {"BIAEXSTS", "BIDTBW", "BIDFFM", "BIDFAT", "BIDPFAT"}.issubset(
        catalog["fluid_and_cellular"]["fields"]
    )
    assert {"DXDTOBMC", "DXDTOFAT", "DXDSTBMC", "DXXLSBMD"}.issubset(
        catalog["bone_health"]["fields"]
    )
    assert {"MGXH1T1", "MGXH2T1", "MGXH1T2", "MGXH2T2"}.issubset(
        catalog["muscle_health"]["fields"]
    )
    assert {"CFASTAT", "CFDCRNC", "CFDCST1", "CFDCIT1", "CFDAPP"}.issubset(
        catalog["brain_cognitive_health"]["fields"]
    )
    assert "DEX_C.XPT" in catalog["skin_health"]["source_files"]
    assert {
        "DEX1FITZ",
        "DED1HDDX",
        "DED1PSDX",
        "DEX2FITZ",
        "DED2HDDX",
        "DED2PSDX",
        "DEX6FITZ",
        "DED6HDDX",
        "DED6PSDX",
    }.issubset(catalog["skin_health"]["fields"])
    assert {"BPXSY1", "BPXDI1", "BPXSY2", "BPXDI2", "BPXSY3", "BPXDI3"}.issubset(
        catalog["cardiovascular_health"]["fields"]
    )
    assert "SPX_G.XPT" in catalog["cardiorespiratory_health"]["source_files"]
    assert {"SPXNFVC", "SPXNFEV1", "SPXNF257", "SPXNPEF"}.issubset(
        catalog["cardiorespiratory_health"]["fields"]
    )
    assert "ENX_G.XPT" in catalog["cardiorespiratory_health"]["source_files"]
    assert {"ENXSTAT", "ENXTR1Q", "ENXTR2Q", "ENXMEAN"}.issubset(
        catalog["cardiorespiratory_health"]["fields"]
    )
    assert {"PFQ049", "PFQ061M", "PFQ061N"}.issubset(
        catalog["lifestyle_and_function"]["fields"]
    )
    assert {"LBXTC", "LBXTR", "LBDLDL"}.issubset(
        catalog["cardiovascular_health"]["fields"]
    )
    assert "APOB_G.XPT" in catalog["cardiovascular_health"]["source_files"]
    assert {"LBXAPB", "LBDAPBSI"}.issubset(catalog["cardiovascular_health"]["fields"])
    assert {"SLD010H", "SLQ050", "SLQ060"}.issubset(
        catalog["sleep_and_recovery"]["fields"]
    )
    assert {"DPQ010", "DPQ050", "DPQ100"}.issubset(
        catalog["mental_health_history"]["fields"]
    )
    assert {"HSQ480", "HSQ490", "HSQ493", "HSQ496"}.issubset(
        catalog["mental_health_history"]["fields"]
    )
    assert {"LBXSBU", "LBXSUA"}.issubset(catalog["kidney_health"]["fields"])
    assert "ALB_CR_G.XPT" in catalog["kidney_health"]["source_files"]
    assert {"URXUMA", "URXUCR", "URDACT"}.issubset(catalog["kidney_health"]["fields"])
    assert {"LBXSATSI", "LBXSASSI", "LBXSTB", "LBXSTP"}.issubset(
        catalog["liver_health"]["fields"]
    )
    assert "P_LUX.XPT" in catalog["liver_health"]["source_files"]
    assert {"LUXSMED", "LUXCAPM", "LUAXSTAT"}.issubset(
        catalog["liver_health"]["fields"]
    )
    assert {"LBXLYPCT", "LBDLYMNO", "LBDNENO"}.issubset(
        catalog["immune_inflammatory_health"]["fields"]
    )
    assert "CRP_F.XPT" in catalog["immune_inflammatory_health"]["source_files"]
    assert "LBXCRP" in catalog["immune_inflammatory_health"]["fields"]
    assert catalog["brain_cognitive_health"]["additional_cycle_sources"][
        "NHANES_2013_2014"
    ]["files"] == ["CFQ_H.XPT"]
    assert (
        "DPQ_H.XPT"
        in catalog["mental_health_history"]["additional_cycle_sources"][
            "NHANES_2013_2014"
        ]["files"]
    )
    assert (
        "PAXDAY_H.XPT"
        in catalog["sleep_and_recovery"]["additional_cycle_sources"][
            "NHANES_2013_2014"
        ]["files"]
    )
    assert (
        "BPX_H.XPT"
        in catalog["cardiovascular_health"]["additional_cycle_sources"][
            "NHANES_2013_2014"
        ]["files"]
    )
    assert (
        "ALB_CR_H.XPT"
        in catalog["kidney_health"]["additional_cycle_sources"]["NHANES_2013_2014"][
            "files"
        ]
    )
    assert (
        catalog["liver_health"]["additional_cycle_sources"]["NHANES_2017_2018"][
            "receipt"
        ]
        == "REAL_DATA_INTAKE_2017_2018_LIVER_RECEIPT_2026-09-11"
    )
    assert catalog["body_composition"]["additional_cycle_sources"]["NHANES_2015_2016"][
        "files"
    ] == ["BMX_I.XPT"]
    assert catalog["body_composition"]["additional_cycle_sources"]["NHANES_2005_2006"][
        "files"
    ] == ["BMX_D.XPT"]
    assert catalog["body_composition"]["additional_cycle_sources"]["NHANES_2007_2008"][
        "files"
    ] == ["BMX_E.XPT"]
    assert catalog["liver_health"]["additional_cycle_sources"]["NHANES_2015_2016"][
        "files"
    ] == ["BIOPRO_I.XPT"]
    assert (
        "NHANES_2015_2016"
        not in catalog["fluid_and_cellular"]["additional_cycle_sources"]
    )
    assert (
        "NHANES_2005_2006"
        not in catalog["fluid_and_cellular"]["additional_cycle_sources"]
    )
    assert (
        "NHANES_2007_2008"
        not in catalog["fluid_and_cellular"]["additional_cycle_sources"]
    )
    assert catalog["fluid_and_cellular"]["cycle_coverage"]["NHANES_2005_2006"] == {
        "status": "not_collected_in_cycle",
        "reason": "no usable BIX_D.XPT source file was available",
    }
    assert (
        catalog["body_composition"]["cycle_coverage"]["NHANES_2007_2008"]["status"]
        == "real_source_present"
    )
    assert catalog["bone_health"]["cycle_coverage"]["NHANES_2021_2023"] == {
        "status": "not_collected_in_cycle",
        "reason": "reduced exam source absent",
    }
    assert (
        "NHANES_2015_2016"
        not in catalog["brain_cognitive_health"]["additional_cycle_sources"]
    )
    assert catalog["body_composition"]["additional_cycle_sources"]["NHANES_2017_2018"][
        "files"
    ] == ["BMX_J.XPT"]
    assert (
        "BIOPRO_J.XPT"
        in catalog["liver_health"]["additional_cycle_sources"]["NHANES_2017_2018"][
            "files"
        ]
    )
    assert (
        "LUX_J.XPT"
        in catalog["liver_health"]["additional_cycle_sources"]["NHANES_2017_2018"][
            "files"
        ]
    )
    assert catalog["body_composition"]["additional_cycle_sources"]["NHANES_2021_2023"][
        "files"
    ] == ["BMX_L.XPT"]
    assert catalog["mental_health_history"]["additional_cycle_sources"][
        "NHANES_2021_2023"
    ]["files"] == ["DPQ_L.XPT"]
    assert catalog["lifestyle_and_function"]["additional_cycle_sources"][
        "NHANES_2021_2023"
    ]["files"] == ["ALQ_L.XPT", "PAQ_L.XPT", "SMQ_L.XPT"]
    assert "NHANES_2021_2023" not in catalog["bone_health"]["additional_cycle_sources"]


def test_category_reports_expose_source_coverage_without_claiming_measurement() -> None:
    patient = parse_patient_data({"patient_id": "test", "age": 50, "sex": "female"})
    reports = build_category_reports(patient, [])
    assert len(reports) == 17
    for report in reports:
        assert report["source_data"]["status"] == "real_source_available"
        assert report["measured_count"] == 0
        assert report["age_report"]["status"] == "not_available"


def test_catalog_counts_match_receipt_maxima() -> None:
    receipt = json.loads(
        (
            Path(__file__).resolve().parents[1]
            / "docs/CATEGORY_DATA_RECEIPT_2026-09-11.json"
        ).read_text()
    )
    catalog = category_source_catalog()
    for category, payload in receipt["categories"].items():
        assert catalog[category]["observed_source_rows"] == max(
            field["nonmissing_rows"] for field in payload["fields"]
        )
        assert catalog[category]["observed_source_participants"] == max(
            field["unique_participants_with_value"] for field in payload["fields"]
        )
