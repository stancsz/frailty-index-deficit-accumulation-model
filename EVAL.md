# Evaluation contract

This file separates deterministic software evidence from the clinical and
production evidence that is not available in this blank repository.
The current checkout collects 120 Python tests and 23 Node Pages/parser tests.
The checked-in [`docs/test-receipt.json`](docs/test-receipt.json) is the
machine-checked source for those current counts; older checkpoint narratives
retain the test counts observed when those checkpoints were recorded.

<!-- goal-loop:managed:start -->
## Goal Loop Evaluation

| criterion_id | requirement | verifier | evidence_required | observed_evidence | status |
|---|---|---|---|---|---|
| E-001 | Canonical feature matrix contains exactly 35 variables and preserves the named categories | Codex | automated test and source inspection | `py -3 -m pytest`: 120 passed; `FEATURE_NAMES` contains 35 unique entries and the model matrix contains 36 columns (35 inputs plus FI) | passing |
| E-002 | MVV rejects missing mandatory fields, fewer than 6 blood values, missing glucose/HbA1c, or fewer than 4 history values | Codex | focused unit/API tests | Unit test covers all three rejection branches; live API returned HTTP 422 with structured `InsufficientDataError` | passing |
| E-003 | FI uses 0/0.5/1 scoring, excludes missing values from the denominator, and exposes the denominator caveat | Codex | focused tests and output inspection | Unit test proved denominator changes without imputation; every FI feature has a visible source/coding reference; CLI response includes the denominator caveat | passing |
| E-004 | BIA z-score calibration, neutral public schema, development prediction, CLI, and API are executable | Codex | build/import, tests, CLI, runtime smoke | Ruff check/format, byte compilation, editable wheel, CLI output, live `/health` 200, live assessment 200, native XGBoost fit/predict and artifact round-trip; regression test locks raw `output_margin=True` log-hazard behavior | passing |
| E-005 | External CLSA/equivalent validation, stratified metrics, calibration, cutoff approval, and production model evidence are complete | Clinical reviewer | approved cohort analysis and sign-off | Evaluation harness exists, but no approved external cohort, clinical cutoff review, or production model approval exists in this blank checkout | blocked |
| E-006 | Validation tooling computes concordance, sex/age/ethnicity subgroup metrics, probability/homeostatic-deviation/biological-age calibration data, and both plot artifacts | Codex | automated tests and generated plot files | `py -3 -m pytest`: 56 passed, including native XGBoost artifact round-trip and both `homeostatic_deviation_calibration.png` and `biological_age_calibration.png` outputs | passing |
| E-007 | Public NHANES BIA/XPT and linked-mortality files can be parsed into explicit canonical rows without imputation | Codex | focused tests and live official-file smoke | 56 Python tests cover fixed-width padding, missing-value dots, explicit column mapping, BIA/FIB-4 derivations, and cycle manifest; live CDC smoke parsed 5,445 eligible mortality rows and a `(5311, 115)` BIX XPT table | passing |
| E-008 | GitHub Pages documentation is polished, accessible, source-linked, and accurately communicates the evidence boundary | Claude proposal plus Codex inspection/rendered browser check | docs/index.html, local assets, research-wiki entry, link/accessibility/site checks | Browser render verified: 12 sections, valid metadata, 39 evidence items, 29 status rows, document-level heading, responsive layout rules, working filter and copy interactions; local same-site links returned 200 and repository links use stable GitHub URLs | passing |
| E-009 | The repository is operationally skill-compatible: one-command serving, reproducible evaluation, agent handoff, and explicit production gates | Codex, high-budget Claude documentation worker plus independent review | skill contract, docs, smoke checks, and source inspection | `frailty-engine` skill validator passed; goal docs validator reports no structural issues after dispatch reconciliation; CLI/API/XGBoost artifact smoke paths, typed request/response schemas with PII-safe envelope errors, optional API-key/request-size controls, liveness/readiness split with actionable fail-closed production mode, request IDs, body-free structured logs, configured dependency health metadata, automated public-receipt checks, the cross-surface privacy/security threat model, and the contributor/operator `SECURITY.md` vulnerability-reporting and security-sensitive release checklist are documented | passing |
| E-010 | SECA TableView CSV import is non-destructive and typed; Pages provides selectable synthetic examples and a range-based wellness report | Codex | importer tests, generated demo fixtures, browser interaction, and privacy/source inspection | 56 Python tests pass, including a two-date TableView fixture, FFMI derivation, single-scan trend messaging, explicit SECA assessment-readiness requirements, wellness direction and action-type fields, strict wellness-schema coverage, readiness-control coverage, demo artifact parity, API-control coverage, and wellness-focus intervention fallback; the supplied local export selected its latest dated scan, mapped 4 canonical fields, preserved 5 segment values, and produced a 2-date trend; `demo-data.json` is generated from synthetic profiles; browser selected examples and previewed a local CSV with no upload | passing |
| E-011 | Training preserves optional missingness, XGBoost artifact identity is approval-bound, and calibration inputs reject ambiguous band/plot state | Codex | focused tests, source inspection, and approval-sidecar round-trip | 56 Python tests pass; sparse training rows retain `NaN` outside the age/sex/BMI anchors; native XGBoost default hazard-ratio versus raw-margin semantics are locked; approval sidecar binds artifact and reference-panel SHA-256, model id, 36 feature names, panel id, uncertainty method/parameter, and evidence refs; reference bands reject overlap/unsorted input and empty calibration plots fail closed | passing |
| E-012 | Training exposes inspectable cohort and subgroup-quality evidence without imputing optional features | Codex | focused tests, source inspection, and artifact metadata round-trip | 56 Python tests pass; `SurvivalTrainingFrame.quality` reports row/event/censoring totals plus per-feature missing counts/rates on the exact 36-column matrix and standard sex/age-band/ethnicity slices, and `fit_xgb_survival` persists the same JSON-safe summary as `model.training_quality`; study-specific strata remain an explicit extension requirement | passing |
| E-013 | Calibration uses censoring-aware horizon estimates, blocks unestimable bins, and refitting clears prior approval identity | Codex | focused tests and source inspection | 56 Python tests pass; calibration bins report Kaplan–Meier horizon event probability using only horizon-eligible rows, all-early-censored cohorts block validation, plots require estimable adjusted rates, and XGBoost refit clears approval manifest, panel hash, artifact hash, and uncertainty state | passing |
| E-014 | Pages and serving boundaries harden accessibility, local-parser safety, and request rejection behavior | Codex | Node tests, static checks, focused API test, and browser check | 10 Node tests pass; the Pages shell has one `h1`, the shared parser strips BOM/rejects invalid dates/limits files to 5 MB, the API authenticates before body consumption, and oversized responses carry retry/connection controls | passing |
| E-015 | Python and browser SECA importers preserve the same strict date, row-shape, numeric-normalization, and derivation-provenance contract | Codex | Python/Node parser tests and source inspection | 56 Python tests plus 10 Node tests pass; both parsers reject ambiguous dates and extra non-empty columns, normalize UTF-8 BOM/Unicode minus/NBSP values, reject fat mass above weight, and represent estimated height separately from recorded height with explicit FFMI derivations | passing |
| E-016 | Native survival training is numerically guarded, reproducibly described, and exercised in CI | Codex | focused tests, artifact round-trip, and workflow inspection | 56 Python tests pass; extreme-risk Gompertz mapping remains bounded, non-binary events and infinite features are rejected, optional missingness remains `NaN`, weighted frames report `xgboost_dmatrix_case_weight`, artifacts persist XGBoost version/parameters/rounds/mapper provenance and mapper weight mode, and CI installs `.[dev,ml]` with Node 20 | passing |
| E-017 | Wellness directions preserve whether an attention value is below or above its development band, and Pages shows numeric target bounds | Codex | focused wellness test, generated demo artifact, and browser check | 56 Python tests pass; BIA attention values carry `below`/`above` directions, the synthetic SECA-informed example is regenerated from the corrected pipeline, Pages announces single-scan trend limits, and Pages renders numeric range bounds plus the explanatory reference-band label | passing |
| E-018 | Training reproducibility has an inspectable, non-approval manifest shape for source files, eligibility, missingness, survey design, splits, recipe, and hashes | Codex | manifest validator, source inspection, and docs verification | `py -3 scripts/validate_training_manifest.py docs/TRAINING_MANIFEST_TEMPLATE.json` passes; the template enumerates the three supported BIA/mortality cycle pairs, explicit `SEQN`/eligibility/vital-status/duration linkage, cycle-specific review placeholders, native-missingness and DMatrix-weight limits, fixed 36-column/300-round recipe, sensitivity obligations, reference-panel identity, and `production_ready: false` | passing |
| E-019 | Locked dependency resolution, documented serving entrypoints, and a clean installed-wheel smoke path are continuously verifiable | Codex | `uv.lock`, CI inspection, package smoke, and local locked-environment run | `uv lock --check`, `uv sync --locked --extra dev --extra ml`, and a newly built wheel completed under CPython 3.13; a separate locked CPython 3.11.14 environment also ran all 56 Python tests and the sample CLI; an isolated runtime environment populated from `uv export --locked --no-dev --no-editable --no-emit-project` returned health `200`, assessment `200`, invalid request `422`, comparison `200`, and SECA smoke `assessment_ready=false`, `canonical=4`, `segments=5`; CI now runs the same isolated wheel smoke through `scripts/verify_package_install.py` | passing |
| E-020 | The SECA Pages workflow can preserve a normalized local summary without uploading the raw export or a patient identifier | Codex | Node/static tests and browser upload/download exercise with the supplied local export | 10 Node tests pass; browser parsing of the supplied export exposed the latest scan, 4 canonical fields, 5 segment values, 3 derivations, and a two-scan trend; the generated `seca-normalized-summary.json` contract contained format/date/measurements/units/segments/derivations/trend, excluded patient-specific identifiers, and reported no upload | passing |
| E-021 | The selected Pages example can be handed off as a privacy-safe improvement report without overstating the development surrogate | Codex | Node/static tests and browser interaction | 23 Node tests pass; the selected synthetic profile can download `wellness-improvement-report-v1-development.json` or print the visible report, including the readout, ranges, focus areas, missing inputs, recommendations, model/readiness boundary, and explicit no-action-effect/no-clinical-claim flags; payload and patient identifiers are excluded | passing |
| E-022 | A SECA-only preview makes the remaining assessment MVV requirements explicit without inferring unavailable fields | Codex | Python/Node parser tests, CLI output, and browser upload exercise | 56 Python tests plus 10 Node tests pass; Python and browser parsers expose the same not-assessment-ready state, list missing age/sex, absent scan fields, blood, and history requirements, and include a safe next-step note; the supplied export browser preview visibly reports the remaining MVV inputs and no upload | passing |
| E-023 | Serving and release operations are documented with fail-closed admission, privacy-safe monitoring, rollback, and incident boundaries | Codex | operations runbook, source inspection, docs verifier, and runtime smoke | `docs/OPERATIONS.md` documents development versus production configuration, `/health` versus `/readyz`, locked release preflight, immutable model/panel/sidecar promotion, body-free observability, monitoring boundaries, rollback, incident response, and SECA/wellness privacy limits; docs verification and live API/wheel smoke pass | passing |
| E-024 | External validation subgroup metrics expose support denominators rather than only aggregate scores | Codex | focused validation test and source inspection | 56 Python tests pass; each external sex, age-band, and ethnicity slice reports row count, observed events, censored rows, event fraction, mean follow-up, and concordance when estimable, while sparse strata remain descriptive and do not imply fairness or clinical sufficiency | passing |
| E-025 | Static GitHub Pages publication is guarded by evidence and parser verification before deploy | Codex | workflow inspection, docs verifier, and Node parser tests | `.github/workflows/pages.yml` verifies `scripts/verify_docs.py`, JavaScript syntax, and all 5 Pages/parser tests before `actions/upload-pages-artifact@v4` and `actions/deploy-pages@v4`; its deploy job requires the verify job, Pages permissions, the `github-pages` environment, and `main`; it deploys only `docs/` and does not deploy API, model, or patient artifacts | passing |
| E-026 | External concordance uncertainty is deterministic, support-aware, and visible for the cohort and every subgroup | Codex | validation tests and JSON report inspection | 56 Python tests pass; `validate_external_cohort` emits a deterministic percentile bootstrap interval, requested/valid replicate counts, and the effective comparable-pair denominator for the overall cohort and each subgroup; replicates without comparable event pairs are excluded, intervals are withheld when support is sparse, and the report explicitly remains an engineering review aid rather than a clinical confidence interval | passing |
| E-027 | External-validation engineering behavior is reproducible on a committed synthetic fixture and fixture-only panels remain visibly blocked from readiness | Codex | committed fixture, deterministic generator check, CI smoke, focused tests, and API health inspection | 56 Python tests pass; the byte-for-byte regenerated 300-row fixture covers both sexes, all four age bands, three synthetic ethnicity strata, calibration bins, and support-aware concordance; the smoke reports `clinical_use: forbidden` and remains blocked only by development predictor/panel state; `/health` exposes `reference_panel_fixture_only: true` and `/readyz` reports the actionable fixture blocker | passing |
| E-028 | Training fit/holdout boundaries are deterministic, patient-level, event/censor-stratified, and reject duplicate identifiers | Codex | split helper, fixture smoke, focused test, and CI inspection | 56 Python tests pass; `split_survival_rows` assigns by seeded SHA-256 patient identifier, preserves event/censor support on the synthetic fixture, reports zero patient overlap without exposing IDs, is repeatable, and rejects duplicate identifiers; this is leakage-control engineering evidence, not a prespecified clinical analysis plan | passing |
| E-029 | Serving exposes a safe, deterministic release identity for model/panel reconciliation | Codex | focused API test, source inspection, and runtime health/readiness inspection | 56 Python tests pass; `/health` exposes service version, model artifact SHA-256 when available, reference-panel SHA-256 when available, and a deterministic deployment fingerprint; `/readyz` carries the same fingerprint without exposing API keys, request data, or patient identifiers | passing |
| E-030 | A running service can be reconciled to a privacy-safe release receipt without credentials or patient data | Codex | focused receipt test, CLI help check, and live capture/check smoke | 56 Python tests pass; `scripts/capture_release_receipt.py` projects only an explicit allow-list from `/health`, emits a stable schema with the runtime fingerprint and readiness state, refuses overwrite unless `--force` is supplied, preserves a previous receipt on forced replacement, reports safe mismatch fields, and verifies a stored receipt against fresh health metadata; schema-field drift invalidates reconciliation, and the receipt contains no credential, request-body, or patient-identifier fields | passing |
| E-031 | A model, reference panel, and approval sidecar can be validated as one software release unit without implying clinical approval | Codex | focused preflight test, CLI help check, and source inspection | 56 Python tests pass; `scripts/validate_model_release.py` verifies the native artifact's persisted feature manifest and SHA-256 sidecar binding, hashes the panel file, checks the sidecar panel id/hash and production/uncertainty flags, returns a blocked non-zero result for fixture state, and returns a ready software gate only after the exact panel hash is updated; the report retains `clinical_status=requires_e005_external_validation_and_clinical_review` | passing |
| E-032 | Every assessment exposes the interpretation and no-action-effect/no-clinical-claim boundary as typed fields | Codex | focused response-contract test, generated demo artifact, docs verification, and source inspection | 56 Python tests pass; `metrics.biological_age.interpretation` explicitly describes the output as age-equivalent and non-lifespan/non-diagnostic/non-treatment-effect, while `wellness_report.action_effect_estimated` and `wellness_report.clinical_or_lifespan_claim` are both `false`; the strict Pydantic response schema and synthetic Pages artifact carry the same fields | passing |
| E-033 | Longitudinal review compares two dated same-person assessments descriptively, exposes reference-band transitions, and excludes the raw input payload from the report | Codex | focused API/pure-function tests, generated synthetic Pages artifact, Node/static tests, and source inspection | 56 Python tests and 10 Node tests pass; `POST /v1/assessment-comparisons` is typed, rejects different patient identifiers, non-chronological dates, and model/panel changes, reports readout deltas plus measured range transitions/new or resolved focus areas, and returns false action-effect/no-clinical-claim flags without echoing the input payload; all three synthetic Pages examples carry the same report contract | passing |
| E-034 | Pages provides a downloadable and loadable synthetic SECA TableView sample without exposing patient data | Codex | Node parser test, docs verifier, local asset inspection, and browser interaction | The 9-test Node suite parses `docs/example-seca-tableview.csv` with two dated scans and five segment values; Pages exposes `#seca-load-sample` and a download link, loads the asset through the same local parser, and the asset contains no patient-specific text; the sample remains a software fixture, not clinical data | passing |
| E-035 | Pages makes input completeness visible beside the age-equivalent readout without fabricating missing values | Codex | Node/static test, generated demo artifact, docs verifier, and browser interaction | The 9-test Node suite checks measured, not-measured, and focus-area hooks plus the missing-input explanation; the live selected example renders those counts and lists missing canonical inputs while preserving the non-clinical boundary | passing |
| E-036 | Python and Pages SECA handoffs expose descriptive latest-minus-previous segment trends without inferring clinical asymmetry | Codex | focused Python/Node tests, CLI/source inspection, docs verifier, and browser interaction | The 56-test Python suite and 9-test Node suite verify shared segment deltas; the CLI and normalized local JSON include `segmental_trend_latest_minus_previous`, while Pages renders segment changes and labels them descriptive; versioned script assets prevent a stale parser/UI generation from being silently mixed; no asymmetry threshold or action effect is claimed | passing |
| E-037 | Assessment handoffs expose typed fixture-only reference-panel state instead of requiring downstream inference | Codex, bounded Claude audit | full Python/Node tests, generated demo artifact, Pages/static test, live API/browser interaction, and source inspection | `AssessmentResponse.data_quality.reference_panel_fixture_only` is populated from the configured panel, validates as a boolean, is regenerated into all three synthetic Pages examples, and is included in the local wellness-report model boundary; the default synthetic panel remains explicitly distinguishable from other non-production states; versioned `e037` assets were loaded in fresh Pages QA | passing |
| E-038 | The committed synthetic Pages demo artifact is deterministically reproducible and independently checked before deployment | Codex, bounded Claude audit | generator check, Pages workflow/static test, docs verification, and source inspection | `scripts/build_demo_data.py --check` renders the fixed-input/fixed-date document in memory and compares it byte-for-byte without writing; the Pages verify job runs this check before deploy, and the 9-test Node suite plus docs verifier assert the deploy marker | passing |
| E-039 | Reference-panel approval flags reject malformed JSON types instead of truthiness-coercing readiness state | Codex | focused regression test, full suite, source inspection, and direct malformed-config reproduction | `ReferencePanel.from_mapping` now accepts absent flags as `false` but requires explicit `bool` values for `production_ready` and `fixture_only`; the regression test rejects string values, while the pre-change reproduction showed `"false"` becoming `production_ready=True`; the 56-test Python suite and release/docs checks pass | passing |
| E-040 | Local SECA preview errors do not leave details from a previous file visible | Codex, bounded Claude audit | Node/static coverage, source inspection, and browser error-path interaction | `clearSecaDetails()` is called on parse failure, synthetic-sample load failure, oversized-file rejection, and `FileReader` failure; the 9-test Node suite asserts the helper and four failure-path calls, and fresh browser QA verifies valid local details can be followed by an error status without retaining the prior preview rows | passing |
| E-041 | Python and Pages SECA importers handle unmapped auxiliary rows consistently | Codex | focused Python/Node parser regression, normalized-handoff coverage, and source inspection | Direct reproduction showed Python ignored an unmapped `N/A` row while Pages rejected it as nonnumeric. The browser parser now records `unmappedLabels`, skips numeric parsing for unmapped labels, and the normalized local handoff/preview exposes those labels; the 56-test Python suite and 10-test Node suite pass. E-005 remains unchanged. | passing |
| E-042 | Production readiness and ready-state receipts require hash-bound model and reference-panel identities | Codex, bounded Claude audit | direct readiness reproduction, focused API/receipt regression, full suite, and source inspection | A custom predictor/panel with production flags and API key but no digests previously reached `/readyz` HTTP 200. The gate now blocks any production-ready predictor without a valid artifact SHA-256 or production-ready panel without a valid source SHA-256; `health_to_receipt` also rejects a `ready` health payload missing either identity, while blocked development receipts retain null digests. The 56-test Python suite passes; E-005 remains unchanged. | passing |
| E-043 | Inference vectors and persisted model feature manifests share one encoded order contract | Codex, bounded Claude audit | source inspection, exact vector-name regression, focused model-vector/training tests, and full suite | The prior implementation maintained a hand-written 36-name manifest and a separate hand-written encoder sequence. `MODEL_VECTOR_SOURCE_FEATURE_NAMES` now drives both the encoded `MODEL_VECTOR_FEATURE_NAMES` manifest and the runtime vector encoder, preserving the existing order and smoking ordinal encoding; the regression asserts the exact 36-name contract. The 56-test Python suite passes; E-005 remains unchanged. | passing |
| E-044 | Release receipts reject contradictory readiness and panel approval state | Codex, bounded Claude audit | direct malformed-health reproduction, focused receipt regression, full suite, and source inspection | A malformed health payload previously serialized as ready while marking the reference panel both production-ready and fixture-only. `health_to_receipt` now rejects inconsistent top-level/control fixture flags, production-ready fixture panels, ready states with blockers, not-ready states without blockers, and ready states lacking model/uncertainty/auth invariants. The 57-test Python suite passes; E-005 remains unchanged. | passing |
| E-045 | NHANES mortality-linked durations cannot be double-converted between months and years | Codex, bounded Claude audit | direct reproduction, focused regression, source inspection, and full suite | `read_public_use_mortality` emits the CDC MEC follow-up as canonical years. Previously, `build_nhanes_rows` divided that value again whenever `NHANESColumnMap.duration_unit="months"`, turning 24 months into 2 years. Linked mortality rows now require the explicit `"years"` contract, direct source-row durations retain the months-to-years conversion, and the regression rejects the incompatible configuration while preserving 24.0 years. E-005 remains unchanged. | passing |
| E-046 | Pages wellness handoffs expose typed safety flags at the report top level and status rows cannot drift from EVAL criteria | Codex, bounded Claude audit | source inspection, Node regression, and docs verification | The downloadable `wellness-improvement-report-v1` now carries top-level `action_effect_estimated: false` and `clinical_or_lifespan_claim: false` in addition to its model boundary. The Node suite asserts those keys and parses every EVAL criterion ID against `site.js` status rows; the suite passes with 23 tests. E-005 remains unchanged. | passing |
| E-047 | Wellness reports expose the complete focus-area list while Pages keeps a bounded, transparent display | Codex, bounded Claude worker, bounded Claude verifier | focused wellness/API test, generated demo parity, Pages static test, and browser interaction | `build_wellness_report` now returns every measured non-in-range focus item in deterministic priority/biomarker order, so `summary.focus_areas == len(focus_areas)` for the support example and all generated examples. The 60-test Python suite and 12-test Node suite pass; live Pages QA showed 5 of 27 visible focus items plus 22 disclosed remainder items, and the local report contained all 27 without an identifier or raw payload. E-005 remains unchanged. | passing |
| E-048 | External validation and clinical review are specified as a reproducible, evidence-bounded protocol template | Codex, bounded Claude documentation worker | document inspection, required-section/static verifier, and cross-link review | `docs/EXTERNAL_VALIDATION_PROTOCOL.md` is a placeholder-only template covering intended use and decision fields, frozen cohort/source identity, endpoint/censoring/horizon, age/sex/BMI training-anchor versus assessment MVV, patient-level leakage, missingness, denominators, subgroup support, discrimination, censoring-aware calibration, uncertainty, clinical utility, sensitivity analysis, reproducibility artifacts, reviewer sign-off, stop/rollback conditions, and an explicit non-proof boundary. It contains no cohort, human-subject, or result data and explicitly does not satisfy E-005. | passing |
| E-049 | Unvalidated intervals are nullable, runtime receipt checks known nested schema fields, and validation reports carry exact model/panel identity | Codex, bounded Claude runtime audit | focused uncertainty, receipt, and validation tests; full suite; docs/static checks; package and runtime smoke | Development and unapproved XGBoost paths now serialize `ci_95: null` for both biological age and trajectory while an approval-bound validated path remains numeric. Receipt reconciliation detects additions inside `operational_controls` and `readiness`. External reports serialize model id/digest/readiness and panel id/digest/readiness/fixture state, with explicit synthetic-fixture evidence remaining blocked. | passing |
| E-050 | External-validation receipts expose excluded-row counts/reasons and explicit concordance interval status | Codex, bounded Claude calibration audit | focused validation tests, synthetic smoke output, docs verification, browser QA, and full suite | `ValidationReport` now serializes `rows_excluded` plus privacy-safe aggregated `row_exclusion_counts`; the overall report and every subgroup expose `concordance_ci_status` (`emitted`, `withheld_no_records`, `withheld_no_comparable_pairs`, or `withheld_insufficient_valid_replicates`). The synthetic smoke asserts zero exclusions and an emitted engineering interval; the Pages asset cache marker is versioned to `e050` after the status/evidence contract change. This remains review evidence, not clinical approval. | passing |
| E-051 | FI denominator context is typed and reference-panel identity is bound into assessment and progress handoffs | Codex, high-budget bounded Claude contract audit | focused FI/progress tests, typed response validation, generated demo parity, Pages static test, docs verification, full suite, and package/runtime smoke | Assessment data_quality now carries the available reference_panel_sha256 and a count-only fi_denominator_strength label. FI details and wellness fi_context carry the same low/moderate/high label plus an explicit engineering-only caveat. Progress comparisons reject different non-null panel digests and echo both identities; null digests remain valid only for matching in-memory development panels. Pages renders the label, panel identity context, and privacy-safe report boundary. This is engineering evidence, not clinical adequacy, calibration, or E-005 approval. | passing |
| E-052 | Assessment and external-validation serving use one explicit encoded predictor adapter contract, and readiness/receipts agree across configuration states | Codex, higher-budget bounded Claude contract audit | focused adapter parity/rejection tests, 16-cell readiness matrix, full suite, docs/static checks, package/runtime smoke, and Pages verification | `ModelAdapterProtocol` requires `predict_for_assessment(age, encoded_vector)`; `DevelopmentPredictor` now consumes the same 36-column encoded vector as fitted adapters and a parity regression proves its legacy output is unchanged. Assessment and external-validation paths reject a predictor that only exposes the legacy raw-component call. A parametrized 16-cell matrix covers model readiness, panel readiness, fixture state, and API-key configuration; `/readyz`, `/health`, and `health_to_receipt` agree, including fail-closed contradictory fixture/production metadata. This is software-contract evidence; E-005 remains unchanged. | passing |
| E-053 | Readiness diagnostics, external-validation aliases/exclusions, and optional training support strata are explicit and reproducible | Codex, higher-budget bounded Claude maturity audit | focused API/receipt/validation/split tests, full suite, smoke runners, docs/static checks, and contributor/runbook review | `/readyz` now carries the same non-secret model/panel identity fields as `/health`, and receipt mismatch output includes aggregated readiness blockers. External validation accepts the legacy `race_ethnicity` alias, rejects conflicting aliases without retaining row identifiers, and the smoke exercises duration, event, and alias-conflict exclusions (303 received, 300 evaluated, 3 excluded). `split_survival_rows` can additionally stratify by `sex` and `age_band` while retaining deterministic patient-level assignment. The 86-test Python suite passes; E-005 remains unchanged. | passing |
| E-054 | Panel readiness and fixture identity are explicit in assessment, serving, receipts, and Pages handoffs | Codex, higher-budget bounded Claude maturity audit | focused panel/API/receipt tests, generated demo artifact, Pages/static tests, full suite, and source inspection | The panel exposes one conservative state (`development_fixture_only`, `loaded_unapproved`, or `loaded_production_ready`) in typed assessment quality and `/health`/`/readyz` identity; receipts validate and preserve that state. The built-in fixture has a deterministic canonical-content SHA-256 while remaining fixture-only and blocked from production. Pages pins the state beside the report, labels the SECA preview local-only, and offers a complete focus-list JSON copy action. The 86-test Python suite and 14-test Node suite pass; E-005 remains unchanged. | passing |
| E-055 | Pages demo and local SECA handoff are failure-safe, race-safe, accessible, and printable | Codex, high-budget bounded Claude Pages audit/worker | Node tests, JavaScript syntax check, docs verifier, browser interaction, and source inspection | The 22-test Node suite covers visible demo-data failure state with disabled actions, stale synthetic-sample/FileReader guards, individually navigable segment/trend lists, expanded acronym labels, finite-value display, copy-button focus visibility, sequence-labelled status updates, and print reflow. `node --check docs/site.js`, `node --test tests/site_parser.test.cjs`, docs verification, and local Pages browser QA pass; the raw supplied SECA export remains local-only and the committed fixture remains synthetic. | passing |
| E-056 | Runtime predictor failures produce a typed privacy-safe 500 without changing domain validation responses | Codex, high-budget bounded Claude serving worker plus independent verification | focused API tests, full Python suite, Ruff, and runtime inspection | `PredictionFailure` catches only the runtime/model exception family around the explicit assessment adapter, preserves `InsufficientDataError`/`ValidationError` as 422 responses, chains the original cause for server-side debugging, and returns only `{error: {code: "PredictionFailure", message: "prediction failed"}}` for assessment and comparison failures. The current 95-test Python suite and focused API tests pass; no request body, patient identifier, model path, or exception text is returned. | passing |
| E-057 | The external-validation protocol makes support thresholds and outcome-level performance obligations explicit without fabricating clinical evidence | Codex, high-budget bounded Claude documentation worker plus independent verification | protocol/model-card source inspection and docs verifier | `EXTERNAL_VALIDATION_PROTOCOL.md` now requires the future SAP/reviewer to record minimum rows, observed events, comparable pairs, and valid bootstrap replicates per subgroup, and to report Brier or an approved survival analogue, calibration-in-the-large, calibration slope/ICI, and decision-curve/net-benefit only with prespecified decisions and thresholds. Values remain placeholders; the synthetic fixture and smoke runner remain explicitly `clinical_use: forbidden`, and E-005 remains blocked. | passing |
| E-058 | The Windows-first release path exercises the supported Python, Node, docs, and installed-wheel entry-point surfaces | Codex, high-budget bounded Claude release audit | workflow inspection, local Windows package smoke, and static/docs verification | `.github/workflows/ci.yml` now includes a `windows-latest` job that installs the locked Python 3.11 environment, runs the full Python and Node suites, verifies docs and the training-manifest template, then builds and smoke-tests an isolated wheel through PowerShell. The local Windows equivalent returns health `200`, assessment `200`, invalid request `422`, comparison `200`, and SECA smoke `assessment_ready=false`; E-005 remains unchanged. | passing |
| E-059 | Clinical-ML credibility research is mapped to current repository artifacts without overstating validation or regulatory status | Codex, high-budget bounded Claude documentation writer plus independent review | source review, crosswalk inspection, wiki entry, link/static verification, and docs parity | `docs/CLINICAL_ML_EVIDENCE_CROSSWALK.md` selectively maps TRIPOD+AI, PROBAST+AI, BMJ validation guidance, GMLP, Health Canada MLMD/transparency guidance, and WHO AI-health governance to implemented controls, templates/deferred decisions, and missing external evidence. `docs/wiki/003-clinical-ml-evidence-standards.md` preserves the reusable research receipts as a draft. The artifacts explicitly state that E-005 remains blocked and that no synthetic test or framework crosswalk is clinical validation or regulatory clearance. | passing |
| E-060 | Every Pages wellness handoff preserves typed safety and model/panel boundary fields | Codex, high-budget Claude product/runtime audit | static Node contract test, docs verification, and live Pages interaction | The copyable `wellness-focus-areas-v2` JSON now carries top-level `action_effect_estimated: false`, `clinical_or_lifespan_claim: false`, a model/panel readiness boundary, and a privacy note alongside the complete focus and missing-input lists. The operations runbook documents the boundary; no patient identifier, raw CSV, or uploaded data is included. | passing |
| E-061 | Synthetic development reference-panel content cannot be promoted by changing approval metadata alone | Codex, high-budget Claude statistical credibility audit | focused API/preflight tests, full suite, and source inspection | `is_development_fixture_content` compares the shipped band values independently of approval flags/source labels. `/readyz` blocks a production-marked panel carrying those values, and `scripts/validate_model_release.py` reports the blocker. Tests cover a promoted in-memory fixture and a promoted JSON panel; approved panels remain an external E-005 requirement. | passing |
| E-062 | Panel age-band coverage is visible and out-of-coverage validation rows are excluded without guessing | Codex, high-budget Claude statistical review plus independent correction | focused geometry/assessment/validation tests, full suite, and source inspection | `ReferencePanel.coverage_for` reports the minimum all-feature band count and narrowest matched span; assessment quality exposes both fields. External validation pre-checks coverage before z-score inference and aggregates `age outside reference-panel band coverage` without exposing row identifiers. The default development fixture reports 1 band spanning 102 years for covered ages; this remains engineering metadata, not clinical coverage evidence. | passing |
| E-063 | Production approval cannot rely on an in-sample or unknown Gompertz mapper provenance | Codex, bounded high-budget Claude implementation request plus independent implementation/verification | focused release-preflight tests, full suite, and source inspection | Fitting can still use the deterministic in-sample mapper for development, while `fit_xgb_survival` accepts an explicit mapper for approved workflows. Release preflight requires `training_config.mapper_source == "supplied"` whenever production readiness is requested, reports the mapper source, and blocks in-sample or missing provenance. This is a software gate and does not satisfy E-005. | passing |
| E-064 | Every uncertainty interval identifies how it was constructed independently of clinical validation status | Codex, high-budget Claude scientific review plus independent implementation | typed API schema, validation-report regression, synthetic smoke, docs verification, and full suite | Assessment biological-age and trajectory responses now expose `uncertainty_construction` as `wald_1_96_se` when an approved numeric interval is emitted or `none_withheld` otherwise. External validation reports and subgroup metrics expose `concordance_ci_construction` as `bootstrap_percentile` only for an emitted percentile interval and `none_withheld` otherwise. These labels make construction auditable without calling the intervals clinically calibrated; E-005 remains blocked. | passing |
| E-065 | Deterministic Python/Node test receipt | Codex, high-budget Claude design review plus independent implementation | checked-in JSON receipt, live count check, docs verifier, CI, Pages workflow, and browser/static test coverage | `scripts/build_test_receipt.py --check` reconciles 120 collected Python tests and 23 Node tests using explicit UTF-8 subprocess decoding; `verify_docs.py` checks the public counts and receipt link; Linux and Windows CI plus Pages verify the receipt before publication. | passing |
| E-066 | Runtime diagnostics expose bounded privacy-safe request metrics | Codex, high-budget Claude read-only production audit | focused API test, docs/runbook inspection, full suite, and runtime smoke | `/metrics` returns only process-local totals, status classes, latency aggregates, and oversize-rejection counts; it retains no routes, request IDs, caller identifiers, or payload fields and is API-key protected when `FRAILTY_API_KEY` is configured. Regression coverage proves the same aggregate-only field set when the key is unset. | passing |
| E-067 | API interventions and wellness focus areas carry the same measurement context and provenance | Codex, high-budget Claude principal-engineer audit plus independent implementation review | focused API/Node parity tests, generated demo parity, docs verification, and Pages interaction | `top_interventions` and `wellness_report.focus_areas` now carry the matching feature/value, unit, direction, target-range label, z-score, action type, recommendation, and source provenance from one wellness-range item; BMI-only fallback actions remain present even without a dedicated FI recommendation. The current 120-test Python suite and 23-test Node suite pass; this is presentation parity, not a clinical recommendation or action-effect estimate. | passing |

