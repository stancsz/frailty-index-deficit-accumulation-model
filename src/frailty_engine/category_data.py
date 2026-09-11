"""Real public-data source catalog for the full category report.

This catalog describes source availability independently of whether a current
assessment contains a participant measurement. It does not turn population
coverage into a patient result, clinical reference range, or category age.
"""

from __future__ import annotations

from typing import Any


_REPRESENTATIVE_DISTRIBUTION_FIELDS = {
    "body_composition": ("BMX_E.XPT", "BMXBMI"),
    "fluid_and_cellular": ("BIX_C.XPT", "BIDTBW"),
    "muscle_health": ("BMX_E.XPT", "BMXARMC"),
    "joint_health": ("PFQ_E.XPT", "PFQ054"),
    "bone_health": ("DXX_D.XPT", "DXDTOBMD"),
    "skin_health": ("DEQ_D.XPT", "DEQ034C"),
    "blood_health": ("CBC_E.XPT", "LBXHGB"),
    "cardiovascular_health": ("BPX_E.XPT", "BPXSY1"),
    "cardiorespiratory_health": ("BPX_E.XPT", "BPXSY1"),
    "immune_inflammatory_health": ("CBC_E.XPT", "LBXWBCSI"),
    "brain_cognitive_health": ("CFQ_H.XPT", "CFDCCS"),
    "metabolic_health": ("GLU_E.XPT", "LBXGLU"),
    "kidney_health": ("ALB_CR_E.XPT", "URXUCR"),
    "liver_health": ("BIOPRO_E.XPT", "LBXSATSI"),
    "sleep_and_recovery": ("SLQ_E.XPT", "SLD010H"),
    "lifestyle_and_function": ("PFQ_E.XPT", "PFQ049"),
    "mental_health_history": ("DPQ_E.XPT", "DPQ010"),
}


