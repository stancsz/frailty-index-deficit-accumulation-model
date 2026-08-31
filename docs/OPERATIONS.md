# Operations runbook

Status: development-serving contract; this is not a production approval.

This runbook describes how to run, verify, observe, and roll back the
healthspan engine. It is intentionally explicit about the boundary between
software operations and clinical/model approval. The repository currently
ships a synthetic reference panel and a development predictor, so the default
configuration must remain outside production traffic.

The cross-surface data flows, abuse cases, retention boundaries, and incident
checklist are summarized in
[`PRIVACY_THREAT_MODEL.md`](PRIVACY_THREAT_MODEL.md). That document is a
development review artifact and does not replace deployment, privacy, security,
or clinical approval.
The root [`SECURITY.md`](../SECURITY.md) adds the vulnerability-reporting and
security-sensitive change checklist for contributors and deployment owners.

## 1. Runtime modes

### Local development

Use the locked environment and the development fixtures:

```powershell
uv sync --locked --extra dev --extra ml
uv run uvicorn frailty_engine.api:app --app-dir src
```

In this mode:

- `GET /health` should return HTTP 200 with `readiness.status: "not_ready"`.
- `GET /readyz` should return HTTP 503.
- `POST /v1/assessments` remains useful for contract and integration checks.
- The response must retain `production_ready: false` and
  `uncertainty_validated: false`.
- The response's `data_quality.reference_panel_fixture_only` must remain
  `true`; downstream callers should use this typed flag rather than infer
  fixture state from the panel id.
- The response's `data_quality.reference_panel_readiness` must remain
  `development_fixture_only`; use this explicit state rather than inferring
  readiness from a panel id or digest.

### Production admission

Production admission is fail-closed. Configure all of the following before
starting a production process:

```text
FRAILTY_REQUIRE_PRODUCTION=true
FRAILTY_MODEL_PATH=<immutable fitted XGBoost artifact>
FRAILTY_MODEL_APPROVAL_PATH=<matching human-authored approval sidecar>
FRAILTY_REFERENCE_PANEL_PATH=<approved reference-panel JSON>
FRAILTY_API_KEY=<secret supplied by the secret manager>
FRAILTY_MAX_REQUEST_BYTES=<reviewed positive integer>
```

The default request-body limit is 65,536 bytes (64 KiB). Treat that as an
explicit operational control, not a promise that every deployment has the
same capacity; review and record any override in the release receipt.

