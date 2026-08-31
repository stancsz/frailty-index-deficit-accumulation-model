# 001 — What evidence is required before this biological-age engine can be called credible or production-ready?

- **scope:** the `frailty-index-deficit-accumulation-model` Python package at version `0.1.0`, its deterministic FI calculator, the optional `XGBoost survival:cox` adapter, the synthetic BIA reference panel, and any output derived from those components within this repository as of 2026-08-28.
- **status:** draft
- **verified:** 2026-08-28
- **decision it feeds:** whether downstream documentation, stakeholder communication, or deployment plans can claim the engine is "credible," "validated," or "production-ready"; and which reviewer, dataset, and approval obligations must be cleared before that claim becomes defensible.

## Answer

"Credible" and "production-ready" are not interchangeable. **Credibility** requires that the methods — accumulated-deficit construction, BIA transfer calibration, Gompertz age-equivalent inversion — are correctly implemented and traceable to published sources. **Production-readiness** requires additionally that the cutoffs, the reference panel, the training cohort, and the external cohort evaluation be approved for a specific population, device, and intended use.

As of 2026-08-28 the repository demonstrates the *credibility-surface* evidence only: a fixed 35-variable contract, a deterministic FI calculator that excludes `age`/`sex` from its scoring set, MVV enforcement, the synthetic fixture panel, and a development-only predictor. It does **not** demonstrate production-readiness for any real cohort. The gap between those states is closed by approval work, not by more code.

The remaining obligations fall into four named buckets, each with a distinct reviewer and a distinct evidence artifact:

1. **Reference-panel approval.** Replace the synthetic `ReferencePanel(production_ready=False)` shipped as `default_development_panel()` (see `src/frailty_engine/calibration.py:162`) with a versioned, age/sex-stratified panel whose tables are licensed/published sources with provenance (Peine et al., 2013 SECA; Bosy-Westphal et al., 2017 — both listed in `docs/SOURCES.md`).
2. **Cutoff approval.** Every ordinal cutoff in `src/frailty_engine/fi.py` is currently annotated as an "explicit, reviewable engineering default." Each must be re-validated for the target population with sex/age/ethnicity subgroup metrics before clinical claim.
3. **Cohort provenance and training-cohort approval.** An approved NHANES linked-mortality extract (or equivalent) must be assembled with explicit survey-weighting, eligibility, and disclosure documentation per `docs/SOURCES.md` (NHANES data-preparation section), and the `XGBoost survival:cox` adapter must be refit with that cohort.
4. **External, stratified validation.** A held-out external cohort (CLSA or equivalent per `GOAL.md` §6) must be run through `validate_external_cohort`, producing concordance, sex/age/ethnicity subgroup metrics, and the two required calibration plots (`homeostatic_deviation_calibration.png`, `biological_age_calibration.png`) via `write_calibration_plots` — and the report must clear `ValidationReport.blockers` (currently hard-blocked per `EVAL.md` E-005).

Until all four are satisfied, public-facing material must keep the `production_ready: false` flag, the development-predictor marker (`model_id="development-surrogate-v1"`), and the wellness framing; it must not assert clinical validity, causal health benefit, mortality risk, or prognostic utility.

## Receipts

### Measured repository evidence (what the checkout actually shows)