_CATALOG: dict[str, dict[str, Any]] = {
    "body_composition": {
        "status": "real_source_available",
        "directness": "direct_measurements",
        "source_files": ["BMX_G.XPT", "DXXAG_G.XPT"],
        "fields": [
            "BMXWT",
            "BMXHT",
            "BMXBMI",
            "BMXWAIST",
            "BMXARMC",
            "BMXSAD1",
            "DXXANFM",
            "DXXANLM",
            "DXXVFATM",
        ],
        "coverage_receipt": "CATEGORY_DATA_RECEIPT_2026-09-11",
    },
    "fluid_and_cellular": {
        "status": "real_source_available",
        "directness": "direct_BIA_measurements",
        "source_files": ["BIX_C.XPT"],
        "fields": [
            "BIAEXSTS",
            "BIDFIT",
            "BIDRECF",
            "BIDRICF",
            "BIDCM",
            "BIDTD",
            "BIDALPHA",
            "BIDFC",
            "BIDECF",
            "BIDTBW",
            "BIDICF",
            "BIDFFM",
            "BIDFAT",
            "BIDPFAT",
        ],
        "coverage_receipt": "CATEGORY_DATA_RECEIPT_2026-09-11",
    },
    "muscle_health": {
        "status": "real_source_available",
        "directness": "direct_measurements",
        "source_files": ["MGX_G.XPT", "DXX_G.XPT"],
        "fields": [
            "MGDEXSTS",
            "MGDCGSZ",
            "MGXH1T1",
            "MGXH2T1",
            "MGXH1T2",
            "MGXH2T2",
            "DXDLALE",
            "DXDRALE",
        ],
        "coverage_receipt": "CATEGORY_DATA_RECEIPT_2026-09-11",
    },
    "joint_health": {
        "status": "real_source_available",
        "directness": "radiographic_and_clinical_mobility_measurements_plus_history_and_function_proxy",
        "source_files": [
            "ARQ_F.XPT",
            "ARX_F.XPT",
            "xr.dat",
            "MCQ_G.XPT",
            "PFQ_G.XPT",
        ],
        "fields": [
            "ARQ010",
            "ARQ020A",
            "ARQ020B",
            "ARQ020C",
            "ARQ020D",
            "ARQ020E",
            "ARQ020F",
            "ARQ020G",
            "ARQ040",
            "ARQ050",
            "ARQ060",
            "ARQ070",
            "ARQ073",
            "ARQ077",
            "ARQ080",
            "ARQ100",
            "ARQ110",
            "ARD125A",
            "ARQ125C",
            "ARQ125D",
            "ARQ125E",
            "ARDEXSTS",
            "ARXO2WD",
            "ARXCCIN",
            "ARXCCEX",
            "ARDDINEX",
            "ARXXDIST",
            "ARDLFTL",
            "XRPKLR",
            "XRPKLL",
            "XRPOMFR",
            "XRPOMFL",
            "XRPOMTR",
            "XRPOMTL",
            "XRPOLFR",
            "XRPOLFL",
            "XRPOLTR",
            "XRPOLTL",
            "XRPSMFR",
            "XRPSMFL",
            "XRPSMTR",
            "XRPSMTL",
            "XRPSLFR",
            "XRPSLFL",
            "XRPSLTR",
            "XRPSLTL",
            "XRPCHOR",
            "XRPCHOL",
            "XRPJRR",
            "XRPJRL",
            "MCQ160A",
            "MCQ160N",
            "MCQ180A",
            "MCQ180N",
            "PFQ054",
            "PFQ059",
            "PFQ061B",
            "PFQ061C",
            "PFQ061D",
            "PFQ061E",
            "PFQ061F",
            "PFQ061G",
            "PFQ061H",
            "PFQ061I",
            "PFQ061J",
            "PFQ061K",
            "PFQ061L",
            "PFQ061M",
            "PFQ061N",
            "PFQ061O",
            "PFQ061P",
            "PFQ061Q",
            "PFQ061R",
            "PFQ061S",
            "PFQ061T",
        ],
        "coverage_receipt": "CATEGORY_DATA_RECEIPT_2026-09-11",
    },
    "bone_health": {
        "status": "real_source_available",
        "directness": "direct_DXA_measurements",
        "source_files": ["DXX_G.XPT"],
        "fields": [
            "DXDTOBMD",
            "DXDTOBMC",
            "DXDTOFAT",
            "DXDSTBMD",
            "DXDSTBMC",
            "DXDSTFAT",
            "DXXLSBMD",
        ],
        "coverage_receipt": "CATEGORY_DATA_RECEIPT_2026-09-11",
    },
    "skin_health": {
        "status": "real_source_available",
        "directness": "direct_dermatology_image_readings_plus_questionnaire_proxy",
        "source_files": ["DEX_C.XPT", "DEQ_G.XPT"],
        "fields": [
            "MXAEXSTS",
            "DEABACK",
            "DEAINARM",
            "DEAFRLEG",
            "DEALOLEG",
            "DEX1FITZ",
            "DED1HDDX",
            "DED1PSDX",
            "DEX2FITZ",
            "DED2HDDX",
            "DED2PSDX",
            "DEX6FITZ",
            "DED6HDDX",
            "DED6PSDX",
            "DEX6PSFH",
            "DEX6PSBK",
            "DEX6PSPL",
            "DEX6PSAL",
            "DED031",
            "DEQ034A",
            "DEQ034C",
            "DEQ034D",
            "DEQ038G",
            "DEQ038Q",
            "DED120",
            "DED125",
        ],
        "coverage_receipt": "CATEGORY_DATA_RECEIPT_2026-09-11",
    },
    "blood_health": {
        "status": "real_source_available",
        "directness": "laboratory_measurements",
        "source_files": [
            "APOB_G.XPT",
            "BIOPRO_G.XPT",
            "CBC_G.XPT",
            "TCHOL_G.XPT",
            "TRIGLY_G.XPT",
        ],
        "fields": [
            "LBXAPB",
            "LBDAPBSI",
            "LBXSAL",
            "LBXSCR",
            "LBXWBCSI",
            "LBXRDW",
            "LBXRBCSI",
            "LBXHGB",
            "LBXHCT",
            "LBXMCVSI",
            "LBXPLTSI",
            "LBXTC",
            "LBXTR",
            "LBDLDL",
        ],
        "coverage_receipt": "CATEGORY_DATA_RECEIPT_2026-09-11",
    },
    "cardiovascular_health": {
        "status": "real_source_available",
        "directness": "repeated_examination_measurements",
        "source_files": [
            "APOB_G.XPT",
            "BPX_G.XPT",
            "TCHOL_G.XPT",
            "TRIGLY_G.XPT",
        ],
        "fields": [
            "LBXAPB",
            "LBDAPBSI",
            "BPXPLS",
            "BPXSY1",
            "BPXDI1",
            "BPXSY2",
            "BPXDI2",
            "BPXSY3",
            "BPXDI3",
            "LBXTC",
            "LBXTR",
            "LBDLDL",
        ],
        "coverage_receipt": "CATEGORY_DATA_RECEIPT_2026-09-11",
    },
    "cardiorespiratory_health": {
        "status": "real_source_available",
        "directness": "repeated_examination_and_spirometry_measurements",
        "source_files": ["BPX_G.XPT", "ENX_G.XPT", "SPX_G.XPT"],
        "fields": [
            "ENXSTAT",
            "ENAATMPT",
            "ENXTR1Q",
            "ENXTR2Q",
            "ENXMEAN",
            "BPXPLS",
            "BPXSY1",
            "BPXDI1",
            "BPXSY2",
            "BPXDI2",
            "BPXSY3",
            "BPXDI3",
            "SPXNFVC",
            "SPXNFEV1",
            "SPXNF257",
            "SPXNPEF",
            "SPXNQFVC",
            "SPXNQFV1",
            "SPDNACC",
        ],
        "coverage_receipt": "CATEGORY_DATA_RECEIPT_2026-09-11",
    },
    "immune_inflammatory_health": {
        "status": "real_source_available",
        "directness": "laboratory_measurements",
        "source_files": ["CBC_G.XPT", "CRP_F.XPT", "ENX_G.XPT"],
        "fields": [
            "LBXCRP",
            "ENXMEAN",
            "LBXWBCSI",
            "LBXRDW",
            "LBXLYPCT",
            "LBXMOPCT",
            "LBXNEPCT",
            "LBXEOPCT",
            "LBXBAPCT",
            "LBDLYMNO",
            "LBDMONO",
            "LBDNENO",
            "LBDEONO",
            "LBDBANO",
        ],
        "coverage_receipt": "CATEGORY_DATA_RECEIPT_2026-09-11",
    },
    "brain_cognitive_health": {
        "status": "real_source_available",
        "directness": "standardized_cognitive_testing",
        "source_files": ["CFQ_G.XPT"],
        "fields": [
            "CFASTAT",
            "CFDCCS",
            "CFDCRNC",
            "CFDCST1",
            "CFDCSR",
            "CFDCIT1",
            "CFDAST",
            "CFDAPP",
            "CFDDS",
        ],
        "coverage_receipt": "CATEGORY_DATA_RECEIPT_2026-09-11",
    },
    "metabolic_health": {
        "status": "real_source_available",
        "directness": "laboratory_and_history",
        "source_files": [
            "GLU_G.XPT",
            "GHB_G.XPT",
            "DIQ_G.XPT",
            "TCHOL_G.XPT",
            "TRIGLY_G.XPT",
        ],
        "fields": ["LBXGLU", "LBXGH", "DIQ010", "LBXTC", "LBXTR", "LBDLDL"],
        "coverage_receipt": "CATEGORY_DATA_RECEIPT_2026-09-11",
    },
    "kidney_health": {
        "status": "real_source_available",
        "directness": "laboratory_measurement",
        "source_files": ["ALB_CR_G.XPT", "BIOPRO_G.XPT"],
        "fields": [
            "URXUMA",
            "URXUMS",
            "URXUCR",
            "URXCRS",
            "URDACT",
            "LBXSCR",
            "LBXSBU",
            "LBXSUA",
        ],
        "coverage_receipt": "CATEGORY_DATA_RECEIPT_2026-09-11",
    },
    "liver_health": {
        "status": "real_source_available",
        "directness": "direct_transient_elastography_plus_laboratory_measurements",
        "source_files": ["P_LUX.XPT", "BIOPRO_G.XPT"],
        "fields": [
            "LUAXSTAT",
            "LUANMVGP",
            "LUXSMED",
            "LUXSIQR",
            "LUXSIQRM",
            "LUXCAPM",
            "LUXCPIQR",
            "LBXSAL",
            "LBXSATSI",
            "LBXSASSI",
            "LBXSAPSI",
            "LBXSGTSI",
            "LBXSTB",
            "LBXSTP",
        ],
        "coverage_receipt": "CATEGORY_DATA_RECEIPT_2026-09-11",
    },
    "sleep_and_recovery": {
        "status": "real_source_available",
        "directness": "questionnaire_and_objective_monitoring",
        "source_files": ["SLQ_G.XPT", "PAXHD_G.XPT", "PAXDAY_G.XPT"],
        "fields": [
            "SLD010H",
            "SLQ050",
            "SLQ060",
            "PAXSTS",
            "PAXVMD",
            "PAXSWMD",
            "PAXQFD",
        ],
        "coverage_receipt": "CATEGORY_DATA_RECEIPT_2026-09-11",
    },
    "lifestyle_and_function": {
        "status": "real_source_available",
        "directness": "questionnaire_and_functional_measurements",
        "source_files": [
            "PAQ_G.XPT",
            "SMQ_G.XPT",
            "ALQ_G.XPT",
            "PFQ_G.XPT",
            "PAXHD_G.XPT",
            "PAXDAY_G.XPT",
        ],
        "fields": [
            "PAQ605",
            "SMQ020",
            "ALQ101",
            "PFQ049",
            "PFQ054",
            "PFQ061B",
            "PFQ061C",
            "PFQ061M",
            "PFQ061N",
            "PAXSTS",
            "PAXVMD",
            "PAXMTSD",
            "PAXWWMD",
            "PAXQFD",
        ],
        "coverage_receipt": "CATEGORY_DATA_RECEIPT_2026-09-11",
    },
    "mental_health_history": {
        "status": "real_source_available",
        "directness": "depression_screening_and_current_health_status_questionnaire",
        "source_files": ["DPQ_G.XPT", "HSQ_G.XPT"],
        "fields": [
            "HSD010",
            "HSQ470",
            "HSQ480",
            "HSQ490",
            "HSQ493",
            "HSQ496",
            "HSAQUEX",
            "DPQ010",
            "DPQ020",
            "DPQ030",
            "DPQ040",
            "DPQ050",
            "DPQ060",
            "DPQ070",
            "DPQ080",
            "DPQ090",
            "DPQ100",
        ],
        "coverage_receipt": "CATEGORY_DATA_RECEIPT_2026-09-11",
    },
}