| E-068 | A local SECA scan can be completed into a privacy-safe assessment handoff without inferred fields | Codex, high-budget Claude architecture and safety audit plus independent implementation review | Python/Node tests, CLI smoke, Pages interaction, docs verification, and workflow inspection | The local Pages intake form pre-fills only the canonical fields actually present in the latest SECA scan (up to six), keeps those observed values read-only, requires explicit user-entered MVV fields, and downloads a bounded overlay without uploading scan or measurement data. The assess-overlay CLI merges the same scan overlay with the downloaded measurements and routes the result through the canonical Python assessor; evaluate_mvv and assessment_payload_overlay preserve the explicit missingness boundary. This is a software handoff and development readout path, not clinical validation, a lifespan claim, or action-effect estimate. | passing |
| E-069 | The local SECA assessment handoff is versioned, reviewable, preview-first, and deterministic across Pages and Python | Codex, three high-budget Claude principal-engineer/safety reviews plus independent implementation | Python/Node contract tests, CLI error smoke, docs verifier, full suite, installed-wheel/runtime smoke, and BrowserOS interaction | `intake_overlay.py` defines one versioned envelope and merges observed latest-scan values without inference or silent conflicts; Pages exposes an explicit pseudonymous local identifier, validates the canonical MVV categories, previews the JSON before download, and performs no upload; `assess-overlay` emits bounded JSON errors with exit 2 for MVV shortfall, 3 for validation (including malformed SECA CSV), and 4 for other expected engine failures. The 105-test Python suite and 23-test Node suite cover the round-trip, unknown/range/wrong-format/SECA-input errors, patient-id precedence and length, conflict rejection, and Python/Node MVV parity. The synthetic overlay fixture also passes the installed-wheel CLI smoke with `mvv_passed=true` and a 42.6 development age-equivalent. E-005 remains blocked. | passing |

