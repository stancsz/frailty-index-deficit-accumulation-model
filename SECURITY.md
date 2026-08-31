# Security Policy

Status: development-serving artifact. This repository is a wellness and
healthspan engineering prototype, not a certified medical device, a production
clinical service, or a regulated product. Nothing here claims HIPAA, GDPR, ISO
27001/27799, NIST 800-53, NIST AI RMF, HITRUST, SOC 2, MDR, FDA, Health Canada,
or any equivalent conformance, and nothing here establishes clinical
effectiveness, treatment benefit, fairness, or calibration. A passing software
check is an integrity check, not clinical approval; the E-005 external-cohort
and clinical-review gate remains the binding promotion boundary. See the
[privacy threat model](docs/PRIVACY_THREAT_MODEL.md) and
[operations runbook](docs/OPERATIONS.md) for the detailed boundaries.

## 1. Supported versions and development-only status

The repository currently ships one development line at the version recorded in
`pyproject.toml` (`0.1.0`). The default reference panel is a synthetic
development fixture and the shipped predictor is a deterministic development
predictor that does not carry `uncertainty_validated: true`. There is no
long-term support branch, no backported security patch lane, and no committed
response-time service-level agreement.

Security fixes are landed on `main` through normal review and CI. Deployment
owners who mirror a release are responsible for picking up those changes; the
project does not maintain parallel patch releases for older tags. Production
admission is fail-closed: starting Uvicorn with
`FRAILTY_REQUIRE_PRODUCTION=true` blocks traffic until the model artifact,
approval sidecar, reference panel, uncertainty validation, and API-key boundary
are all present and pass their hash bindings.

## 2. Reporting a suspected vulnerability

Keep patient data, raw SECA scans, credentials, API keys, model artifacts,
internal hostnames, and detailed exploit material out of public issues,
pull-request comments, Discussions, and GitHub Actions logs. Anything shared
there may become visible to a broader audience than intended and is difficult
to retract.

The preferred private channel is GitHub's private vulnerability reporting for
this repository, if maintainers have enabled “Report a security vulnerability”
under the repository's Security tab. If that path is unavailable, contact the
maintainer through a private channel documented on their GitHub profile. Do not
invent an email address for this project. If no private maintainer channel is
clearly available, open a minimal, non-revealing issue asking for a secure
point of contact and wait for a private reply before sharing technical detail.

When reporting, share what you observed, the affected component or commit, the
impact, and a short reproduction sketch. Strip identifiers, raw measurements,
filenames, and bearer tokens before sending. There is no guaranteed response
window or pre-committed disclosure timeline; this is a volunteer-maintained
prototype, not a commercial security-response program.

## 3. Supported software and dependency surface

The supported repository surface is a Python package and a static
documentation/demo site:

- Python 3.10+ with runtime dependencies declared in `pyproject.toml` and
  resolved through `uv.lock`; optional ML, validation, data, and development
  dependencies are also declared there.
- FastAPI serving from `src/frailty_engine/api.py`, including
  `POST /v1/assessments`, `POST /v1/assessment-comparisons`, `GET /health`,
  `GET /readyz`, and `GET /metrics`.
- Node-only static parsing and rendering under `docs/`, exercised by
  `tests/site_parser.test.cjs`.
- GitHub Actions verification and Pages workflows under `.github/workflows/`.
  Jobs use read-only repository permissions by default; the Pages deploy job
  grants only the Pages and OIDC permissions required for deployment.

Anything outside this list is a deployment component—such as a reverse proxy,
secret manager, identity provider, CI image, or third-party Pages mirror—that
the deployment owner must review separately.

## 4. Security-sensitive change checklist

Before requesting review on a change that can leak data, weaken a gate, or
change a public contract, confirm that:

- Logs still contain method, path, request ID, status code, and duration only;
  no request body, filename, patient identifier, raw measurement, chained
  exception text, or payload-derived free text is logged.
- `/metrics` exposes only totals, fixed status classes, total and maximum
  latency, and oversize-rejection counts; no high-cardinality label is added.
- API-key middleware still covers `/v1/*` and `/metrics`, uses a constant-time
  comparison, and returns a bounded 401 envelope when a key is configured.
- The streaming body cap and `Content-Length` check still enforce
  `FRAILTY_MAX_REQUEST_BYTES` and return HTTP 413 with `Retry-After: 1` before
  normal body parsing.
- API responses retain `Cache-Control: no-store` and the restrictive
  `Content-Security-Policy`, `Permissions-Policy`, `Referrer-Policy`,
  `X-Content-Type-Options`, and `X-Frame-Options` headers; these are
  defense-in-depth and do not replace TLS or deployment access controls.
