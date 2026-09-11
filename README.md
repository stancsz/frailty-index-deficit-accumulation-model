# Clinical Healthspan & Deficit Accumulation Engine

**Research-use-only — not for clinical use.** This repository does not satisfy
E-005, establish clinical approval, or make lifespan, diagnostic, mortality, or
treatment-effect claims.

**Distribution:** unresolved pending IR0 reconciliation. The source repository
currently reports public visibility while the working product decision retains
private/proprietary wording. External use must follow the reviewed license and
authorization decision. See [`LICENSE.md`](LICENSE.md) and the
[product decision record](docs/wiki/008-product-decisions.md).

## What this project is

This is a Python engine and agent skill for a structured healthspan/wellness
readout. It accepts a 35-feature assessment, enforces a minimum viable vector
(MVV), calculates a deterministic Rockwood-style deficit-accumulation FI, and
exposes a guarded biological-age interface.

The current checkout ships a deterministic predictor and synthetic BIA
reference panel for software integration only. It does not ship an approved
survival model, clinical reference panel, or validated uncertainty analysis.

## What the model does

The engine has two distinct outputs:

- **Current deficit load:** a transparent FI ratio over validly measured
  variables, with its numerator, denominator, and completeness caveat.
- **Age-equivalent development readout:** a biological-age interface whose
  uncertainty is withheld (`ci_95: null`) for the development predictor.

Each assessment also returns a full-body `category_reports` collection. It
groups the available measurements into body composition, fluid/cellular,
muscle, blood, cardiovascular, metabolic, kidney, liver, sleep/recovery,
lifestyle/function, mental-health history, cardiorespiratory,
immune/inflammatory, brain/cognitive, skin, and bone sections. The report
shows measured values, reference-band status, missing measurements, and a
conservative interpretation. Skin, bone, and brain/cognitive are explicitly
unavailable in the current 35-feature contract. Numeric category ages are withheld until each
category has its own approved model, reference panel, uncertainty method, and
review record; the engine never invents an age from an arbitrary formula.

The roadmap target is a richer system-by-system age-equivalent profile
(musculoskeletal, cardiorespiratory, metabolic, inflammatory, cognitive, and
other governed domains). The current release provides the measurement profile
and explicit withheld/unavailable states; see the detailed
[`docs/SYSTEM_AGE_REPORT_SPEC.md`](docs/SYSTEM_AGE_REPORT_SPEC.md).

## Documentation and agent contract

This repository uses Goal-Driven Engineering as its documentation operating
model. Read the authority layers in this order:

1. [`docs/product-specs/PRODUCT_INTENT.md`](docs/product-specs/PRODUCT_INTENT.md)
   for product purpose and boundaries.
2. [`ARCHITECTURE.md`](ARCHITECTURE.md) for system shape and invariants.
3. [`GOAL.md`](GOAL.md) for project-wide evidence and readiness gates.
4. [`goals/active/documentation-governance/GOAL.md`](goals/active/documentation-governance/GOAL.md)
   for the current execution cycle.

The complete documentation inventory and reconciliation rules are in the
[`documentation catalog`](docs/DOCUMENTATION_CATALOG.md).

The reports, operations guides, release receipts, and Wiki mirror these
authorities. Historical receipts are retained evidence, not active plans.

## Use the agent skill

The supported agent contract is [`skills/frailty-engine/SKILL.md`](skills/frailty-engine/SKILL.md).
It explains how an agent should run assessments, import a local SECA export,
complete the MVV overlay, compare follow-up snapshots, inspect category
reports, evaluate an external cohort, and respect the research-use-only
boundary. Read it together with [`GOAL.md`](GOAL.md) and
[`docs/OPERATIONS.md`](docs/OPERATIONS.md) before changing behavior.

## Quick start

```powershell
uv sync --locked --extra dev --extra ml
uv run frailty-engine sample
uv run frailty-engine seca examples/seca_tableview_fixture.csv
uv run python scripts/verify_project.py --json
```

For a local assessment service:

```powershell
uv run uvicorn frailty_engine.api:app
```

Use `POST /v1/assessments` with `{ "patient_id": "local-id", "measurements": { ... } }`.
The response is typed and includes `metrics`, `trajectory`, `wellness_report`,
`category_reports`, data-quality fields, and model/readiness metadata. Missing
MVV inputs return a structured HTTP 422 response; missing values are never
fabricated.

For a local SECA-to-assessment handoff:

```powershell
uv run frailty-engine assess-overlay <path-to-SECA.csv> --overlay frailty-assessment-overlay.json
```

The SECA path is local-only. It never infers age, sex, blood, history, or
functional measurements. See [`docs/ASSESSMENT_OVERLAY.md`](docs/ASSESSMENT_OVERLAY.md).

## Evidence and release status

```powershell
uv run python scripts/verify_project.py --json
```

A passing result is software evidence only. The expected result is
`status: "passed"` with `clinical_gate: "E-005 blocked"`. The synthetic
external-validation report, development predictor, and temporary strict
serving smoke cannot satisfy E-005.

The detailed roadmap is [`ROADMAP.md`](ROADMAP.md). Scientific provenance,
model approval, operations, security, and external-validation details live in
the repository documentation and the [research wiki index](docs/wiki/index.md).
The clinician-first narrative, evidence ledger, limitations, and practical
usage report is [`docs/RESEARCH_REPORT.md`](docs/RESEARCH_REPORT.md). The IR1
study protocol is [`docs/CLINICIAN_WORKFLOW_STUDY.md`](docs/CLINICIAN_WORKFLOW_STUDY.md).
The current public claim inventory, applicability limits, source identities and
evidence status are recorded in
[`docs/CLAIM_INVENTORY_2026-09-10.md`](docs/CLAIM_INVENTORY_2026-09-10.md).
The current full-body report design and its limitations are documented in
[`docs/wiki/005-full-body-category-reports.md`](docs/wiki/005-full-body-category-reports.md).
The finished system-specific age-equivalent profile and its scientific evidence
gate are specified in
[`docs/SYSTEM_AGE_REPORT_SPEC.md`](docs/SYSTEM_AGE_REPORT_SPEC.md).
The verbose local usage and release guide is
[`docs/wiki/006-detailed-user-and-release-guide.md`](docs/wiki/006-detailed-user-and-release-guide.md).

## Development

```powershell
uv run python -m pytest
node --test tests/site_parser.test.cjs
uv run python scripts/verify_docs.py
uv run python scripts/build_demo_data.py --check
```

Do not commit patient exports, credentials, downloaded NHANES files, model
artifacts, or transient workstation directories. See [`SECURITY.md`](SECURITY.md)
and [`CONTRIBUTING.md`](CONTRIBUTING.md).