| E-070 | A local NHANES intake can be mechanically audited with explicit mapping and privacy-safe deterministic evidence | Codex, three high-budget Claude maturity/code-design/final reviews plus independent implementation | focused script tests, aggregate receipt, docs verifier, CI help smoke, and full suite | `scripts/review_nhanes_intake.py` requires a supported cycle, repeated local XPT inputs, the CDC fixed-width mortality file, and an explicit `SEQN`/age/sex/BMI map; it rejects duplicate or missing join keys and incompatible duration units, uses only eligible mortality records for canonical rows, and records hashes plus aggregate counts without paths, identifiers, durations, measurements, or raw rows. Five focused tests cover determinism, privacy boundary, duplicate-key blocking, map/unit guards, byte-for-byte `--check`, and CLI help. The command is local-only and remains an intake-shape audit, not clinical validation or production approval. E-005 remains blocked. | passing |
| E-071 | Survey-design metadata is typed, versioned, propagated, and kept separate from unsupported complex-survey variance claims | Codex, two high-budget Claude design reviews plus independent final review | focused contract/training/validation/preflight tests, artifact round-trip, manifest/docs verification, full suite, and smoke checks | `SurveyDesign` strictly parses schema version 1 and the four supported weight kinds; training rejects contradictory raw-weight/design combinations, applies only `case_weight` as an XGBoost DMatrix weight, and persists the declaration; external-validation reports carry the declaration into the report, every subgroup, and calibration bins with `weighting_applied: false` and `design_reviewed: false`; release preflight distinguishes missing, malformed, `not_provided`, and unsupported declarations. Complex-survey variance remains `NOT_IMPLEMENTED_BY_THIS_ADAPTER`; E-005 remains blocked. | passing |
| E-072 | The next maturity tranche is independently selected and implemented without weakening reproducibility, privacy, or the E-005 clinical boundary | Codex, two high-budget Claude maturity audits plus independent adjudication | bounded implementation, focused tests, deterministic receipt/docs checks, runtime/Pages verification, and final review | Independent adjudication selected the public artifact/privacy/reviewer-receipt proposal as the single bounded R-074 tranche. Codex implemented and independently validated that exact slice without changing the clinical boundary; E-005 remains the separate blocked criterion. | passing |
| E-073 | Demo, fixture, and test receipts have deterministic sidecar attestations; research-use-only/local-only boundaries are visible; and a synthetic external-validation report is persisted without implying E-005 evidence | Codex, high-budget Claude adjudication plus bounded implementation and final review | sidecar regeneration/checks, report-envelope tests, docs verifier, Python/Node suites, installed-wheel/runtime smoke, and Pages verification | The four committed artifacts have separate deterministic `*.sha256` sidecars; CLI, README, and Pages expose research-use-only/not-for-clinical-use copy; `scripts/run_external_validation_report.py --check` verifies a deterministic envelope carrying `clinical_status=requires_e005_external_validation_and_clinical_review`, `kind=synthetic`, and `clinical_use=forbidden`. The 120-test Python suite and 23-test Node suite, docs/workflow checks, synthetic smoke, split smoke, wheel smoke, and installed-wheel CLI boundary check pass. Passing software checks do not satisfy E-005. | passing |
| E-074 | The next non-clinical production-readiness gap is independently selected and closed without weakening reproducibility, privacy, skill compatibility, or the E-005 boundary | Codex, three high-budget Claude maturity audits plus bounded Codex implementation and final review | bounded implementation, focused tests, runtime/package checks, docs/Pages verification, and final evidence reconciliation | Three high-budget Claude audit attempts were made but produced no terminal report within bounded waits and made no repository changes. Direct inspection selected and Codex closed a restrictive API response-boundary tranche: every endpoint now receives `Cache-Control: no-store`, a default-deny content security policy, restrictive permissions/referrer policy, `nosniff`, and `DENY`; runbook/README/skill guidance, a focused response-header regression covering normal, validation, authentication, and size-rejection paths, 120 Python plus 23 Node tests, docs/artifact checks, runtime header capture, and isolated-wheel smoke pass. E-005 remains blocked and out of scope. | passing |
| E-075 | The installed package behaves correctly through a real loopback HTTP serving process, not only an in-process ASGI harness | Codex | installed-wheel loopback smoke, CI workflow inspection, docs verification, and runtime evidence | `scripts/run_serving_contract_smoke.py` starts a short-lived Uvicorn process, checks `/health` 200, fail-closed `/readyz` 503, `/metrics` 200, valid assessment 200, and typed invalid assessment 422 over HTTP; it verifies all five response paths carry the security headers and that the synthetic patient identifier is not echoed. The smoke passes from the checkout and from an isolated built wheel, and Ubuntu/Windows CI runs it after wheel installation. E-005 remains unchanged. | passing |
| E-076 | Runtime health/readiness and release receipts identify the installed serving build without exposing secrets or patient data | Codex, high-budget Claude production-maturity review plus independent implementation | runtime provenance unit/API/receipt tests, isolated-wheel package and loopback smoke, CI/docs inspection, and full repository gates | `runtime_provenance` exposes a package-tree digest, installation mode, sorted dependency-set digest, Python runtime identity, and effective-configuration digest; API key values are never retained or hashed. Health and readiness carry the same block, receipts allow-list it, and strict production admission rejects incomplete/source-only provenance. The installed-wheel package smoke and real HTTP smoke require `installed_distribution` and pass locally; E-005 remains unchanged. | passing |

