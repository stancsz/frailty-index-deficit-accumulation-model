# Production roadmap

This roadmap turns the repository goal into the shortest safe path to a client-
usable agent skill. It is ordered by dependency: later stages must not be
treated as complete because an earlier software check is green.

## Current position

The repository is a substantial research-use-only engineering prototype. The
following surfaces are already implemented and covered by automated evidence:

- 35-feature input contract, minimum viable vector (MVV), deterministic
  deficit-accumulation/FI calculation, BIA calibration plumbing, and a
  biological-age response contract;
- optional native XGBoost survival adapter, explicit feature-vector manifest,
  missingness and training-quality receipts, patient-level split controls, and
  external-validation engineering harness;
- local SECA TableView parsing, synthetic Pages examples, wellness report,
  local MVV-gated assessment overlay, and stateless progress comparison;
- typed agent skill instructions, CLI/API serving, fail-closed readiness,
  release identity, runtime provenance, security headers, bounded metrics,
  installed-wheel HTTP smoke, Windows/Linux CI, and privacy/security guidance;
- public evidence documents, model-approval and external-validation templates,
  synthetic fixtures, reproducible artifact checks, and a canonical
  `scripts/verify_project.py` gate.

The critical limitation is intentional: `E-005` remains blocked. No real
external cohort, clinically reviewed cutoffs/reference panel, validated
uncertainty analysis, or human production-model approval is present. The
development predictor and reference panel must not be used for clinical or
real-person longevity decisions.

## Ordered work plan

| ID | Workstream | Status | Depends on | Exit evidence |
|---|---|---|---|---|
| P0 | Publish a clean repository baseline | Complete for publication; license decision open | none | Public GitHub repository contains the intended source, skill, tests, docs, CI, and no patient exports, credentials, or transient workstation files. `main` has a reproducible commit and CI is enabled. An explicit software-license/private-distribution decision remains before external reuse. |
| P1 | Make the software gate fully green | Complete | P0 | `uv run python scripts/verify_project.py --json` returns `status: passed`; Ruff format, Python/Node tests, receipts, docs, artifact checks, and real loopback serving all pass. The output still reports `clinical_gate: E-005 blocked`. |
| P2 | Freeze the agent-skill contract | Mostly implemented | P1 | A clean install can invoke `frailty-engine` or the documented HTTP service from an agent. The skill documents input JSON, MVV failures, output fields, uncertainty semantics, local-only SECA behavior, versioning, and safe error handling. Add a client-facing invocation example and an integration smoke from a fresh environment. |
| P3 | Freeze scientific/data provenance | Partially implemented | P1, P2 | A reviewed training manifest identifies exact NHANES/equivalent files, linkage and endpoint rules, units, quality filters, survey-design/weight semantics, split/tuning boundary, BIA transfer panel, mapper provenance, and checksums. Replace all development fixtures in the candidate release with approved/licensed inputs. |
| P4 | Train and package a candidate model release | Blocked by P3 | P3 | A reproducible native model artifact, 36-column feature manifest, supplied Gompertz mapper, approved reference panel, uncertainty method, model/panel hashes, and human-authored approval sidecar pass `validate_model_release.py`. No artifact is promoted by changing flags alone. |
| P5 | Complete external validation and clinical review (`E-005`) | Blocked | P4 | An approved CLSA or equivalent held-out cohort is evaluated without leakage. The evidence package contains discrimination, censoring-aware horizon calibration, biological-age/homeostatic-deviation calibration, uncertainty, missingness sensitivity, FI denominator sensitivity, clinical utility, and sex/age/ethnicity subgroup support. A qualified clinical/statistical review signs off cutoffs, panel, intended use, limitations, rollback criteria, and production approval. |
| P6 | Harden the deployment boundary | Not started | P5 | The approved artifact is served only from an installed, immutable release. Deployment has TLS, authentication/authorization, secret management, rate limiting, network policy, backups/retention rules, and an operator-owned configuration. `/readyz` is HTTP 200 only for the approved artifact/panel/uncertainty/release receipt and complete runtime provenance. |
| P7 | Run a controlled pilot | Not started | P6 | A limited, consented pilot uses a written SOP, synthetic/non-patient smoke tests, support escalation, access controls, incident handling, monitoring, and rollback. Pilot outputs are framed as wellness/healthspan estimates unless the approved intended-use review says otherwise. No outcome or intervention effect is inferred from before/after changes. |
| P8 | Launch and maintain | Not started | P7 | Versioned releases have signed/retained receipts, changelogs, model/data drift review, missingness and subgroup monitoring, periodic revalidation, security patching, and a documented change-control process. Any model, panel, cutoff, feature, or mapper change re-enters the relevant approval gates. |

