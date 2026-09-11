"""Fetch and receipt official CDC/NHANES codebook pages for mapped sources."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


SOURCES = {
    "2003_2004": ["BIX_C.XPT", "DEX_C.XPT"],
    "2009_2010": ["ARQ_F.XPT", "ARX_F.XPT", "CRP_F.XPT"],
    "2011_2012": [
        "ALB_CR_G.XPT",
        "ALQ_G.XPT",
        "APOB_G.XPT",
        "BIOPRO_G.XPT",
        "BMX_G.XPT",
        "BPX_G.XPT",
        "CBC_G.XPT",
        "CFQ_G.XPT",
        "DEQ_G.XPT",
        "DIQ_G.XPT",
        "DPQ_G.XPT",
        "DXXAG_G.XPT",
        "DXX_G.XPT",
        "ENX_G.XPT",
        "GLU_G.XPT",
        "GHB_G.XPT",
        "HSQ_G.XPT",
        "MCQ_G.XPT",
        "MGX_G.XPT",
        "PAXDAY_G.XPT",
        "PAXHD_G.XPT",
        "PAQ_G.XPT",
        "PFQ_G.XPT",
        "SLQ_G.XPT",
        "SMQ_G.XPT",
        "SPX_G.XPT",
        "TCHOL_G.XPT",
        "TRIGLY_G.XPT",
    ],
    "2013_2014": [
        "ALB_CR_H.XPT",
        "BIOPRO_H.XPT",
        "BMX_H.XPT",
        "BPX_H.XPT",
        "CBC_H.XPT",
        "CFQ_H.XPT",
        "DEQ_H.XPT",
        "DPQ_H.XPT",
        "DXX_H.XPT",
        "GHB_H.XPT",
        "GLU_H.XPT",
        "MCQ_H.XPT",
        "PAXDAY_H.XPT",
        "PFQ_H.XPT",
        "SLQ_H.XPT",
        "TCHOL_H.XPT",
        "TRIGLY_H.XPT",
    ],
    "2015_2016": [
        "ALB_CR_I.XPT",
        "BIOPRO_I.XPT",
        "BMX_I.XPT",
        "BPX_I.XPT",
        "CBC_I.XPT",
        "DEQ_I.XPT",
        "DPQ_I.XPT",
        "DXX_I.XPT",
        "GHB_I.XPT",
        "GLU_I.XPT",
        "MCQ_I.XPT",
        "PFQ_I.XPT",
        "SLQ_I.XPT",
        "TCHOL_I.XPT",
        "TRIGLY_I.XPT",
    ],
    "2017_2018": [
        "ALB_CR_J.XPT",
        "BIOPRO_J.XPT",
        "BMX_J.XPT",
        "BPX_J.XPT",
        "CBC_J.XPT",
        "DEQ_J.XPT",
        "DPQ_J.XPT",
        "DXX_J.XPT",
        "GHB_J.XPT",
        "GLU_J.XPT",
        "LUX_J.XPT",
        "ALQ_J.XPT",
        "PAQ_J.XPT",
        "SMQ_J.XPT",
        "MCQ_J.XPT",
        "PFQ_J.XPT",
        "SLQ_J.XPT",
        "TCHOL_J.XPT",
        "TRIGLY_J.XPT",
    ],
    "2021_2023": [
        "ALB_CR_L.XPT",
        "ALQ_L.XPT",
        "BIOPRO_L.XPT",
        "BMX_L.XPT",
        "CBC_L.XPT",
        "DEQ_L.XPT",
        "DPQ_L.XPT",
        "GLU_L.XPT",
        "GHB_L.XPT",
        "MCQ_L.XPT",
        "PAQ_L.XPT",
        "SLQ_L.XPT",
        "SMQ_L.XPT",
        "TCHOL_L.XPT",
        "TRIGLY_L.XPT",
    ],
}


def _url(cycle: str, filename: str) -> str:
    if filename == "xr.dat":
        return "https://wwwn.cdc.gov/nchs/data/nhanes3/11a/xr.sas"
    year = {
        "2003_2004": "2003",
        "2009_2010": "2009",
        "2011_2012": "2011",
        "2013_2014": "2013",
        "2015_2016": "2015",
        "2017_2018": "2017",
        "2021_2023": "2021",
    }[cycle]
    return f"https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/{year}/DataFiles/{filename[:-4]}.htm"


def build_receipt() -> dict[str, object]:
    entries: list[dict[str, object]] = []
    for cycle, filenames in SOURCES.items():
        for filename in filenames:
            url = _url(cycle, filename)
            entry: dict[str, object] = {
                "cycle": cycle,
                "filename": filename,
                "url": url,
            }
            try:
                request = Request(
                    url, headers={"User-Agent": "frailty-index-evidence/1.0"}
                )
                with urlopen(request, timeout=30) as response:
                    body = response.read()
                    entry.update(
                        {
                            "http_status": int(response.status),
                            "bytes": len(body),
                            "sha256": hashlib.sha256(body).hexdigest(),
                        }
                    )
            except HTTPError as error:
                entry.update(
                    {"http_status": int(error.code), "bytes": 0, "sha256": None}
                )
            except (OSError, URLError) as error:
                entry.update(
                    {
                        "http_status": None,
                        "bytes": 0,
                        "sha256": None,
                        "error_type": type(error).__name__,
                    }
                )
            entries.append(entry)
    return {
        "schema_version": 1,
        "receipt_type": "nhanes-official-codebook-receipt-v1",
        "source_count": len(entries),
        "entries": entries,
        "boundary": {
            "raw_rows_emitted": False,
            "measurements_emitted": False,
            "clinical_use": False,
            "e005_status": "blocked",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    receipt = build_receipt()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        f"codebook receipt written: {args.output} ({receipt['source_count']} sources)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
