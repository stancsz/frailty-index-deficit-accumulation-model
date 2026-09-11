# 009 — What can permitted public data prove about this tool, and what can it not prove for clinical readiness?

- **scope:** Permitted public data (NHANES public-use BIA and linked-mortality files), the repository's deterministic engineering tests, synthetic fixtures, and public Pages artifacts, and their role in advancing research readiness versus clinical production readiness. Verified 2026-09-01.
- **status:** draft
- **verified:** 2026-09-01
- **decision it feeds:** Whether public-data receipts advance the evidence package for G3 ("Build the public-data proof package" in GOAL.md §7) and whether they may be cited toward clinical readiness without implying E-005 approval.
- **gap statement:** Public NHANES data and software tests can demonstrate that the intake, parsing, and FI calculation work deterministically on real public data, and they can support development-stage model training. They cannot establish clinical validity, transportability, fairness, safety, outcome prediction, mortality risk, or regulatory clearance.

## Answer

Public data proves engineering competence and reproducibility. It does not prove clinical readiness.

### What public data can prove

1. **Deterministic intake and provenance.** The NHANES adapter parses cycle-specific BIA XPT tables and linked-mortality fixed-width files without imputation, preserves source columns, units, and quality fields, and records each file's URL, cycle, and SHA-256 digest. This proves that real public data can be consumed reproducibly.
2. **FI calculation on real data.** The accumulated-deficit calculator accepts parsed NHANES rows, excludes age and sex from scoring, computes a denominator-aware FI, and exposes the denominator caveat. This proves the core algorithm works on real-world missingness.
3. **Development-stage model training.** The XGBoost `survival:cox` adapter can be trained on an approved NHANES extract using the manifest contract in `TRAINING_MANIFEST_TEMPLATE.json`. This proves the pipeline from public data to a trained artifact is reproducible.
4. **Internal holdout and leakage controls.** Patient-level split logic and fixture smoke tests demonstrate that the pipeline can enforce separation between training, internal validation, and any future external holdout set.
5. **Synthetic external-validation harness.** The `examples/external_validation_synthetic.json` fixture and `run_external_validation_smoke.py` runner exercise concordance, subgroup, and calibration-plot logic without requiring a real external cohort.
6. **Public documentation surface.** The GitHub Pages site can publish the method, the intake receipts, the synthetic demonstration, and the evidence boundary so a clinician or investor can trace every claim back to source code and public data.

### What public data cannot prove for clinical readiness

1. **Clinical validity or outcome prediction.** A model trained on NHANES public data with perturbed mortality endpoints and disclosure-controlled follow-up cannot be treated as a validated mortality or healthspan predictor.
2. **External transportability.** NHANES is a US household-representative survey from 1999-2004. It does not establish that the model generalizes to other countries, eras, device generations, or clinic populations.
3. **Cutoff approval.** Every ordinal cutoff in the FI calculator remains an engineering default pending cohort-specific review. Public-data parsing does not replace that review.
4. **Reference-panel approval.** The shipped BIA reference panel is synthetic (`production_ready: False`). Published SECA panels (Peine et al., 2013; Bosy-Westphal et al., 2017) are starting points only, not embedded tables.
5. **Subgroup fairness or support.** Any sex, age band, or ethnicity subgroup metrics computed on NHANES public data are descriptive. They do not establish equity, transportability, or adequate support in a deployment population.
6. **Uncertainty calibration.** The shipped predictors return `ci_95: null`. A numeric confidence interval requires an approved predictor and cohort-based uncertainty analysis per the external-validation protocol.
7. **Regulatory clearance.** Nothing in this repository constitutes FDA clearance, CE marking, or any equivalent regulatory approval. The product is research-use-only and wellness-oriented per GOAL.md.

### Proof ladder: from public data toward clinical readiness