| E-077 | Pages publication explicitly guards its real Node test runner, and runtime-provenance helper names distinguish well-formed identity from strict admission | Codex, high-budget Claude read-only maturity audit plus independent implementation | Pages workflow/verifier inspection, focused provenance contract tests, full Python/Node suites, package/runtime smokes, and docs verification | `.github/workflows/pages.yml` runs `node --test tests/site_parser.test.cjs`, and `verify_docs.py` now requires that marker. `provenance_is_well_formed` accepts complete source or installed identities for diagnostics, while `provenance_is_ready_for_strict_admission` additionally requires `installed_distribution`; one focused test proves the distinction and the strict production API guard remains green. Full `uv run pytest` passes with 120 tests, the Node suite passes 23/23, docs/receipt/control-plane checks pass, and the rebuilt wheel plus real loopback smoke report installed-distribution provenance. E-005 remains unchanged. | passing |
| E-078 | Pages preserves canonical readout semantics and emits a complete, clearly development-only wellness handoff | Codex, high-budget Claude read-only product/accessibility audit plus independent implementation | focused Pages contract tests, docs verification, full Python/Node suites, and report/print source inspection | The Pages trajectory card labels the normalized age-equivalent difference and renders the response's uncertainty state; the report region has a named accessible boundary and a print-only research-use banner; download controls and filename identify the synthetic development output; the JSON handoff carries the complete `top_interventions` list; SECA status numbering is independent of async request tokens. The 120-test Python suite and 23-test Node suite pass, and E-005 remains unchanged. | passing |
| E-079 | The installed serving path proves both fail-closed development behavior and a strict production-like software gate over real HTTP without implying clinical approval | Codex, high-budget Claude read-only serving/model credibility audit plus independent implementation | temporary native XGBoost release bundle, real loopback HTTP smoke, CI wheel dependency inspection, focused source/docs checks, and full repository gates | `scripts/run_serving_contract_smoke.py` first observes the development fixture (`/readyz` 503), then creates and deletes a temporary non-clinical model, reference panel, and hash-bound approval sidecar. With `FRAILTY_REQUIRE_PRODUCTION=true`, the real Uvicorn process reports `loaded_production_ready`, returns `/readyz` 200, enforces API-key protection on `/metrics` and `/v1/assessments`, and returns typed authenticated 200/422 responses with security headers and no smoke identifier echo. CI wheel exports now include the locked `ml` extra required by the native XGBoost stage. The 120-test Python suite and 23-test Node suite remain green; this software receipt cannot satisfy E-005. | passing |
| E-080 | The next maturity tranche is independently selected from current evidence without weakening the E-005 boundary | Codex, high-budget Claude read-only post-R-080 audit plus independent Codex adjudication | read-only repository audit, current worktree inspection, candidate ranking, and control-plane reconciliation | Claude identified several candidates; Codex rejected redundant artifact-round-trip and in-memory-digest proposals because R-080/current runtime already exercises artifact loading and exposes the loaded artifact digest. The selected next tranche is explicit support warnings for under-supported external-validation strata, with no arbitrary clinical minimums and no E-005 claim. | passing |
| E-081 | External-validation reports explicitly identify subgroup metric support failures without converting them into clinical validation claims | Codex, independent high-budget Claude recommendation plus implementation | focused validation tests, deterministic synthetic report regeneration, docs/verifier checks, and full Python/Node suites | `ValidationReport` emits deterministic `subgroup_support_warnings` entries with dimension, label, and concrete reasons `no_events`, `no_comparable_pairs`, or `insufficient_valid_replicates`; the public package exports the warning types. The focused sparse-stratum regression observes the expected male no-event/no-pair warnings and female insufficient-replicate warning, while the 300-row synthetic report deterministically carries an empty list because its computed groups trigger none of those concrete limitations. `uv run pytest -q` passes 120 tests, `node --test tests/site_parser.test.cjs` passes 23 tests, `verify_docs.py`, report/fixture/demo/receipt checks, Ruff, compilation, lock, wheel build, and real serving smoke pass. The warning field is engineering metadata only; it does not label a subgroup validated, fair, or safe, invent clinical minimums, or satisfy E-005, which remains blocked. | passing |
| E-082 | Validation reports distinguish future outcome-level clinical metrics that are deliberately withheld from computed engineering metrics | Codex, high-budget Claude model/research audit plus independent bounded implementation | focused validation regression, deterministic report regeneration, protocol/model-card/crosswalk/operations/skill docs, Pages parser/docs checks, and full repository gates | `ValidationReport` and every computed subgroup record expose the same five named outcome metrics with `value: null`, `status: "not_implemented_pending_sap"`, `construction: "none_withheld"`, metric-specific reason, and `review_gate: "E-005"`. The contract is tested and present in the regenerated synthetic report; it never fabricates Brier, calibration-in-the-large, calibration slope/ICI, or decision-curve/net-benefit values. It remains an explicit absence/withholding contract and does not satisfy E-005. | passing |
| E-083 | Operators and agents can run one canonical non-writing software verification gate without confusing it with clinical approval | Codex, two high-budget Claude MCP attempts plus independent repository audit and implementation | verifier unit contract, `verify_project.py --json` execution, full Python/Node/docs/runtime gates, and synchronized skill/operations/README/Pages documentation | `scripts/verify_project.py` composes 18 deterministic checks by default: locked resolution, Ruff, in-memory Python syntax, Python/Node tests, test/demo/fixture/report receipts, training manifest/split and external-validation smokes, docs verification, and real loopback serving. The observed JSON run returned `status: "passed"` for all 18 checks and explicitly emitted `clinical_gate: "E-005 blocked"`; `--skip-serving` and `--json` are documented and the check composition is covered by the existing script-test module. This is a software evidence gate only; E-005 remains blocked. | passing |

A sixteenth bounded read-only Claude CLI review focused on the runtime receipt
and Pages/documentation tranche. It identified missing direct CLI I/O coverage,
unsafe loss of the previous receipt under `--force`, non-diagnostic mismatch
output, and silent receipt schema drift. Codex independently verified those
risks and addressed them with script-level tests, previous-receipt preservation,
safe mismatch diagnostics, and a source-field-set schema guard; E-005 remains
unchanged.

A seventeenth bounded read-only Claude CLI review checked the model/panel
promotion and serving boundary. It identified a real uncertainty-override gap:
the caller could supply a different standard error while a hash-bound sidecar
was present but the model was not yet marked production-ready. Codex independently
confirmed and closed that gap. Claude also suggested per-request filesystem
re-hashing and a broader fixture-provenance rule; those would expand the
immutable-artifact and approval contracts beyond the current scope, so they
were not adopted without stronger evidence. E-005 remains unchanged.

Native Claude team dispatch was unavailable on the installed Claude 2.1.233 surface. A user-authorized bounded direct Claude CLI pass completed the docs/site draft; the resulting files remain subject to independent Codex review and browser verification.

A second bounded read-only Claude CLI review independently flagged stale test
receipts, declared-header-only request limits, silent single-scan trends, and
ambiguous interval/range presentation. Codex verified those findings and
addressed the applicable engineering items; the clinical E-005 blocker is
unchanged.

A third bounded read-only Claude CLI review checked the strict wellness
OpenAPI contract, SECA preview/privacy behavior, and public wording. Codex
independently addressed its transparency findings by exposing an explicit
all-values local-review accessor, adding browser-side privacy/trend text, and
removing the stale static verification date.

A fourth bounded read-only Claude CLI review checked the typed request envelope,
readiness semantics, public privacy boundary, and API response coverage. Codex
independently addressed the applicable findings by adding actionable readiness
remediation text, a schema-validated success-path test, explicit wellness
action types, and deliberately separate synthetic SECA-style demo values.

The repository now includes `.github/workflows/ci.yml`, which enforces the
same Ruff, compilation, test, wheel-build, and Pages JavaScript checks on push
and pull request. CI is engineering verification; it does not satisfy the
clinical E-005 gate.

A fifth bounded read-only Claude CLI review returned no material findings after
the final API, wellness action-type, synthetic-demo, and receipt updates.

A sixth bounded read-only Claude CLI review checked the training anchor contract,
XGBoost raw-margin semantics, approval-sidecar binding, reference-band ordering,
calibration-plot guards, and stale receipts. Claude identified the training
selection-bias risk and the need for explicit artifact governance; its raw-margin
concern was independently contradicted by the installed XGBoost runtime and
official parameter semantics. Codex addressed the confirmed findings and added
regression coverage; E-005 remains unchanged.

A seventh bounded read-only Claude CLI review checked model credibility and
training provenance. It confirmed that the missingness report required by the
goal was not yet implemented, and noted that survey weights are pass-through
weights rather than a full complex-survey design and that the current horizon
calibration bins are not censoring-adjusted survival calibration. Codex added
the cohort-quality report and retained those methodological limits as explicit
approval obligations; E-005 remains unchanged.

An eighth bounded read-only Claude CLI review checked the Pages demo and local
SECA parser. It identified malformed-header/row-shape, Unicode-minus, copy
failure, and segment-detail presentation risks; Codex addressed those parser
and presentation items and rechecked the public synthetic boundary. E-005
remains unchanged.

A ninth bounded read-only Claude CLI review checked the training-quality report,
approval lifecycle, and external-validation methodology. It confirmed the
subgroup denominators were correctly subgroup-specific, identified the need to
clear approval hashes on refit, and recommended censoring-aware horizon
calibration; Codex implemented the confirmed lifecycle and Kaplan–Meier
software guards while retaining external clinical review as E-005.

A tenth bounded read-only Claude CLI review checked the post-review Pages and
serving surface. It confirmed the document-heading gap, browser date-ordering
and file-size risks, and API body-drain ordering; Codex implemented the shared
parser module, Node regression tests, accessibility heading, early API-key
check, and oversized-response controls. E-005 remains unchanged.

An eleventh bounded read-only Claude CLI review checked the survival-model
adapter, calibration numerics, event handling, and training provenance. Codex
rejected findings that contradicted the explicit FI-input contract or valid
Kaplan–Meier boundary behavior, and implemented the confirmed finite-input,
recipe-metadata, and weight-semantics controls. E-005 remains unchanged.