_OBSERVED_SOURCE_ROWS = {
    "body_composition": 9243,
    "fluid_and_cellular": 5329,
    "muscle_health": 7821,
    "joint_health": 5559,
    "bone_health": 4620,
    "skin_health": 3768,
    "blood_health": 7953,
    "cardiovascular_health": 7060,
    "cardiorespiratory_health": 7495,
    "immune_inflammatory_health": 8299,
    "brain_cognitive_health": 1687,
    "metabolic_health": 9363,
    "kidney_health": 7636,
    "liver_health": 10409,
    "mental_health_history": 8956,
    "sleep_and_recovery": 61168,
    "lifestyle_and_function": 61168,
}

_OBSERVED_SOURCE_PARTICIPANTS = {
    "body_composition": 9243,
    "fluid_and_cellular": 5329,
    "muscle_health": 7821,
    "joint_health": 5559,
    "bone_health": 4620,
    "skin_health": 3768,
    "blood_health": 7953,
    "cardiovascular_health": 7060,
    "cardiorespiratory_health": 7495,
    "immune_inflammatory_health": 8299,
    "brain_cognitive_health": 1687,
    "metabolic_health": 9363,
    "kidney_health": 7636,
    "liver_health": 10409,
    "sleep_and_recovery": 7821,
    "lifestyle_and_function": 7821,
    "mental_health_history": 8956,
}