| rung | what it demonstrates | what it requires | current status |
|------|---------------------|------------------|----------------|
| R1: Public-data intake | Real NHANES files parse deterministically | SHA-256 digests, cycle manifest, column map | Implemented; E-007 passing |
| R2: Deterministic FI on public data | Accumulated-deficit computation works with real missingness | Denominator caveat visible, no imputation | Implemented; E-003 passing |
| R3: Development training manifest | Reproducible training recipe from public data | Frozen manifest with SHA-256, eligibility, quality rules | Template exists; not populated or approved |
| R4: Internal holdout validation | Patient-level separation prevents leakage | Split protocol, concordance on development cohort | Smoke tests exist; no approved cohort yet |
| R5: Synthetic external-validation harness | Engineering flow for subgroup/calibration plots | Fixture runner exercises all output paths | Implemented; fixture marked `clinical_use: forbidden` |
| R6: Approved external cohort validation | Outcome discrimination, calibration, subgroup evidence in independent population | CLSA or equivalent cohort, IRB/DUA, prespecified SAP, reviewer sign-off | Not started; E-005 blocked |
| R7: Reference-panel and cutoff approval | Domain-specific BIA tables and FI cutoffs validated for target population | Licensed panels, cohort-specific review, clinical sign-off | Not started; production_ready: false |
| R8: Uncertainty calibration | Clinically usable confidence intervals | Cohort-based CI construction, approved predictor, review | Not started; ci_95: null |
| R9: Clinical utility and human-factors review | Workflow fit, patient-facing language, decision impact | Qualified reviewer, pilot data, usability evidence | Not started |
| R10: Deployment controls and change management | Authenticated access, monitoring, rollback, immutable releases | Infrastructure owner, SOP, audit trail | Not started |

Rungs R1 through R5 advance **research readiness**. Rungs R6 through R10 are prerequisites for **clinical production readiness**. Public data alone cannot climb beyond R5.

## Claim / Evidence / Confidence receipts

| # | claim | evidence source | confidence |
|---|-------|----------------|------------|
| C1 | Public NHANES files can be parsed deterministically without imputation | E-007 passing, `src/frailty_engine/nhanes.py`, `docs/SOURCES.md` | high |
| C2 | FI calculation excludes age/sex, uses denominator-aware coding, and exposes the caveat | E-001, E-003 passing, `src/frailty_engine/fi.py`, `src/frailty_engine/features.py` | high |
| C3 | Training manifest template records all fields needed for reproducible training | `docs/TRAINING_MANIFEST_TEMPLATE.json`, `docs/SOURCES.md` | high |
| C4 | Synthetic external-validation harness exercises all output paths | E-006 passing, `scripts/run_external_validation_smoke.py`, `examples/external_validation_synthetic.json` | high |
| C5 | NHANES-linked mortality follow-up values may be perturbed for disclosure control | `docs/SOURCES.md`, CDC public-use documentation | high |
| C6 | No approved external cohort, clinical cutoff review, or production panel exists | E-005 blocked, `docs/EXTERNAL_VALIDATION_PROTOCOL.md` (template only), `docs/wiki/001-model-credibility.md` | high |
| C7 | Public Pages documentation can be published without patient data or restricted artifacts | E-008 passing, `docs/wiki/008-product-decisions.md` | high |

## Explicit limits

- This entry cites only repository-internal evidence and publicly available source documentation. It does not infer cohort results that are not yet computed.
- Status markers use `[unverified]` where the evidence is a template or placeholder that has not been populated and approved.
- The proof ladder is a planning artifact. Climbing each rung requires separate documentation, review, and sign-off as described in GOAL.md §7 and `ROADMAP.md` P3 through P6.
- The current clinical status remains **not ready**. Public data receipts alone cannot change it.

## Changelog

- 2026-09-01: created from GOAL.md, ROADMAP.md, EVAL.md, SOURCES.md, EXTERNAL_VALIDATION_PROTOCOL.md, TRAINING_MANIFEST_TEMPLATE.json, wiki 001, 002, 003, and 008. Distinguishes research readiness from clinical readiness with a 10-rung proof ladder.
