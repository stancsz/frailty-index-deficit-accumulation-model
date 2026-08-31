# Healthspan Engine model card

Status: development artifact; not clinically validated or production-ready.

This model card records what the repository actually implements, what has been
measured, and what remains an approval obligation. It follows the spirit of
[TRIPOD+AI](https://www.bmj.com/content/385/bmj-2023-078378) for transparent
prediction-model reporting, [PROBAST+AI](https://www.bmj.com/content/388/bmj-2024-082505)
for risk-of-bias and applicability review, and the [NIST AI Risk Management
Framework](https://www.nist.gov/itl/ai-risk-management-framework) for lifecycle
trustworthiness. Those frameworks guide the evidence plan; they do not certify
this implementation.

## Intended use

The engine is a wellness and healthspan software prototype. It summarizes a
current deficit load and an age-equivalent model output for a supplied set of
measurements. It is not a diagnostic device, a clinical decision by itself, or
a substitute for professional judgment. The public API deliberately uses
neutral language and does not expose prognostic endpoint terminology.

## Model and data contract

- The input contract contains exactly 35 named variables across demographics,
  BIA, blood, history, and functional categories.
- The assessment minimum viable vector requires age, sex, BMI, phase angle,
  ECW/TBW, at least six blood variables including glucose or HbA1c, and at
  least four history variables. Survival training deliberately uses only
  age/sex/BMI as row anchors so optional missingness can be retained and
  reported; it does not weaken the inference MVV. Missing variables are not
  fabricated.
- The deterministic FI uses 0/0.5/1 deficit coding and reports its numerator,
  denominator, and valid-variable list. The denominator is measurement-
  completeness-sensitive. It also reports a count-only engineering label:
  low (0–18), moderate (19–27), or high (28–33) measured FI-eligible
  items. This label is not a clinical adequacy or completeness threshold and
  should always be read alongside the exact denominator and caveat.
- The fitted XGBoost matrix has 36 columns: the 35 inputs plus the calculated
  FI. The order is stored in the model artifact manifest.
- Serving uses the `ModelAdapterProtocol`: assessment and
  external-validation code call `predict_for_assessment(age, encoded_vector)`
  with that same 36-column order. Legacy raw-component predictor objects are
  rejected rather than silently routed through a different feature contract.
- `build_survival_frame` and fitted models expose a training-quality report with
  cohort and standard sex/age-band/ethnicity (including `unknown`) slices,
  row/event/censoring totals, and per-feature missing counts and rates. The
  report is descriptive and must be extended for study-specific strata; it is
  not a fairness, calibration, or clinical-approval result.
- `validate_external_cohort` exposes the same support context for each external
  sex, age-band, and ethnicity slice: row count, observed events, censored rows,
  event fraction, mean follow-up, and concordance when estimable. It also emits
  a deterministic percentile bootstrap interval with requested and valid
  replicate counts for concordance; resamples without comparable event pairs
  are discarded and sparse support withholds the interval. The report also
  exposes the effective comparable-pair denominator, since row count is not the
same as evaluable survival-pair support. These fields make sparse strata
visible. It also records `rows_excluded` with privacy-safe aggregated
`row_exclusion_counts`, and `concordance_ci_status` explains whether an
interval was emitted or withheld and why. These fields do not define a
clinically sufficient sample size, establish fairness, or create a clinical
confidence interval.
- The training-quality report records whether weights were absent or passed as
  XGBoost DMatrix case weights (`sample_weight_mode`). The model artifact also
  persists the XGBoost version, fixed parameters, boost-round count, and
  mapper provenance and mapper weight mode. These controls do not implement
  complex-survey variance estimation and do not establish clinical validity.
- Assessment quality reports the conservative all-feature reference-panel band
  count and narrowest matched age span. External validation excludes ages with
  no required-feature band coverage and aggregates the reason without row
  identifiers. These are data-coverage diagnostics, not clinical eligibility
  thresholds.
- BIA variables are represented as age/sex-panel z-scores. The built-in panel
  is a synthetic development fixture. A deployment panel must document device,
  population, age bands, units, provenance, and approval.
- The optional survival adapter uses XGBoost `survival:cox`. Public NHANES
  linked-mortality files are available, but the public-use release includes
  disclosure-protection perturbations for some follow-up or cause-of-death
  values; vital status was not perturbed. See the [CDC linkage
  documentation](https://www.cdc.gov/nchs/linked-data/mortality-files/index.html)
  and [public-use codebook](https://www.cdc.gov/nchs/data/datalinkage/public-use-linked-mortality-files-data-dictionary.pdf).
  The adapter requests the raw `output_margin=True` linear predictor for its
  log-hazard mapping; a native artifact remains development-only until loaded
  with a matching hash-bound approval sidecar.
- The SECA TableView importer accepts dated `Value`/`Unit` columns and maps
  only observed anthropometry/BIA fields. FFMI is derived only from same-scan
  weight, fat mass, and BMI; `latest_measurements()` exposes only canonical
  assessment fields while `latest_all_measurements()` preserves all recorded
  and derived local-review values. Demographic, laboratory, history, and
  functional fields are never inferred. The importer also exposes an explicit
  assessment-readiness checklist so a SECA-only preview cannot be mistaken for
  a complete MVV payload.
- Each API assessment includes a range-based `wellness_report` with source,
  status, priority, missingness, and conservative next steps. It does not
  estimate the effect of an action on biological age. The Pages examples are
  generated from synthetic payloads and are not patient records.
  `wellness_report.focus_areas` is the complete API list of every measured
  non-in-range focus item, in the existing deterministic priority/biomarker
  order; `summary.focus_areas` is the total count and always equals
  `len(focus_areas)`. The Pages demo shows at most five bullets by default,
  displays the count versus shown, and exposes the remaining items through a
  `<details>` disclosure; the downloadable improvement report retains the
  complete API list.
- The Pages SECA preview includes a downloadable and loadable
  `example-seca-tableview.csv` synthetic sample so visitors can exercise the
  parser without a patient export. It is a software fixture, not clinical data.
- When two scans share segment values, the Python/Pages preview and normalized
  handoff expose latest-minus-previous segment changes. These are descriptive
  equipment trends only; the engine does not label asymmetry or estimate an
  action effect from them.
- [`OPERATIONS.md`](OPERATIONS.md) records the development/production runtime
  modes, fail-closed readiness checks, release receipts, body-free logging,
  monitoring boundary, rollback procedure, and SECA privacy handoff. It is an
  operational contract, not evidence of clinical validity.
- `.github/workflows/pages.yml` verifies the public evidence receipt, Pages
  parser tests, and deterministic regeneration of the synthetic demo artifact
  before publishing the static `docs/` artifact; it does not deploy the
  assessment API or any model/patient artifact.

## What is verified in this repository

| Area | Evidence | State |
|---|---|---|
| Feature/MVV contract | Automated tests and live 422 response | Verified engineering behavior |
| FI denominator behavior | Missingness test, response detail, and count-only label | Verified engineering behavior; label bands are not clinically validated |
| BIA transfer plumbing | Reference-panel loader, z-score tests, CDC BIA/XPT parser smoke | Verified plumbing; not clinical calibration |
| Survival adapter | Native XGBoost fit, prediction, artifact round-trip, single-source 36-column vector contract, persisted training-quality and training-configuration metadata | Verified software adapter; not validated performance |
| External evaluation | Concordance, sex/age/ethnicity strata, calibration data and plots, plus deterministic subgroup support warnings | Harness verified; approved cohort absent |
| External-validation engineering smoke | 300-row reproducible synthetic fixture, all standard strata, calibration bins, support-aware concordance, and clinical-use-forbidden provenance | Software path verified; not external validation or a performance estimate |
| Training split boundary | Seeded SHA-256 patient-level fit/holdout partition with event/censor stratification, duplicate rejection, and zero-overlap receipt | Leakage-control behavior verified; study split and tuning protocol remain unapproved |
| Serving | FastAPI liveness/readiness endpoints, injected/configured dependencies, hash-bound non-secret model/panel release identity and deployment fingerprint, runtime-process provenance, allow-listed runtime receipt capture/check CLI, and installed-wheel loopback HTTP contract smoke | Verified development serving path and real HTTP boundary; production mode fails closed, including missing/malformed model or panel digests and incomplete installed provenance |
| SECA import and wellness report | 120-test suite plus 23 Node Pages/parser tests (counts: [`test-receipt.json`](test-receipt.json)), local TableView-shaped fixture, downloadable/loadable synthetic sample, unmapped-row parity, static demo artifact, privacy-safe normalized-summary, wellness-improvement-report, focus-list handoffs, and versioned local MVV-gated assessment overlay with preview and typed CLI errors | Verified software behavior; device/clinical interpretation still requires review |
| Model-release integrity preflight | Native artifact/feature-manifest load, approval-sidecar verification, panel file hash/id binding, production/uncertainty flags, and a non-zero blocked exit | Verified software gate; E-005 clinical approval remains absent |
| Mapper provenance gate | Development fitting may use an in-sample Gompertz mapper, but production preflight requires explicit `training_config.mapper_source: supplied` and reports unknown/missing provenance as blocked | Verified software gate; mapper calibration and E-005 clinical evidence remain absent |
| Typed interpretation boundary | Biological-age interpretation plus explicit `action_effect_estimated: false` and `clinical_or_lifespan_claim: false` fields in every assessment | Verified response-contract behavior; not a clinical claim |
| Assessment readiness identity | Typed `data_quality.reference_panel_fixture_only` and `data_quality.reference_panel_readiness` state in assessment responses, serving probes, receipts, and synthetic report handoff | Verified software contract; fixture state remains a readiness blocker |
| Reference-panel configuration boundary | Explicit boolean parsing for `production_ready` and `fixture_only`; malformed values fail closed | Verified software guard; approval and E-005 clinical evidence remain absent |
| SECA preview failure state | Parse, read, size-limit, and synthetic-sample failures clear prior detail rows while retaining an accessible status message | Verified browser/static behavior; local preview remains non-clinical |
| SECA assessment handoff | Typed Pages overlay form pre-fills only observed canonical scan fields, enforces the explicit MVV checklist, and downloads a local CLI/API handoff; assess-overlay merges it through the canonical Python assessor | Verified software behavior; no scan upload, inference, or clinical approval |
| Longitudinal progress comparison | Stateless dated same-person comparison route and synthetic Pages progress snapshots with readout deltas, reference-band transitions, and no raw-input echo | Verified descriptive behavior; not a causal or clinical claim |
| Packaging and CI runtime | `uv.lock`, locked CI environment, wheel build, installed-wheel smoke with package/dependency provenance, installed-wheel loopback HTTP smoke, deterministic Pages demo check | Verified package path, real HTTP serving contract, runtime-process identity, and generated-artifact gate; deployment infrastructure remains operator-bound |
| NHANES duration-unit boundary | Mortality-reader duration is canonical years; linked rows reject a months map while direct source durations may be normalized | Verified software guard; source endpoint and cohort approval remain separate |
| Pages handoff/status parity | Typed top-level no-action/no-claim flags in the improvement report and exact status-row parity with EVAL criterion IDs | Verified browser contract guard; clinical approval remains absent |

## Credibility and promotion gates

The following must be present before anyone may label a release production-ready:

1. A frozen training manifest with cycle versions, inclusion/exclusion rules,
   survey-weighting plan, missing-value rules, BIA quality filters, units, and
   complete provenance. [`TRAINING_MANIFEST_TEMPLATE.json`](TRAINING_MANIFEST_TEMPLATE.json)
   is the non-approval template for recording those decisions; it intentionally
   contains no downloaded data or real checksums.
2. A locked model artifact with its feature manifest, fitted baseline-risk
   parameters, training code/version, random seeds, and reproducible hash,
   accompanied by a human-authored approval sidecar that matches that hash,
   model id, feature names, reference-panel id and file hash, uncertainty
   method/parameter, and evidence references.
3. Internal validation that is separated from tuning, with uncertainty
   intervals and sensitivity analyses for measurement completeness and FI
   denominator choices.
4. Held-out external validation in a target-relevant cohort, including
   discrimination, calibration, clinical utility, and sex-, age-, and
   ethnicity-stratified results. Report sample sizes and missingness per group;
   do not hide sparse strata behind an aggregate score.
5. Independent review of the FI cutoffs, BIA transfer panel, endpoint
   definition, uncertainty method, intended-use language, and failure modes.
6. A documented monitoring and rollback plan for data drift, missingness drift,
   subgroup degradation, model/panel mismatch, and artifact integrity.

## Known limitations

- The default predictor and BIA panel are explicitly development fixtures.
- The default `ReferencePanel` is also explicitly `fixture_only`; `/health`
  exposes that state and `/readyz` keeps it as a readiness blocker even if a
  caller supplies a mutated development object.
- Several FI thresholds are engineering defaults or general clinical reference
  starting points and still require population-, laboratory-, and device-
  appropriate review.
- The response exposes nullable `ci_95` fields. The shipped predictors set
  `uncertainty_validated: false` and return `ci_95: null`; a numeric interval is
  reserved for an approved predictor with cohort-validated uncertainty. It
  must not be presented as a calibrated clinical confidence interval until
  cohort-based uncertainty analysis is approved.
- The response also exposes `uncertainty_construction`: `wald_1_96_se` when an
  approved-model standard-error interval is emitted and `none_withheld` when
  it is absent. External-validation reports expose
  `concordance_ci_construction` as `bootstrap_percentile` only for an emitted
  percentile interval. These are construction labels, not clinical-calibration
  claims.
- The HTTP factory can require an API key, bound request size, emit request
  IDs, and write body-free structured logs. TLS, rate limiting, secret
  storage, and network policy remain deployment-boundary responsibilities.
- The public NHANES BIA files are from a legacy device era and do not by
  themselves establish equivalence to modern SECA measurements. Transfer
  calibration is required.
- Public-data availability and passing software tests do not demonstrate
  clinical effectiveness, fairness, or safety.
- Calibration bins use a Kaplan–Meier horizon event-probability estimator and
  fail closed when follow-up cannot estimate the requested horizon. This is a
  software safeguard, not proof that the censoring assumptions or target-cohort
  calibration are valid.
- The approval sidecar proves an exact-artifact/configuration binding, not that
  an approver's evidence is clinically sufficient; E-005 still requires an
  external cohort, cutoff review, uncertainty review, and human sign-off.
- Runtime receipts are allow-listed projections of `/health`; they support
  release reconciliation but do not contain credentials, request data, or
  patient identifiers and do not establish clinical validity.
- `scripts/validate_model_release.py` verifies the exact model/panel/sidecar
  software binding as a release unit. A passing preflight is not evidence of
  external validation or clinical approval.
- An equipment scan alone does not meet the MVV and cannot produce the
  biological-age interface without the required demographic and contextual
  inputs.
- The progress comparison is descriptive only. It does not identify which
  action caused a change, estimate treatment effect, or predict that a change
  will alter biological age, lifespan, or a clinical outcome.
- [`EXTERNAL_VALIDATION_PROTOCOL.md`](EXTERNAL_VALIDATION_PROTOCOL.md) is a
  placeholder-only template for freezing the future external-validation and
  clinical-review evidence package. It covers cohort identity, endpoint and
  censoring, leakage, missingness, denominators, subgroup support, calibration,
  uncertainty, reproducibility, sign-off, and rollback; it does not satisfy
  E-005 or contain cohort results.
- The prespecified minimum support fields for each reported subgroup
  (rows, observed events, comparable pairs, valid bootstrap replicates;
  per [`EXTERNAL_VALIDATION_PROTOCOL.md`](EXTERNAL_VALIDATION_PROTOCOL.md)
  §7.2.1) and the outcome-level performance metrics checklist (Brier
  score or an approved survival analogue, calibration-in-the-large,
  calibration slope / ICI, and decision-curve / net-benefit only with a
  prespecified decision and thresholds; per
  [`EXTERNAL_VALIDATION_PROTOCOL.md`](EXTERNAL_VALIDATION_PROTOCOL.md)
  §7.4.1) are **future E-005 obligations**. They are **not** computed,
  evidenced, or implied by the current software evidence in this
  repository: the synthetic `examples/external_validation_synthetic.json`
  fixture (explicitly `clinical_use: forbidden`), the deterministic
  `scripts/run_external_validation_smoke.py` runner, the
  `validate_external_cohort` adapter, the training-quality report, the
  `concordance_*` and `calibration.*` fields, and the
  support-aware bootstrap interval machinery all support the future
  clinical analyses but are not themselves clinical analyses. Numeric
  thresholds and minimums in those protocol subsections are
  placeholders (`RECORD_AFTER_STATISTICAL_REVIEW`) until a prespecified
  SAP, a clinical reviewer, and an approved external cohort are on
  file. This entry does not change the E-005 clinical blocker status
  recorded in `EVAL.md`.

  The serialized validation report now makes this boundary machine-readable
  through `outcome_metric_status` at the overall level and within each
  subgroup. The named future metrics carry `value: null`,
  `status: "not_implemented_pending_sap"`, and
  `construction: "none_withheld"`; this is a deliberate withholding marker,
  not a zero, estimate, or clinical result. Numeric outcome metrics remain
  withheld until the protocol, approved cohort, and review gate are complete.

## Reproducibility entry points

- [README and runbook](../README.md)
- [Goal and acceptance contract](../GOAL.md)
- [Evaluation ledger](../EVAL.md)
- [Source boundary](SOURCES.md)
- [Model approval sidecar](MODEL_APPROVAL.md)
- [Training manifest template](TRAINING_MANIFEST_TEMPLATE.json)
- [External-validation and clinical-review protocol template](EXTERNAL_VALIDATION_PROTOCOL.md)
- [Clinical-ML evidence crosswalk](CLINICAL_ML_EVIDENCE_CROSSWALK.md)
- [`uv.lock`](https://github.com/stancsz/frailty-index-deficit-accumulation-model/blob/main/uv.lock)
  and [installed-wheel smoke](https://github.com/stancsz/frailty-index-deficit-accumulation-model/blob/main/scripts/verify_package_install.py)
- [Public NHANES preparation](../README.md#public-nhanes-preparation)
- [SECA import and wellness report](../README.md#seca-tableview-import-and-wellness-report)