- The repository test suite passes; the exact observed count and command are recorded in `EVAL.md` E-001/E-003/E-006/E-007. — confidence: high
- The canonical input matrix is exactly 35 variables organized into 5 categories (demographics 7, BIA 5, blood 10, history 8, functional 5), each with a `FeatureSpec` containing `kind`, `minimum`, and `maximum` (`src/frailty_engine/features.py:21-57`). — confidence: high
- Fitted model matrix has 36 columns: the 35 inputs (with `sex` encoded as `sex_male`) plus the calculated FI, per `README.md` lines 91-94. — confidence: high
- The FI calculator deterministically excludes `age` and `sex` from scoring via `FI_EXCLUDED_FEATURES = frozenset({"age", "sex"})` (`src/frailty_engine/features.py:69-70`) and exposes the denominator caveat in `FIResult.caveat` (`src/frailty_engine/fi.py:58-60`). — confidence: high
- The shipped reference panel is explicitly synthetic and flagged `production_ready: False` with `source_note` reading "Synthetic values for software tests only; replace with licensed/published panel tables before deployment" (`src/frailty_engine/calibration.py:162-193`). — confidence: high
- The supplied biological-age predictor is `DevelopmentPredictor` with `model_id="development-surrogate-v1"`, `production_ready=False`, and module docstring "Deterministic integration fixture; not a trained mortality model" (`src/frailty_engine/model.py:432-433`). — confidence: high
- The public biological-age and trajectory responses return nullable uncertainty fields; the shipped predictor uses `ci_95: null` with `uncertainty_validated: false`, while the approved path can emit a numeric interval only after validated uncertainty is bound (`src/frailty_engine/model.py`, `src/frailty_engine/pipeline.py`, `src/frailty_engine/schemas.py`). — confidence: high
- MVV requires the 5 mandatory variables (age, sex, bmi, phase_angle, ecw_tbw), at least 6 blood values, glucose OR hba1c, and at least 4 history values; failures raise `InsufficientDataError` mapped to HTTP 422 (`src/frailty_engine/mvv.py:7-33`, `src/frailty_engine/api.py:18-31`). — confidence: high
- The public response schema carries `reference_panel_production_ready: bool`, `reference_panel_fixture_only: bool`, and `model_metadata.production_ready: bool` fields (`src/frailty_engine/schemas.py`), so callers can distinguish a synthetic panel from a merely unapproved panel without parsing identifiers — confidence: high
- `ReferencePanel.from_mapping` requires explicit boolean values for `production_ready` and `fixture_only` when present, so malformed JSON cannot be truthiness-coerced into a readiness decision (`src/frailty_engine/calibration.py`). — confidence: high
- The Pages SECA preview clears its prior detail rows on parse, read, size-limit, and synthetic-sample load failures, so an error state cannot retain measurements from a different file (`docs/site.js`). — confidence: high
- `EVAL.md` rows E-001 through E-004 and E-006 through E-083 are marked **passing** with concrete observed evidence; E-005 remains **blocked** because clinical approval evidence is absent. — confidence: high
- `SurvivalTrainingFrame.quality` reports cohort-level and standard sex/age-band/ethnicity-slice row/event/censoring totals and per-model-feature missing counts/rates without retaining patient identifiers; fitted native artifacts carry the same JSON-safe summary as metadata. This is descriptive software evidence, not a subgroup fairness or clinical validation result. — confidence: high
- `validate_external_cohort` also reports row/event/censoring support, event fraction, mean follow-up, concordance where estimable, and the effective comparable-pair denominator for each external sex, age-band, and ethnicity slice. It adds a deterministic support-aware percentile bootstrap interval with requested/valid replicate counts and withholds that interval when resampling support is sparse. These denominators and intervals expose evidence quality; they do not choose a clinically sufficient subgroup size, establish fairness, or create a clinical confidence interval. — confidence: high
- The Python and browser SECA importers share strict timestamp and row-shape handling, normalize Unicode numeric signs, and expose the same estimated-height/FFMI derivation provenance; native training artifacts retain the fixed XGBoost recipe, mapper provenance, and case-weight mode. These are engineering controls, not clinical validation. — confidence: high
- The Python and browser SECA importers both retain unmapped auxiliary row labels without allowing nonnumeric unmapped content to block mapped measurements; the Pages preview and normalized local handoff expose those labels. This is parser parity evidence, not clinical interpretation. — confidence: high
- The committed synthetic external-validation fixture is generated from a recorded seed, verified byte-for-byte in CI, and exercised through all standard subgroup and calibration paths. It is explicitly clinical-use forbidden and cannot substitute for an approved held-out cohort. — confidence: high
- The committed synthetic Pages demo artifact is rendered from fixed synthetic inputs and dates; its non-writing `--check` path runs in the Pages verification job so a stale `docs/demo-data.json` cannot be published by that workflow. — confidence: high
- The training package exposes a seeded SHA-256 patient-level fit/holdout split with independent event/censor stratification, duplicate-ID rejection, zero-overlap reporting, and no identifier output. It is leakage-control engineering evidence; the study-specific split and tuning boundary remain unapproved. — confidence: high
- The NHANES mortality adapter exposes MEC follow-up in canonical years and rejects a months unit when linked mortality records are supplied, preventing a second months-to-years conversion; direct source-row durations retain their explicit conversion path. This is a software unit guard, not evidence about endpoint validity. — confidence: high
- Wellness reports retain every measured non-in-range focus item in the API; Pages bounds only the default visible list, reports the shown/total count, and discloses the remaining items. This is a completeness and presentation contract, not a clinical prioritization claim. — confidence: high
- `docs/EXTERNAL_VALIDATION_PROTOCOL.md` is a placeholder-only, cross-linked
  template for freezing future external-cohort identity, endpoint/censoring and
  horizon, leakage, missingness, subgroup denominators, calibration, uncertainty,
  reproducibility, sign-off, and rollback evidence. It contains no cohort or
  results and does not satisfy E-005. — confidence: high for document/static
  verification; clinical approval remains absent