_ADDITIONAL_CYCLE_SOURCES = {
    "body_composition": {
        "NHANES_2013_2014": {
            "files": ["BMX_H.XPT"],
            "fields": ["BMXWT", "BMXHT", "BMXBMI", "BMXWAIST", "BMXARMC", "BMXSAD1"],
        }
    },
    "muscle_health": {
        "NHANES_2013_2014": {"files": ["DXX_H.XPT"], "fields": ["DXDLALE", "DXDRALE"]}
    },
    "bone_health": {
        "NHANES_2013_2014": {
            "files": ["DXX_H.XPT"],
            "fields": ["DXDSTBMD", "DXDSTBMC", "DXDSTFAT", "DXXLSBMD"],
        }
    },
    "brain_cognitive_health": {
        "NHANES_2013_2014": {
            "files": ["CFQ_H.XPT"],
            "fields": [
                "CFASTAT",
                "CFDCCS",
                "CFDCRNC",
                "CFDCST1",
                "CFDCSR",
                "CFDCIT1",
                "CFDAPP",
                "CFDAST",
                "CFDDS",
            ],
        }
    },
    "sleep_and_recovery": {
        "NHANES_2013_2014": {
            "files": ["SLQ_H.XPT", "PAXDAY_H.XPT"],
            "fields": ["SLD010H", "SLQ050", "SLQ060", "PAXVMD", "PAXSWMD", "PAXQFD"],
        }
    },
    "lifestyle_and_function": {
        "NHANES_2013_2014": {
            "files": ["PFQ_H.XPT", "PAXDAY_H.XPT"],
            "fields": [
                "PFQ049",
                "PFQ054",
                "PFQ061B",
                "PFQ061M",
                "PFQ061N",
                "PAXVMD",
                "PAXQFD",
            ],
        }
    },
    "mental_health_history": {
        "NHANES_2013_2014": {
            "files": ["DPQ_H.XPT"],
            "fields": [
                "DPQ010",
                "DPQ020",
                "DPQ030",
                "DPQ040",
                "DPQ050",
                "DPQ060",
                "DPQ070",
                "DPQ080",
                "DPQ090",
                "DPQ100",
            ],
        }
    },
    "blood_health": {
        "NHANES_2013_2014": {
            "files": ["CBC_H.XPT", "BIOPRO_H.XPT", "TCHOL_H.XPT", "TRIGLY_H.XPT"],
            "fields": [
                "LBXWBCSI",
                "LBXHGB",
                "LBXHCT",
                "LBXPLTSI",
                "LBXSAL",
                "LBXSCR",
                "LBXTC",
                "LBXTR",
                "LBDLDL",
            ],
        }
    },
    "cardiovascular_health": {
        "NHANES_2013_2014": {
            "files": ["BPX_H.XPT", "TCHOL_H.XPT", "TRIGLY_H.XPT"],
            "fields": [
                "BPXPLS",
                "BPXSY1",
                "BPXDI1",
                "BPXSY2",
                "BPXDI2",
                "BPXSY3",
                "BPXDI3",
                "LBXTC",
                "LBXTR",
                "LBDLDL",
            ],
        }
    },
    "cardiorespiratory_health": {
        "NHANES_2013_2014": {
            "files": ["BPX_H.XPT"],
            "fields": [
                "BPXPLS",
                "BPXSY1",
                "BPXDI1",
                "BPXSY2",
                "BPXDI2",
                "BPXSY3",
                "BPXDI3",
            ],
        }
    },
    "immune_inflammatory_health": {
        "NHANES_2013_2014": {
            "files": ["CBC_H.XPT", "BIOPRO_H.XPT"],
            "fields": ["LBXWBCSI", "LBXLYPCT", "LBXMOPCT", "LBXNEPCT", "LBXSAL"],
        }
    },
    "metabolic_health": {
        "NHANES_2013_2014": {
            "files": ["GLU_H.XPT", "GHB_H.XPT", "TCHOL_H.XPT", "TRIGLY_H.XPT"],
            "fields": ["LBXGLU", "LBXGH", "LBXTC", "LBXTR", "LBDLDL"],
        }
    },
    "kidney_health": {
        "NHANES_2013_2014": {
            "files": ["ALB_CR_H.XPT", "BIOPRO_H.XPT"],
            "fields": [
                "URXUMA",
                "URXUMS",
                "URXUCR",
                "URXCRS",
                "URDACT",
                "LBXSCR",
                "LBXSBU",
                "LBXSUA",
            ],
        }
    },
    "joint_health": {
        "NHANES_2013_2014": {
            "files": ["MCQ_H.XPT"],
            "fields": ["MCQ160A", "MCQ160N", "MCQ180A", "MCQ180N"],
        }
    },
    "skin_health": {
        "NHANES_2013_2014": {
            "files": ["DEQ_H.XPT"],
            "fields": [
                "DED031",
                "DEQ034A",
                "DEQ034C",
                "DEQ034D",
                "DEQ038G",
                "DEQ038Q",
                "DED120",
                "DED125",
            ],
        }
    },
    "liver_health": {
        "NHANES_2017_2018": {
            "files": ["LUX_J.XPT"],
            "fields": [
                "LUAXSTAT",
                "LUANMVGP",
                "LUARXNC",
                "LUARXND",
                "LUARXIN",
                "LUAPNME",
                "LUANMTGP",
                "LUATECH",
                "LUXSMED",
                "LUXSIQR",
                "LUXSIQRM",
                "LUXCAPM",
                "LUXCPIQR",
            ],
            "receipt": "REAL_DATA_INTAKE_2017_2018_LIVER_RECEIPT_2026-09-11",
        }
    },
}