A twelfth bounded read-only Claude CLI review checked the product, serving,
release, and Pages surfaces after the hardening pass. Codex retained the
local-only patient-data boundary, synchronized the browser/Python derivation
contract, and made the ML extra and Node runtime explicit in CI. E-005 remains
unchanged.

A thirteenth bounded read-only Claude CLI review checked practical product
value in the SECA preview, wellness report, synthetic demo, and public wording.
Codex independently verified and addressed the confirmed gaps by making
non-FI wellness focus areas available through `top_interventions`, announcing
single-scan trend limits in the Pages status message, and making the
development-surrogate/uncertainty label travel with the biological-age
headline. E-005 remains unchanged.

A fourteenth bounded read-only Claude CLI review checked packaging, serving,
secret, liveness, and deployment reproducibility. Codex verified the clean
wheel-path and lockfile findings, added `uv.lock`, a locked CI environment, and
an installed-wheel smoke script. The liveness and restart/key-rotation notes
remain documented deployment-boundary policy; E-005 remains unchanged.

A fifteenth bounded read-only Claude CLI review checked the changed lockfile,
wheel-isolation, and CI paths. It found no high-severity release issue; its
earlier same-environment smoke concern is addressed by the isolated runtime
environment and pure-ASGI smoke script. Codex independently re-ran the locked
suite, built wheel, isolated smoke, live API smoke, and browser Pages checks.
E-005 remains unchanged.

The next bounded Claude CLI attempt could not produce a review because the
local CLI exhausted its USD 0.50 budget before returning output. Codex therefore
treated the downloadable wellness-improvement report as a directly reviewed
change: it is generated only from the selected synthetic result, excludes the
input payload and patient identifiers, and carries explicit development,
readiness, and no-action-effect flags. E-005 remains unchanged.

A later bounded read-only Claude CLI attempt (USD 1.00) also exited with a
budget error before returning findings. No Claude output was used for the
operations runbook; Codex independently authored and verified that engineering
handoff as E-023. E-005 remains unchanged.

The next bounded read-only Claude CLI review (USD 2.00) also exited after
exhausting its local budget without returning findings. Codex independently
reviewed the validation surface and implemented E-024; no Claude output was
used for that change. E-005 remains unchanged.

The Pages workflow was added as E-025. It is configuration evidence only until
GitHub Actions executes it on the remote repository; no deployment was
triggered from this checkout. The workflow was then aligned with the current
GitHub artifact action version and restricted to the `main` ref; verification-
only wheel smoke directories are ignored by the repository. E-005 remains
unchanged.

CP-031 added deterministic support-aware bootstrap uncertainty to external
concordance reporting. The report records the requested and valid replicate
counts for the overall cohort and each subgroup, and withholds an interval
when resampling support is sparse. This is engineering evidence for review,
not an approved clinical confidence interval. E-005 remains unchanged.

A bounded read-only Claude review of CP-031 returned three concerns. Codex
accepted the observability concern by exposing the effective comparable-pair
denominator and removed seed reuse between the headline and first subgroup
bootstrap. Codex rejected the claim that event-event ties should be treated as
comparable: the implemented pair rule requires a strict earlier event, so tied
event times have no ordering and remain excluded. No Claude edits were
accepted; E-005 remains unchanged.

A fresh bounded read-only Claude review ranked a committed synthetic
external-validation fixture runner as the highest-leverage remaining
engineering gap and also suggested surfacing fixture-only panel state. Codex
accepted both applicable findings: E-027 adds a deterministic 300-row fixture,
byte-for-byte regeneration check, CI smoke, and explicit clinical-use
provenance; the API now exposes `reference_panel_fixture_only` and keeps that
state in the readiness blockers. A separate suggested bootstrap-median field
was not added because the current report deliberately exposes the raw effective
comparable-pair denominator and its engineering-only interpretation. E-005
remains unchanged.

CP-032 is the final validation receipt for this implementation wave. The
repository passes 50 Python tests and 5 Node Pages/parser tests, Ruff lint and
format checks, byte compilation, docs verification, training-manifest
validation, `uv lock --check`, and an isolated installed-wheel smoke covering
health, valid assessment, invalid request, and SECA import behavior. Manual
BrowserOS Pages QA also confirmed the three profile choices, a generated
biological-age readout, and the expandable measured-range/recommendation
report. The local Pages server was used only for verification; no remote
deployment was triggered. E-005 remains unchanged.

CP-033 added fresh live-runtime evidence after the repository checks: the
development API returned HTTP 200 for `/health`, HTTP 503 for `/readyz` as
designed, HTTP 200 for a complete MVV assessment, and HTTP 422 for an empty
measurement request; the valid response included an `X-Request-ID`. The
development readiness block remains intentional until the approved model,
reference panel, uncertainty evidence, and API key are configured. E-005
remains unchanged.

CP-034 completed R-024. The 50-test Python suite, 5-test Node suite, Ruff
lint/format checks, byte compilation, docs verifier, lock and manifest checks,
byte-for-byte fixture regeneration, synthetic validation runner, rebuilt-wheel
smoke, live API smoke, and refreshed BrowserOS Pages interaction check all
passed. The new fixture and readiness metadata remain engineering controls;
the synthetic report is still blocked and E-005 remains unchanged.

CP-035 completed R-025. The deterministic patient-level SHA-256 split helper
and synthetic fixture smoke passed with 240 training rows and 60 holdout rows,
zero reported patient overlap, and event/censor support in both partitions.
The 50-test Python suite, 5-test Node suite, Ruff checks, byte compilation,
docs verification, fixture reproducibility, external-validation engineering
smoke, training-manifest validation, and lock check all passed. This remains
leakage-control engineering evidence rather than an approved clinical split;
E-005 remains unchanged.

CP-036 completed R-026. The 51-test Python suite, 5-test Node suite, Ruff
lint/format checks, byte compilation, docs and manifest checks, fixture
reproducibility, external-validation smoke, patient-level split smoke, locked
dependency check, rebuilt-wheel/install smoke, live API probes, and BrowserOS
Pages checks all passed. Live health returned HTTP 200 with service version
0.1.0, a 64-character deployment fingerprint, fixture-only state, and null
SHA-256 fields for unfiled development fixtures; readiness returned HTTP 503
with the expected blockers, while a valid assessment returned 200 with
X-Request-ID and an invalid request returned 422. Pages exposed 39 evidence
items, 29 status rows, 3 example profiles, and the expected readouts, focus
areas, ranges, and report-action states. E-005 remains unchanged.

CP-037 completed R-027. The 52-test Python suite, 5-test Node suite, Ruff
checks, compilation, docs verification, manifest validation, lock check,
synthetic validation/split smokes, rebuilt wheel, and isolated installed-wheel
smoke all passed. A live development API receipt captured only the allow-listed
health identity, refused a second write without `--force`, and reconciled
successfully against fresh `/health` metadata. The receipt showed a 64-character
fingerprint, development predictor/panel state, and no credential, request-body,
endpoint-URL, or patient-identifier fields. BrowserOS verified 40 evidence
items, 30 status rows, all 3 example profiles, and focus/range/report action
states on the refreshed Pages artifact. E-005 remains unchanged.

CP-038 hardened R-027 after the focused Claude review. The 53-test Python
suite, 5-test Node suite, Ruff checks, compilation, docs verification, rebuilt
wheel, installed-wheel smoke, live API health, live capture/reconciliation,
and refreshed BrowserOS Pages checks all passed. Receipt tests now cover HTTP
failure, oversized/malformed/non-object responses, overwrite refusal, forced
replacement with a previous-receipt backup, safe mismatch diagnostics, and
schema-field drift. The live API remained HTTP 200 for health and not-ready by
design; Pages showed 40 evidence items, 30 status rows, 3 examples, and valid
readout/focus/range/report-action states. E-005 remains unchanged.

CP-039 completed R-028 and E-031. The 54-test Python suite, 5-test Node suite,
Ruff checks, format check, compilation, lock check, docs verification,
deterministic external-validation/split smokes, rebuilt wheel, installed-wheel
smoke, live API probes, and refreshed BrowserOS Pages checks all passed. The
new model-release preflight verified a native artifact's persisted feature
manifest and sidecar artifact hash, rejected a stale reference-panel hash,
rejected fixture-only/panel-not-ready state, and returned a ready software gate
only after the exact panel hash was updated. A bound uncertainty parameter can
no longer be overridden while the model is blocked or ready. The preflight
retains an explicit E-005 clinical-review status even when its software gate
passes. E-005 remains unchanged.

CP-040 completed R-029 and E-032. The typed response contract now carries an
age-equivalent interpretation plus explicit false action-effect and
clinical/lifespan-claim flags in every assessment and regenerated synthetic
Pages example. Focused and full Python tests, docs verification, lint/format,
Pages parser tests, and the built demo artifact passed. This makes the safety
boundary available to downstream clients without requiring them to parse prose;
E-005 remains unchanged.

CP-041 completed R-030 and E-033. The stateless comparison route now accepts
two dated same-person snapshots, validates identity and chronology, compares
readout deltas and measured reference-band transitions, and returns current
focus areas without persisting or echoing the raw input payload. All three synthetic
Pages examples carry the same descriptive progress report and the local panel
renders it beside the selected readout. The 56-test Python suite, 6-test Node
suite, docs verification, lint/format, compilation, and generated-demo checks
passed. The comparison remains explicitly non-causal and E-005 remains
unchanged.

CP-042 completed R-031 and E-034. Pages now includes a clearly labeled,
downloadable synthetic SECA TableView CSV and a one-click local loader that
passes through the same parser as user equipment exports. The asset contains
two dated scans and five segment values, while remaining separate from the
supplied named export. The 56-test Python suite, 7-test Node suite, docs
verification, lint/format, compilation, and generated-demo checks passed;
BrowserOS confirmed the Pages shell loads without console errors. E-005 remains
unchanged.

CP-043 completed R-032 and E-035. The Pages report now shows measured,
not-measured, and focus-area counts beside the age-equivalent readout and
lists missing canonical inputs with an explicit no-fabrication/MVV explanation.
The 56-test Python suite, 8-test Node suite, docs verification, lint/format,
compilation, and generated-demo checks passed; BrowserOS confirmed the static
shell and sample loader still work without console errors. E-005 remains
unchanged.

CP-044 corrected the longitudinal E-033 evidence receipt to match the current
8-test Node Pages/parser suite. Docs verification, Node tests, and goal-document
validation passed; no product behavior or clinical gate changed. E-005 remains
unchanged.

CP-045 completed R-033 and E-036. The Python and browser SECA paths now expose
latest-minus-previous changes for shared segment values in the CLI, normalized
local handoff, and preview details. The changes remain descriptive equipment
data with no asymmetry threshold or action-effect inference. The focused and
full validation suites, docs verifier, and goal-document validator passed;
E-005 remains unchanged.

CP-046 hardened the R-033 Pages delivery boundary after live QA found a cached
older parser generation. `docs/index.html` now carries an explicit `e036` asset
token for both JavaScript files, with static-test and docs-verifier coverage;
the goal remains on the same clinical E-005 gate.

CP-047 completed the final R-033 validation wave. The 56-test Python suite, the
8-test Node suite, Ruff, compilation, docs/manifest/lock checks, skill
validation, Claude-orchestrator harness checks, rebuilt isolated-wheel smoke,
live API smoke, and fresh BrowserOS Pages QA all passed. The supplied SECA
export remains local-only; E-005 remains the sole unproven clinical gate.

CP-048 completed R-034 and E-037. A bounded Claude audit identified that
assessment responses exposed panel production readiness but omitted the
fixture-only state already present in `/health`; Codex independently confirmed
the gap and added the typed field to the pipeline/schema, regenerated the three
synthetic Pages examples, surfaced the flag in the local report boundary, and
bumped the static assets to `e037` after fresh browser QA. The 56-test Python
suite, 8-test Node suite, Ruff, compilation, docs/manifest/lock checks, live API
smoke, rebuilt isolated-wheel smoke, and fresh BrowserOS Pages interaction all
passed; E-005 remains the sole unproven clinical gate.

CP-049 completed R-035 and E-038. A second bounded read-only Claude CLI review
identified that the Pages verification job did not independently enforce
parity for the committed synthetic `docs/demo-data.json` artifact. Codex
independently confirmed that the generator uses fixed inputs and dates, added
the non-writing `--check` mode, wired it into the Pages deploy gate, and added
static coverage so the workflow cannot silently publish a stale demo artifact.
The 56-test Python suite, 9-test Node suite, Ruff, compilation, docs/manifest/
lock checks, generated-artifact check, and existing runtime/browser evidence
remain passing; E-005 remains the sole unproven clinical gate.

CP-050 completed R-036 and E-039. A bounded Claude CLI audit of the API and
release-configuration surface produced no output after roughly two minutes and
was terminated; it is not treated as evidence of no gap. Direct inspection and
an executable reproduction showed that string-valued reference-panel approval
flags were truthiness-coerced, so Codex added strict boolean parsing and
regression coverage without changing the clinical E-005 boundary. The 56-test
Python suite, 9-test Node suite, full release checks, live API smoke, and fresh
Pages verification all pass; E-005 remains the sole unproven clinical gate.

CP-051 completed R-037 and E-040. A bounded Claude Pages audit identified that
parse, size, file-read, and synthetic-sample load errors left the previous
SECA detail rows mounted. Codex independently confirmed the branches and added
one shared clearing helper plus static coverage for all four failure paths; the
Pages asset generation was bumped to `e039`. Focused Node checks pass; fresh
browser error-path verification and the full release suite remain required for
checkpoint closure. E-005 remains unchanged.