- Runtime release receipts hash the top-level and known nested `/health` field
  sets, and `validate_external_cohort` records exact model/panel ids, available
  SHA-256 identities, readiness, and fixture state in its report. These are
  software release and reproducibility controls, not clinical approval. —
  confidence: high

### Methodological rationale (cited in the repo's source boundary)

- Accumulated-deficit construction, 0-to-1 coding with intermediate 0.5, and missing-variable handling traced to Searle et al., "A standard procedure for creating a frailty index," *BMC Geriatrics* (2008), https://pmc.ncbi.nlm.nih.gov/articles/PMC2573877/, and the deficit-accumulation framing in Mitnitski et al., *The Scientific World Journal* (2001), https://doi.org/10.1100/tsw.2001.58 (see `docs/SOURCES.md` #deficit-accumulation). — confidence: high (citation exists; the prototype inherits the *method*, not validated thresholds)
- BIA transfer calibration rationale traced to Peine et al. (SECA, 2013, listed at https://www.seca.com/en_er/products/body-composition-analysis/clinical-studies.html) and Bosy-Westphal et al., *EJCN* (2017), https://doi.org/10.1038/ejcn.2017.27. None of the published tables are embedded; only a synthetic fixture is. — confidence: high
- Gompertz age-equivalent risk mapping traced to Levine & Crimmins, "Is 60 the New 50?," *Demography* (2018), https://doi.org/10.1007/s13524-017-0644-5 (`docs/SOURCES.md` biological-age section). The development predictor's default `GompertzMapper` values are explicit engineering defaults, **not** a fitted baseline curve; a fitted XGBoost artifact persists its profiled mapper in the model metadata. — confidence: high
- Cutoff anchors (BMI / BP / glycemia / eGFR / grip / FIB-4) traced to WHO, ACC/AHA 2017, ADA Standards of Care 2024, KDIGO 2012, EWGSOP2 2018, and Sterling FIB-4 respectively — all listed in `docs/SOURCES.md`. Each is annotated in `src/frailty_engine/fi.py` as an explicit, reviewable engineering default, not a clinically validated threshold. — confidence: high

### Unverified assumptions (must not be implied in downstream material)

- That any specific real-world clinic, device firmware, ethnicity band, or age range is correctly served by `default_development_panel()` — explicitly contradicted by the fixture's `production_ready: False` flag. — confidence: high (in the sense that this assumption is *not* supported)
- That the Gompertz defaults approximate an approved baseline mortality curve — `model.py:432-433` and the public model card say they do not. — confidence: high
- That the unweighted FI and the (unrun) biological-age predictor agree directionally for any real patient — only the clinical-use-forbidden synthetic engineering smoke exists in this checkout; E-005 remains blocked. — confidence: high
- That NHANES 1999-2004 BIA Xitron measurements are directly equivalent to modern SECA mBCA outputs without transfer calibration — the NHANES data-preparation section in `docs/SOURCES.md` explicitly denies this. — confidence: high
- That any intervention in `top_interventions` produces a causal health benefit — `recommendations.py` (referenced via `src/frailty_engine/__init__.py:13`) generates `action_type: "lifestyle"` strings; causal claims are not supported by the underlying data. — confidence: high
- That the current Kaplan–Meier calibration bins are clinically valid for the target cohort — the harness now excludes rows censored before the horizon from calibration bins and blocks when no usable follow-up remains, but censoring assumptions, uncertainty, target-cohort calibration, and clinical review remain approval obligations. — confidence: high
- That mapped NHANES sample weights alone provide a complex-survey variance estimate — the adapter passes positive weights through to XGBoost, but survey strata/PSU design and variance handling remain cohort-method obligations. — confidence: high

### Approval obligations (gates, not engineering debt)

- **E-005** (external CLSA/equivalent validation, stratified metrics, calibration, cutoff approval, production-model approval) — `verifier: Clinical reviewer`, `status: blocked`, no approved cohort, no clinical cutoff review, no production model approval. — confidence: high
- **E-010 engineering surface.** The SECA TableView importer, synthetic static examples, and range-based wellness report are software-verified, but they do not convert the development artifact into a clinically validated model. — confidence: high
- **Reference-panel replacement.** Production deployment requires `ReferencePanel.production_ready = True` populated from licensed/published SECA tables with provenance and units, not the synthetic fixture. — confidence: high
- **Cutoff review sign-off.** Every entry in `CUTOFF_SOURCES` whose source annotation includes "validate against the target cohort before production" (resting_hr, hs_crp, albumin, creatinine, alp, wbc, rdw, sleep_hours, visceral_fat) requires an explicit per-cutoff review outcome documented against the target cohort. — confidence: high
- **Cohort provenance and survey-weighting plan.** Approved NHANES extract or equivalent with explicit eligibility, mortality linkage choice, and disclosure-control acknowledgement per CDC public-use documentation. — confidence: high
- **Missingness and censoring analysis.** Use the software's cohort report as a starting receipt, then publish cohort and subgroup missingness, complete-case/native-missing sensitivity, and censoring-aware calibration analyses. — confidence: high
- **Wellness framing fence.** `GOAL.md` §4 ("Regulatory Framing") explicitly strips prognostic mortality terminology and renames `relative_aging_velocity` to `homeostatic_deviation_score`; downstream material must not reintroduce the prognostic vocabulary it removed. — confidence: high

## Changelog

- 2026-08-27: created.
- 2026-08-27: added cohort-level training-quality evidence, censoring-aware
  horizon calibration guards, and documented the remaining survey-design and
  clinical-calibration obligations.
- 2026-08-27: added SECA parser parity, numerical training guards, persisted
  recipe metadata, and truthful wellness direction/range presentation.
- 2026-08-27: aligned the browser SECA parser with Python for nonnumeric
  unmapped auxiliary rows and exposed those labels in local review handoffs.
- 2026-08-27: added the CDC-grounded training-manifest entry and a validator-backed
  non-approval template for source, linkage, quality, survey-design, and split provenance.
- 2026-08-27: added locked dependency resolution and an isolated installed-wheel
  smoke path to the engineering release receipts; clinical approval remains separate.
- 2026-08-27: closed a Python/browser SECA input-parity edge case by normalizing
  UTF-8 BOMs for path, text, and in-memory stream inputs; the installed-wheel
  smoke and existing E-015 receipt were rechecked.
- 2026-08-27: added deterministic support-aware bootstrap concordance intervals
  with explicit valid-replicate counts for external validation review; the
  interval remains an engineering aid pending an approved statistical analysis
  plan.
- 2026-08-27: added a reproducible synthetic external-validation engineering
  fixture and CI smoke runner, plus explicit fixture-only reference-panel
  readiness metadata; neither changes the E-005 clinical approval gate.
- 2026-08-27: added a deterministic patient-level training split helper and
  fixture smoke to make accidental row-level leakage harder to introduce;
  the study-specific split protocol remains an approval obligation.
- 2026-08-27: propagated the synthetic reference-panel fixture state into the
  typed assessment response and Pages handoff so downstream callers do not
  have to infer it from a panel identifier.
- 2026-08-27: added a non-writing deterministic check for the committed Pages
  demo artifact and required it before static deployment; clinical approval
  remains separate.
- 2026-08-27: added a placeholder-only external-validation and clinical-review
  protocol template with explicit freeze, evidence, sign-off, and stop/rollback
  fields; E-005 remains blocked.
- 2026-08-28: refreshed the snapshot and ledger coverage after R-084/E-083;
  the canonical software verifier is recorded as engineering evidence while
  E-005 remains blocked.
