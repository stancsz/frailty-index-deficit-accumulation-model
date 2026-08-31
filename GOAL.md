# Project Goal: Clinical Healthspan & Deficit Accumulation Engine

## Primary Objective

To build a deterministic Clinical Frailty Index (FI) and a predictive Biological Age machine learning model. Designed for clinical decision support, the engine ingests standardized BIA data (SECA), routine bloods, and functional metrics to calculate current deficit load and predict biological aging velocity. The system is framed as a wellness and healthspan optimization tool, not a diagnostic medical device.

## Scope Addendum: SECA-to-Wellness Product Surface

This goal also covers the complete, evidence-bounded handoff from the clinic's
SECA TableView exports to a usable wellness workflow:

- Use the supplied SECA export shape to improve the importer and algorithm
  mapping, while keeping the raw patient export local and out of the repository.
  A synthetic, anonymized TableView-shaped fixture may be committed for
  reproducible tests and GitHub Pages examples.
- Make the Pages demo executable and reviewable: people can select synthetic
  examples, see the generated readout, load a local SECA CSV, and run the
  repository's browser/static tests before publication. A SECA-only scan stays
  a preview until the full MVV is met; no missing clinical fields are guessed.
- Provide a local assessment handoff after a SECA preview: prefill only observed
  canonical SECA fields, keep those values read-only, collect the remaining
  MVV inputs explicitly, and download a CLI/API-ready overlay. Route any
  assessment through the canonical Python engine; do not add a browser scorer,
  upload scan data, or infer missing measurements.
- Add a second, range-based wellness-improvement report alongside the biological
  age readout. It must identify measured focus areas, missing inputs, reference
  ranges, direction, practical recommendations, and a safe next step. It must
  state when an action effect is not estimated and must not promise a change in
  biological age, lifespan, diagnosis, or treatment outcome.
- Treat model credibility, uncertainty, privacy, accessibility, and production
  approval as part of the product scope. The engineering implementation can be
  complete while external-cohort validation, clinical cutoff review, and
  production model approval remain an explicit blocked gate.
- Include a local-only NHANES intake-shape review surface in the product
  scope. It must require an explicit supported-cycle map, preserve the CDC
  fixed-width mortality contract without inventing headers, emit deterministic
  aggregate evidence without paths, identifiers, raw rows, durations, or
  measurements, and keep data-review obligations separate from E-005.
- Carry a strict, versioned survey-design declaration through training frames,
  persisted model artifacts, and external-validation reports. The declaration
  must distinguish `case_weight`, `replicate`, `stratum`, and `not_provided`,
  reject contradictory raw-weight combinations, preserve explicit
  `weighting_applied`/`design_reviewed` flags, and block production-ready model
  approval when the declaration is missing, unsupported, or not provided.
  Complex-survey variance remains an explicit reviewer obligation until a
  dedicated adapter is implemented.
- Treat the installed-wheel loopback HTTP serving contract as a release
  invariant. A bounded smoke must start the real Uvicorn process, exercise
  liveness/readiness, diagnostics, valid and invalid assessment responses,
  response security headers, privacy-safe output, and clean process teardown
  on the supported Windows and Linux paths.
- Treat runtime-process provenance as a release invariant. Health/readiness and
  receipts must expose only non-secret identity for the installed project
  package tree, dependency set, Python runtime, and effective configuration;
  strict production admission must not accept an unverifiable source-only
  process. This identifies software drift and remains separate from E-005
  clinical validity.
- Treat subgroup support visibility as part of external-validation reporting.
  Reports must enumerate concrete engineering limitations for observed sex,
  age-band, and ethnicity strata—no events, no comparable pairs, or
  insufficient valid bootstrap replicates—without inventing clinical minimums
  or labeling a subgroup validated, fair, or safe. Prespecified numeric
  thresholds remain a statistical/clinical review obligation, not a software
  default.

---

## 1. Phase 0: Transfer-Calibration (Resolving BIA Drift)

Before training the ML model, we must reconcile the drift between NHANES (1999–2004 BIA) and the clinic's modern SECA mBCA data.

- **Reference Panels:** Utilize published, peer-reviewed SECA normative datasets (e.g., Peine et al., 2013; Bosy-Westphal et al., 2017) which provide age- and sex-stratified means and standard deviations for Phase Angle, ECW/TBW, and FFMI in modern populations.
- **Transformation:** All BIA inputs (both NHANES training data and clinic inference data) are converted to Z-scores relative to their respective device-era reference panels. The ML model trains and infers strictly on these normalized Z-scores, eliminating hardware-specific drift.

---

## 2. Feature Matrix & Minimum Viable Vector (MVV)

The system relies on an explicitly defined 35-variable matrix. The MVV is enforced at the API gateway. If the MVV is not met, the pipeline raises `InsufficientDataError`.

