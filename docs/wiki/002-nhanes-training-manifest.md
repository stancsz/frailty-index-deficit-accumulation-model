# 002 — What must a reproducible NHANES BIA-survival training manifest record?

- **scope:** public continuous-NHANES BIA cycles supported by this repository (1999-2000, 2001-2002, and 2003-2004), paired with the 2019 public-use linked-mortality release; verified 2026-08-27.
- **status:** draft
- **verified:** 2026-08-27
- **decision it feeds:** which provenance and analysis decisions must be frozen before a future training run can be independently reconstructed or submitted for clinical review.

## Answer

A useful manifest must bind each downloaded BIA and mortality file to its cycle,
official URL, retrieval date, and SHA-256 digest. It must also keep the
cycle-reviewed column map and missing-value policy beside the data rather than
letting a broad alias table decide silently.

The manifest must record the mortality join and endpoint semantics explicitly:
`SEQN` as the key, the eligibility rule, the vital-status event mapping, and the
follow-up field and unit. It must acknowledge the public-use disclosure-control
boundary before treating follow-up as a research endpoint.

For the BIA side, the manifest should preserve the exam-status and fit-quality
decision from each codebook, the measurement protocol/device context, units,
derived-field formulas, and the accepted quality codes. The accepted quality
codes are a study decision and should remain unfilled until reviewed; the
repository template therefore does not silently choose them.

Finally, it should bind the training anchor contract, optional-feature
missingness policy, sample-weight semantics, survey-variance plan, internal and
external split boundary, sensitivity runs, fixed model recipe, reference-panel
identity, and artifact hash. This makes a software-reproducible run inspectable
without implying that a populated manifest is clinical approval.

## Receipts

- CDC's 1999-2000 BIX documentation describes the BIA component as collected in the Mobile Examination Center and exposes examination status, fit quality, and raw/derived body-composition fields; this supports recording cycle-specific protocol and quality decisions — https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/1999/DataFiles/BIX.htm, accessed 2026-08-27 — confidence: high.
- CDC's continuous-NHANES index publishes component data and documentation by cycle, so the manifest should identify each cycle-specific file and codebook rather than only naming NHANES generally — https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=1999, accessed 2026-08-27 — confidence: high.
- CDC's linked-mortality page says researchers link 1999-2018 NHANES records using `SEQN`, and warns that public-use follow-up or cause-of-death values may be substituted for disclosure control while vital status is unchanged; this supports explicit linkage and disclosure fields — https://www.cdc.gov/nchs/linked-data/mortality-files/index.html, accessed 2026-08-27 — confidence: high.
- The public-use mortality dictionary identifies `ELIGSTAT`, `MORTSTAT`, and `SEQN` and defines the vital-status values; this supports recording eligibility and event mapping rather than inferring them — https://www.cdc.gov/nchs/data/datalinkage/public-use-linked-mortality-files-data-dictionary.pdf, accessed 2026-08-27 — confidence: high.
- The repository's `NHANESColumnMap` requires explicit source-column choices and its training frame preserves optional missingness while treating supplied weights as XGBoost case weights; this supports the software-side fields in `docs/TRAINING_MANIFEST_TEMPLATE.json` — `src/frailty_engine/nhanes.py` and `src/frailty_engine/training.py`, inspected 2026-08-27 — confidence: high for current repository behavior.

## Changelog

- 2026-08-27: created from the CDC source review and added the repository's non-approval manifest template.
