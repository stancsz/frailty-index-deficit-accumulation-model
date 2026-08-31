# Clinical Healthspan & Deficit Accumulation Engine

**Research-use-only — not for clinical use. This software does not satisfy
E-005 or establish clinical approval.**

This repository implements the software contract in [`GOAL.md`](GOAL.md): a
35-variable input vector, an API-enforced minimum viable vector (MVV), a
deterministic deficit-accumulation score, BIA reference-panel calibration, and
a biological-age prediction interface.

The implementation is deliberately honest about development status. A
deterministic development predictor is available so the API and data contract
can be exercised without a trained model. The XGBoost survival adapter is
optional (`pip install -e ".[ml]"`) and must be trained and externally
validated before clinical or production use. The built-in BIA panel is a
synthetic development fixture, not a clinical normative panel.

## Quick start

```powershell
py -3 -m pip install -e ".[dev]"
py -3 -m pytest
py -3 scripts/verify_docs.py
py -3 -m frailty_engine sample
# Inspect a local SECA TableView export without uploading or inferring fields
py -3 -m frailty_engine seca examples/seca_tableview_fixture.csv
```

After reviewing a local SECA preview, the Pages form can collect the remaining
values explicitly and download a CLI/API-ready overlay. The overlay is merged
with the latest canonical SECA fields by the same Python path:

```powershell
py -3 -m frailty_engine assess-overlay <path-to-your-SECA.csv> --overlay frailty-assessment-overlay.json
```

The repository's synthetic, non-patient smoke path is:

```powershell
py -3 -m frailty_engine assess-overlay examples/seca_tableview_fixture.csv --overlay examples/assessment_overlay_synthetic.json
```

See [`docs/ASSESSMENT_OVERLAY.md`](docs/ASSESSMENT_OVERLAY.md) for the versioned
overlay shape, local-identifier convention, and CLI exit codes. The overlay
command is a local handoff, not a browser upload or a clinical approval
shortcut. It rejects the same MVV failures as the API and never infers age,
sex, blood, history, or functional values from a scan.

For a locked environment, use `uv` instead. `uv.lock` is the checked-in
cross-platform resolution used by CI:

```powershell
uv sync --locked --extra dev --extra ml
uv run python -m pytest
uv run python scripts/build_test_receipt.py --check
uv run python scripts/verify_docs.py
uv run python scripts/run_serving_contract_smoke.py
uv run frailty-engine sample
```

For one repeatable, non-writing software gate, run the canonical verifier:

```powershell
uv run python scripts/verify_project.py
```

It composes the locked-resolution, lint/format, in-memory Python syntax,
Python/Node tests, deterministic artifact checks, training/external-validation
smokes, documentation checks, and the real loopback serving contract. Use
`--skip-serving` for a faster code/docs pass or `--json` for an agent/CI
receipt. A passing run is software evidence only; it reports E-005 as a
separate blocked clinical gate.

The serving smoke requires the locked `ml` extra. It exercises both the
development fixture boundary and, over real loopback HTTP, an ephemeral
hash-bound native model/panel/approval bundle with
`FRAILTY_REQUIRE_PRODUCTION=true`. The strict stage proves software loading,
readiness, authentication, privacy, and typed response behavior only; its
temporary values are not clinical evidence and cannot satisfy E-005.

Run the HTTP API with:

```powershell
py -3 -m uvicorn frailty_engine.api:app --app-dir src
```

After an editable install, the same command can omit `--app-dir src`:

```powershell
py -3 -m uvicorn frailty_engine.api:app
```

`GET /health` is a liveness check and remains HTTP `200` for the development
fixture; inspect its `readiness.status` body field for deployment state.
`GET /readyz` is the deployment readiness check and returns HTTP `503`
until the predictor, uncertainty method, reference panel, and API-key boundary
are all marked/configured for production and both the model artifact and
reference-panel file expose valid SHA-256 identities. Set
`FRAILTY_REQUIRE_PRODUCTION=true` to fail startup instead of serving when those
gates are not met.

Both endpoints expose a non-secret release identity: the service version,
model and reference-panel SHA-256 digests when configured, and a deterministic
`deployment_fingerprint`. A ready runtime must expose both valid digests;
development fixtures may report null values but remain blocked. Keep that
fingerprint with the release receipt so an operator can reconcile the running
model/panel pair without exposing API keys, request bodies, model parameters,
or patient identifiers.