| Category (Count) | Variables | MVV Requirement |
| :--- | :--- | :--- |
| Demographics (7) | Age, Sex, BMI, Systolic BP, Diastolic BP, Resting HR, Waist Circumference. | Age, Sex, BMI mandatory. |
| BIA / SECA (5) | Phase Angle, ECW/TBW, FFMI, Skeletal Muscle Mass, Visceral Fat. | Phase Angle, ECW/TBW mandatory. |
| Blood Panel (10) | Fasting Glucose, HbA1c, hs-CRP, Albumin, Creatinine, eGFR, ALP, WBC, RDW, FIB-4. | ≥ 6 of 10. If both Glucose and HbA1c missing, reject. |
| Clinical History (8) | Hypertension, T2D, Osteoarthritis, Sleep Apnea, CVD, COPD, Cancer, Depression (0=No, 1=Yes). | ≥ 4 of 8. |
| Functional (5) | Grip Strength, Chair-Rise time, Smoking status, Alcohol heavy use, Sleep hours. | No strict minimum; XGBoost handles missingness. |

**Notes:**
- FIB-4 replaces AST/ALT ratio. FIB-4 uses Age, AST, ALT, and Platelets — a standard gerontological marker with established frailty associations.
- AST/ALT ratio is removed.
- The assessment MVV remains strict, but the survival-training frame uses a
  smaller anchor contract (age, sex, BMI) so optional blood, history, and
  functional missingness remains explicit `NaN` for XGBoost. Training-row
  eligibility and missingness rates must be reported through a cohort-quality
  receipt with event/censoring totals and per-feature counts/rates; this is not permission
  to bypass MVV at inference time.

---

## 3. The Dual-Pipeline Architecture

### Pipeline A: Deterministic Frailty Index (FI)

Strict rule-based calculator following the Rockwood methodology.

- Continuous variables map to deficits using sex-stratified clinical cutoffs (0 = healthy, 0.5 = intermediate, 1.0 = clinical deficit).
- FI is the ratio of accumulated deficit scores to the total number of validly measured variables.
- All ordinal cutoffs must be cited from published reference sources before production deployment.
- **Denominator caveat:** FI is sensitive to measurement completeness. A patient reported with 32 valid variables vs. 28 valid variables can yield different FI scores for the same biology. This is documented in the schema response.

### Pipeline B: Biological Age Predictor (ML)

- **Training Target:** All-cause mortality (Time-to-Event) using NHANES linked mortality files.
- **Model:** XGBoost Survival (`survival:cox`).
- **Missingness:** MNAR remains an analysis assumption, not a solved clinical
  fact. The training frame preserves optional missing values for XGBoost's
  native `missing` parameter (sparsity-aware split finding), with no MICE
  fabrication or completeness-only row selection. Assessment inference still
  enforces the MVV.
- **Inputs:** Z-score normalized BIA variables plus the calculated FI from Pipeline A.
- **HR-to-Age Mapping (Gompertz Inversion per Levine 2018):**
  1. Model outputs log-hazard ratio (linear predictor).
  2. Convert to 10-year mortality probability.
  3. Map that probability back to the Gompertz mortality curve of the baseline population to find the chronological age sharing identical mortality risk.
  4. Propagate an explicitly labeled uncertainty interval through to
     `biological_age.point_estimate` and `ci_95`; until cohort-based
     uncertainty analysis is approved, the API must set
     `uncertainty_validated: false` and must not call it a calibrated clinical
     confidence interval.

---

## 4. Reconciliation & Output Schema

**Reconciliation Rule:** FI represents Current Deficit Load (state). Biological Age represents Trajectory (rate). On conflict (e.g., acute injury spikes FI but underlying biology is robust), Biological Age is the headline metric — it captures the weighted survival outcome rather than a raw unweighted deficit sum.

**Regulatory Framing:** Wellness and healthspan tracker, not a diagnostic medical device. Prognostic mortality terminology is stripped from API output. `relative_aging_velocity` is renamed to `homeostatic_deviation_score` to neutralize prognostic meaning — the unit is deviation from age-expected norms, not a hazard ratio.

### JSON API Schema

```json
{
  "patient_id": "uuid",
  "data_quality": {
    "variables_measured": 32,
    "mvv_passed": true
  },
  "metrics": {
    "chronological_age": 45.0,
    "biological_age": {
      "point_estimate": 41.2,
      "ci_95": [38.5, 43.9],
      "uncertainty_method": "cohort_bootstrap_or_model_based",
      "uncertainty_construction": "wald_1_96_se",
      "uncertainty_validated": true,
      "interpretation": "Age-equivalent wellness estimate; not a lifespan, diagnostic, or treatment-effect prediction."
    },
    "current_deficit_load_fi": 0.14
  },
  "trajectory": {
    "homeostatic_deviation_score": -0.18,
    "score_ci_95": [-0.25, -0.09],
    "uncertainty_construction": "wald_1_96_se"
  },
  "top_interventions": [
    {
      "biomarker": "Phase Angle",
      "current_value": 4.8,
      "z_score": -1.2,
      "action_type": "lifestyle",
      "recommendation": "Increase load-bearing resistance training to improve cellular membrane integrity and intracellular volume."
    }
  ],
  "wellness_report": {
      "summary": {
      "status": "focus_areas",
      "measured_features": 13,
      "missing_features": 20,
        "focus_areas": 2
      },
      "action_effect_estimated": false,
      "clinical_or_lifespan_claim": false,
      "ranges": [
      {
        "biomarker": "Phase Angle",
        "current_value": 4.8,
        "target_range": {"label": "within ±1 development reference SD"},
        "status": "attention",
        "priority": "review",
        "action_type": "lifestyle",
        "recommendation": "Discuss progressive resistance training, adequate nutrition, and recovery with a qualified professional."
      }
    ],
    "focus_areas": [],
    "missing_features": ["systolic_bp", "waist_circumference"],
    "disclaimer": "Ranges are engineering or development reference bands, not individualized medical targets."
  }
}
```