_ADDITIONAL_CYCLE_SOURCES_2015_2016 = {
    "body_composition": {
        "files": ["BMX_I.XPT"],
        "fields": ["BMXWT", "BMXHT", "BMXBMI", "BMXWAIST", "BMXARMC", "BMXSAD1"],
    },
    "muscle_health": {"files": ["DXX_I.XPT"], "fields": ["DXDLALE", "DXDRALE"]},
    "bone_health": {
        "files": ["DXX_I.XPT"],
        "fields": ["DXDSTBMD", "DXDSTBMC", "DXDSTFAT", "DXXLSBMD"],
    },
    "joint_health": {
        "files": ["MCQ_I.XPT"],
        "fields": ["MCQ160A", "MCQ160N", "MCQ180A", "MCQ180N"],
    },
    "skin_health": {
        "files": ["DEQ_I.XPT"],
        "fields": [
            "DED031",
            "DEQ034A",
            "DEQ034C",
            "DEQ034D",
            "DEQ038G",
            "DEQ038Q",
            "DED120",
            "DED125",
        ],
    },
    "blood_health": {
        "files": ["CBC_I.XPT", "BIOPRO_I.XPT", "TCHOL_I.XPT", "TRIGLY_I.XPT"],
        "fields": [
            "LBXWBCSI",
            "LBXHGB",
            "LBXHCT",
            "LBXPLTSI",
            "LBXSAL",
            "LBXSCR",
            "LBXTC",
            "LBXTR",
            "LBDLDL",
        ],
    },
    "cardiovascular_health": {
        "files": ["BPX_I.XPT", "TCHOL_I.XPT", "TRIGLY_I.XPT"],
        "fields": [
            "BPXPLS",
            "BPXSY1",
            "BPXDI1",
            "BPXSY2",
            "BPXDI2",
            "BPXSY3",
            "BPXDI3",
            "LBXTC",
            "LBXTR",
            "LBDLDL",
        ],
    },
    "cardiorespiratory_health": {
        "files": ["BPX_I.XPT"],
        "fields": [
            "BPXPLS",
            "BPXSY1",
            "BPXDI1",
            "BPXSY2",
            "BPXDI2",
            "BPXSY3",
            "BPXDI3",
        ],
    },
    "immune_inflammatory_health": {
        "files": ["CBC_I.XPT", "BIOPRO_I.XPT"],
        "fields": ["LBXWBCSI", "LBXLYPCT", "LBXMOPCT", "LBXNEPCT", "LBXSAL"],
    },
    "metabolic_health": {
        "files": ["GLU_I.XPT", "GHB_I.XPT", "TCHOL_I.XPT", "TRIGLY_I.XPT"],
        "fields": ["LBXGLU", "LBXGH", "LBXTC", "LBXTR", "LBDLDL"],
    },
    "kidney_health": {
        "files": ["ALB_CR_I.XPT", "BIOPRO_I.XPT"],
        "fields": [
            "URXUMA",
            "URXUMS",
            "URXUCR",
            "URXCRS",
            "URDACT",
            "LBXSCR",
            "LBXSBU",
            "LBXSUA",
        ],
    },
    "liver_health": {
        "files": ["BIOPRO_I.XPT"],
        "fields": [
            "LBXSAL",
            "LBXSATSI",
            "LBXSASSI",
            "LBXSAPSI",
            "LBXSGTSI",
            "LBXSTB",
            "LBXSTP",
        ],
    },
    "sleep_and_recovery": {
        "files": ["SLQ_I.XPT"],
        "fields": ["SLD012", "SLQ030", "SLQ040", "SLQ050", "SLQ120"],
    },
    "lifestyle_and_function": {
        "files": ["PFQ_I.XPT"],
        "fields": ["PFQ049", "PFQ054", "PFQ061B", "PFQ061M", "PFQ061N"],
    },
    "mental_health_history": {
        "files": ["DPQ_I.XPT"],
        "fields": [
            "DPQ010",
            "DPQ020",
            "DPQ030",
            "DPQ040",
            "DPQ050",
            "DPQ060",
            "DPQ070",
            "DPQ080",
            "DPQ090",
            "DPQ100",
        ],
    },
}