CP-052 closed R-037 and E-040. Fresh BrowserOS QA loaded the synthetic SECA
sample, confirmed its detail rows, then uploaded the repository's non-CSV JSON
fixture and observed the parse error with zero remaining detail rows. The full
56-test Python suite, 9-test Node suite, Ruff, compilation, lock, docs,
manifest, generated-fixture, wheel build, isolated-wheel smoke, and prior live
API checks pass; the updated `e039` Pages assets loaded successfully. E-005
remains the sole unproven clinical gate.

CP-053 completed R-038 and E-041. Direct parity reproduction found that the
browser parser rejected a nonnumeric unmapped auxiliary row that the Python
importer safely retained as an unmapped label. The Pages parser now records and
exposes those labels in the preview and privacy-safe normalized handoff while
continuing to reject malformed mapped values. The 56-test Python suite, 10-test
Node suite, docs verification, and parser syntax checks pass; E-005 remains the
sole unproven clinical gate.

CP-054 completed R-039 and E-042. A bounded read-only Claude CLI review
identified a possible release-receipt identity gap; Codex independently
reproduced the concrete variant in which custom production-ready dependencies
with missing model/panel digests reached `/readyz` HTTP 200. The API now fails
closed on missing or malformed production identities, and the allow-listed
receipt rejects any health payload marked ready without both identities. The
focused API/receipt tests pass and the broader release checks are pending for
checkpoint closure; E-005 remains the sole unproven clinical gate.

CP-055 completed R-040 and E-043. A bounded Claude credibility review found
that the persisted 36-column feature-name list and the inference encoder were
maintained separately. Codex independently confirmed the duplication, then
made one source-name tuple drive both the encoded manifest and vector values,
with an exact order regression that preserves existing artifacts. The full
software and Pages gates remain required for checkpoint closure; E-005 remains
the sole unproven clinical gate.

CP-056 completed R-041 and E-044. A bounded read-only Claude serving audit
identified a receipt-integrity edge case; Codex independently reproduced that
`health_to_receipt` accepted a forged ready payload with a production-ready
fixture panel. The receipt projection now validates readiness semantics and
cross-field fixture consistency, with focused regression coverage. The 57-test
Python suite remains green and E-005 remains the sole unproven clinical gate.

CP-057 completed R-042 and E-045. Direct reproduction found that a linked
mortality duration already normalized to years could be divided by 12 again
when a caller supplied a months unit on the column map. The NHANES adapter now
rejects that incompatible combination, documents the canonical-year contract,
and retains months conversion only for directly mapped durations. Focused and
full validation remain required; E-005 remains the sole unproven clinical gate.

CP-058 completed R-043 and E-046. The high-budget bounded Claude review found
that the Pages improvement-report download nested its typed safety flags only
inside `model_boundary`; Codex confirmed the mismatch against the API contract.
The handoff now exposes both flags at top level, and Node/docs checks require
the Pages status rows to cover every EVAL criterion in order. E-005 remains the
sole unproven clinical gate.

CP-059 closed the final software and publication-surface verification for
R-043. The 58-test Python suite and 11-test Node suite passed, along with Ruff,
compilation, lockfile, reproducible demo, training-manifest, training-split,
external-validation smoke, wheel build, isolated installed-wheel smoke, docs
verification, and goal-document validation. Fresh BrowserOS QA loaded the
Pages demo and parsed the improvement-report handoff: 46 status rows, no
patient identifier or raw payload, and both top-level safety flags false. The
temporary local docs server was stopped; E-005 remains the sole unproven
clinical gate.

CP-060 completed R-044 and E-047. A high-budget bounded Claude implementation
pass removed the silent wellness focus-area truncation and added the bounded
Pages disclosure. Codex independently found and corrected the empty-state
reset path, regenerated the synthetic artifact, and verified that the support
example now exposes all 27 measured non-in-range focus items while Pages shows
five by default and discloses the remainder. The full software gates completed
green; a shorter independent Claude verifier also returned PASS for the
integrated contract. E-005 remains the sole unproven clinical gate.

CP-061 completed R-045 and E-048. A high-budget bounded Claude documentation
worker produced `docs/EXTERNAL_VALIDATION_PROTOCOL.md`; Codex reviewed the
placeholder-only boundary, required evidence sections, cross-links, and static
guards. A separate bounded Claude verifier raised one source-location concern
that does not reproduce in this checkout: `validate_external_cohort` currently
passes its defined `records` list through the smoke-tested bootstrap path, and
`scripts/run_external_validation_smoke.py` completed with 300 evaluated rows.
Codex accepted the useful status-integrity concern by making the docs verifier
compare both EVAL criterion IDs and passing/blocked verdicts to `site.js`.
The protocol explicitly leaves external missingness reporting, calibration
interpretation, and clinical approval as future E-005 obligations; it adds no
clinical result or approval claim. E-005 remains the sole unproven clinical
gate.

CP-062 completed R-046 and E-049. A high-budget bounded Claude runtime audit
identified three integrity gaps: unvalidated biological-age intervals were
still numeric, receipt schema hashing only covered top-level fields, and
external-validation reports did not record the exact model/panel identities
used for evaluation. Codex implemented the nullable uncertainty boundary,
known nested `/health` field-set hashing, and model/panel identity fields with
digests and readiness/fixture state. Focused regressions prove development and
unapproved model paths withhold intervals, an approval-bound path can still
emit one, nested receipt drift is rejected, and report identity fields survive
JSON serialization. The 60-test Python suite, 12-test Node suite, Ruff,
reproducible demo/docs checks, lock check, synthetic validation/training smokes,
and fresh isolated wheel/runtime smoke all pass. E-005 remains the sole
unproven clinical gate.

CP-063 completed R-047 and E-050. A high-budget bounded Claude calibration
audit identified that repeated external-validation row failures were collapsed
into a single blocker and that a nullable concordance interval did not explain
whether records, comparable pairs, or bootstrap support were missing. Codex
independently reproduced those gaps and added privacy-safe exclusion counts,
`rows_excluded`, and explicit interval status for the headline and subgroup
reports, then extended the synthetic smoke and protocol/runbook documentation.
The same audit suggested a calibration-bin failure path; direct review showed
the current eligibility rule excludes early-censored rows before binning, so
that unreachable path was not changed. The 61-test Python suite and remaining
software gates pass; E-005 remains the sole unproven clinical gate.

CP-064 completed R-048 and E-051. A higher-budget bounded Claude contract audit
confirmed that the panel digest existed on health and validation receipts but
was absent from ordinary assessment data_quality, and recommended low,
moderate, and high count-only FI denominator labels rather than language that
could imply clinical adequacy. Codex independently reviewed the compatibility
surface and implemented typed assessment/wellness fields, digest-aware
longitudinal comparison, Pages rendering/download context, regenerated demo
data, and regression coverage. The 65-test Python suite, 12-test Node suite,
Ruff, demo/docs checks, synthetic validation/training smokes, and package
runtime smoke pass. E-005 remains the sole unproven clinical gate.

CP-065 completed R-049 and E-052. A higher-budget bounded Claude contract audit
identified that assessment serving still accepted two incompatible predictor
input contracts and that readiness coverage lacked a direct configuration
matrix. Codex independently repaired the vector source order, introduced the
explicit `ModelAdapterProtocol`, routed both assessment and external-validation
prediction through `predict_for_assessment`, and added encoded-contract parity,
legacy-adapter rejection, and 16-cell health/receipt tests. The 83-test Python
suite, 13-test Node suite, Ruff, compilation, demo/docs checks, synthetic
validation/training smokes, and package runtime smoke remain the required gates;
E-005 remains the sole unproven clinical gate.

CP-066 completed R-050 and E-053. A higher-budget bounded Claude maturity audit
identified readiness identity parity, blocker diagnostics, alias conflict
handling, optional sex/age-band split support, exclusion-path smoke coverage,
and contributor/runbook gaps. Codex independently reconciled those findings
with the checkout, retained the already-present and tested calibration-plot
writer, and implemented the feasible engineering tranche. The 85-test Python
suite, 13-test Node suite, Ruff, compilation, docs checks, synthetic
validation/training smokes, and package boundary remain the release gates;
E-005 remains the sole unproven clinical gate.

CP-067 completed R-051 and E-054. A higher-budget bounded Claude review
identified that panel readiness still required downstream inference from three
booleans, and that the in-memory fixture had no stable reportable identity.
Codex added a conservative typed panel state, propagated it through assessment,
health/readiness, receipts, and the Pages handoff, gave the fixture a canonical
content digest without changing its fixture-only block, and added a local-only
SECA label plus complete focus-list copy action. The 86-test Python suite and
14-test Node suite, locked build, smoke runners, docs checks, and package
boundary remain required gates; E-005 remains the sole unproven clinical gate.

CP-068 completed R-052 and E-055 through E-057. Two isolated higher-budget
Claude audits reviewed the model/credibility and Pages/product surfaces. A
bounded Pages worker supplied scoped hardening ideas and edits but did not
provide a completion report; Codex inspected and independently repaired the
result before testing. The serving worker added a typed generic prediction
failure envelope and focused tests; Codex corrected one invalid comparison
assertion in that worker's test and verified the API behavior. The documentation
worker completed the additive external-validation support and outcome-metric
checklist, which Codex inspected. The final 89-test Python suite and 20-test
Node suite, static checks, docs checks, smoke runners, package boundary, and
local Pages browser QA are the release gates for this tranche. E-005 remains
the sole unproven clinical gate.

CP-069 completed R-053 and E-058. A higher-budget bounded Claude release audit
confirmed that the Ubuntu CI and Pages gates already covered the documented
reproducibility contract, but identified that the Windows-first Python/Node and
Windows console-entry-point paths were not exercised in CI. Codex added a
`windows-latest` verification job with a PowerShell isolated-wheel smoke and
verified the equivalent local Windows path. E-005 remains the sole unproven
clinical gate.

CP-070 completed R-054 and E-059. A high-budget Claude credibility audit was
used as a hypothesis source, then independently checked against the current
checkout and current primary regulator/methodology sources. Claude's scoped
crosswalk writer completed `docs/CLINICAL_ML_EVIDENCE_CROSSWALK.md`; its wiki
writer could not create a new file because its write tool was unavailable, so
Codex created and reviewed the bounded draft wiki entry. The crosswalk and wiki
entry are explicitly selective and do not claim E-005, clinical validation, or
regulatory clearance. E-005 remains the sole unproven clinical gate.

CP-071 completed R-055 and E-060/E-061. A high-budget Claude product/runtime
audit identified that the copyable Pages focus-list handoff lacked the same
typed safety boundary as the full report, and a statistical review identified
that synthetic panel metadata could be rewritten without changing its band
values. Codex added the v2 typed handoff, a content-aware fixture guard, and
independent tests. E-005 remains the sole unproven clinical gate.

CP-072 completed R-056 and E-062/E-063. A high-budget Claude statistical
review prioritized inspectable panel age-band geometry and explicit mapper
provenance. A bounded implementation request produced the coverage draft;
Codex independently corrected it to require coverage across every BIA
feature, added the optional explicit-mapper training path, and added a
fail-closed release preflight gate for in-sample or unknown mapper provenance.
The current checkout collects 95 Python tests; E-005 remains the sole
unproven clinical gate.

CP-073 completed R-057 and E-064. A high-budget Claude scientific review
identified that numeric interval fields could still be consumed without a
machine-readable construction label. Codex added typed assessment and
trajectory construction fields, explicit bootstrap construction labels for
external-validation reports and subgroups, regression assertions, smoke-runner
checks, and documentation/control-plane coverage. The labels describe
engineering construction only; they do not convert development or synthetic
evidence into clinical confidence intervals. E-005 remains the sole unproven
clinical gate.

CP-074 completed R-058 and E-065. A high-budget Claude design review caught
the difference between raw Python test functions and pytest's collected-case
count (95 collected Python tests, including parametrized cases) and recommended
keeping the receipt independent from static documentation verification. Codex
added the deterministic `docs/test-receipt.json`, a live Python/Node receipt
checker with portable output parsing, exact public-count checks, Pages and CI
guards, and static Node coverage for the published receipt link. The receipt
contains only test metadata; E-005 remains the sole unproven clinical gate.

CP-075 completed R-059 and E-066. A repository re-audit identified that the
runbook described operational metrics but the service emitted only logs. Codex
added a bounded process-local `/metrics` endpoint with status-class, latency,
request-total, and oversize-rejection aggregates; protected it with the API-key
boundary when configured; added a regression for the no-label/privacy contract;
and documented reset-on-restart and nonclinical monitoring limits. E-005
remains the sole unproven clinical gate.

CP-076 extended E-066 after a high-budget, read-only Claude production audit
confirmed the aggregate-only metrics boundary, installed-wheel smoke path, and
public non-diagnostic framing, while identifying the missing no-key regression.
Codex added that regression, proving the exact bounded metrics field set remains
unchanged when `/metrics` is intentionally open on a local development process.
The receipt now records 97 Python and 20 Node tests; E-005 remains the sole
unproven clinical gate.

CP-077 started R-060. A high-budget Claude Opus documentation pass inspected
the repository but exited after announcing the draft without creating the
requested file. Codex verified that no worktree paths changed and recorded the
dispatch as inconclusive; the bounded documentation request will be retried as
an output-only draft so Codex can review and write the artifact.