---

## 5. SECA Equipment Import, Demonstration, and Wellness Report (Added Scope)

The product must use the practical data available from the clinic's SECA
equipment without publishing or silently completing a patient's record.

- **SECA TableView import:** Accept the equipment's exported CSV shape (`Value`,
  `Unit`, and one or more dated measurements). Map BMI, skeletal muscle mass,
  visceral adipose tissue, weight, fat mass, and segmental skeletal muscle
  values into a typed import preview. Derive fat-free mass and FFMI only when
  the same scan contains the required inputs; label every derivation and
  preserve the scan date. Never infer age, sex, laboratory values, history, or
  functional values from an equipment export.
- **Static public demonstration:** GitHub Pages must include at least two
  complete, clearly synthetic example profiles selectable without an API
  server. It must show the biological-age/healthspan readout, current FI,
  homeostatic deviation, data-quality flags, and the wellness report. The
  demonstration must state that the development surrogate is not a lifespan,
  mortality, diagnostic, or treatment-effect prediction.
- **Wellness report:** Every assessment must return measured-feature ranges,
  status, priority, and a conservative next-step recommendation. The report
  must distinguish engineering/reference bands from clinically approved
  thresholds, identify missing measurements, and never claim that a suggested
  action will lower biological age. Recommendations are for discussion with a
  qualified professional and are not medical advice. The API must also expose
  typed interpretation fields stating that action effects are not estimated and
  that the result makes no clinical or lifespan claim.
- **Report handoff:** The public Pages demonstration must make the selected
  wellness report usable beyond the screen by offering a local print action and
  a privacy-safe JSON handoff. The handoff may contain the synthetic readout,
  FI context, ranges, focus areas, missing inputs, recommendations, and model
  readiness boundary, but must exclude the input payload, patient identifiers,
  and any claim that an action changes biological age or lifespan.
- **Privacy boundary:** Do not commit the supplied named/patient-specific SECA
  export to the public repository or Pages site. Use it locally to verify the
  importer; public examples must be anonymized synthetic fixtures.
- **SECA readiness handoff:** A SECA-only preview must explicitly state that it
  is not a complete assessment and list the remaining MVV inputs (including
  absent scan fields, blood values, and history values). It must never imply
  that a body-composition export can supply age, sex, labs, history, or
  function.
- **Model approval boundary:** A fitted XGBoost artifact is not production-ready
  by itself. Promotion requires a hash-bound, human-authored approval sidecar
  that matches the artifact's model id, feature manifest, exact reference-panel
  file, uncertainty method/parameter, and evidence record; the serving API
  verifies that binding before admitting readiness.
- **Longitudinal progress view:** Provide a stateless comparison of two dated
  assessments for the same person. It must report readout deltas, measured
  reference-band/status transitions, new or resolved focus areas, and current
  recommendations without persisting or echoing the raw input payload. It must
  clearly state that descriptive change does not establish action effect or a
  change in biological age, lifespan, or clinical outcome.
- **Public SECA sample:** The Pages workflow must include a clearly labeled,
  anonymized synthetic TableView CSV that visitors can download or load into
  the local-only parser. It must remain separate from the supplied
  patient-specific export and must not imply that the sample is clinical data.
- **Completeness context:** The Pages report must make measured-feature,
  missing-feature, and focus-area counts visible beside the readout, list the
  missing canonical inputs without fabricating values, and explain that sparse
  inputs limit interpretation.
- **Segment trend handoff:** When two SECA scans contain the same segment
  values, the local preview and normalized handoff must expose latest-minus-
  previous segment changes. This is descriptive equipment data only; do not
  infer asymmetry thresholds, diagnoses, or action effects.
- **Assessment readiness identity:** Every assessment response must expose a
  typed `reference_panel_fixture_only` flag alongside the panel id and
  production-ready flag, so downstream callers can distinguish a synthetic
  development panel from a merely unapproved non-fixture panel without
  parsing identifiers.
- **Generated demo artifact gate:** The deterministic synthetic Pages artifact
  must have a non-writing `--check` path, and the Pages verification job must
  run it before deployment so published readouts cannot silently drift from
  the current Python assessment pipeline.
- **Release-configuration type boundary:** Reference-panel approval flags must
  be parsed as JSON booleans, not truthiness-coerced values, so malformed
  configuration cannot weaken the fail-closed production-readiness gate.