_ADDITIONAL_CYCLE_SOURCES_2005_2006 = {
    "body_composition": {
        "files": ["BMX_D.XPT"],
        "fields": ["BMXWT", "BMXBMI", "BMXWAIST"],
    },
    "muscle_health": {"files": ["DXX_D.XPT"], "fields": ["DXDSTBMC", "DXXRABMC"]},
    "bone_health": {
        "files": ["DXX_D.XPT"],
        "fields": ["DXDTOBMC", "DXDTOBMD", "DXDTOFAT"],
    },
    "blood_health": {
        "files": ["CBC_D.XPT"],
        "fields": ["LBXWBCSI", "LBXHGB", "LBXPLTSI"],
    },
    "cardiovascular_health": {
        "files": ["BPX_D.XPT", "TCHOL_D.XPT", "TRIGLY_D.XPT"],
        "fields": ["BPXSY1", "BPXDI1", "LBXTC", "LBXTR"],
    },
    "cardiorespiratory_health": {
        "files": ["BPX_D.XPT"],
        "fields": ["BPXSY1", "BPXDI1"],
    },
    "immune_inflammatory_health": {
        "files": ["CBC_D.XPT"],
        "fields": ["LBXLYPCT", "LBDLYMNO", "LBDNENO"],
    },
    "joint_health": {
        "files": ["MCQ_D.XPT", "PFQ_D.XPT"],
        "fields": ["MCQ160A", "MCQ160C", "PFQ054", "PFQ059"],
    },
    "kidney_health": {"files": ["ALB_CR_D.XPT"], "fields": ["URXUMA", "URXUCR"]},
    "liver_health": {
        "files": ["BIOPRO_D.XPT"],
        "fields": ["LBXSATSI", "LBXSASSI", "LBXSTB", "LBXSTP"],
    },
    "lifestyle_and_function": {
        "files": ["PFQ_D.XPT"],
        "fields": ["PFQ049", "PFQ054", "PFQ059"],
    },
    "mental_health_history": {
        "files": ["DPQ_D.XPT"],
        "fields": ["DPQ010", "DPQ050", "DPQ100"],
    },
    "metabolic_health": {
        "files": ["GLU_D.XPT", "GHB_D.XPT", "TRIGLY_D.XPT"],
        "fields": ["LBXGLU", "LBXGH", "LBXTR"],
    },
    "skin_health": {"files": ["DEQ_D.XPT"], "fields": ["DED031", "DEQ034C", "DEQ038G"]},
    "sleep_and_recovery": {
        "files": ["SLQ_D.XPT"],
        "fields": ["SLD010H", "SLQ050", "SLQ060"],
    },
}

_ADDITIONAL_CYCLE_SOURCES_2007_2008 = {
    "body_composition": {
        "files": ["BMX_E.XPT"],
        "fields": ["BMXWT", "BMXBMI", "BMXWAIST"],
    },
    "muscle_health": {"files": ["BMX_E.XPT"], "fields": ["BMXARMC"]},
    "blood_health": {
        "files": ["CBC_E.XPT"],
        "fields": ["LBXWBCSI", "LBXHGB", "LBXPLTSI"],
    },
    "cardiovascular_health": {
        "files": ["BPX_E.XPT", "TCHOL_E.XPT", "TRIGLY_E.XPT"],
        "fields": ["BPXSY1", "BPXDI1", "LBXTC", "LBXTR"],
    },
    "cardiorespiratory_health": {
        "files": ["BPX_E.XPT"],
        "fields": ["BPXSY1", "BPXDI1"],
    },
    "immune_inflammatory_health": {
        "files": ["CBC_E.XPT"],
        "fields": ["LBXLYPCT", "LBDLYMNO", "LBDNENO"],
    },
    "joint_health": {
        "files": ["MCQ_E.XPT", "PFQ_E.XPT"],
        "fields": ["MCQ160A", "MCQ160C", "PFQ054", "PFQ059"],
    },
    "kidney_health": {"files": ["ALB_CR_E.XPT"], "fields": ["URXUMA", "URXUCR"]},
    "liver_health": {
        "files": ["BIOPRO_E.XPT"],
        "fields": ["LBXSATSI", "LBXSASSI", "LBXSTB", "LBXSTP"],
    },
    "lifestyle_and_function": {
        "files": ["PFQ_E.XPT"],
        "fields": ["PFQ049", "PFQ054", "PFQ059"],
    },
    "mental_health_history": {
        "files": ["DPQ_E.XPT"],
        "fields": ["DPQ010", "DPQ050", "DPQ100"],
    },
    "metabolic_health": {
        "files": ["GLU_E.XPT", "GHB_E.XPT", "TRIGLY_E.XPT"],
        "fields": ["LBXGLU", "LBXGH", "LBXTR"],
    },
    "sleep_and_recovery": {
        "files": ["SLQ_E.XPT"],
        "fields": ["SLD010H", "SLQ050", "SLQ060"],
    },
}