CP-078 completed R-060. A second high-budget Claude Opus pass returned a full
privacy/security threat-model draft in stdout. Codex independently corrected
the flow count and removed a nonexistent repository dependency, integrated the
document into README, contributor, operations, source, and Pages navigation,
and added required-marker checks to `verify_docs.py`. The documentation gate
passes with 97 Python and 20 Node tests; E-005 remains the sole unproven
clinical gate.

CP-079 completed R-061. A high-budget Claude Opus pass returned a complete
root `SECURITY.md` policy in stdout. Codex independently corrected the
request-ID wording to match the implementation (invalid or oversized values
are replaced with a generated bounded ID), corrected the GitHub Actions
permissions description, integrated the policy into README, contributor,
operations, source, and Pages navigation, and added deterministic verifier
markers. The final validation pass then confirmed 97 Python and 20 Node tests,
the docs and goal-loop validators, reproducible synthetic fixtures, zero
patient overlap in the split smoke, the isolated wheel contract, the live API
health/readiness/metrics/422 contract, and fresh Pages interaction with no
console errors. E-005 remains the sole unproven clinical gate.

CP-080 completed R-062. A high-budget Claude Opus principal-engineer audit
identified a real drift risk between `top_interventions` and the wellness
range/focus surfaces. Codex independently confirmed the finding, made the
wellness range the source of truth for feature/value, unit, direction,
target-range label, z-score, action type, recommendation, and provenance,
added strict/additive response fields and API/Node parity tests, and exposed
the same explicit safe projection in the Pages focus-list handoff. The final
receipt rebuild also exposed and fixed Windows console-code-page handling in
`build_test_receipt.py` by using explicit UTF-8 subprocess decoding. E-005
remains the sole unproven clinical gate.

CP-081 completed R-068. Claude's high-budget architecture and safety review
recommended a local-only SECA intake handoff with explicit MVV gating and a
thin `assess-overlay` wrapper around the canonical Python assessor. It rejected
a second browser scorer or a Pyodide runtime for this static Pages surface
because that would add model-drift, bundle, and validation complexity. Codex
adopted the recommendation, kept observed SECA values read-only in the form,
and independently owned the implementation, tests, docs, and acceptance gates.
E-005 remains the sole unproven clinical gate.

CP-082 completed R-069. Two independent high-budget Claude reviews converged
on the same operator-ready hardening tranche: one versioned local SECA overlay
contract, canonical Python MVV/scoring, typed CLI error exits, explicit local
identifier rules, preview-before-download UX, and parity/round-trip tests. The
second review specifically rechecked privacy, unknown-feature/range rejection,
overlay precedence, accessibility, and the E-005 boundary. Codex integrated the
implementation, aligned the Python patient-id limit with Pages, completed the
full repository, installed-wheel, runtime, and BrowserOS gates, and received a
final independent Claude GO review with no blockers. E-005 remains the sole
unproven clinical gate.

CP-083 completed the R-070 implementation tranche. Three high-budget Claude
passes converged on a local-only NHANES intake-shape receipt: explicit cycle
mapping, fixed-width mortality parsing without a fabricated header assumption,
aggregate-only evidence, and clear separation from E-005 clinical approval.
Codex independently corrected the proposal's edge cases, implemented the
command and focused tests, wired the docs/CI guards, and will complete the full
repository gates, and integrated the final independent Claude GO review. E-005
remains the sole unproven clinical gate.

CP-084 completed the R-073/E-071 survey-design contract tranche. Two high-budget
Claude design passes converged on a strict nested schema, legacy-artifact
compatibility in development, explicit production preflight blockers, and a
clear case-weight versus complex-survey boundary. Codex implemented the typed
value object, training/artifact/validation propagation, focused regressions,
manifest/protocol/crosswalk documentation, and the release gate. The final
independent Claude review and repository gates are recorded with the dispatch
ledger below; E-005 remains the sole unproven clinical gate.

CP-027 corrected horizon calibration binning so rows censored before the
requested horizon are excluded from the estimable calibration population rather
than being treated as if they had follow-up. The report now exposes matching
`eligible_rows` and `calibration_rows`; a regression fixture covers both a
partially early-censored cohort and an all-early-censored blocked cohort.
E-005 remains unchanged.

CP-094 completed R-075/E-074. Two user-authorized high-budget Claude audit
attempts were started but produced no terminal report within their bounded
waits and made no repository changes. Direct inspection selected a narrow
serving-boundary tranche. Codex added response middleware and a focused
normal, validation, authentication, and size-rejection regression proving
`Cache-Control: no-store`, default-deny CSP,
restrictive permissions/referrer policy, `nosniff`, and `DENY`; the same
boundary is documented for operators and the serving skill. The 117-test
Python suite, 23-test Node suite, artifact/docs checks, runtime header capture,
and isolated-wheel smoke pass. E-005 remains the sole unproven clinical gate.

CP-095 recorded a final user-authorized high-budget Claude read-only review
attempt after R-075 closure. It remained silent through the bounded wait,
returned no report, and made no repository changes, so no Claude claim was
accepted as evidence. The completed R-075 evidence remains Codex-owned and
reproduced by the repository gates above; E-005 remains the sole unproven
clinical gate.

CP-096 completed R-076/E-075. Direct audit found that the installed-wheel
smoke exercised the ASGI app in process but did not prove the network serving
process. Codex added a bounded loopback HTTP smoke that launches Uvicorn,
clears deployment-specific environment overrides, checks liveness/readiness,
metrics, valid and invalid assessments, verifies response headers on every
path, rejects identifier echo, and always terminates the child process. The
smoke passes locally and from an isolated wheel, and both Ubuntu and Windows
CI invoke it. E-005 remains the sole unproven clinical gate.

CP-097 extended the durable goal scope to make the loopback HTTP serving
contract a release invariant on both supported operating-system paths. No
clinical claim or E-005 status changed.

CP-098 completed R-077/E-076. A high-budget Claude production-maturity review
identified the remaining software supply-chain gap: the existing model/panel
fingerprint did not identify the installed project bytes, dependency set,
interpreter, or resolved configuration. Codex implemented a privacy-safe
runtime-provenance block, propagated it through health/readiness and receipts,
made the isolated package and loopback smokes require installed-distribution
identity, and added strict source-only admission protection. E-005 remains the
sole unproven clinical gate.

CP-100 completed R-078/E-077. A larger-budget Claude audit identified a useful
Pages verifier guard and a naming footgun in the runtime-provenance helpers.
Current-file inspection corrected that the Pages workflow already runs the
Node suite; Codex added the missing verifier marker, renamed the structural
predicate to `provenance_is_well_formed`, added the explicit
`provenance_is_ready_for_strict_admission` predicate, and documented the
well-formed versus admissible distinction. The 120-test Python suite, 23-test
Node suite, docs/receipt/control-plane checks, rebuilt wheel smoke, and real
loopback HTTP smoke pass. E-005 remains the sole unproven clinical gate.

CP-101 completed R-079/E-078. A high-budget Claude Pages audit identified a
real handoff gap: the downloadable wellness report omitted the canonical
`top_interventions` field, while the filename/button wording and trajectory
presentation could be more explicit about development-only status and
uncertainty. Codex independently rejected the audit's incorrect claim about
the normalized deviation math and its stale-failure-placeholder claim, then
implemented the evidence-backed subset: complete intervention handoff,
development-only download naming, normalized deviation/uncertainty wording,
print-only research-use banner, named report region, and independent SECA
status sequencing. The 120-test Python suite, 23-test Node suite, docs/receipt/
control-plane checks, and source inspection pass. E-005 remains the sole
unproven clinical gate.

CP-103 completed R-080/E-079. The high-budget Claude serving/model audit ranked
a real production-mode loopback smoke as the highest-leverage bounded tranche.
Codex independently implemented it with a temporary native XGBoost artifact,
non-clinical non-fixture-content panel, hash-bound approval sidecar, strict
readiness, and API-key checks. The smoke retains the development 503 boundary,
then observes strict `/readyz` 200 and authenticated typed HTTP behavior while
deleting all temporary release files. CI now exports the locked `ml` extra for
the installed-wheel stage. This proves software integration and release
plumbing only; E-005 remains the sole unproven clinical gate.

CP-105 completed R-081/E-080. A high-budget Claude post-R-080 audit ranked a
deterministic native-artifact round-trip as its first candidate, but Codex
independently rejected that as substantially covered by the strict R-080 server
load path and existing approval-sidecar tests. Codex also rejected the proposed
in-memory digest change as redundant with the loaded artifact identity already
exposed by health metadata. The audit's genuinely open, low-risk scientific
credibility gap was explicit support warnings for under-supported validation
strata; Codex selected that as R-082/E-081. E-005 remains unchanged.

CP-106 completed R-082/E-081. Codex added the public `SubgroupSupportWarning`
contract and deterministic serialization to `ValidationReport`, covering only
concrete no-event, no-comparable-pair, and insufficient-bootstrap-replicate
limitations. A sparse-stratum regression, regenerated synthetic report, protocol,
README, operations/skill guidance, model card, Pages evidence, and documentation
verifier now agree on the same engineering-only boundary. The final observed
gates were 120 Python tests, 23 Node tests, deterministic demo/fixture/report/
receipt checks, `verify_docs.py`, Ruff, compilation, lock validation, wheel build,
and the two-stage real HTTP serving smoke. R-002 remains blocked only by E-005.

CP-107 completed R-083/E-082. The high-budget Claude model/research audit was
accepted through the local MCP fallback after direct CLI attempts were
inconclusive; its proposed outcome-level performance gap was independently
reduced to a safe, typed withholding contract. `ValidationReport` now exposes
`outcome_metric_status` overall and within each subgroup for Brier score (or an
approved survival analogue), calibration-in-the-large, calibration slope, ICI,
and decision-curve/net-benefit. Every value is explicitly `null` with
`not_implemented_pending_sap` and `none_withheld`, a metric-specific reason,
and `review_gate: E-005`; no clinical metric or threshold is fabricated. The
contract is covered by the existing external-validation regression, regenerated
synthetic report, protocol/model-card/crosswalk/operations/skill guidance,
Pages/parser checks, and the full 120-test Python, 23-test Node, docs, package,
fixture, split, external-validation, and real HTTP serving gates. E-005 remains
unchanged and is still the only remaining blocked criterion.

CP-108 opened R-084/E-083 with two focused, read-only high-budget Claude MCP
audits: one for model/research/longevity semantics and practical value, and
one for serving/Pages/skill compatibility. Both workers reached the local
server's 300-second timeout without stdout, stderr, or repository changes.
Those attempts are recorded as inconclusive; no Claude finding was accepted
as evidence. Direct repository inspection selected the highest-leverage
bounded gap: one canonical, non-writing software verification entry point
that agents and operators can run without conflating software readiness with
clinical approval.

CP-109 completed R-084/E-083. `scripts/verify_project.py` now composes 18
deterministic checks by default, including locked resolution, Ruff, in-memory
syntax compilation, 120 Python tests, 23 Pages tests, deterministic artifact
and report receipts, training/split/external-validation smokes, documentation
parity, and a real loopback serving contract. The observed JSON run passed all
18 checks and emitted `clinical_gate: "E-005 blocked"`; the software-only
variant passed all 17 non-serving checks. README, operations, skill, Pages,
and documentation-verifier surfaces now point to the same command. R-002 and
E-005 remain blocked pending an approved external cohort, clinical cutoff
review, and production model approval.

## Dispatch Evaluations