- **SECA preview failure clarity:** A failed local parse, file read, size check,
  or synthetic-sample load must clear the prior preview details so an error
  cannot leave a visitor looking at measurements from a different file.

## 6. Out of Scope (Deferred)

- Facial photogrammetry / CNN-based age estimation.
- DEXA, MRI, or any imaging-based bone density or sarcopenia measurement.
- Real-time wearable integration.
- Multi-clinic federated training.

---

## 7. Validation Requirements (Pre-Production)

- Held-out external cohort validation (CLSA or equivalent).
- Sex-stratified, age-stratified, and ethnicity-stratified performance metrics.
- Calibration plots on `homeostatic_deviation_score` and `biological_age`.
- Documentation of FI denominator sensitivity to measurement completeness.
- Training-row eligibility and optional-feature missingness by cohort and
  subgroup, including sensitivity to complete-case selection versus native
  missing-value handling.
- Censoring-aware horizon calibration with an explicit estimator, follow-up
  sufficiency guard, and documented assumptions.
- External validation must report a deterministic, support-aware concordance
  uncertainty summary with requested and valid bootstrap replicate counts;
  this is an engineering review aid and must not be labeled a clinical
  confidence interval without an approved statistical analysis plan.
- The validation harness must include a committed, deterministically generated
  synthetic engineering fixture and CI smoke runner that exercises row
  evaluation, subgroup coverage, calibration bins, and support-aware
  concordance before an approved external cohort is available; this fixture
  must remain explicitly forbidden for clinical use and cannot satisfy E-005.
- Training must expose a deterministic patient-level fit/holdout split with
  duplicate-identifier rejection, explicit event/censor support, and
  serializable split provenance; this is a leakage-control aid and must not be
  mistaken for a prespecified clinical analysis plan or external validation.
- Serving health and readiness metadata must distinguish a fixture-only
  reference panel from an approved panel, and fixture-only state must remain a
  readiness blocker even if a caller mutates the development object.
- Assessment responses must carry the same fixture-only panel state as a typed
  field; the synthetic development panel must remain visibly distinguishable
  from other non-production states in downstream handoffs.
- SECA browser and Python importers must share strict timestamp, row-shape,
  UTF-8-BOM/numeric-normalization, and derivation-provenance behavior across
  file and in-memory inputs so a local preview
  cannot silently disagree with the engine.
- SECA segment values must have parity across Python and browser trend
  summaries, and the local handoff must label those changes as descriptive
  rather than clinical asymmetry or treatment-effect evidence.
- The static Pages shell must version its JavaScript assets when the parser or
  UI contract changes so browser/CDN caching cannot silently mix generations.
- External-validation reports must preserve reviewable denominators: rows
  received/evaluated/excluded, privacy-safe aggregated exclusion reasons, and
  an explicit status for emitted or withheld concordance uncertainty. A null
  interval without a machine-readable reason is not an adequate review receipt.
- External-validation reports must also expose a machine-readable
  `outcome_metric_status` map overall and per subgroup for future Brier,
  calibration, and decision-curve/net-benefit metrics. Until the prespecified
  SAP, approved cohort, endpoint/censoring method, and reviewer gate exist,
  each value must remain explicitly withheld rather than represented as zero
  or as a clinical result.
- Every serialized uncertainty interval must expose its construction separately
  from its method and validation flag: approved model intervals use the
  declared `wald_1_96_se` construction, external concordance intervals use
  `bootstrap_percentile`, and withheld intervals use `none_withheld`. These
  labels describe software construction only and do not make an interval a
  clinical confidence interval.
- The committed synthetic `docs/demo-data.json` artifact must be reproducible
  from `scripts/build_demo_data.py`; the Pages verification job must run the
  generator's non-writing check before uploading `docs/`.
- Reference-panel `production_ready` and `fixture_only` values must be explicit
  booleans; malformed approval state must fail closed before a panel can enter
  serving or release validation.
- Local SECA preview errors must clear stale detail rows while retaining an
  accessible error status tied to the current file action.
- Native survival training must record its fixed engineering recipe and weight
  semantics, reject non-finite inputs that are not valid missing values, and be
  exercised in CI with the optional ML dependency installed.
- The wellness report and Pages view must preserve the side of a development
  reference band that needs attention and show numeric bounds alongside any
  explanatory range label.
- Cited sources for all ordinal cutoffs in the FI calculator.
- Hash-bound model approval metadata and an approved reference-panel binding
  before production serving.
- A repository-visible operations runbook covering development/production
  startup, readiness admission, release receipts, privacy-safe monitoring,
  rollback, incident response, and the SECA/wellness handoff boundary.
- Serving health and readiness must expose a deterministic, non-secret release
  identity with available model and reference-panel SHA-256 digests so an
  operator can reconcile the running configuration to an immutable release
  receipt without exposing API keys, request bodies, model parameters, or
  patient identifiers.
- The repository must provide a bounded capture-and-reconcile command that
  allow-lists the runtime release identity from `/health`, refuses accidental
  receipt overwrites, and verifies a stored receipt against fresh health
  metadata without persisting credentials, request data, or patient identifiers.
