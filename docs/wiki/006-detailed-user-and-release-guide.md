# 006 — Detailed user and release guide

- **scope:** verbose operational and usage material intentionally kept out of
  the short README, reviewed 2026-08-31.
- **status:** current engineering guide; production and clinical gates remain
  operator/reviewer-owned.

## Start locally

```powershell
uv sync --locked --extra dev --extra ml
uv run frailty-engine sample
uv run uvicorn frailty_engine.api:app
```

The development process uses the deterministic predictor and synthetic BIA
panel. `GET /health` is liveness. `GET /readyz` is the admission probe and is
expected to return HTTP 503 for the development fixture. Do not expose the
development process to patient or production traffic.

## Assessment paths

The preferred local path is the installed CLI:

```powershell
uv run frailty-engine assess request.json
```

The service path is authenticated `POST /v1/assessments` behind a private,
TLS-protected deployment boundary. Set `FRAILTY_API_KEY` for the API-key
boundary and review `FRAILTY_MAX_REQUEST_BYTES`. The response contains the FI,
overall age-equivalent development readout, wellness ranges, and
`category_reports`; category coverage and missingness must be shown before an
agent interprets any value.

The local SECA path is:

```powershell
uv run frailty-engine seca examples/seca_tableview_fixture.csv
uv run frailty-engine assess-overlay <path-to-SECA.csv> --overlay <overlay.json>
```

SECA data stays local. The importer may derive only supported body-composition
fields from the same scan; it never infers age, sex, labs, history, or function.
The Pages overlay keeps observed scan fields read-only and requires missing MVV
fields to be entered explicitly. See
[`005-full-body-category-reports.md`](005-full-body-category-reports.md) and
[`../../docs/ASSESSMENT_OVERLAY.md`](../../docs/ASSESSMENT_OVERLAY.md).

## What the agent may say

The skill at [`../../skills/frailty-engine/SKILL.md`](../../skills/frailty-engine/SKILL.md)
is the agent-facing contract. It may describe measured values, engineering
reference-band direction, data completeness, FI context, and conservative next
steps. It must preserve the no-action-effect and no-clinical/lifespan-claim
flags.

The overall biological age is an age-equivalent wellness interface, not a
lifespan prediction. Category reports currently provide measurement coverage
and a typed age-report shell. Numeric category ages remain withheld until a
category-specific model, reference panel, uncertainty method, held-out
validation, subgroup analysis, and human approval are present. Missing skin and
bone measurements are unavailable, not normal.

## Verification

Run the complete software gate from the locked environment:

```powershell
uv run python scripts/verify_project.py --json
```

The expected software result is `status: "passed"` with
`clinical_gate: "E-005 blocked"`. The gate covers Python and Node tests,
artifact receipts, manifest and validation smokes, documentation, and the
loopback serving contract. It does not establish clinical validity.

For a release-path check, CI also builds a wheel, installs it in an isolated
environment, and runs `scripts/verify_package_install.py` plus the real HTTP
smoke. The wheel smoke confirms packaging and runtime identity; it is not
clinical evidence.

## Training and validation

`docs/TRAINING_MANIFEST_TEMPLATE.json` records the required source, linkage,
units, missingness, survey-design, split, recipe, mapper, reference-panel, and
hash fields. It is a template, not a populated approval record. Use the
NHANES intake review and training helpers only with an explicitly reviewed
cycle map and permitted data.

The external-validation harness and
[`docs/EXTERNAL_VALIDATION_PROTOCOL.md`](../../docs/EXTERNAL_VALIDATION_PROTOCOL.md)
define the future evidence package. Synthetic fixtures are useful for
reproducibility and are marked clinical-use-forbidden. They cannot satisfy
E-005.

## Production boundary

Before production, an operator must provide an immutable model artifact, exact
feature manifest, approved reference panel, hash-bound approval sidecar,
validated uncertainty, TLS, authentication/authorization, secret management,
rate limiting, network policy, retention controls, monitoring, rollback, and
incident procedures. The implementation documents these boundaries in
[`../../docs/OPERATIONS.md`](../../docs/OPERATIONS.md),
[`../../SECURITY.md`](../../SECURITY.md), and
[`../../docs/MODEL_APPROVAL.md`](../../docs/MODEL_APPROVAL.md).

E-005 additionally requires an approved external cohort, cutoff and panel
review, uncertainty and subgroup evidence, clinical utility where applicable,
and qualified sign-off. No local smoke, synthetic report, or metadata flag can
replace that evidence.