Health and readiness also expose a non-secret runtime-process provenance block:
the installed project package-tree digest, installation mode, sorted dependency
set digest, Python implementation/version, and resolved-configuration digest.
The loopback serving smoke compares those fields from the running process with
the installed environment. Strict production admission requires complete
installed-distribution provenance; these values identify software drift, not
clinical validity.

Capture and reconcile that runtime identity with the repository-provided
allow-listed receipt tool. It sends only a bounded `GET /health`, never stores
the endpoint URL or request data, and refuses to replace an existing receipt
unless `--force` is explicit:

```powershell
uv run python scripts/capture_release_receipt.py --output release-receipt.json
uv run python scripts/capture_release_receipt.py --output release-receipt.json --check
```

The receipt also records a hash of the source health-field set, so adding a
new health field makes an older receipt fail reconciliation until it is
deliberately regenerated.
Receipt parsing also validates the health state semantically: a `ready`
receipt must have no blockers, production-ready model/panel metadata, API-key
protection, and a non-fixture panel; top-level and operational-control
fixture flags must agree. Contradictory or incomplete health payloads fail
closed instead of becoming release evidence.

Before promoting a fitted artifact, validate the artifact, reference panel,
and approval sidecar together:

```powershell
uv run python scripts/validate_model_release.py `
  --model models/healthspan-cox.json `
  --panel config/seca-reference-panel.json `
  --approval models/healthspan-cox.approval.json