- The repository must provide a model-release preflight that validates the
  exact artifact, persisted feature manifest, approval sidecar, reference-panel
  file hash/id binding, production flags, and uncertainty flags as one software
  release unit; its result must remain separate from E-005 clinical approval.
- The persisted model feature order and its encoder must have one implementation
  source, with an exact regression contract so a future feature change cannot
  silently drift the artifact manifest from inference vectors.
- Release receipts must reject contradictory health metadata, including a
  ready state with blockers, a production-ready fixture panel, or a mismatch
  between top-level and operational-control fixture flags.
- NHANES linked-mortality durations must have one explicit canonical unit:
  `read_public_use_mortality` returns years, and `build_nhanes_rows` must reject
  an incompatible months map instead of double-converting the follow-up time.
- Every Pages wellness handoff, including the copyable focus-list JSON, must
  expose the no-action-effect and no-clinical/lifespan-claim booleans plus the
  model/panel readiness boundary at the report top level, and its status
  summary must stay in exact criterion-ID parity with `EVAL.md`.
- Wellness reports must expose every measured non-in-range focus area in the
  API in deterministic order. Pages may bound the default visible list only
  when it reports shown versus total and offers an accessible disclosure; the
  downloadable improvement report must retain the complete list.
- The repository must include a reviewable external-validation and clinical-
  review protocol template covering cohort identity, endpoint/censoring,
  horizon, feature and missingness rules, patient-level leakage, subgroup
  denominators, discrimination, calibration, uncertainty, clinical utility,
  reproducibility, sign-off, and stop/rollback conditions. It must remain
  explicitly a template and must not be counted as clinical approval.
- Unvalidated biological-age uncertainty must not be serialized as a numeric
  `ci_95`; approved uncertainty may remain numeric, while development and
  otherwise unvalidated paths must expose `null` and the explicit validation
  flag.
- Runtime release receipts must detect schema drift inside the known nested
  `/health` objects, not only additions to the top-level field set.
- External-validation reports must carry the exact model and reference-panel
  identities used for evaluation, including available SHA-256 digests and
  readiness/fixture state, without converting those fields into clinical
  approval.
- The longitudinal comparison contract must reject different patient
  identifiers and non-chronological dates, expose typed no-action-effect and
  no-clinical/lifespan-claim flags, and exclude the raw input payload from its
  response and public handoff.
- Assessment and progress handoffs must expose the available reference-panel
  SHA-256 identity and a count-only FI denominator band (low, moderate, or
  high) beside the exact denominator. These are engineering review fields,
  not clinical adequacy thresholds or patient targets; progress must reject
  mismatched non-null panel digests.
- Every serving predictor must implement the explicit
  `predict_for_assessment(age, encoded_vector)` adapter contract; the assessment
  path must not silently fall back to legacy raw-component predictor calls.
  Readiness, `/health`, `/readyz`, and release receipts must remain consistent
  across model, panel, fixture, and API-key states.
- Serving readiness and release preflight must reject the shipped synthetic
  reference-panel band values even if an operator rewrites only the approval
  flags or source labels. A production flag cannot promote development data.
- Assessment quality must expose conservative reference-panel band geometry for
  the patient's age, and external validation must aggregate and exclude rows
  outside every required feature's panel coverage rather than guessing a
  calibration value.
- A production model release must carry explicit `supplied` Gompertz mapper
  provenance; an in-sample or missing mapper provenance remains development
  only even when an approval sidecar requests production readiness.
- Operational diagnostics must expose non-secret model/panel identity on both
  health and readiness probes, retain safe readiness blockers in receipt
  reconciliation, reject conflicting external-cohort ethnicity aliases, and
  support deterministic patient-level sex/age-band split strata without
  exposing identifiers. Public contribution and runbook guidance must keep
  these controls, synthetic-fixture boundary, and E-005 review gate explicit.
- The current Python and Node test counts must be captured in the checked-in,
  privacy-safe `docs/test-receipt.json`. `scripts/build_test_receipt.py
  --check` must reconcile the receipt with live collection/execution, while
  `verify_docs.py`, CI, and the Pages publication gate must keep the visible
  test counts and receipt link synchronized. The receipt must contain no
  patient data, fixture rows, credentials, or machine-specific paths.
- The serving app must expose bounded process-local operational metrics that
  contain only aggregate request totals, status classes, latency, and
  oversize-rejection counts. Metrics must not retain route, caller, request-ID,
  patient, or payload labels; when an API key is configured, the endpoint must
  require the same authentication boundary as versioned assessment routes.
  Documentation must state that counters reset on restart and do not establish
  clinical monitoring evidence.
- The repository must provide a local-only NHANES intake-shape review command
  that requires an explicit supported-cycle column map, parses the CDC
  fixed-width mortality contract without inventing a header row, rejects
  incomplete or duplicate join keys and incompatible duration units, and
  emits deterministic aggregate evidence without paths, identifiers, raw rows,
  durations, or measurement values. Its reviewer obligations must remain
  separate from E-005 clinical validation and production approval.