_ADDITIONAL_CYCLE_SOURCES_2017_2018 = {
    category: {
        "files": sorted(
            {source.replace("_I.XPT", "_J.XPT") for source in payload["files"]}
        ),
        "fields": list(payload["fields"]),
        "receipt": "REAL_DATA_INTAKE_2017_2018_CATEGORY_RECEIPT_2026-09-11",
    }
    for category, payload in _ADDITIONAL_CYCLE_SOURCES_2015_2016.items()
}
_ADDITIONAL_CYCLE_SOURCES_2017_2018["body_composition"]["fields"].remove("BMXSAD1")
_ADDITIONAL_CYCLE_SOURCES_2017_2018["joint_health"]["fields"] = [
    "MCQ160A",
    "MCQ160N",
]
_ADDITIONAL_CYCLE_SOURCES_2017_2018["lifestyle_and_function"]["files"] += [
    "ALQ_J.XPT",
    "PAQ_J.XPT",
    "SMQ_J.XPT",
]
_ADDITIONAL_CYCLE_SOURCES_2017_2018["lifestyle_and_function"]["fields"] += [
    "ALQ111",
    "PAQ605",
    "SMQ020",
]

_ADDITIONAL_CYCLE_SOURCES_2021_2023 = {
    "body_composition": {
        "files": ["BMX_L.XPT"],
        "fields": ["BMXWT", "BMXHT", "BMXBMI", "BMXWAIST", "BMXARMC"],
    },
    "joint_health": {"files": ["MCQ_L.XPT"], "fields": ["MCQ160A"]},
    "skin_health": {
        "files": ["DEQ_L.XPT"],
        "fields": ["DEQ034A", "DEQ034C", "DEQ034D"],
    },
    "blood_health": {
        "files": ["CBC_L.XPT", "BIOPRO_L.XPT", "TCHOL_L.XPT", "TRIGLY_L.XPT"],
        "fields": [
            "LBXWBCSI",
            "LBXHGB",
            "LBXHCT",
            "LBXPLTSI",
            "LBXSAL",
            "LBXSCR",
            "LBXTC",
            "LBXTLG",
            "LBDLDL",
        ],
    },
    "cardiovascular_health": {
        "files": ["TCHOL_L.XPT", "TRIGLY_L.XPT"],
        "fields": ["LBXTC", "LBXTLG", "LBDLDL"],
    },
    "immune_inflammatory_health": {
        "files": ["CBC_L.XPT", "BIOPRO_L.XPT"],
        "fields": ["LBXWBCSI", "LBXLYPCT", "LBXMOPCT", "LBXNEPCT", "LBXSAL"],
    },
    "metabolic_health": {
        "files": ["GLU_L.XPT", "GHB_L.XPT", "TCHOL_L.XPT", "TRIGLY_L.XPT"],
        "fields": ["LBXGLU", "LBXGH", "LBXTC", "LBXTLG", "LBDLDL"],
    },
    "kidney_health": {
        "files": ["ALB_CR_L.XPT", "BIOPRO_L.XPT"],
        "fields": [
            "URXUMA",
            "URXUMS",
            "URXUCR",
            "URXCRS",
            "URDACT",
            "LBXSCR",
            "LBXSBU",
            "LBXSUA",
        ],
    },
    "liver_health": {
        "files": ["BIOPRO_L.XPT"],
        "fields": [
            "LBXSAL",
            "LBXSATSI",
            "LBXSASSI",
            "LBXSAPSI",
            "LBXSGTSI",
            "LBXSTB",
            "LBXSTP",
        ],
    },
    "sleep_and_recovery": {
        "files": ["SLQ_L.XPT"],
        "fields": ["SLD012", "SLQ300", "SLQ310", "SLQ320", "SLQ330", "SLD013"],
    },
    "mental_health_history": {
        "files": ["DPQ_L.XPT"],
        "fields": [
            "DPQ010",
            "DPQ020",
            "DPQ030",
            "DPQ040",
            "DPQ050",
            "DPQ060",
            "DPQ070",
            "DPQ080",
            "DPQ090",
            "DPQ100",
        ],
    },
    "lifestyle_and_function": {
        "files": ["ALQ_L.XPT", "PAQ_L.XPT", "SMQ_L.XPT"],
        "fields": ["ALQ111", "PAD790Q", "PAD800", "SMQ020"],
    },
}

