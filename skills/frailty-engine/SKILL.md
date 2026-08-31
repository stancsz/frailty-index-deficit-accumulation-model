---
name: frailty-engine
description: Operate this repository's deficit-accumulation and biological-age engine with evidence-bounded serving, training, and external validation.
---

# Frailty Engine

Use this skill when working on the repository's assessment API, deterministic
frailty index, BIA transfer calibration, survival-model adapter, NHANES data
preparation, or held-out validation workflow.

## Operating contract

Read `GOAL.md`, `EVAL.md`, `ROADMAP.md`, and `docs/SOURCES.md` before changing
behavior. Treat the 35-feature contract and the model's explicit 36-column
manifest as interfaces: do not reorder, rename, impute, or silently coerce
features. Missing values remain missing; the FI denominator must remain
visible in user-facing results.

For serving, release, monitoring, rollback, and privacy-boundary decisions,
also follow `docs/OPERATIONS.md`. It describes the repository's operational
contract but cannot substitute for the E-005 clinical approval evidence.

The default reference panel and predictor are development fixtures. They are
useful for integration checks only. Never describe them as clinically
validated, production-ready, diagnostic, or as evidence of a health outcome.
The public response uses neutral healthspan language and must not grow
prognostic or diagnostic claims.

## Choose the smallest safe mode

- **Run an assessment:** install the development extra (or use
  `uv sync --locked --extra dev`), run the sample CLI or
  `uv run uvicorn frailty_engine.api:app`, and verify `/health` plus a
  `/readyz`, a valid assessment, and an MVV-rejected assessment. `/health` is
  liveness; `/readyz` must be `200` before production traffic is admitted. For a configured service, set both
  `FRAILTY_MODEL_PATH`, `FRAILTY_MODEL_APPROVAL_PATH`, and
  `FRAILTY_REFERENCE_PANEL_PATH`; never assume an
  absent setting is production configuration. For a bounded deployment, set
  `FRAILTY_API_KEY` and review `FRAILTY_MAX_REQUEST_BYTES`; `/health` reports
  these controls, while TLS, rate limiting, secret storage, and network policy
  belong at the deployment boundary. Confirm API responses retain
  `Cache-Control: no-store`, `X-Content-Type-Options: nosniff`,
  `X-Frame-Options: DENY`, a default-deny content security policy, no referrer,
  and a restrictive permissions policy. Also retain the non-secret
  `runtime_provenance` block and ensure strict release paths report
  `package_installation_mode: installed_distribution`; its digests identify
  software/environment drift but do not establish clinical validity.
  `provenance_is_well_formed` is a diagnostic structure check;
  `provenance_is_ready_for_strict_admission` additionally requires an installed
  distribution. Well-formed does not mean admissible.
- **Prepare or train:** use `frailty_engine.nhanes` with an explicit,
  cycle-specific `NHANESColumnMap`. Review raw questionnaire codes, laboratory
  sentinels, units, and BIA quality fields before mapping. Fit only on an
  approved survival frame; the training frame needs age/sex/BMI anchors but
  preserves optional blood/history/functional missingness and censoring for
  native XGBoost handling. Inspect `frame.quality` for cohort-level and
  standard sex/age-band/ethnicity-slice missing-count/rate and event/censoring
  evidence; add study-specific strata before validation. `fit_xgb_survival`
  carries the same JSON-safe summary on `model.training_quality`. Do not
  confuse this with the stricter assessment MVV, which remains mandatory at
  inference.
  `sample_weight_mode` distinguishes absent weights from XGBoost DMatrix case
  weights; it is not a complex-survey variance estimator. Native artifacts
  also retain the XGBoost version, fixed training parameters, boost-round
  count, and mapper provenance for reproducibility review.
- **Import SECA:** use `read_seca_tableview_csv` for the observed TableView
  CSV shape. Treat `latest_measurements()` as a typed BIA/anthropometry subset,
  review `derivations` and `unit_warnings`, and never infer demographics,
  bloods, history, or functional values from the export. Check
  `assessment_readiness` before handing the preview to an assessment workflow;
  it explicitly lists the remaining MVV requirements and should remain false
  for a SECA-only scan.
  The equivalent smoke-test CLI is `py -3 -m frailty_engine seca <path>`.
- **Complete a local assessment handoff:** use the Pages form to enter the
  missing MVV fields, review the versioned `frailty-engine-assessment-overlay-v1`
  JSON, and then run `frailty-engine assess-overlay <seca.csv> --overlay
  frailty-assessment-overlay.json`. The handoff keeps a local pseudonymous
  `patient_id`, never uploads scan data, rejects conflicting observed SECA
  values, and returns exit `2` for MVV shortfall, `3` for overlay/input
  validation, and `4` for another expected engine failure. See
  `docs/ASSESSMENT_OVERLAY.md` for the full contract.
- **Explain improvement:** use the assessment's `wellness_report` to show
  measured-feature ranges, provenance, missingness, and conservative next
  steps. It is a wellness interpretation layer, not a treatment plan or an
  estimate of action effect.
- **Compare follow-up:** use `POST /v1/assessment-comparisons` with two dated
  snapshots for the same person when a longitudinal view is needed. It returns
  descriptive readout deltas, reference-band transitions, and current focus
  areas without persisting or echoing raw measurements. A transition toward a
  development band is not evidence that an action caused a change.
- **Evaluate:** use `validate_external_cohort` on a held-out cohort with
  ethnicity, sex, and age strata. Generate both required calibration plots and
  retain the report. Review `subgroup_support_warnings` alongside subgroup
  denominators; these warnings describe concrete engineering support gaps and
  never grant a subgroup a clinical, fairness, or safety label. A passing
  engineering report does not grant clinical approval.
  The report also exposes `outcome_metric_status` overall and per subgroup.
  Future Brier/calibration/decision-curve metrics must remain `value: null`
  with `status: "not_implemented_pending_sap"` and
  `construction: "none_withheld"` until the protocol, approved cohort, and
  review gate are complete; do not replace those markers with guessed zeros or
  clinical claims.
- **Promote:** do not mark a model or reference panel production-ready unless
  the external cohort provenance, subgroup metrics, calibration, FI cutoff
  review, uncertainty checks, and clinical sign-off are present in the
  repository's evidence record. Load native artifacts with the hash-bound
  approval sidecar described in `docs/MODEL_APPROVAL.md`; `/readyz` is expected
  to remain blocked without it.

## Required verification

For code changes, run the focused tests and then the full suite, the public
evidence-receipt check (`py -3 scripts/verify_docs.py`), Ruff, byte compilation,
wheel build, the loopback HTTP contract smoke
(`py -3 scripts/run_serving_contract_smoke.py`; it requires the locked `ml`
extra and exercises both the development fixture boundary and a temporary
strict software-gate release), and the relevant runtime smoke test.
The canonical composed gate is
`uv run python scripts/verify_project.py`; use `--skip-serving` only when the
HTTP stage is intentionally unavailable and use `--json` when another agent
needs a bounded receipt. It is a software gate and must preserve the explicit
E-005 clinical blocker in its output.
For release-path checks, use
the locked environment and run `scripts/verify_package_install.py` against the
built wheel from an isolated environment; this must not rely on the checkout's
`src` path. Report observed commands and outputs separately from proposals or
human approvals. Do not commit, push, deploy, or overwrite model artifacts
without explicit user authorization.