The model sidecar must bind the exact artifact SHA-256, 36-column feature
manifest (generated from the repository's single-source vector contract), model
id, reference-panel id and SHA-256, uncertainty method and
parameter, approver, and evidence references. The configured reference panel
must be marked `production_ready: true`. With
`FRAILTY_REQUIRE_PRODUCTION=true`, startup fails if any of those checks or
the API-key boundary is missing. A successful startup is still not clinical
approval; E-005 requires external cohort evidence and human review.
Any runtime marked ready must expose valid SHA-256 identities for both the
loaded model artifact and the frozen reference-panel file; `/readyz` remains
blocked if either identity is missing or malformed. The built-in development
fixture exposes a deterministic canonical-content digest for report
reconciliation, but `reference_panel_readiness` remains
`development_fixture_only` and it cannot become ready. A panel is
`loaded_production_ready` only when its production flag and digest are both
present; other non-fixture panels are `loaded_unapproved`.
The panel loader also rejects non-boolean `production_ready` or `fixture_only`
values rather than coercing them, keeping malformed approval configuration out
of the readiness path.

For model release, keep the Gompertz baseline provenance visible in the fitted
artifact's `training_config.mapper_source`. Development fitting may use the
deterministic `training_cohort_in_sample` mapper, but the release preflight
requires `supplied` provenance before a production-ready approval can pass;
missing or unknown provenance is blocked. This is a software integrity gate,
not evidence that the mapper or model has been clinically calibrated.

The same preflight blocks a production-ready artifact when its persisted
`training_config.survey_design` is missing, malformed, explicitly
`not_provided`, or declares a `replicate`/`stratum` kind unsupported by the
current adapter. Development artifacts may load without this nested field for
backward compatibility, but they cannot pass the production software gate.

Every predictor loaded into the serving path must implement the same
`ModelAdapterProtocol` method,
`predict_for_assessment(age, encoded_vector)`. The assessment and
external-validation paths pass the persisted 36-column encoded order to that
method; a legacy predictor exposing only raw FI/z-score arguments is rejected.
Keep the readiness matrix and release receipt checks in the release gate when
changing model or panel configuration.

Do not place secrets in `.env` files committed to the repository, demo data,
Pages assets, logs, or model artifacts. TLS termination, rate limiting,
secret storage, firewall/network policy, and process supervision belong at
the deployment boundary.

## 2. Release preflight

Run the checks in this order from a clean, locked environment:

```powershell
uv lock --check
uv run ruff check src tests scripts
uv run ruff format --check src tests scripts
uv run python -m compileall -q src scripts tests
uv run python -m pytest -q
node --check docs/seca-parser.js
node --check docs/site.js
node --test tests/site_parser.test.cjs
uv run python scripts/build_test_receipt.py --check
uv run python scripts/build_demo_data.py --check
uv run python scripts/validate_training_manifest.py docs/TRAINING_MANIFEST_TEMPLATE.json
uv run python scripts/build_external_validation_fixture.py --output examples/external_validation_synthetic.json --check
uv run python scripts/run_external_validation_smoke.py
uv run python scripts/run_training_split_smoke.py
uv run python scripts/validate_model_release.py --model <artifact> --panel <panel> --approval <sidecar>
uv run python scripts/verify_docs.py
uv build --wheel
```

The same non-writing software contract is available through one canonical
entry point:

```powershell
uv run python scripts/verify_project.py
```

This runs the checks above plus the real loopback serving smoke and emits a
human-readable pass/fail summary. `--skip-serving` omits only the HTTP stage;
`--json` emits a bounded machine-readable receipt for an agent or CI wrapper.
The command intentionally reports E-005 as a separate blocked clinical gate.

The Pages workflow runs the same non-writing demo check before uploading
`docs/`. A failed check means the committed `docs/demo-data.json` no longer
matches the current deterministic Python generator; regenerate it through the
script and review the resulting diff rather than hand-editing the JSON.

For the package boundary, install the wheel into an isolated runtime
environment and run `scripts/verify_package_install.py`. Do not treat an
editable checkout import as a substitute for the installed-wheel smoke. The
smoke must cover liveness, a valid assessment, an invalid request, and the
SECA import path.

Also run the loopback HTTP contract smoke from that isolated environment:

```powershell
uv run python scripts/run_serving_contract_smoke.py
```

This starts short-lived Uvicorn processes and checks the development fixture
boundary first. It then creates a temporary, non-clinical
model/reference-panel/approval bundle and starts a strict process with
`FRAILTY_REQUIRE_PRODUCTION=true`. That second stage must report
`loaded_production_ready`, return `/readyz` `200`, enforce the configured API
key, and return typed authenticated responses. Every path is checked for the
response security headers and the synthetic identifier is checked for absence.
The temporary bundle is removed before return. This is a serving/software-gate
integration check only; it is not clinical validation or E-005 approval.

The CI wheel smoke exports the locked `ml` extra because the strict stage fits
and loads a temporary native XGBoost artifact. Run it from the installed-wheel
environment, not from a checkout that happens to resolve `src/`.

Before a real model is promoted, attach the following to the release record:

1. the immutable model artifact and SHA-256;
2. the exact reference-panel file and SHA-256;
3. the populated training manifest and source checksums;
4. the validation report, calibration artifacts, and subgroup denominators;
5. the reviewed cutoff/uncertainty decisions;
6. the matching approval sidecar; and
7. the command receipts and commit/release identifier.

The model-release preflight must be run against those exact three files. It
loads the native artifact and verifies its persisted feature manifest and
artifact hash, verifies the approval sidecar, computes the panel file hash,
and checks the sidecar's panel id/hash plus production and uncertainty flags.
It emits no patient data or absolute paths and exits non-zero for a blocked
software gate. Its `clinical_status` remains
`requires_e005_external_validation_and_clinical_review` even when the software
gate passes; this command is an integrity check, not clinical approval.

The synthetic Pages artifact is a documentation fixture. It must not be used
as a production model or copied into a patient record.

For the evidence work that precedes any production decision, keep the
[`EXTERNAL_VALIDATION_PROTOCOL.md`](EXTERNAL_VALIDATION_PROTOCOL.md) template
with the cohort, model, panel, and release receipts. It defines the freeze
boundary, leakage checks, support denominators, uncertainty and calibration
obligations, sign-off fields, and stop/rollback conditions. It is not an
approval record and does not satisfy E-005.

The committed `examples/external_validation_synthetic.json` fixture and its
runner exercise validation, subgroup coverage, calibration bins, and
support-aware concordance reporting before an approved cohort arrives. The
fixture is deterministically regenerated from its recorded seed and is
explicitly clinical-use forbidden. A passing smoke is software evidence only;
it is not external validation or a performance estimate.

Retain the validation report's `rows_excluded` and aggregated
`row_exclusion_counts` with the cohort receipt. For concordance, retain
`concordance_ci_status` alongside the nullable interval so a reviewer can
distinguish a supported engineering interval from a deliberate withholding
because there were no records, no comparable event pairs, or insufficient
valid bootstrap replicates.
Also retain `concordance_ci_construction`: it is `bootstrap_percentile` only
when the interval was emitted, and `none_withheld` otherwise. Assessment
handoffs use the same explicit construction vocabulary for biological-age and
trajectory intervals. These fields describe implementation mechanics; they do
not establish clinical calibration.

Retain `subgroup_support_warnings` with the report. Each warning names the
observed `dimension` and `label` and uses only the concrete reasons
`no_events`, `no_comparable_pairs`, or `insufficient_valid_replicates`. An
empty list is not evidence that a subgroup is clinically validated, fair, or
safe; it only means that the current computed groups triggered none of those
engineering warnings. Do not add a local numeric clinical minimum to this
software field; record approved thresholds in the study SAP and protocol.

Retain `outcome_metric_status` with the validation receipt. Its named metrics
are intentionally serialized with `value: null`,
`status: "not_implemented_pending_sap"`, and
`construction: "none_withheld"` until the E-005 protocol and approved cohort
are complete. Treat this as a machine-readable withholding state, not as a
zero, estimate, or approval signal.

For training review, `split_survival_rows` creates a deterministic patient-level
fit/holdout boundary using a SHA-256 assignment keyed by an explicit seed and
stratified by event/censor status. Optional `strata=("sex", "age_band")`
preserves those support slices when the cohort is large enough. It rejects
duplicate patient identifiers, reports partition support without exposing
identifiers, and preserves the boundary across repeated runs. This prevents
an accidental row-level leakage pattern in engineering workflows; it does
not choose the final study split or replace a prespecified clinical analysis
plan.

The NHANES mortality adapter normalizes the CDC MEC follow-up field from months
to the model's canonical years before returning a mortality record. Keep
`NHANESColumnMap.duration_unit` at `"years"` when passing those records to
`build_nhanes_rows`; a non-year setting is rejected so a linked duration cannot
be divided by 12 a second time. The setting remains available for a directly
mapped source-row duration when no mortality record is supplied.

The public documentation deployment is defined in
`.github/workflows/pages.yml`. Its verification job runs the evidence-receipt
check and Pages parser tests before the deploy job can upload `docs/`. The
workflow is a static documentation release path; it does not deploy the
assessment API, model artifacts, or patient data.

## 3. Health and readiness checks

`/health` is a liveness and configuration-observability endpoint. It reports
the active model id, panel id, available artifact/panel SHA-256 digests,
readiness status, approval binding state, API-key requirement, request-size
limit, and the current blockers. It also returns a deterministic,
non-secret `deployment_fingerprint`; retain it with the release receipt to
reconcile what is serving. The fingerprint excludes API keys, request bodies,
model parameters, and patient identifiers. It should not be used as the
traffic-admission gate.

`/readyz` is the traffic-admission gate:

- HTTP 200 means the configured software checks passed.
- HTTP 503 means traffic must not be admitted; inspect `blockers`.

`/readyz` includes the same service version, deployment fingerprint, model id
and artifact digest, reference-panel id and digest, production/uncertainty
flags, fixture state, and approval-binding state as non-secret identity fields
so a readiness probe can be joined to the release identity without logging
payload data. `readiness.blockers` remains the status detail; it is safe to
retain because it contains configuration diagnostics rather than payloads or
secrets.
The gate also requires a valid SHA-256 digest for the production-ready model
artifact and reference-panel file. A missing or malformed digest is an
actionable blocker, even when the readiness flags and API key are present.

### Bounded runtime metrics

`/metrics` is a process-local diagnostic endpoint. It exposes only aggregate
request totals, 2xx/3xx/4xx/5xx status-class counts, total and maximum latency,
and oversize-request rejection counts. It intentionally has no route, method,
request-ID, caller, patient, or payload labels, so it cannot become a
high-cardinality or PHI-bearing log substitute. Metrics reset on process
restart and are not a clinical monitoring result; durable aggregation and
alerting belong at the deployment boundary. When `FRAILTY_API_KEY` is
configured, `/metrics` requires the same API-key or Bearer authentication as
the versioned assessment routes. Keep the endpoint internal to the operator
network and expose it to a scraper only through the deployment's access
policy.

```powershell
Invoke-RestMethod http://127.0.0.1:8000/metrics
```

### Runtime release receipt

Capture the running identity after startup, model/panel change, secret
rotation, or rollback. The tool uses only a bounded `GET /health` request and
an explicit allow-list; it does not copy future health fields automatically,
and the receipt contains no credential, request body, endpoint URL, or patient
identifier:

```powershell
uv run python scripts/capture_release_receipt.py --output release-receipt.json
uv run python scripts/capture_release_receipt.py --output release-receipt.json --check
```

The first command refuses to overwrite an existing receipt unless `--force` is
provided. The second command exits non-zero if the stored fingerprint,
artifact/panel identity, readiness state, or safe operational controls differ
from the fresh runtime response. The mismatch output includes the safe
`readiness.blockers` field so operators can see why admission changed. Keep
the receipt with the immutable release record. A source-field-set hash makes
schema additions fail closed until the receipt is deliberately regenerated.
The receipt is an operational reconciliation artifact, not clinical evidence.
Receipt projection also checks semantic consistency: `ready` cannot carry
blockers, `not_ready` cannot have an empty blocker list, a fixture panel cannot
be production-ready, and the top-level/control fixture flags must agree.
Ready health must also identify a production-ready model, validated
uncertainty, valid artifact/panel digests, and API-key protection.

### Runtime-process provenance

`/health` and `/readyz` include a non-secret `runtime_provenance` object with
the installed project package-tree SHA-256, `package_installation_mode`, a
sorted installed-distribution name/version digest, Python implementation and
version, and a digest of the effective runtime settings. The package-tree
digest is not called a wheel hash because an installed process does not retain
the wheel archive; it binds the process to the bytes and relative files
resolved by its distribution. Configuration provenance never stores or hashes
the API key: it records only whether authentication is configured, while path
values are represented by digests.

The isolated-wheel checks require `package_installation_mode:
installed_distribution` and compare the runtime block returned over loopback
HTTP with the importing process. A `source_tree` value is useful for local
development and test diagnostics but is not sufficient for strict production
admission. Keep the provenance fields in the release receipt beside the model
and panel identities; a mismatch indicates software/environment drift and is
not evidence of clinical validity.
The implementation names this distinction explicitly:
`provenance_is_well_formed` checks diagnostic structure, while
`provenance_is_ready_for_strict_admission` also requires installed-distribution
identity. Well-formed does not mean admissible.

After every start, model/panel change, secret rotation, or rollback:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-WebRequest http://127.0.0.1:8000/readyz
```

Confirm that the valid assessment response has the expected model id, panel id,
panel SHA-256 identity when available, readiness metadata, FI denominator and
its nonclinical count-only band, biological-age uncertainty state, and wellness
report. Longitudinal comparisons must use the same panel id; when both
snapshots have a panel SHA-256, that digest must also match. A null digest means
the panel has no file identity and must not be replaced with a fabricated hash.

Then exercise one synthetic or approved test payload and one deliberately
invalid MVV payload. Confirm that the valid response has the expected model id,
panel id, readiness metadata, FI denominator, biological-age uncertainty
state, and wellness report. For the stateless longitudinal route, use two dated
synthetic snapshots for the same identifier and confirm the comparison returns
deltas without echoing the input payload. Never use a real patient payload as a
smoke test.

The Pages `Copy focus list JSON` action uses the versioned
`wellness-focus-areas-v2` handoff. Treat it as a development-only artifact just
like the full improvement-report download: preserve its typed
`action_effect_estimated: false`, `clinical_or_lifespan_claim: false`, and
`model_boundary` fields when passing it to another system. Do not paste a focus
list into a clinical record as if it were a validated recommendation, and do
not remove the panel fixture/readiness fields from the handoff.

## 4. Observability and privacy

The application emits body-free structured request logs containing the HTTP
method, path, request id, status code, and duration. Keep those fields in the
service log stream and attach infrastructure metrics for request rate,
latency, 4xx/5xx rate, 413 rate, readiness transitions, and process restarts.
Do not add request bodies, names, filenames, raw scan values, or free-text
clinical notes to logs.

For an approved monitoring program, aggregate and access-control the following
without retaining raw payloads by default:

- feature missingness and MVV rejection rates;
- FI denominator distribution and FI score distribution;
- BIA z-score and unit-warning rates;
- biological-age interval/uncertainty state;
- model id, panel id, artifact hash, and approval-binding state; and
- subgroup performance or missingness slices approved by the study protocol.

Clinical alert thresholds, drift limits, and subgroup minimums must be set in
the approved monitoring protocol. The repository does not invent those limits
or claim that a passing software metric proves safety, fairness, or benefit.

### API response boundary

Every API response is marked `Cache-Control: no-store` so health, readiness,
metrics, and assessment responses are not retained by an intermediary or
browser cache. The application also sends
`Content-Security-Policy: default-src 'none'; frame-ancestors 'none'`,
`Permissions-Policy: camera=(), geolocation=(), microphone=()`,
`Referrer-Policy: no-referrer`, `X-Content-Type-Options: nosniff`, and
`X-Frame-Options: DENY`. These headers are defense-in-depth, not a substitute
for TLS, ingress policy, authentication, rate limiting, or secret management
at the deployment boundary. Keep the response-header regression test in the
release gate when changing middleware or adding an endpoint.

## 5. Rollback and incident response

Treat the model artifact, approval sidecar, and reference panel as an
immutable, versioned pair. Never overwrite a file in place. To roll back:

1. stop admission at the deployment boundary or route traffic away;
2. select the last known-good artifact/panel/sidecar trio from the release
   record;
3. verify all three SHA-256 values and the sidecar feature/model bindings;
4. update the deployment's versioned configuration or secret references;
5. restart the process under the same production-required settings;
6. require `/readyz` HTTP 200 and run the non-patient smoke payload; and
7. restore traffic gradually while watching errors, latency, missingness, and
   readiness transitions.

Keep the failed release available for forensic review. If `/readyz` returns
503 because of a model/panel/sidecar mismatch, uncertainty state, missing API
key, or non-production fixture, keep traffic blocked and repair the release
record rather than bypassing the check.

For a privacy incident, stop sharing the affected artifact, preserve the
body-free logs, identify whether raw data entered logs or static assets, and
follow the operator's privacy and breach process. The Pages SECA preview is
designed to stay local; it must never be changed into an upload path without a
separate privacy and security review.

Pages also ships `example-seca-tableview.csv` as a clearly labeled synthetic
sample. It is safe for public parser demonstrations, but it must not be
described as a patient record or used as clinical validation data.
The page's JavaScript assets carry a versioned query token; bump that token in
`docs/index.html` with each static JavaScript contract change to avoid serving a
stale parser after a Pages release.

## 6. SECA and wellness workflow boundary

`py -3 -m frailty_engine seca <path>` and the Pages local preview are import
and review tools. They map observed fields, preserve units and derivation
provenance, and show trend information only when at least two dated scans are
available. This includes a descriptive latest-minus-previous segment trend when
the same segment is present in both scans; it is not a clinical asymmetry
threshold or action-effect estimate. A SECA-only export does not supply age, sex, blood values, history,
or functional measures; its `assessment_readiness` checklist must be reviewed
before an assessment workflow.

The Pages preview also exposes a local assessment-intake form. It pre-fills
only the canonical fields observed in the latest scan and requires the user to
enter every remaining MVV field before enabling the overlay download. The
downloaded frailty-assessment-overlay.json can be merged and scored locally
with the assess-overlay CLI subcommand; neither the scan nor the typed values
are uploaded. This is a handoff convenience, not a clinical assessment,
prediction guarantee, or replacement for E-005 approval.

The handoff format is documented in
[`ASSESSMENT_OVERLAY.md`](ASSESSMENT_OVERLAY.md). It requires the versioned
`frailty-engine-assessment-overlay-v1` envelope and nested `measurements` map,
preserves a local pseudonymous `patient_id`, and rejects a manual replacement
of a non-null observed SECA value. The CLI writes the assessment JSON to stdout
and a bounded typed error to stderr: exit `2` means MVV shortfall, exit `3`
means overlay/SECA/measurement validation failure, and exit `4` means another
expected engine failure. An existing overlay identifier wins over the optional
`--patient-id` fallback. Never use a direct identifier in a shared artifact.

The wellness report is an auditable interpretation layer. It provides measured
values, development/reference ranges, status, priority, provenance, missing
inputs, and conservative next steps. It does not estimate whether a suggested
action will change biological age, lifespan, or a clinical outcome.

`wellness_report.focus_areas` is the complete API list of every measured
non-in-range focus item, in the existing deterministic priority/biomarker
order; `summary.focus_areas` is the total count and always equals
`len(focus_areas)`. The Pages demo shows at most five focus bullets by
default, displays a "Showing N of M" count statement, and exposes the
remaining items through a `<details>` disclosure so no actionable area is
hidden. The downloadable `wellness-improvement-report-v1-development.json` always contains
the complete API list.

`POST /v1/assessment-comparisons` is a stateless follow-up view. It accepts two
dated snapshots for the same person, validates chronological order, and returns
derived readout deltas, reference-band transitions, and current focus areas.
The service does not persist either snapshot, and the comparison response must
remain free of the raw input payload. A transition toward a development band is a
descriptive software label, not proof of health improvement or action effect.

## 7. Current blockers

The current checkout intentionally remains development-only because E-005 is
not complete. A clinical reviewer still needs to approve the external cohort,
cutoff decisions, reference panel, uncertainty method, calibration results,
and production artifact before any real-world clinical or prognostic use.

See the [GOAL.md](https://github.com/stancsz/frailty-index-deficit-accumulation-model/blob/main/GOAL.md),
[EVAL.md](https://github.com/stancsz/frailty-index-deficit-accumulation-model/blob/main/EVAL.md),
[MODEL_CARD.md](MODEL_CARD.md), and [MODEL_APPROVAL.md](MODEL_APPROVAL.md) for
the evidence and promotion contracts.