## Detailed acceptance criteria

### P0 — Publish a clean repository baseline

1. Decide and add an explicit software license or document the client's private
   distribution terms before external reuse.
2. Stage only project files. Exclude `.venv`, build/wheel smoke directories,
   caches, `.ableton-mcp` failure logs, raw SECA exports, model artifacts,
   downloaded NHANES data, credentials, and patient identifiers.
3. Commit the repository on `main`, push it to
   `https://github.com/stancsz/frailty-index-deficit-accumulation-model`, and
   verify that the public tree contains `skills/frailty-engine/SKILL.md`.
4. Enable/verify Actions and GitHub Pages. Pages may publish only the static
   `docs/` surface and synthetic fixtures; it must never receive patient data
   or the assessment API.

### P1 — Make the software gate fully green

The gate was previously blocked by a Ruff-format issue in
`scripts/verify_docs.py`; that issue is now fixed. Keep the gate green,
regenerate/check the privacy-safe test and demo receipts when inputs change,
then rerun the complete gate from the locked environment. Do not call an
isolated test rerun a full release result.

Required command:

```powershell
uv run python scripts/verify_project.py --json
```

Required interpretation:

- `status: passed` means the software contract is reproducible;
- `clinical_gate: E-005 blocked` must remain visible until P5 is complete;
- a synthetic external-validation report, passing model preflight, or green
  serving smoke is not clinical validation.

### P2 — Freeze the agent-skill contract

The client integration should have one supported path and one explicit
fallback:

- preferred local path: install the locked package and invoke
  `frailty-engine assess` with a JSON request;
- optional service path: call authenticated `POST /v1/assessments` over a
  private, TLS-protected deployment boundary;
- SECA path: parse locally, collect missing MVV values explicitly, and use the
  versioned overlay; never upload or infer missing age, sex, laboratory,
  history, or functional values;
- response path: consume `metrics.biological_age.point_estimate`, FI,
  `homeostatic_deviation_score`, data-quality fields, wellness ranges, model
  boundary, and uncertainty flags without treating them as lifespan, mortality,
  diagnostic, or treatment-effect predictions.

The agent skill must fail closed on missing MVV inputs, development fixtures,
unvalidated uncertainty, model/panel mismatch, and unsafe deployment
configuration. It must never silently substitute a legacy predictor call or
fabricate missing measurements.

### P3 — Freeze scientific/data provenance

The training and validation package must be reviewable without publishing raw
health data. Freeze:

- target population, inclusion/exclusion, age range, sex/ethnicity definitions,
  endpoint, censoring, follow-up unit, and disclosure-control limitations;
- exact source URLs/releases, retrieval dates, file hashes, cycle-specific
  column maps, BIA quality filters, units, derived fields, and missing-value
  sentinels;
- survey-design declaration, weighting and variance plan, optional-feature
  missingness handling, patient-level split, tuning boundary, and sensitivity
  analyses;
- modern SECA reference-panel provenance and transfer-calibration method;
- all FI cutoff sources and each target-population review decision;
- the fixed XGBoost recipe, random seeds, mapper provenance, dependency
  versions, and artifact-generation command.

`docs/TRAINING_MANIFEST_TEMPLATE.json` and
`docs/EXTERNAL_VALIDATION_PROTOCOL.md` are templates and review aids. Filling
them with a plausible-looking value does not constitute approval.

### P4 — Train and package a candidate release

The candidate release is one immutable unit:

```text
model artifact
  + exact 36-column feature manifest
  + supplied reference panel and file hash
  + supplied Gompertz mapper provenance
  + uncertainty method and validation state
  + training/data manifest
  + human approval sidecar
  + release receipt
```

The release preflight must reject development fixture content, missing or
contradictory booleans, unknown mapper provenance, incomplete runtime
provenance, absent hashes, and a sidecar that does not bind to the exact
artifact/panel/feature order. Numeric uncertainty intervals are allowed only
after the uncertainty review has approved their construction and validity.

### P5 — Complete external validation and clinical review

This is the principal production blocker. The reviewer-owned evidence package
must include:

1. cohort identity, governance/consent or permitted-use basis, endpoint and
   censoring definitions, follow-up sufficiency, and patient-level leakage
   checks;
2. model discrimination with uncertainty and transparent denominators;
3. censoring-aware calibration for the approved horizon and the biological-age
   mapping, with a prespecified statistical analysis plan;
4. outcome-level performance and clinical-utility analysis where the intended
   workflow requires it, including prespecified decisions and thresholds;
5. subgroup results for sex, age bands, and ethnicity, with support warnings,
   missingness, events, comparable pairs, and valid replicates reported;
6. sensitivity analyses for native missingness versus complete-case handling,
   FI denominator completeness, BIA transfer assumptions, cutoffs, survey
   weights/variance, and mapper uncertainty;
7. independent review and sign-off for intended use, patient-facing language,
   reference panel, FI cutoffs, uncertainty, failure modes, monitoring, and
   stop/rollback conditions.

Until this package is approved, the product remains research-use-only and the
development predictor/panel cannot produce a production or clinical claim.

### P6–P8 — Deploy, pilot, and maintain

The operations contract already defines readiness, body-free logs, privacy-safe
metrics, release receipts, rollback, and SECA boundaries. Production work adds
the deployment owner's infrastructure controls and a real change-management
process. At minimum, retain:

- immutable release bundles and reproducible environment locks;
- TLS, authenticated access, secret rotation, least privilege, rate limits,
  network allow-lists, and retention/deletion controls;
- aggregate monitoring for availability, latency, errors, oversize requests,
  MVV rejection, missingness, FI denominator, model/panel identity, and
  approved drift/subgroup measures;
- a canary/pilot plan, support and incident contacts, rollback drills, and
  revalidation triggers;
- public documentation that distinguishes software evidence, external clinical
  evidence, and production approval.

## Source-of-truth documents

- [`GOAL.md`](GOAL.md) — product scope, feature contract, safety boundaries,
  and required validation.
- [`EVAL.md`](EVAL.md) — criterion-by-criterion engineering evidence; `E-005`
  is the clinical approval gate.
- [`README.md`](README.md) — quick start and user-facing commands.
- [`skills/frailty-engine/SKILL.md`](skills/frailty-engine/SKILL.md) — agent
  operating contract.
- [`docs/MODEL_CARD.md`](docs/MODEL_CARD.md) — intended use, limitations, and
  current evidence.
- [`docs/EXTERNAL_VALIDATION_PROTOCOL.md`](docs/EXTERNAL_VALIDATION_PROTOCOL.md)
  — future external-validation and clinical-review template.
- [`docs/MODEL_APPROVAL.md`](docs/MODEL_APPROVAL.md) — artifact/panel/sidecar
  promotion gate.
- [`docs/OPERATIONS.md`](docs/OPERATIONS.md) — serving, monitoring, rollback,
  privacy, and SECA handoff.
- [`docs/CLINICAL_ML_EVIDENCE_CROSSWALK.md`](docs/CLINICAL_ML_EVIDENCE_CROSSWALK.md)
  — standards-to-artifact map.

## Definition of production usable

The client can plug the skill into an agent, provide a validated assessment
payload, and receive a deterministic, versioned, privacy-safe age-equivalent
healthspan readout with FI, quality, uncertainty, and wellness context. The
service is reproducible from an immutable release, operationally protected,
documented in the public wiki, and supported by approved external evidence.

The definition is not met by passing software tests alone. It is not met until
P5/E-005 is approved and P6 deployment controls are in place.
