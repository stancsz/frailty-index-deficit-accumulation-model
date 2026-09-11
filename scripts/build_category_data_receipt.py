"""Build a privacy-safe category coverage receipt from local NHANES XPT files.

The command reads explicit public-use source fields, counts non-missing rows,
and emits no SEQN values, measurements, raw rows, or local paths. It is an
intake and mapping check, not a clinical validation or reference-panel fit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from frailty_engine.nhanes import read_xpt  # noqa: E402


SCHEMA_VERSION = 1
FIELD_MAP: dict[str, tuple[tuple[str, str], ...]] = {
    "body_composition": (
        ("BMX_G.XPT", "BMXWT"),
        ("BMX_G.XPT", "BMXHT"),
        ("BMX_G.XPT", "BMXBMI"),
        ("BMX_G.XPT", "BMXWAIST"),
        ("BMX_G.XPT", "BMXARMC"),
        ("BMX_G.XPT", "BMXSAD1"),
        ("DXXAG_G.XPT", "DXXANFM"),
        ("DXXAG_G.XPT", "DXXANLM"),
        ("DXXAG_G.XPT", "DXXVFATM"),
    ),
    "fluid_and_cellular": (
        ("BIX_C.XPT", "BIAEXSTS"),
        ("BIX_C.XPT", "BIDFIT"),
        ("BIX_C.XPT", "BIDRECF"),
        ("BIX_C.XPT", "BIDRICF"),
        ("BIX_C.XPT", "BIDCM"),
        ("BIX_C.XPT", "BIDTD"),
        ("BIX_C.XPT", "BIDALPHA"),
        ("BIX_C.XPT", "BIDFC"),
        ("BIX_C.XPT", "BIDECF"),
        ("BIX_C.XPT", "BIDTBW"),
        ("BIX_C.XPT", "BIDICF"),
        ("BIX_C.XPT", "BIDFFM"),
        ("BIX_C.XPT", "BIDFAT"),
        ("BIX_C.XPT", "BIDPFAT"),
    ),
    "muscle_health": (
        ("MGX_G.XPT", "MGDEXSTS"),
        ("MGX_G.XPT", "MGDCGSZ"),
        ("MGX_G.XPT", "MGXH1T1"),
        ("MGX_G.XPT", "MGXH2T1"),
        ("MGX_G.XPT", "MGXH1T2"),
        ("MGX_G.XPT", "MGXH2T2"),
        ("DXX_G.XPT", "DXDLALE"),
        ("DXX_G.XPT", "DXDRALE"),
    ),
    "joint_health": (
        ("ARQ_F.XPT", "ARQ010"),
        ("ARQ_F.XPT", "ARQ020A"),
        ("ARQ_F.XPT", "ARQ020B"),
        ("ARQ_F.XPT", "ARQ020C"),
        ("ARQ_F.XPT", "ARQ020D"),
        ("ARQ_F.XPT", "ARQ020E"),
        ("ARQ_F.XPT", "ARQ020F"),
        ("ARQ_F.XPT", "ARQ020G"),
        ("ARQ_F.XPT", "ARQ040"),
        ("ARQ_F.XPT", "ARQ050"),
        ("ARQ_F.XPT", "ARQ060"),
        ("ARQ_F.XPT", "ARQ070"),
        ("ARQ_F.XPT", "ARQ073"),
        ("ARQ_F.XPT", "ARQ077"),
        ("ARQ_F.XPT", "ARQ080"),
        ("ARQ_F.XPT", "ARQ100"),
        ("ARQ_F.XPT", "ARQ110"),
        ("ARQ_F.XPT", "ARD125A"),
        ("ARQ_F.XPT", "ARQ125C"),
        ("ARQ_F.XPT", "ARQ125D"),
        ("ARQ_F.XPT", "ARQ125E"),
        ("ARX_F.XPT", "ARDEXSTS"),
        ("ARX_F.XPT", "ARXO2WD"),
        ("ARX_F.XPT", "ARXCCIN"),
        ("ARX_F.XPT", "ARXCCEX"),
        ("ARX_F.XPT", "ARDDINEX"),
        ("ARX_F.XPT", "ARXXDIST"),
        ("ARX_F.XPT", "ARDLFTL"),
        ("xr.dat", "XRPKLR"),
        ("xr.dat", "XRPKLL"),
        ("xr.dat", "XRPOMFR"),
        ("xr.dat", "XRPOMFL"),
        ("xr.dat", "XRPOMTR"),
        ("xr.dat", "XRPOMTL"),
        ("xr.dat", "XRPOLFR"),
        ("xr.dat", "XRPOLFL"),
        ("xr.dat", "XRPOLTR"),
        ("xr.dat", "XRPOLTL"),
        ("xr.dat", "XRPSMFR"),
        ("xr.dat", "XRPSMFL"),
        ("xr.dat", "XRPSMTR"),
        ("xr.dat", "XRPSMTL"),
        ("xr.dat", "XRPSLFR"),
        ("xr.dat", "XRPSLFL"),
        ("xr.dat", "XRPSLTR"),
        ("xr.dat", "XRPSLTL"),
        ("xr.dat", "XRPCHOR"),
        ("xr.dat", "XRPCHOL"),
        ("xr.dat", "XRPJRR"),
        ("xr.dat", "XRPJRL"),
        ("MCQ_G.XPT", "MCQ160A"),
        ("MCQ_G.XPT", "MCQ160N"),
        ("MCQ_G.XPT", "MCQ180A"),
        ("MCQ_G.XPT", "MCQ180N"),
        ("PFQ_G.XPT", "PFQ054"),
        ("PFQ_G.XPT", "PFQ059"),
        ("PFQ_G.XPT", "PFQ061B"),
        ("PFQ_G.XPT", "PFQ061C"),
        ("PFQ_G.XPT", "PFQ061D"),
        ("PFQ_G.XPT", "PFQ061E"),
        ("PFQ_G.XPT", "PFQ061F"),
        ("PFQ_G.XPT", "PFQ061G"),
        ("PFQ_G.XPT", "PFQ061H"),
        ("PFQ_G.XPT", "PFQ061I"),
        ("PFQ_G.XPT", "PFQ061J"),
        ("PFQ_G.XPT", "PFQ061K"),
        ("PFQ_G.XPT", "PFQ061L"),
        ("PFQ_G.XPT", "PFQ061M"),
        ("PFQ_G.XPT", "PFQ061N"),
        ("PFQ_G.XPT", "PFQ061O"),
        ("PFQ_G.XPT", "PFQ061P"),
        ("PFQ_G.XPT", "PFQ061Q"),
        ("PFQ_G.XPT", "PFQ061R"),
        ("PFQ_G.XPT", "PFQ061S"),
        ("PFQ_G.XPT", "PFQ061T"),
    ),
    "bone_health": (
        ("DXX_G.XPT", "DXDTOBMD"),
        ("DXX_G.XPT", "DXDTOBMC"),
        ("DXX_G.XPT", "DXDTOFAT"),
        ("DXX_G.XPT", "DXDSTBMD"),
        ("DXX_G.XPT", "DXDSTBMC"),
        ("DXX_G.XPT", "DXDSTFAT"),
        ("DXX_G.XPT", "DXXLSBMD"),
    ),
    "skin_health": (
        ("DEX_C.XPT", "MXAEXSTS"),
        ("DEX_C.XPT", "DEABACK"),
        ("DEX_C.XPT", "DEAINARM"),
        ("DEX_C.XPT", "DEAFRLEG"),
        ("DEX_C.XPT", "DEALOLEG"),
        ("DEX_C.XPT", "DEX1FITZ"),
        ("DEX_C.XPT", "DED1HDDX"),
        ("DEX_C.XPT", "DED1PSDX"),
        ("DEX_C.XPT", "DEX2FITZ"),
        ("DEX_C.XPT", "DED2HDDX"),
        ("DEX_C.XPT", "DED2PSDX"),
        ("DEX_C.XPT", "DEX6FITZ"),
        ("DEX_C.XPT", "DED6HDDX"),
        ("DEX_C.XPT", "DED6PSDX"),
        ("DEX_C.XPT", "DEX6PSFH"),
        ("DEX_C.XPT", "DEX6PSBK"),
        ("DEX_C.XPT", "DEX6PSPL"),
        ("DEX_C.XPT", "DEX6PSAL"),
        ("DEQ_G.XPT", "DED031"),
        ("DEQ_G.XPT", "DEQ034A"),
        ("DEQ_G.XPT", "DEQ034C"),
        ("DEQ_G.XPT", "DEQ034D"),
        ("DEQ_G.XPT", "DEQ038G"),
        ("DEQ_G.XPT", "DEQ038Q"),
        ("DEQ_G.XPT", "DED120"),
        ("DEQ_G.XPT", "DED125"),
    ),
    "blood_health": (
        ("APOB_G.XPT", "LBXAPB"),
        ("APOB_G.XPT", "LBDAPBSI"),
        ("BIOPRO_G.XPT", "LBXSAL"),
        ("BIOPRO_G.XPT", "LBXSCR"),
        ("CBC_G.XPT", "LBXWBCSI"),
        ("CBC_G.XPT", "LBXRDW"),
        ("CBC_G.XPT", "LBXRBCSI"),
        ("CBC_G.XPT", "LBXHGB"),
        ("CBC_G.XPT", "LBXHCT"),
        ("CBC_G.XPT", "LBXMCVSI"),
        ("CBC_G.XPT", "LBXPLTSI"),
        ("TCHOL_G.XPT", "LBXTC"),
        ("TRIGLY_G.XPT", "LBXTR"),
        ("TRIGLY_G.XPT", "LBDLDL"),
    ),
    "cardiovascular_health": (
        ("APOB_G.XPT", "LBXAPB"),
        ("APOB_G.XPT", "LBDAPBSI"),
        ("BPX_G.XPT", "BPXPLS"),
        ("BPX_G.XPT", "BPXSY1"),
        ("BPX_G.XPT", "BPXDI1"),
        ("BPX_G.XPT", "BPXSY2"),
        ("BPX_G.XPT", "BPXDI2"),
        ("BPX_G.XPT", "BPXSY3"),
        ("BPX_G.XPT", "BPXDI3"),
        ("TCHOL_G.XPT", "LBXTC"),
        ("TRIGLY_G.XPT", "LBXTR"),
        ("TRIGLY_G.XPT", "LBDLDL"),
    ),
    "cardiorespiratory_health": (
        ("ENX_G.XPT", "ENXSTAT"),
        ("ENX_G.XPT", "ENAATMPT"),
        ("ENX_G.XPT", "ENXTR1Q"),
        ("ENX_G.XPT", "ENXTR2Q"),
        ("ENX_G.XPT", "ENXMEAN"),
        ("BPX_G.XPT", "BPXPLS"),
        ("BPX_G.XPT", "BPXSY1"),
        ("BPX_G.XPT", "BPXDI1"),
        ("BPX_G.XPT", "BPXSY2"),
        ("BPX_G.XPT", "BPXDI2"),
        ("BPX_G.XPT", "BPXSY3"),
        ("BPX_G.XPT", "BPXDI3"),
        ("SPX_G.XPT", "SPXNFVC"),
        ("SPX_G.XPT", "SPXNFEV1"),
        ("SPX_G.XPT", "SPXNF257"),
        ("SPX_G.XPT", "SPXNPEF"),
        ("SPX_G.XPT", "SPXNQFVC"),
        ("SPX_G.XPT", "SPXNQFV1"),
        ("SPX_G.XPT", "SPDNACC"),
    ),
    "immune_inflammatory_health": (
        ("CRP_F.XPT", "LBXCRP"),
        ("ENX_G.XPT", "ENXMEAN"),
        ("CBC_G.XPT", "LBXWBCSI"),
        ("CBC_G.XPT", "LBXRDW"),
        ("CBC_G.XPT", "LBXLYPCT"),
        ("CBC_G.XPT", "LBXMOPCT"),
        ("CBC_G.XPT", "LBXNEPCT"),
        ("CBC_G.XPT", "LBXEOPCT"),
        ("CBC_G.XPT", "LBXBAPCT"),
        ("CBC_G.XPT", "LBDLYMNO"),
        ("CBC_G.XPT", "LBDMONO"),
        ("CBC_G.XPT", "LBDNENO"),
        ("CBC_G.XPT", "LBDEONO"),
        ("CBC_G.XPT", "LBDBANO"),
    ),
    "brain_cognitive_health": (
        ("CFQ_G.XPT", "CFASTAT"),
        ("CFQ_G.XPT", "CFDCCS"),
        ("CFQ_G.XPT", "CFDCRNC"),
        ("CFQ_G.XPT", "CFDCST1"),
        ("CFQ_G.XPT", "CFDCSR"),
        ("CFQ_G.XPT", "CFDCIT1"),
        ("CFQ_G.XPT", "CFDAST"),
        ("CFQ_G.XPT", "CFDAPP"),
        ("CFQ_G.XPT", "CFDDS"),
    ),
    "metabolic_health": (
        ("GLU_G.XPT", "LBXGLU"),
        ("GHB_G.XPT", "LBXGH"),
        ("DIQ_G.XPT", "DIQ010"),
        ("TCHOL_G.XPT", "LBXTC"),
        ("TRIGLY_G.XPT", "LBXTR"),
        ("TRIGLY_G.XPT", "LBDLDL"),
    ),
    "kidney_health": (
        ("ALB_CR_G.XPT", "URXUMA"),
        ("ALB_CR_G.XPT", "URXUMS"),
        ("ALB_CR_G.XPT", "URXUCR"),
        ("ALB_CR_G.XPT", "URXCRS"),
        ("ALB_CR_G.XPT", "URDACT"),
        ("BIOPRO_G.XPT", "LBXSCR"),
        ("BIOPRO_G.XPT", "LBXSBU"),
        ("BIOPRO_G.XPT", "LBXSUA"),
    ),
    "liver_health": (
        ("P_LUX.XPT", "LUAXSTAT"),
        ("P_LUX.XPT", "LUANMVGP"),
        ("P_LUX.XPT", "LUXSMED"),
        ("P_LUX.XPT", "LUXSIQR"),
        ("P_LUX.XPT", "LUXSIQRM"),
        ("P_LUX.XPT", "LUXCAPM"),
        ("P_LUX.XPT", "LUXCPIQR"),
        ("BIOPRO_G.XPT", "LBXSAL"),
        ("BIOPRO_G.XPT", "LBXSATSI"),
        ("BIOPRO_G.XPT", "LBXSASSI"),
        ("BIOPRO_G.XPT", "LBXSAPSI"),
        ("BIOPRO_G.XPT", "LBXSGTSI"),
        ("BIOPRO_G.XPT", "LBXSTB"),
        ("BIOPRO_G.XPT", "LBXSTP"),
    ),
    "sleep_and_recovery": (
        ("SLQ_G.XPT", "SLD010H"),
        ("SLQ_G.XPT", "SLQ050"),
        ("SLQ_G.XPT", "SLQ060"),
        ("PAXHD_G.XPT", "PAXSTS"),
        ("PAXDAY_G.XPT", "PAXVMD"),
        ("PAXDAY_G.XPT", "PAXSWMD"),
        ("PAXDAY_G.XPT", "PAXQFD"),
    ),
    "lifestyle_and_function": (
        ("PAQ_G.XPT", "PAQ605"),
        ("SMQ_G.XPT", "SMQ020"),
        ("ALQ_G.XPT", "ALQ101"),
        ("PFQ_G.XPT", "PFQ049"),
        ("PFQ_G.XPT", "PFQ054"),
        ("PFQ_G.XPT", "PFQ061B"),
        ("PFQ_G.XPT", "PFQ061C"),
        ("PFQ_G.XPT", "PFQ061M"),
        ("PFQ_G.XPT", "PFQ061N"),
        ("PAXHD_G.XPT", "PAXSTS"),
        ("PAXDAY_G.XPT", "PAXVMD"),
        ("PAXDAY_G.XPT", "PAXMTSD"),
        ("PAXDAY_G.XPT", "PAXWWMD"),
        ("PAXDAY_G.XPT", "PAXQFD"),
    ),
    "mental_health_history": (
        ("HSQ_G.XPT", "HSD010"),
        ("HSQ_G.XPT", "HSQ470"),
        ("HSQ_G.XPT", "HSQ480"),
        ("HSQ_G.XPT", "HSQ490"),
        ("HSQ_G.XPT", "HSQ493"),
        ("HSQ_G.XPT", "HSQ496"),
        ("HSQ_G.XPT", "HSAQUEX"),
        ("DPQ_G.XPT", "DPQ010"),
        ("DPQ_G.XPT", "DPQ020"),
        ("DPQ_G.XPT", "DPQ030"),
        ("DPQ_G.XPT", "DPQ040"),
        ("DPQ_G.XPT", "DPQ050"),
        ("DPQ_G.XPT", "DPQ060"),
        ("DPQ_G.XPT", "DPQ070"),
        ("DPQ_G.XPT", "DPQ080"),
        ("DPQ_G.XPT", "DPQ090"),
        ("DPQ_G.XPT", "DPQ100"),
    ),
}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    return parser


def _find(data_dir: Path, filename: str) -> Path:
    matches = sorted(path for path in data_dir.rglob(filename) if path.is_file())
    if len(matches) != 1:
        raise ValueError(f"expected exactly one local source for {filename}")
    return matches[0]


def _digest(path: Path) -> dict[str, Any]:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    frame = _read_source(path)
    return {
        "filename": path.name,
        "sha256": digest.hexdigest(),
        "rows": int(len(frame)),
        "columns": int(len(frame.columns)),
    }


def _field_summary(frame: Any, source: str, field: str) -> dict[str, Any]:
    if "SEQN" not in frame.columns or field not in frame.columns:
        raise ValueError(f"{source} is missing required field {field}")
    values = frame[["SEQN", field]].dropna(subset=[field])
    numeric = values[field]
    try:
        numeric = numeric.astype(float).dropna()
    except (TypeError, ValueError):
        numeric = []
    summary: dict[str, Any] = {
        "source": source,
        "field": field,
        "nonmissing_rows": int(len(values)),
        "unique_participants_with_value": int(values["SEQN"].nunique()),
    }
    if len(numeric):
        summary["descriptive_numeric_summary"] = {
            "n": int(len(numeric)),
            "mean": round(float(numeric.mean()), 6),
            "median": round(float(numeric.median()), 6),
            "min": round(float(numeric.min()), 6),
            "max": round(float(numeric.max()), 6),
            "interpretation": "unfiltered public-use source distribution; not a clinical reference interval",
        }
    return summary


def _read_source(path: Path) -> Any:
    if path.suffix.lower() == ".dat":
        names = ["SEQN"] + [
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
        ]
        return pd.read_fwf(
            path,
            widths=[5] + [1] * 22,
            names=names,
            dtype=str,
            keep_default_na=False,
        )
    return read_xpt(path)


def build_receipt(data_dir: Path) -> dict[str, Any]:
    files = sorted({source for fields in FIELD_MAP.values() for source, _ in fields})
    paths = {name: _find(data_dir, name) for name in files}
    frames = {name: _read_source(path) for name, path in paths.items()}
    categories: dict[str, Any] = {}
    for category, fields in FIELD_MAP.items():
        summaries = [
            _field_summary(frames[source], source, field) for source, field in fields
        ]
        categories[category] = {
            "status": "real_source_fields_present",
            "fields": summaries,
            "mapping_review": "pending",
            "clinical_validity": "not_established",
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "nhanes-category-data-receipt-v1",
        "data_sources": [_digest(paths[name]) for name in files],
        "categories": categories,
        "boundary": {
            "raw_rows_emitted": False,
            "measurements_emitted": False,
            "clinical_use": False,
            "numeric_category_age": "withheld",
            "e005_status": "blocked",
        },
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.check and args.output is None:
        raise SystemExit("--check requires --output")
    try:
        receipt = build_receipt(args.data_dir)
    except (OSError, ValueError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    serialized = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if args.check:
        if args.output.read_bytes() != serialized:
            print("ERROR: category receipt drift", file=sys.stderr)
            return 3
        print(f"category receipt verified: {args.output}")
        return 0
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(serialized)
        print(f"category receipt written: {args.output}")
    else:
        sys.stdout.buffer.write(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