```

The command emits a privacy-safe JSON preflight and exits non-zero when the
software gate is blocked by an unapproved model, unvalidated uncertainty,
fixture-only panel, or panel-binding mismatch. A passing software gate still
does not satisfy E-005 or establish clinical approval.

For a configured serving process, set both paths before starting Uvicorn:

```powershell
$env:FRAILTY_MODEL_PATH = "models/healthspan-cox.json"
$env:FRAILTY_REFERENCE_PANEL_PATH = "config/seca-reference-panel.json"
$env:FRAILTY_MODEL_APPROVAL_PATH = "models/healthspan-cox.approval.json"
py -3 -m uvicorn frailty_engine.api:app --app-dir src
```

If either setting is absent, the app intentionally starts with the
development predictor or synthetic panel and reports `production_ready: false`
in its health/assessment metadata. A saved XGBoost artifact includes the
feature manifest and fitted Gompertz mapper parameters so loading it cannot
silently revert to a different baseline-risk curve. An XGBoost artifact also
requires the optional approval sidecar above before it can become production
ready; the sidecar binds the exact SHA-256 artifact hash and reference-panel
file hash, model id, 36-column feature manifest, reference-panel id,
uncertainty method/parameter, approver, and evidence references. See
[`docs/MODEL_APPROVAL.md`](docs/MODEL_APPROVAL.md) and the
[`clinical-ML evidence crosswalk`](docs/CLINICAL_ML_EVIDENCE_CROSSWALK.md).

Reference-panel JSON approval flags are parsed strictly: `production_ready` and
`fixture_only` must be booleans when present. Malformed strings or numbers are
rejected instead of being coerced into a readiness decision.

For a deployment boundary, set `FRAILTY_API_KEY` to require `X-API-Key` or
`Authorization: Bearer ...` on `/v1/*` and `/metrics`, and optionally set
`FRAILTY_MAX_REQUEST_BYTES` (default `65536`). The service returns an
`X-Request-ID`, writes body-free structured request logs, and exposes bounded
process-local counters at `/metrics`. Metrics contain only totals, status
classes, latency aggregates, and oversize-rejection counts; they reset on
restart and are not a clinical monitoring result. Put a real rate limit, TLS
termination, secret manager, and network policy at the reverse proxy; this
small development service is not an internet-facing security boundary by
itself. Configure the API key before binding the service beyond loopback, even
for an internal network.

Then send an assessment to `POST /v1/assessments`:

```json
{
  "patient_id": "00000000-0000-0000-0000-000000000001",
  "measurements": {
    "age": 45,
    "sex": "female",
    "bmi": 23.4,
    "phase_angle": 6.1,
    "ecw_tbw": 0.39,
    "fasting_glucose": 92,
    "hba1c": 5.3,
    "albumin": 4.2,
    "egfr": 98,
    "hs_crp": 0.7,
    "wbc": 6.0,
    "hypertension": 0,
    "t2d": 0,
    "osteoarthritis": 0,
    "sleep_apnea": 0
  }
}
```

`InsufficientDataError` is returned as a structured 422 response when the
MVV is not met. Missing values are not fabricated: they are omitted from the
FI denominator and remain missing for the XGBoost adapter.

The response field `metrics.biological_age.ci_95` is nullable. The shipped
development predictor marks `uncertainty_validated: false` and returns
`ci_95: null`; it does not serialize an unvalidated engineering interval as a
confidence interval. A numeric interval is emitted only when an approved
predictor supplies validated uncertainty. It must not be presented as a
calibrated clinical confidence interval until cohort-based uncertainty
analysis is approved.

The adjacent `uncertainty_construction` field makes the interval mechanics
explicit: `wald_1_96_se` for an emitted approved-model standard-error interval
and `none_withheld` when no interval is serialized. This is a software
construction label, not evidence that the interval is clinically calibrated.
External-validation reports use `concordance_ci_construction` with
`bootstrap_percentile` only when a supported percentile interval is emitted.

External-validation reports also retain the exact `model_id`, model artifact
SHA-256 when available, reference-panel id, panel SHA-256 when available, and
their production/fixture state. These identities make a report reproducible;
they do not establish clinical approval.

Assessment responses expose `data_quality.reference_panel_fixture_only` and
the conservative `data_quality.reference_panel_readiness` state:
`development_fixture_only`, `loaded_unapproved`, or
`loaded_production_ready`. Treat the typed state as the public panel boundary;
do not infer readiness from the panel id or one boolean alone.

Assessment responses also carry `data_quality.reference_panel_sha256`. A file
panel uses its source-file hash; the built-in development fixture uses a
deterministic canonical-content digest while remaining fixture-only.
Longitudinal comparisons echo both panel identities and reject a digest
mismatch. The FI response includes a
count-only engineering denominator band (low, moderate, or high) beside the
exact number of valid FI variables; it is not a clinical adequacy judgment or
a patient target.

For the operator-facing startup, readiness, monitoring, rollback, and privacy
handoff contract, see [`docs/OPERATIONS.md`](docs/OPERATIONS.md). It is a
development-serving runbook and does not replace the clinical approval gate.
The cross-surface privacy and security trust boundaries are summarized in
[`docs/PRIVACY_THREAT_MODEL.md`](docs/PRIVACY_THREAT_MODEL.md); it is a review
artifact, not a compliance attestation.
The contributor/operator security policy, private vulnerability-reporting
boundary, and security-sensitive release checklist are in
[`SECURITY.md`](SECURITY.md).
Contribution and release-evidence rules are in
[`CONTRIBUTING.md`](CONTRIBUTING.md).

## Safety and validation boundary

This is a wellness and healthspan software prototype, not a diagnostic device
or a substitute for clinical judgment. The supplied defaults are useful for
contract and integration tests only. Before production deployment, supply
peer-reviewed SECA reference panels, replace/approve the engineering FI
cutoffs, train on an approved NHANES linked-mortality extract, and complete
the external, subgroup, calibration, and measurement-completeness validation
listed in `EVAL.md`.

See [`docs/SOURCES.md`](docs/SOURCES.md) for the implementation's source
boundary and explicit evidence gaps.

## GitHub Pages

The site is a dependency-free static artifact under [`docs/`](docs/). The
[`deploy-pages` workflow](.github/workflows/pages.yml) verifies the evidence
receipt, browser-parser tests, and a non-writing deterministic regeneration
check for `docs/demo-data.json`, then publishes `docs/` through the official
GitHub Pages artifact/deploy actions on `main` or manual dispatch from `main`.
Enable GitHub Pages with the `GitHub Actions` source once for the repository; no
site build command is required. `docs/.nojekyll` keeps the HTML, CSS, JavaScript,
JSON demo artifact, and Markdown evidence files available as-is.

## SECA TableView import and wellness report

The supplied clinic export shape is supported as a local, non-uploading
preview. It accepts UTF-8-BOM-safe `Value`, `Unit`, and dated columns, maps BMI, skeletal
muscle mass, visceral adipose tissue, weight, fat mass, and segmental muscle,
and derives fat-free mass/FFMI only when the same scan contains the required
inputs:

```python
from frailty_engine import read_seca_tableview_csv

export = read_seca_tableview_csv("exports/seca_tableview.csv")
print(export.latest.measured_at)
print(export.latest_measurements())
print(export.latest_all_measurements())  # includes non-canonical support values
print(export.trend())  # latest minus previous dated scan
```

The importer does not infer age, sex, bloods, history, or functional values;
the resulting subset still needs the MVV before it can be assessed. Derived
values and unit warnings remain attached to the parsed scan for review. Do not
commit a named patient export to this repository or its Pages site.

The Pages site includes [`docs/example-seca-tableview.csv`](docs/example-seca-tableview.csv),
an anonymized synthetic two-scan sample that visitors can download or load
with the local parser. It is a software fixture for trying the workflow, not
clinical equipment data.

The static page uses a versioned query token on its JavaScript assets. Bump the
token in `docs/index.html` whenever the Pages JavaScript contract changes so a
new deployment cannot be masked by a stale browser cache.

The Python CLI and Pages preview also expose an `assessment_readiness` checklist.
It explicitly reports that a SECA-only scan is not assessment-ready and lists
the remaining age/sex, missing scan, blood-panel, and history requirements,
along with a safe next step. This prevents a rich body-composition preview from
being mistaken for a complete model input record.

The Pages preview also offers **Download normalized local summary** after a
successful parse. It writes `seca-normalized-summary.json` in the browser with
the latest mapped values, units, derivations, warnings, segmental values, and
labels for any unmapped auxiliary export rows, so nonnumeric notes or other
unmapped TableView content is retained as a review signal without blocking the
mapped measurements. The raw CSV, original filename, and patient identifier are
not included, and the file is never uploaded by the site.
Available measurement and segment trend deltas remain descriptive
latest-minus-previous equipment values, not a clinical asymmetry threshold or
action-effect estimate.

If a later local file fails parsing, reading, or the 5 MB size check, the
preview details are cleared before the error status is shown. This prevents
measurements from an earlier file from being mistaken for the current one.

Every successful assessment now includes `wellness_report`: measured-feature
target/reference ranges, status, priority, provenance, missing features, and
conservative next steps. Each range also labels the action as `lifestyle` or
`review`; `review` means contextualize or discuss the result, not that the
measurement should be driven up or down. These are development/reference bands, not
individualized medical targets, and the engine does not estimate whether an
action will change biological age. `top_interventions` preserves the highest-
priority FI-derived actions and also surfaces measured non-in-range wellness
items (such as BMI, waist, or blood pressure) that do not have a separate FI
recommendation entry, so the API's action list cannot silently omit a reported
focus area. Each action also carries the matching unit, direction, target-range
label, and source provenance from the wellness range, so consumers do not have
to reconcile two independently formatted versions of the same finding.

`wellness_report.focus_areas` is the complete API list: every measured
non-in-range focus item, in the existing deterministic priority/biomarker
order. `summary.focus_areas` is the total count of measured non-in-range
items (the API does not silently truncate the list). The Pages demo shows at
most five focus bullets by default, displays a "Showing N of M" count, and
exposes the remaining items inside a `<details>` disclosure so no actionable
area is hidden. The downloadable `wellness-improvement-report-v1-development.json` always
contains the complete API list.

The static Pages demo uses `docs/demo-data.json`, generated by
`scripts/build_demo_data.py` from synthetic profiles. It includes a SECA-style
example, a focus-area example, and a balanced example without exposing the
supplied patient export. Run `uv run python scripts/build_demo_data.py --check`
to verify that the committed artifact is byte-for-byte reproducible without
rewriting it.

For a selected synthetic profile, Pages also offers a local
`wellness-improvement-report-v1-development.json` download and a print action. That handoff
contains the readout, FI context, numeric development ranges, focus areas,
missing inputs, recommendations, the complete `top_interventions` list, and model/readiness boundary, but excludes the
input payload and patient identifiers. It explicitly records that action
effects and clinical/lifespan claims are not established.

For longitudinal review, the API also exposes a stateless
`POST /v1/assessment-comparisons` route. Send two dated, same-person
assessment snapshots and it returns readout deltas, measured range/status
transitions, newly appearing or resolved focus areas, and the current
recommendations. The response contains derived outputs only; it does not
persist snapshots or echo the input payload. It is descriptive comparison
evidence, not a causal action-effect estimate or a prediction that a change
will alter biological age or lifespan.

The API makes that boundary machine-readable too: biological-age results carry
an explicit `interpretation`, and the wellness report carries
`action_effect_estimated: false` and `clinical_or_lifespan_claim: false`.
Clients should preserve and display these fields rather than treating a numeric
readout or recommendation as a treatment-effect estimate.

For upstream data preparation, `frailty_engine.derived.calculate_fib_4` makes
the required age/AST/ALT/platelet formula explicit, while the public 35-feature
vector stores only the resulting `fib_4` value.

## Training and external validation

Approved flat rows can be prepared and fitted with the optional native
XGBoost adapter:

```python
from frailty_engine import fit_xgb_survival

model = fit_xgb_survival(rows, reference_panel=approved_seca_panel)
model.save_model("models/healthspan-cox.json")
```

When no mapper is supplied, fitting estimates the baseline Gompertz scale and
growth rate from the training survival rows and the fitted Cox linear
predictors. This is a reproducible calibration step, not evidence of clinical
validity; retain its training-cohort provenance and verify it on held-out data.
When case weights are supplied, the same positive weights are applied to this
profile-likelihood baseline calibration and recorded as
`mapper_weight_mode`.

Each row must include `duration`, `event`, `patient_id`, `age`, `sex`, and
`bmi`. This is the training anchor contract; it is intentionally less strict
than the assessment MVV so optional blood, history, and functional missingness
can be measured and preserved rather than selecting only complete rows.
Censored rows are retained and missing feature values remain `NaN` for
XGBoost's sparsity-aware split handling. Assessment requests still require the
full MVV before they reach the predictor.

`build_survival_frame` exposes a descriptive `frame.quality` report with row,
event, censoring, per-feature missing counts, and per-feature missing rates on
the exact 36-column matrix. It also reports standard `sex`, `age_band`, and
`ethnicity` slices, using `unknown` rather than silently dropping missing
ethnicity labels. `fit_xgb_survival` carries the same JSON-safe summary as
`model.training_quality` and persists it in the artifact metadata. Add any
study-specific strata and recompute the report before making a validation
claim; these summaries are descriptive evidence, not clinical approval.
The fitted artifact also records the XGBoost version, fixed training
parameters, boost-round count, and whether the mapper was supplied or fitted
in-sample. This makes the engineering training recipe inspectable; it does not
replace a frozen cohort manifest or external validation.
Training and validation can carry the strict, versioned `SurveyDesign` contract
(`weight_kind` is `case_weight`, `replicate`, `stratum`, or `not_provided`).
Only positive `case_weight` values are applied by this adapter; replicate and
stratum declarations are retained as metadata and do not enable complex-survey
variance. Validation reports explicitly emit `design_reviewed` and
`weighting_applied` flags, and release preflight blocks production-ready
artifacts without an explicit supported design declaration.
For a production approval workflow, pass a reviewed `GompertzMapper` explicitly
to `fit_xgb_survival(..., mapper=reviewed_mapper)`. The release preflight blocks
an artifact whose mapper provenance is in-sample, missing, or unknown even when
an approval sidecar requests production readiness.

For a reproducible review boundary, `split_survival_rows` creates fit and
holdout partitions at the patient level using a seeded SHA-256 assignment and
separate event/censor strata. An optional `strata=("sex", "age_band")`
boundary preserves those support slices when the cohort is large enough. It
rejects duplicate identifiers and returns partition counts without exposing
patient IDs. Run the fixture smoke with:

```powershell
uv run python scripts/run_training_split_smoke.py
```

This is leakage-control engineering, not a substitute for the study's
prespecified split, tuning boundary, or external validation.

Use [`docs/TRAINING_MANIFEST_TEMPLATE.json`](docs/TRAINING_MANIFEST_TEMPLATE.json)
to record the exact cycle files, download checksums, cycle-specific eligibility,
missing-value and BIA fit-quality decisions, linkage fields, survey-weighting
limits, split strategy, sensitivity runs, and reference-panel identity before a
training run is treated as reproducible. The template is deliberately marked
`status: template`, contains no downloaded data, and keeps `production_ready:
false`; populate it only from the source codebooks and reviewed study protocol.
Validate its shape with:

```powershell
py -3 scripts/validate_training_manifest.py docs/TRAINING_MANIFEST_TEMPLATE.json
```

The canonical input matrix remains 35 variables. The fitted model matrix has
36 columns: those 35 inputs (with `sex` encoded as `sex_male`) plus the
calculated FI feature. The source order and encoding are defined once by
`MODEL_VECTOR_SOURCE_FEATURE_NAMES`; `MODEL_VECTOR_FEATURE_NAMES` is derived
from it for the persisted artifact manifest. Both assessment and
external-validation inference use `ModelAdapterProtocol.predict_for_assessment`
with this encoded vector; legacy raw-component predictor calls are rejected.
Do not reorder it without a new model artifact and approval record.

Once an approved external cohort is available, use
`frailty_engine.validation.validate_external_cohort` to produce concordance,
sex/age/ethnicity subgroup metrics, and calibration data, then
`write_calibration_plots` to render the two required plots. The report remains
blocked until the model, reference panel, cohort provenance, and clinical
review are explicitly approved. Each subgroup record includes its row count,
event count, censor count, event fraction, mean follow-up, and concordance
when comparable pairs exist. The report also includes a deterministic,
support-aware percentile bootstrap interval for concordance, together with the
requested and valid replicate counts and the effective comparable-pair
denominator; resamples without comparable event pairs are excluded and sparse
support withholds the interval. The serialized report also records
`rows_excluded`, privacy-safe aggregated `row_exclusion_counts`, and a
`concordance_ci_status` explaining why an interval was emitted or withheld.
The serialized report also includes `subgroup_support_warnings`, a deterministic
list of observed subgroup limitations with `dimension`, `label`, and one or more
concrete reasons: `no_events`, `no_comparable_pairs`, or
`insufficient_valid_replicates`. An empty list means that no such concrete
limitation was detected in the computed groups; it is not a validation, fairness,
or safety claim. These are engineering review aids, not a minimum sample-size,
fairness, or clinical confidence-interval approval, and the harness does not
invent clinical thresholds.
The report also includes `outcome_metric_status` at the overall level and
inside each subgroup record. It names the future outcome-level metrics (Brier
score or approved survival analogue, calibration-in-the-large, calibration
slope, ICI, and decision-curve/net-benefit) with `value: null`,
`status: "not_implemented_pending_sap"`, and
`construction: "none_withheld"`. This explicit absence contract prevents a
missing clinical metric from being mistaken for zero or for a computed result.
The values remain withheld until the protocol's prespecified SAP, endpoint and
censoring method, decision/threshold review, and approved external cohort are
available; this software contract does not satisfy E-005.
The API applies a defense-in-depth response boundary to every endpoint:
responses are `Cache-Control: no-store` and carry restrictive browser headers
(`nosniff`, `DENY`, no referrer, no permissions, and a default-deny content
security policy). These headers do not replace TLS, rate limiting, ingress
controls, or secret management at deployment time.
Assessment quality also reports the minimum reference-band count and narrowest
matched age span across all required BIA features. External-validation rows
outside any required feature's panel coverage are aggregated under a stable
exclusion reason and are not coerced into a z-score or calibration value.

Before an approved cohort is available, the repository also carries a
deterministically generated, clinical-use-forbidden fixture at
`examples/external_validation_synthetic.json`. Verify that it reproduces
byte-for-byte and exercise the full validation path with:

```powershell
uv run python scripts/build_external_validation_fixture.py --output examples/external_validation_synthetic.json --check
uv run python scripts/run_external_validation_smoke.py
```

The smoke covers 300 synthetic rows, both sexes, all four age bands, three
synthetic ethnicity strata, calibration bins, and concordance support. Its
blocked status is expected because the predictor and reference panel remain
development fixtures; this evidence cannot satisfy E-005.

The deterministic synthetic validation report envelope at
`examples/external_validation_validation_report.json` is a reviewable
software artifact, not external-cohort evidence. Its `clinical_status` keeps
the requirement for E-005 external validation and clinical review explicit;
its separate `.sha256` sidecar attests bytes only.

Calibration bins use only rows with observable follow-up at the requested
horizon (or an event before it), use a Kaplan–Meier estimate of event
probability, and report early-censoring counts separately. Validation blocks
when no usable horizon follow-up remains; this is a software guard, not
clinical calibration evidence.

Before an external cohort is opened or unblinded, use the reviewable
[`docs/EXTERNAL_VALIDATION_PROTOCOL.md`](docs/EXTERNAL_VALIDATION_PROTOCOL.md)
template to freeze the intended use, cohort/source identity, endpoint,
censoring and horizon, leakage checks, feature and missingness rules, subgroup
denominators, calibration and uncertainty analyses, reproducibility artifacts,
reviewer sign-off, and stop/rollback conditions. The document is deliberately
placeholder-only: it contains no cohort or results and does not satisfy E-005.

## Public NHANES preparation

`frailty_engine.nhanes` contains a mechanical adapter for the public
1999-2000, 2001-2002, and 2003-2004 BIA cycles and the CDC fixed-width
2019 public-use linked-mortality files. It reads XPT files with the optional
data extra and parses the mortality file's MEC follow-up duration from months
into the canonical model unit of years. The adapter does not guess
cycle-specific questionnaire codes or missing-value sentinels; provide an
explicit `NHANESColumnMap` for each cycle. When linking the output of
`read_public_use_mortality`, leave `duration_unit="years"`; the map's unit
conversion is only for a duration column mapped directly from an XPT row.
This fail-closed distinction prevents a linked duration from being divided by
12 twice.

```powershell
py -3 -m pip install -e ".[data,ml]"
```

For a local, aggregate-only intake receipt, use the bounded review command in
[`docs/NHANES_INTAKE.md`](docs/NHANES_INTAKE.md). It requires an explicit
cycle-specific map, parses the CDC fixed-width mortality file without assuming
a header row, and records only hashes and aggregate counts; it never downloads
or serializes SEQN values, patient identifiers, durations, measurements, or
local paths.

```python
from frailty_engine import (
    NHANESColumnMap,
    build_nhanes_rows,
    merge_xpt_files,
    read_public_use_mortality,
)

merged = merge_xpt_files(
    [
        "data/1999-2000/DEMO.XPT",
        "data/1999-2000/BMX.XPT",
        "data/1999-2000/BIX.XPT",
    ]
)
mortality = read_public_use_mortality(
    "data/1999-2000/NHANES_1999_2000_MORT_2019_PUBLIC.dat"
)
column_map = NHANESColumnMap(
    {
        "bia_resistance_50k": "BIXS050K",
        "bia_reactance_50k": "BIXC050K",
        "bia_ecf": "BIDECF",
        "bia_tbw": "BIDTBW",
        "bia_fat_free_mass": "BIDFFM",
        "height_cm": "BMXHT",
        "sample_weight": "WTMEC2YR",
        # Add cycle-reviewed maps for RIDAGEYR, RIAGENDR, BMXBMI, blood,
        # history, functional, and ethnicity fields after their raw codes
        # have been explicitly normalized for this cycle.
    },
    missing_values=frozenset({7, 9, 77, 99}),
)
rows = build_nhanes_rows(
    merged.to_dict("records"),
    column_map=column_map,
    mortality_records=mortality,
)
```

In practice, merge BIX with the cycle's demographics, body-measures,
laboratory, and questionnaire XPT tables before mapping them. Numeric NHANES
codes such as sex, race/ethnicity, questionnaire responses, and special
missing values require a cycle-reviewed recoding step; this library does not
silently infer those definitions.

The adapter can derive 50-kHz phase angle, ECW/TBW, FFMI, and FIB-4 only when
their explicit source columns are mapped. Skeletal muscle mass, visceral fat,
and questionnaire/history definitions are not invented when the public cycle
does not provide a reviewed equivalent. Rows need the training anchor contract
(age, sex, and BMI) before they enter `fit_xgb_survival`; the stricter MVV is
enforced for assessment inference, and no missing value is imputed. When a
survey weight is mapped, it must be present and positive for every training row and
is passed through to XGBoost.
These are DMatrix case weights, not a full complex-survey variance, replicate,
or jackknife design. Record and review the survey design separately before
using weighted results as evidence; the external-validation harness keeps its
metrics unweighted and reports `weighting_applied: false` until an approved
analysis adapter exists.