- The serving process must expose a privacy-safe runtime-provenance block with
  an installed package-tree digest, installation mode, dependency-set digest,
  Python runtime identity, and effective-configuration digest. The built-wheel
  smoke must compare the block over real loopback HTTP and fail closed when
  strict production admission is attempted from source-only or incomplete
  provenance.
- The Pages publication gate must keep its real Node test runner explicitly
  guarded by the documentation verifier. Runtime-provenance helpers must
  distinguish a well-formed diagnostic identity from an identity admissible for
  strict production, so a source-tree process cannot be mistaken for an
  installed release.
- The Pages development readout and local wellness handoff must preserve the
  semantics of the canonical response: label normalized deviation and withheld
  uncertainty honestly, identify downloaded output as development-only, carry
  the complete `top_interventions` list, and keep print output visibly bounded
  as research-use-only. Async SECA status updates must use an independent
  monotonic presentation counter rather than an internal request token.

<!-- goal-loop:managed:start -->
## Goal Loop Control

- goal_id: GL-frailty-engine-v1
- goal_revision: 104
- status: running
- roadmap_path: ROADMAP.md
- roadmap_item_id: R-084
- eval_path: EVAL.md
- active_lease_until: null
- last_checkpoint: CP-109
- remaining_criteria: E-005 (approved external cohort, clinical cutoff review, and production model approval)
- transport: native-mcp unavailable for team mode on installed Claude 2.1.233; user-authorized bounded cli-fallback is active

## Claude Dispatch Ledger