_ADDITIONAL_CYCLE_ABSENCES = {
    "NHANES_2005_2006": {
        "brain_cognitive_health": "no usable CFQ_D.XPT source file was available",
        "fluid_and_cellular": "no usable BIX_D.XPT source file was available",
    },
    "NHANES_2007_2008": {
        "bone_health": "no usable DXX_E.XPT source file was available",
        "brain_cognitive_health": "no usable CFQ_E.XPT source file was available",
        "fluid_and_cellular": "no usable BIX_E.XPT source file was available",
        "skin_health": "no usable DEQ_E.XPT source file was available",
    },
    "NHANES_2015_2016": {
        "brain_cognitive_health": "not mapped in the cycle receipt",
        "fluid_and_cellular": "not mapped in the cycle receipt",
    },
    "NHANES_2017_2018": {
        "brain_cognitive_health": "not mapped in the cycle receipt",
        "fluid_and_cellular": "not mapped in the cycle receipt",
    },
    "NHANES_2021_2023": {
        "bone_health": "reduced exam source absent",
        "brain_cognitive_health": "reduced exam source absent",
        "cardiorespiratory_health": "BPX/spirometry source absent",
        "fluid_and_cellular": "BIA source absent",
        "muscle_health": "grip/DXA source absent",
    },
}


def category_source_for(
    category: str, *, include_additional_cycles: bool = False
) -> dict[str, Any]:
    """Return a copy of the real-source catalog entry for one category."""

    try:
        entry = _CATALOG[category]
    except KeyError as error:
        raise KeyError(f"unknown category source catalog entry: {category}") from error
    result = {
        **entry,
        "observed_source_rows": _OBSERVED_SOURCE_ROWS[category],
        "observed_source_participants": _OBSERVED_SOURCE_PARTICIPANTS[category],
        "source_files": list(entry["source_files"]),
        "fields": list(entry["fields"]),
        "interpretation": (
            "Real public source fields or measured proxies are available for "
            "local research mapping; this does not establish patient validity "
            "or a category-specific age."
        ),
        "distribution_evidence": {
            "status": "real_distribution_receipt",
            "receipt": "CATEGORY_DISTRIBUTION_RECEIPT_2026-09-11",
            "source_file": _REPRESENTATIVE_DISTRIBUTION_FIELDS[category][0],
            "field": _REPRESENTATIVE_DISTRIBUTION_FIELDS[category][1],
            "interpretation": (
                "representative unfiltered public-use distribution; not a "
                "clinical reference interval"
            ),
        },
    }
    if include_additional_cycles:
        additional_sources = {**_ADDITIONAL_CYCLE_SOURCES.get(category, {})}
        if _ADDITIONAL_CYCLE_SOURCES_2005_2006.get(category):
            additional_sources["NHANES_2005_2006"] = {
                **_ADDITIONAL_CYCLE_SOURCES_2005_2006[category],
                "receipt": "REAL_DATA_INTAKE_2005_2006_CATEGORY_RECEIPT_2026-09-11",
            }
        if _ADDITIONAL_CYCLE_SOURCES_2007_2008.get(category):
            additional_sources["NHANES_2007_2008"] = {
                **_ADDITIONAL_CYCLE_SOURCES_2007_2008[category],
                "receipt": "REAL_DATA_INTAKE_2007_2008_CATEGORY_RECEIPT_2026-09-11",
            }
        if _ADDITIONAL_CYCLE_SOURCES_2015_2016.get(category):
            additional_sources["NHANES_2015_2016"] = (
                _ADDITIONAL_CYCLE_SOURCES_2015_2016[category]
            )
        if _ADDITIONAL_CYCLE_SOURCES_2017_2018.get(category):
            cycle = _ADDITIONAL_CYCLE_SOURCES_2017_2018[category]
            existing = additional_sources.get("NHANES_2017_2018")
            if existing:
                cycle = {
                    **cycle,
                    "files": sorted(set(existing["files"]) | set(cycle["files"])),
                    "fields": list(existing["fields"])
                    + [
                        field
                        for field in cycle["fields"]
                        if field not in existing["fields"]
                    ],
                    "receipt": existing.get("receipt", cycle["receipt"]),
                }
            additional_sources["NHANES_2017_2018"] = cycle
        if _ADDITIONAL_CYCLE_SOURCES_2021_2023.get(category):
            additional_sources["NHANES_2021_2023"] = {
                **_ADDITIONAL_CYCLE_SOURCES_2021_2023[category],
                "receipt": "REAL_DATA_INTAKE_2021_2023_CATEGORY_RECEIPT_2026-09-11",
            }
        result["additional_cycle_sources"] = {
            cycle: {
                "files": list(source["files"]),
                "fields": list(source["fields"]),
                "receipt": source.get(
                    "receipt", "REAL_DATA_INTAKE_2013_2014_RECEIPT_2026-09-11"
                ),
            }
            for cycle, source in additional_sources.items()
        }
        cycle_coverage: dict[str, dict[str, Any]] = {}
        for cycle, source in result["additional_cycle_sources"].items():
            cycle_coverage[cycle] = {
                "status": "real_source_present",
                "files": list(source["files"]),
                "fields": list(source["fields"]),
                "receipt": source["receipt"],
            }
        for cycle, absences in _ADDITIONAL_CYCLE_ABSENCES.items():
            if category in absences:
                cycle_coverage[cycle] = {
                    "status": "not_collected_in_cycle",
                    "reason": absences[category],
                }
        result["cycle_coverage"] = cycle_coverage
    return result


def category_source_catalog() -> dict[str, dict[str, Any]]:
    """Return the complete serializable catalog without shared mutable lists."""

    return {
        category: category_source_for(category, include_additional_cycles=True)
        for category in _CATALOG
    }