- Invalid or oversized supplied `X-Request-ID` values remain replaced by a
  generated bounded ID; they must never be logged verbatim.
- Reference-panel booleans remain strict, fixture content cannot be promoted
  by metadata edits, and release preflight keeps artifact/panel/sidecar hashes
  bound together.
- Assessment and longitudinal responses retain typed panel state,
  `uncertainty_validated`, `action_effect_estimated: false`, and
  `clinical_or_lifespan_claim: false`; unvalidated `ci_95` remains `null`.
- JavaScript contract changes bump the versioned query token and update the
  browser tests; `build_demo_data.py --check`, `verify_docs.py`, and
  `build_test_receipt.py --check` still pass.
- No real patient export, named SECA scan, or identifiable test corpus is
  added to `docs/`, `examples/`, fixtures, generated artifacts, or history.
- No claim of HIPAA, GDPR, ISO, NIST, FDA, Health Canada, MDR, or other
  regulatory or clinical-performance conformance is introduced.

## 5. Model, panel, and release-artifact integrity

The release unit is the XGBoost artifact, approved reference-panel JSON, and
human-authored approval sidecar. `scripts/validate_model_release.py` verifies
the artifact hash, 36-column encoded feature manifest, panel file SHA-256,
sidecar panel binding, production flags, and explicit `supplied` Gompertz
mapper provenance. It refuses a ready result when a check fails and retains
`clinical_status: requires_e005_external_validation_and_clinical_review` even
when the software gate passes.

`scripts/capture_release_receipt.py` obtains a bounded `GET /health`, projects
an explicit allow-list, and refuses silent receipt replacement. The source
field-set hash causes a new health field to fail reconciliation until the
receipt is deliberately regenerated. Treat the artifact, sidecar, panel, and
receipt as reviewable release records; do not edit them in place.

## 6. SECA and GitHub Pages privacy boundary

The Pages site is static, dependency-free, served from `docs/`, and deployed
only after the evidence and parser checks pass. It does not load remote fonts,
analytics, or third-party scripts. The SECA preview reads the visitor's chosen
CSV through `FileReader`, writes a local normalized summary only on explicit
action, and never uploads the file, original filename, or patient identifier.
The committed `docs/example-seca-tableview.csv` is a synthetic two-scan fixture
and must not be relabeled as a real record.

The Pages preview is not an upload path. Turning it into one requires a
separate privacy and security review, not only a code change.

## 7. Deployment-owner controls

The repository does not implement TLS termination, HSTS, certificate
management, network policy, ingress allow-listing, secret management or
rotation, rate limiting, concurrent-connection limits, process supervision,
durable metric aggregation, alerting, authorization over logs and receipts, or
tenant-specific data-handling rules. Those controls live at the deployment
boundary and remain the deployment owner's responsibility.

Treat `FRAILTY_API_KEY` as a deployment secret. Keep it, the model artifact,
approval sidecar, and reference panel in controlled storage; bind the API key,
terminate TLS, and restrict the service before exposing it beyond loopback.

## 8. Incident triage

The deployment owner owns clinical, legal, and breach-notification duties.
Recommended first moves for a security report are:

1. Stop admission at the deployment boundary; do not rely solely on the
   in-process API key if the boundary is suspect.
2. Preserve body-free logs, release receipts, and before/after deployment
   fingerprints without editing the model, panel, or sidecar in place.
3. Check whether raw payload data entered logs or static assets, and confirm
   body-free logging and local-only Pages behavior.
4. Rotate the API key and any affected deployment secret.
5. Re-run `scripts/validate_model_release.py` and reconcile the runtime receipt
   with `scripts/capture_release_receipt.py --check`.
6. Inspect `/health`, `/readyz`, and `readiness.blockers`; do not restore
   traffic while a release-integrity blocker remains.
7. Restore traffic gradually while watching aggregate errors, latency,
   oversize rejections, and readiness transitions.
8. Record the event through the deployment's privacy, security, and clinical
   incident process. This document does not define notification scope or a
   response SLA.

## 9. Explicit non-goals

- Compliance attestation of any kind.
- Clinical effectiveness, calibration, transportability, fairness, safety, or
  treatment-benefit claims.
- A guaranteed response SLA, coordinated-disclosure timeline, or paid security
  response channel.
- Long-term support, backported security patches, or an LTS branch for older
  versions.
- Replacement for deployment review, a data-use agreement, an IRB or ethics
  review, a prespecified statistical analysis plan, or institutional approval.

See [PRIVACY_THREAT_MODEL.md](docs/PRIVACY_THREAT_MODEL.md) for the
cross-surface privacy/security review boundary and [OPERATIONS.md](docs/OPERATIONS.md)
for the runbook, release preflight, and rollback contract.