| dispatch_id | receipt | changed_paths | verification | codex_verdict | notes |
|---|---|---|---|---|---|
| GL-frailty-engine-v1-R060-CLI-001 | exec-37899 | none | Claude exited 0 after repository inspection; target file absent and `git status --short` unchanged | inconclusive | No artifact was created; no Claude self-report was accepted as completion. |
| GL-frailty-engine-v1-R060-CLI-002 | exec-36282 | docs/PRIVACY_THREAT_MODEL.md (Codex-integrated from Claude draft), README.md, CONTRIBUTING.md, docs/OPERATIONS.md, docs/SOURCES.md, docs/index.html, scripts/verify_docs.py | Claude returned the full draft; Codex reviewed and corrected it; `verify_docs.py` passed with 97 Python and 20 Node receipt counts | accepted | Claude supplied the bounded documentation content; Codex owned the repository write and acceptance decision. |
| GL-frailty-engine-v1-R061-CLI-001 | exec-88272 | SECURITY.md (Codex-integrated from Claude draft), README.md, CONTRIBUTING.md, docs/OPERATIONS.md, docs/SOURCES.md, docs/index.html, scripts/verify_docs.py | Claude returned the full high-budget draft; Codex independently reviewed implementation-sensitive claims, corrected request-ID replacement and workflow-permission wording, integrated links and verifier coverage, and re-ran the repository gates | accepted | Claude supplied the bounded security-policy content; Codex owned the repository writes and acceptance decision. |
| GL-frailty-engine-v1-R062-CLI-001 | exec-45700 | src/frailty_engine/schemas.py, src/frailty_engine/recommendations.py, src/frailty_engine/wellness.py, tests/test_engine.py, tests/site_parser.test.cjs, docs/site.js, docs/index.html, README.md, docs/MODEL_CARD.md, scripts/verify_docs.py, scripts/build_test_receipt.py | Claude returned a full read-only principal-engineer audit; Codex confirmed the drift finding, implemented the additive parity contract, fixed UTF-8 receipt decoding discovered during validation, and passed 99 Python plus 20 Node tests and the docs/receipt gates | accepted | Claude supplied the ranked gap analysis; Codex owned implementation, test updates, and acceptance. |
| GL-frailty-engine-v1-R068-CLI-001 | exec-47443 | src/frailty_engine/mvv.py, src/frailty_engine/seca.py, src/frailty_engine/__main__.py, docs/intake-form.js, docs/site.js, docs/index.html, docs/site.css, tests/test_engine.py, tests/site_parser.test.cjs, README.md, CONTRIBUTING.md, docs/OPERATIONS.md, scripts/verify_docs.py, .github/workflows/ci.yml, .github/workflows/pages.yml | Claude returned a high-budget architecture and safety review recommending the local-only intake plus canonical assess-overlay tranche; Codex independently adopted Option B, kept observed fields read-only, implemented the writes and tests, and completed the repository/runtime/Pages gates | accepted | Claude supplied the architecture and safety recommendation; Codex owns implementation and acceptance. |
| GL-frailty-engine-v1-R069-CLI-001 | exec-63928 | none (read-only audit) | Claude returned a high-budget Opus principal-engineer audit; it identified MVV parity, structured CLI errors, patient-id provenance, preview-before-download, and round-trip tests as the highest-leverage local handoff gaps | accepted | Claude supplied the ranked architecture/product/safety recommendation; Codex owned all repository writes. |
| GL-frailty-engine-v1-R069-CLI-002 | exec-20305 | none (read-only safety review) | Claude independently confirmed the selected tranche and its privacy, validation, accessibility, and E-005 boundaries before implementation acceptance | accepted | Independent Claude review; Codex owns implementation and final evidence decision. |
| GL-frailty-engine-v1-R069-CLI-003 | exec-56924 | none (read-only final review) | Claude rechecked the implemented contract against the five acceptance questions and returned GO with no blockers; it identified only optional follow-ups, including the patient-id default/length symmetry that Codex then aligned | accepted | Final independent Claude review; Codex owns implementation and final evidence decision. |
| GL-frailty-engine-v1-R070-CLI-001 | exec-78713 | none (read-only audit) | Claude returned a high-budget Opus maturity audit, ranked the bounded local NHANES intake review as the highest-leverage next tranche, and explicitly rejected invented mortality-header assumptions and any implication of clinical approval | accepted | Claude supplied the architecture and safety recommendation; Codex independently implemented the receipt contract and acceptance gates. |
| GL-frailty-engine-v1-R070-CLI-002 | exec-26571 | none (read-only code design) | Claude returned a high-budget implementation proposal for the local review command, aggregate receipt, focused tests, documentation, and CI guard; Codex reviewed the proposal, corrected its edge cases, and owned all repository writes | accepted | Claude supplied implementation options; Codex owns the final design, code, tests, and evidence decision. |
| GL-frailty-engine-v1-R070-CLI-003 | exec-88205 | none (read-only final review) | Claude returned a high-budget final GO after reviewing the implemented command, failure/privacy paths, deterministic receipt, docs, CI, EVAL/site synchronization, and E-005 boundary; it found no R-070 blocker | accepted | Final independent Claude review; the optional diagnostics and string-SEQN observations were explicitly non-blocking. Codex owns acceptance. |
| GL-frailty-engine-v1-R073-CLI-001 | exec-1673 | none (read-only audit) | Claude returned a high-budget Opus maturity audit and ranked a typed/versioned sample-weight and survey-design contract as the highest-leverage next tranche; it explicitly separated descriptive metadata from complex-survey variance and kept E-005 blocked | accepted | Claude supplied the ranked design; Codex reviewed and owned implementation. |
| GL-frailty-engine-v1-R073-CLI-002 | exec-36336 | none (read-only compatibility review) | Claude returned a high-budget GO-WITH-CONDITIONS review with mandatory strict schema, legacy artifact, weight-kind contradiction, and production-preflight conditions; Codex implemented each condition and added focused regressions | accepted | The conditions constrained the additive implementation; Codex owns final acceptance. |
| GL-frailty-engine-v1-R073-CLI-003 | exec-37838 | none (read-only final review) | Claude returned a high-budget final review of the typed contract, artifact compatibility, DMatrix behavior, validation metadata, privacy boundary, and docs/tests; final verdict recorded after the repository gates | accepted | Independent final review; Codex owns implementation and evidence acceptance. |
| GL-frailty-engine-v1-R074-CLI-001 | exec-87825 | none (read-only audit) | Claude returned a high-budget scientific-credibility audit, ranked complex-survey variance and external metric construction as the highest remaining risks, and recommended a bounded fail-closed/typed pending-metrics tranche without inventing data or bypassing E-005 | accepted | Claude supplied the ranked scientific gap analysis; Codex owns selection and implementation. |
| GL-frailty-engine-v1-R074-CLI-002 | exec-24415 | none (read-only audit) | Claude returned a high-budget product/serving/Pages audit after three read-only exploration passes, ranked public artifact attestation, local-only messaging, and archival validation-report output as implementable polish gaps, and recommended a bounded E-005-neutral tranche | accepted | Claude supplied the product/runtime gap analysis; Codex owns selection and implementation. |
| GL-frailty-engine-v1-R074-CLI-003 | exec-55292 | none (read-only adjudication) | Claude returned a high-budget adjudication with GO for the sidecar/artifact/privacy/report-envelope proposal, rejected already-implemented survey-weight work as the tranche, and hard-baked the E-005 boundary plus the non-self-referential sidecar pattern | accepted | The adjudication selected Proposal B as the single R-074 implementation slice; Codex owns implementation, control-document updates, and final acceptance. |
| GL-frailty-engine-v1-R074-CLI-004 | exec-1342 | scripts/attestation.py, scripts/build_demo_data.py, scripts/build_external_validation_fixture.py, scripts/build_test_receipt.py | Claude initialized an implementation run but did not produce a terminal implementation result; Codex stopped the idle process after it started an unrelated Ableton MCP child and no repository result was accepted | inconclusive | No repository result from this worker was accepted. |
| GL-frailty-engine-v1-R074-CLI-005 | exec-55976 | scripts/attestation.py, scripts/build_demo_data.py, scripts/build_external_validation_fixture.py, scripts/build_test_receipt.py | Claude partially added the generic sidecar helper and generator hooks, then became unresponsive before completing the requested slice; Codex reviewed the partial changes, completed the bounded implementation, and is independently validating the result | inconclusive | Partial worker edits were retained only after Codex inspection; no Claude self-report or unverified claim is accepted. |
| GL-frailty-engine-v1-R074-CLI-006 | exec-25598 | none (read-only final review) | Claude started a high-budget read-only final review but produced no terminal output or repository result after an extended wait; Codex stopped the idle process and completed the independent final review and validation gates | inconclusive | No Claude self-report was accepted; the tranche was accepted on Codex-owned inspection and reproduced repository evidence. |
| GL-frailty-engine-v1-R075-CLI-001 | exec-72070 | none (read-only maturity audit) | Claude started a high-budget repository audit but produced no terminal report within the bounded wait; it made no repository changes and Codex stopped the idle process | inconclusive | No audit recommendation was accepted as evidence. Codex selected the API response-boundary tranche from direct inspection and prior serving findings. |
| GL-frailty-engine-v1-R075-CLI-002 | exec-80055 | none (read-only focused maturity audit) | Claude started a second high-budget read-only audit but produced no terminal report within the bounded wait; it made no repository changes and Codex stopped the idle process | inconclusive | No audit recommendation was accepted as evidence. |
| GL-frailty-engine-v1-R075-CLI-003 | exec-38123 | none (read-only final review) | Claude started a final high-budget read-only review with repository inspection tools restricted to read-only access, produced no terminal report within the bounded waits, made no repository changes, and Codex stopped the idle process | inconclusive | No Claude self-report was accepted; the already-closed tranche remains supported by Codex-owned implementation and reproduced gates. |
| GL-frailty-engine-v1-R077-CLI-001 | exec-99730 | none (read-only maturity audit) | Claude returned a high-budget report identifying runtime-process provenance as the remaining software supply-chain gap; Codex independently implemented and verified the bounded package/dependency/configuration identity tranche | accepted | Claude supplied the ranked gap analysis; Codex owns repository writes and final evidence. E-005 remains unchanged. |
| GL-frailty-engine-v1-R078-CLI-001 | exec-49576 | none (read-only maturity audit) | Claude returned a high-budget post-R-077 audit ranking Pages deploy-gate verification and runtime-provenance helper semantics; Codex source inspection corrected that the Pages job already runs the Node suite and accepted the missing verifier marker plus helper-clarity proposal for bounded implementation | accepted | Claude supplied the ranked gap analysis; one workflow observation was corrected against the current file. Codex owns repository writes and final evidence. E-005 remains unchanged. |
| GL-frailty-engine-v1-R079-CLI-001 | exec-11422 | docs/index.html, docs/site.css, docs/site.js, tests/site_parser.test.cjs, README.md, docs/OPERATIONS.md, scripts/verify_docs.py, ROADMAP.md, GOAL.md, EVAL.md | Claude returned a high-budget read-only Pages/product/accessibility audit. Codex independently verified the canonical deviation math, rejected two inaccurate audit findings, implemented the complete intervention handoff and development-only presentation tranche, and is validating the repository gates | accepted | Claude supplied the ranked gap analysis; Codex owns repository writes, correction of unsupported findings, and final evidence decision. E-005 remains unchanged. |
| GL-frailty-engine-v1-R080-CLI-001 | exec-41032 | scripts/run_serving_contract_smoke.py, .github/workflows/ci.yml, README.md, docs/OPERATIONS.md, skills/frailty-engine/SKILL.md, docs/index.html, docs/site.js, tests/site_parser.test.cjs, scripts/verify_docs.py, ROADMAP.md, GOAL.md, EVAL.md | Claude returned a high-budget read-only scientific/model credibility, serving, reproducibility, and skill-compatibility audit recommending a real production-mode loopback smoke. Codex independently selected and implemented the bounded temporary-release stage; `scripts/run_serving_contract_smoke.py` passed with development `/readyz` 503 and strict `/readyz` 200/API-key/typed-response checks. | accepted | Claude supplied the ranked gap analysis; Codex owns repository writes, independent verification, and final evidence acceptance. The temporary release is software-only and E-005 remains unchanged. |
| GL-frailty-engine-v1-R081-CLI-001 | exec-85818 | none (read-only audit) | Claude returned a high-budget post-R-080 audit and ranked explicit external-validation subgroup-support warnings as the strongest non-clinical next tranche after Codex rejected redundant artifact-round-trip and in-memory-digest proposals against current source/runtime evidence | accepted | Claude supplied the ranked gap analysis; Codex independently adjudicated redundancy and owns the R-082 implementation and final evidence decision. E-005 remains unchanged. |
| GL-frailty-engine-v1-R083-CLI-001 | exec-21338 | none (read-only audit) | Direct CLI invocation returned only a generic readiness response and no repository audit; no worktree change was observed | inconclusive | No Claude finding was accepted as evidence. |
| GL-frailty-engine-v1-R083-CLI-002 | exec-63267 | none (read-only audit) | Corrected direct CLI invocation returned only a generic readiness response and no repository audit; no worktree change was observed | inconclusive | No Claude finding was accepted as evidence. |
| GL-frailty-engine-v1-R083-CLI-003 | exec-30076 | none (read-only audit) | Stdin-based high-budget CLI review produced no substantive terminal report within the bounded wait and was stopped; no worktree change was observed | inconclusive | No Claude finding was accepted as evidence. |
| GL-frailty-engine-v1-R083-CLI-004 | mcp-8001-run-4 | none (read-only audit) | Local Claude MCP returned exit 0 but only a generic no-task response rather than repository findings | inconclusive | The MCP transport was reachable, but this response was not treated as an audit. |
| GL-frailty-engine-v1-R083-MCP-001 | mcp-8001-dispatch-6:model-research | none (read-only audit) | Local Claude MCP returned a substantive model/research audit with observed source references, three post-R-082 gaps, and one recommended non-E-005 tranche; no repository changes were reported | accepted | Claude supplied the ranked analysis. Codex must independently adjudicate the proposed outcome-metric scaffolding and owns implementation and final acceptance. E-005 remains unchanged. |
| GL-frailty-engine-v1-R083-MCP-002 | mcp-8001-dispatch-6:product-serving-pages | none (read-only audit) | Local Claude MCP worker reached the 300-second timeout without a report or repository changes | inconclusive | No product/Pages finding was accepted as evidence; Codex will perform the remaining local surface audit. |
| GL-frailty-engine-v1-R084-MCP-001 | mcp-8001-r084-model-practical | none (read-only audit) | Local Claude MCP worker was killed at the 300-second server timeout without stdout, stderr, or repository changes | inconclusive | No model/practical-value finding was accepted; Codex is performing the local audit. |
| GL-frailty-engine-v1-R084-MCP-002 | mcp-8001-r084-serving-pages | none (read-only audit) | Local Claude MCP worker was killed at the 300-second server timeout without stdout, stderr, or repository changes | inconclusive | No serving/Pages finding was accepted; Codex is performing the local audit. |
<!-- goal-loop:managed:end -->