| dispatch_id | parent_id | role | instance_id | job_id | roadmap_id | scope | status | started_at | last_seen_at | checkpoint |
|---|---|---|---|---|---|---|---|---|---|---|
| GL-frailty-engine-v1-R060-CLI-001 | codex | claude-worker | cli-29200 | exec-37899 | R-060 | draft docs/PRIVACY_THREAT_MODEL.md only | inconclusive | 2026-08-27T19:45:00-06:00 | 2026-08-27T19:47:40-06:00 | CP-077 |
| GL-frailty-engine-v1-R060-CLI-002 | codex | claude-worker | cli-83644 | exec-36282 | R-060 | return complete docs/PRIVACY_THREAT_MODEL.md draft in stdout only | accepted | 2026-08-27T19:49:30-06:00 | 2026-08-27T19:53:50-06:00 | CP-078 |
| GL-frailty-engine-v1-R061-CLI-001 | codex | claude-worker | cli-92152 | exec-88272 | R-061 | return complete root SECURITY.md draft in stdout only | accepted | 2026-08-27T20:00:23-06:00 | 2026-08-27T20:06:11-06:00 | CP-079 |
| GL-frailty-engine-v1-R062-CLI-001 | codex | claude-worker | cli-84972 | exec-45700 | R-062 | return a read-only principal-engineer gap audit and recommend one implementable maturity tranche | accepted | 2026-08-27T20:21:15-06:00 | 2026-08-27T20:28:29-06:00 | CP-080 |
| GL-frailty-engine-v1-R068-CLI-001 | codex | claude-worker | cli-47443 | exec-47443 | R-068 | return a high-budget architecture and safety review for the SECA assessment handoff and recommend one implementable tranche | accepted | 2026-08-27T21:00:00-06:00 | 2026-08-27T21:10:00-06:00 | CP-081 |
| GL-frailty-engine-v1-R069-CLI-001 | codex | claude-worker | cli-63928 | exec-63928 | R-069 | read-only high-budget principal-engineer audit of local SECA handoff parity, CLI errors, privacy, and operator UX | accepted | 2026-08-27T21:20:00-06:00 | 2026-08-27T21:35:00-06:00 | CP-082 |
| GL-frailty-engine-v1-R069-CLI-002 | codex | claude-worker | cli-20305 | exec-20305 | R-069 | independent high-budget safety review of the selected local SECA overlay contract and implementation scope | accepted | 2026-08-27T21:36:00-06:00 | 2026-08-27T21:48:00-06:00 | CP-082 |
| GL-frailty-engine-v1-R069-CLI-003 | codex | claude-worker | cli-56924 | exec-56924 | R-069 | final read-only high-budget implementation, privacy, accessibility, and evidence-contract review after the R-069 changes | accepted | 2026-08-27T21:55:00-06:00 | 2026-08-27T22:06:47-06:00 | CP-082 |
| GL-frailty-engine-v1-R070-CLI-001 | codex | claude-worker | cli-78713 | exec-78713 | R-070 | read-only high-budget maturity audit of the NHANES data-intake and reproducibility surface | accepted | 2026-08-27T22:12:00-06:00 | 2026-08-27T22:25:00-06:00 | CP-083 |
| GL-frailty-engine-v1-R070-CLI-002 | codex | claude-worker | cli-26571 | exec-26571 | R-070 | read-only high-budget implementation/code-design proposal for a privacy-safe local NHANES intake receipt and CI/docs guard | accepted | 2026-08-27T22:26:00-06:00 | 2026-08-27T22:30:00-06:00 | CP-083 |
| GL-frailty-engine-v1-R070-CLI-003 | codex | claude-worker | cli-88205 | exec-88205 | R-070 | read-only high-budget final safety, privacy, determinism, docs, CI, and E-005 boundary review after implementation | accepted | 2026-08-27T22:34:00-06:00 | 2026-08-27T22:41:56-06:00 | CP-083 |
| GL-frailty-engine-v1-R073-CLI-001 | codex | claude-worker | cli-1673 | exec-1673 | R-073 | read-only high-budget maturity audit of the training/validation survey-design and sample-weight contract | accepted | 2026-08-27T22:45:00-06:00 | 2026-08-27T22:55:00-06:00 | CP-084 |
| GL-frailty-engine-v1-R073-CLI-002 | codex | claude-worker | cli-36336 | exec-36336 | R-073 | read-only high-budget compatibility review of strict schema, legacy artifacts, DMatrix weight semantics, validation metadata, and production preflight | accepted | 2026-08-27T22:56:00-06:00 | 2026-08-27T23:05:00-06:00 | CP-084 |
| GL-frailty-engine-v1-R073-CLI-003 | codex | claude-worker | cli-37838 | exec-37838 | R-073 | read-only high-budget final review of the implemented survey-design contract, tests, docs, privacy, and E-005 boundary | accepted | 2026-08-27T23:11:40-06:00 | 2026-08-27T23:22:14-06:00 | CP-084 |
| GL-frailty-engine-v1-R074-CLI-001 | codex | claude-worker | cli-87825 | exec-87825 | R-074 | read-only high-budget scientific-credibility and next-gap maturity audit across model, validation, serving, Pages, and research boundaries | accepted | 2026-08-27T23:25:45-06:00 | 2026-08-27T23:34:50-06:00 | CP-085 |
| GL-frailty-engine-v1-R074-CLI-002 | codex | claude-worker | cli-24415 | exec-24415 | R-074 | read-only high-budget product, serving, accessibility, Pages, and runtime maturity audit for the next production-like tranche | accepted | 2026-08-27T23:26:15-06:00 | 2026-08-27T23:34:50-06:00 | CP-085 |
| GL-frailty-engine-v1-R074-CLI-003 | codex | claude-worker | cli-55292 | exec-55292 | R-074 | read-only high-budget adjudication of the competing scientific/reporting and Pages/artifact-attestation next-tranche proposals | accepted | 2026-08-27T23:35:58-06:00 | 2026-08-27T23:44:28-06:00 | CP-086 |
| GL-frailty-engine-v1-R074-CLI-004 | codex | claude-worker | cli-1342 | exec-1342 | R-074 | implement deterministic artifact sidecars, explicit research-use-only/local-only copy, and a synthetic E-005-marked external-validation report envelope with tests and workflow/docs checks | inconclusive | 2026-08-27T23:45:00-06:00 | 2026-08-27T23:52:00-06:00 | CP-087 |
| GL-frailty-engine-v1-R074-CLI-005 | codex | claude-worker | cli-55976 | exec-55976 | R-074 | implement deterministic artifact sidecars, explicit research-use-only/local-only copy, and a synthetic E-005-marked external-validation report envelope with tests and workflow/docs checks | inconclusive | 2026-08-27T23:52:00-06:00 | 2026-08-28T00:00:00-06:00 | CP-088 |
| GL-frailty-engine-v1-R074-CLI-006 | codex | claude-worker | cli-25598 | exec-25598 | R-074 | final read-only high-budget review of sidecar integrity, synthetic report provenance, CLI/Pages boundary copy, workflows, tests, packaging, and E-005 neutrality | inconclusive | 2026-08-28T00:10:00-06:00 | 2026-08-28T00:20:00-06:00 | CP-089 |
| GL-frailty-engine-v1-R075-CLI-001 | codex | claude-worker | cli-72070 | exec-72070 | R-075 | read-only high-budget principal-engineer audit of remaining research credibility, skill compatibility, serving, Pages, security, privacy, operability, and reproducibility gaps | inconclusive | 2026-08-28T00:25:47-06:00 | 2026-08-28T00:40:30-06:00 | CP-091 |
| GL-frailty-engine-v1-R075-CLI-002 | codex | claude-worker | cli-80055 | exec-80055 | R-075 | read-only high-budget focused audit of skill compatibility, serving/readiness, reproducibility, Windows release checks, Pages behavior, privacy, and E-005 boundary | inconclusive | 2026-08-28T00:42:13-06:00 | 2026-08-28T00:53:30-06:00 | CP-092 |
| GL-frailty-engine-v1-R075-CLI-003 | codex | claude-worker | cli-38123 | exec-38123 | R-075 | final read-only high-budget review of the response-header boundary, SECA/Pages workflow, reproducibility, package smoke, privacy, and E-005 boundary | inconclusive | 2026-08-28T00:59:00-06:00 | 2026-08-28T01:05:14-06:00 | CP-095 |
| GL-frailty-engine-v1-R077-CLI-001 | codex | claude-worker | cli-99730 | exec-99730 | R-077 | read-only high-budget production-maturity audit of runtime-process provenance, dependency identity, configuration identity, package smoke, and E-005 boundary | accepted | 2026-08-28T01:35:00-06:00 | 2026-08-28T01:37:47-06:00 | CP-098 |
| GL-frailty-engine-v1-R078-CLI-001 | codex | claude-worker | cli-49576 | exec-49576 | R-078 | read-only high-budget post-R-077 maturity audit of Pages deploy verification, runtime-provenance semantics, skill compatibility, privacy, and E-005 boundary | accepted | 2026-08-28T01:49:29-06:00 | 2026-08-28T01:57:30-06:00 | CP-100 |
| GL-frailty-engine-v1-R079-CLI-001 | codex | claude-worker | cli-11422 | exec-11422 | R-079 | read-only high-budget Pages product, accessibility, report-semantics, privacy, and E-005-boundary audit | accepted | 2026-08-28T02:08:00-06:00 | 2026-08-28T02:23:40-06:00 | CP-101 |
| GL-frailty-engine-v1-R080-CLI-001 | codex | claude-worker | cli-41032 | exec-41032 | R-080 | read-only high-budget scientific/model credibility, serving, skill compatibility, reproducibility, and E-005-boundary audit | accepted | 2026-08-28T02:30:20-06:00 | 2026-08-28T02:32:40-06:00 | CP-103 |
| GL-frailty-engine-v1-R081-CLI-001 | codex | claude-worker | cli-85818 | exec-85818 | R-081 | read-only high-budget post-R-080 audit of model credibility, practical product value, serving, skill compatibility, reproducibility, and E-005 boundary | accepted | 2026-08-28T03:00:00-06:00 | 2026-08-28T03:04:30-06:00 | CP-105 |
| GL-frailty-engine-v1-R083-CLI-001 | codex | claude-worker | cli-21338 | exec-21338 | R-083 | read-only high-budget post-R-082 maturity audit of model credibility, practical product value, serving, skill compatibility, reproducibility, Pages, research evidence, and E-005 boundary | inconclusive | 2026-08-28T03:06:35-06:00 | 2026-08-28T03:08:05-06:00 | CP-106 |
| GL-frailty-engine-v1-R083-CLI-002 | codex | claude-worker | cli-63267 | exec-63267 | R-083 | read-only high-budget post-R-082 maturity audit of model credibility, practical product value, serving, skill compatibility, reproducibility, Pages, research evidence, and E-005 boundary with corrected non-interactive CLI invocation | inconclusive | 2026-08-28T03:08:05-06:00 | 2026-08-28T03:08:05-06:00 | CP-106 |
| GL-frailty-engine-v1-R083-CLI-003 | codex | claude-worker | cli-30076 | exec-30076 | R-083 | read-only high-budget post-R-082 maturity audit of model credibility, practical product value, serving, skill compatibility, reproducibility, Pages, research evidence, and E-005 boundary over stdin | inconclusive | 2026-08-28T03:08:05-06:00 | 2026-08-28T03:08:05-06:00 | CP-106 |
| GL-frailty-engine-v1-R083-CLI-004 | codex | claude-worker | mcp-8001-run-4 | mcp-8001-run-4 | R-083 | read-only post-R-082 maturity audit through the local Claude MCP server, with explicit repository scope and E-005 boundary | inconclusive | 2026-08-28T03:08:05-06:00 | 2026-08-28T03:16:00-06:00 | CP-106 |
| GL-frailty-engine-v1-R083-MCP-001 | codex | claude-worker | mcp-8001-dispatch-6:model-research | mcp-8001-dispatch-6:model-research | R-083 | read-only model/research credibility and validation audit through the local Claude MCP server | accepted | 2026-08-28T03:16:00-06:00 | 2026-08-28T03:20:07-06:00 | CP-106 |
| GL-frailty-engine-v1-R083-MCP-002 | codex | claude-worker | mcp-8001-dispatch-6:product-serving-pages | mcp-8001-dispatch-6:product-serving-pages | R-083 | read-only product/serving/Pages/skill compatibility and documentation audit through the local Claude MCP server | inconclusive | 2026-08-28T03:16:00-06:00 | 2026-08-28T03:21:00-06:00 | CP-106 |
| GL-frailty-engine-v1-R084-MCP-001 | codex | claude-worker | mcp-8001-r084-model-practical | mcp-8001-r084-model-practical | R-084 | read-only focused audit of model semantics, research credibility, longevity-readout boundaries, wellness value, and next material improvement | inconclusive | 2026-08-28T03:37:49-06:00 | 2026-08-28T03:42:50-06:00 | CP-108 |
| GL-frailty-engine-v1-R084-MCP-002 | codex | claude-worker | mcp-8001-r084-serving-pages | mcp-8001-r084-serving-pages | R-084 | read-only focused audit of serving architecture, Pages product usability, accessibility, skill compatibility, and deployment maturity | inconclusive | 2026-08-28T03:37:49-06:00 | 2026-08-28T03:42:50-06:00 | CP-108 |
<!-- goal-loop:managed:end -->
