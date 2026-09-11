# Documentation catalog

Status: current GDE reconciliation register
Owner: project steward
Last audited: 2026-09-11

This catalog is the inventory and authority map for the project documentation
set. A document listed here is not automatically authoritative. Authority is
determined by the layer below, and reader-facing material must not make a
stronger claim than the layer it mirrors.

## Authority hierarchy

1. **Product intent**: `docs/product-specs/PRODUCT_INTENT.md` and
   `NORTHSTAR.md` define purpose, users, boundaries, and durable direction.
2. **Architecture**: `ARCHITECTURE.md` defines system shape and invariants.
3. **Project evidence contract**: root `GOAL.md`, `ROADMAP.md`, and `EVAL.md`
   define ordered gates and criterion-level evidence.
4. **Execution**: `goals/active/*/GOAL.md` contains the one current execution
   contract. Superseded goals remain historical records.
5. **Evidence**: source, tests, scripts, receipts, screenshots, and runtime
   outputs prove or fail claims. They do not redefine product intent.
6. **Reader guidance**: `README.md`, `docs/`, and `docs/wiki/` explain the
   current state for users and reviewers.

## Root governance and product documents

| Path | GDE role | Authority | Audience |
|---|---|---|---|
| `AGENTS.md` | Repository operating instructions | Process | Agents and maintainers |
| `ARCHITECTURE.md` | Durable system boundaries | Architecture | Engineers and reviewers |
| `docs/product-specs/PRODUCT_INTENT.md` | Product purpose and boundary | Product intent | Steward, agents, collaborators |
| `NORTHSTAR.md` | Durable product direction | Product intent context | Steward and collaborators |
| `GOAL.md` | Project-wide evidence contract | Project contract | All agents and reviewers |
| `ROADMAP.md` | Strategic ordering and exit evidence | Project plan | Maintainers and reviewers |
| `EVAL.md` | Criterion-level evidence status | Evidence contract | Reviewers and release operators |
| `README.md` | Orientation and quick start | Reader guidance | Users and contributors |
| `CONTRIBUTING.md` | Contribution and release rules | Reader guidance | Contributors |
| `LICENSE.md` | License terms | Legal boundary | Users and maintainers |
| `SECURITY.md` | Vulnerability reporting boundary | Security guidance | Reporters and maintainers |
| `skills/frailty-engine/SKILL.md` | Agent usage contract | Tool guidance | Coding agents |
| `goals/active/frontier-value-measurement/GOAL.md` | Current frontier-token value measurement | Active execution | Builder and verifier |
| `goals/completed/documentation-governance/GOAL.md` | Completed documentation migration | Historical execution | Reviewers and future agents |
| `goals/completed/trustworthy-research-showcase/GOAL.md` | Superseded showcase execution | Historical execution | Reviewers and future agents |

## Scientific, product, and operational guidance

These documents are reader guidance or evidence templates. They must defer to
the product boundary, architecture invariants, and root evidence contract.

| Path | Role |
|---|---|
| `docs/RESEARCH_REPORT.md` | Clinician-first methods and limitations |
| `docs/SOURCES.md` | Citation scope and applicability limits |
| `docs/MODEL_CARD.md` | Intended use, model limitations, and promotion boundary |
| `docs/CLINICAL_ML_EVIDENCE_CROSSWALK.md` | Standards-to-artifacts map, not approval |
| `docs/EXTERNAL_VALIDATION_PROTOCOL.md` | Placeholder external-validation protocol |
| `docs/SYSTEM_AGE_REPORT_SPEC.md` | Future system-age contract and evidence gate |
| `docs/ACCESSIBILITY_MANUAL_CHECKLIST_2026-09-10.md` | Human accessibility review protocol |
| `docs/CLINICIAN_WORKFLOW_STUDY.md` | Intended-user study protocol |
| `docs/ASSESSMENT_OVERLAY.md` | Local SECA handoff contract |
| `docs/NHANES_INTAKE.md` | Public-data intake and provenance contract |
| `docs/MODEL_APPROVAL.md` | Hash-bound model approval schema |
| `docs/OPERATIONS.md` | Serving, release, rollback, and privacy operations |
| `docs/PRIVACY_THREAT_MODEL.md` | Privacy and security threat model |
| `docs/INDUSTRY_READINESS_REVIEW.md` | Readiness assessment and open gates |
| `docs/PROJECT_MATURITY_AND_TRUST_REVIEW.md` | Dated maturity and trust audit |
| `docs/IR4_MUSCULOSKELETAL_PROTOCOL_2026-09-10.md` | Non-approving IR4 protocol preparation |
| `docs/IR4_PUBLIC_DATA_MANIFEST_2026-09-10.json` | Public-data manifest preparation |
| `docs/IR6_SYNTHETIC_OPERATIONS_REVIEW_2026-09-10.md` | Synthetic operations review |
| `docs/FRONTIER_TOKEN_MEASUREMENT.md` | Frontier-token measurement protocol and evidence boundary |
| `docs/WORK_LOG_2026-09-11.md` | Dated inventory of completed engineering work and verification |
| `docs/CLAIM_INVENTORY_2026-09-10.md` | Claim-to-evidence inventory |

The dated review package under `docs/reviews/` is retained evidence. Its
`README.md` and `REVIEWER_PACKAGE.md` explain how to interpret the package;
neither file changes the active goal or the E-005 boundary.

## Release, QA, and retained evidence

The following files are receipts, fixtures, templates, or review artifacts.
They are evidence below the goal layer and never independently establish
clinical validity, production readiness, or publication identity.

| Path group | Role |
|---|---|
| `docs/browser-qa-2026-09-10.json` | Automated browser QA receipt |
| `docs/test-receipt.json` and its hash | Test-count receipt metadata |
| `docs/demo-data.json` and its hash | Synthetic public demo artifact |
| `docs/example-seca-tableview.csv` | Synthetic local-import fixture |
| `docs/publication-failure-demo-2026-09-10.json` | Negative publication-path receipt |
| `docs/ir0-*.json` | Historical and current IR0 candidate receipts |
| `docs/reviews/trust-maturity-2026-09-10/` | Candidate, QA, review, security, and live-audit package |
| `docs/SYSTEM_AGE_MODEL_MANIFEST_TEMPLATE.json` | Non-approval model manifest template |
| `docs/TRAINING_MANIFEST_TEMPLATE.json` | Non-approval training manifest template |
| `examples/assessment_overlay_synthetic.json` | Synthetic overlay fixture |
| `examples/external_validation_synthetic.json` | Synthetic validation fixture |
| `examples/external_validation_validation_report.json` | Synthetic validation report |

## Public showcase surface

| Path | Role | Boundary |
|---|---|---|
| `docs/index.html` | Static public evidence showcase | Synthetic, research-use-only |
| `docs/site.js` and `docs/site.css` | Showcase implementation | Must preserve local-only and withheld-output rules |
| `docs/intake-form.js` and `docs/seca-parser.js` | Browser-local intake behavior | No measurement data leaves the browser |
| `docs/assets/` | Static visual assets | Presentation only, not scientific evidence |

## Wiki mirror

`docs/wiki/index.md` is the Wiki index. Entries `001` through `019` are
research, product, release, and evidence guidance. Entry `018` documents this
GDE authority model, and `hits.md` is retained search/evidence material. Wiki
entries are reader guidance and historical decision records; they cannot
override the product spec, architecture, root goal, or active goal.

The public showcase files (`docs/index.html`, `docs/site.js`,
`docs/site.css`, `docs/intake-form.js`, and `docs/seca-parser.js`) are an
implementation surface, not a second product specification. Their visible
copy must remain consistent with the product intent, architecture invariants,
and research-use-only boundary.

## Reconciliation rules

- New product intent starts in the product-spec layer.
- New durable technical boundaries start in `ARCHITECTURE.md`.
- New execution work starts in the single active `GOAL.md`.
- New evidence is retained under code, tests, scripts, or dated review assets
  and linked from the active goal.
- Setup, safety, scientific, operational, or release changes update the
  relevant reader guidance and Wiki mirror.
- Historical or superseded documents stay labeled as such.
- A green local verifier is recorded as software evidence only. E-005 and human
  acceptance remain explicit until their required evidence exists.

## Verification

```powershell
uv run python scripts/verify_docs.py
uv run python scripts/build_test_receipt.py --check
uv run python scripts/verify_project.py --json
```

The completed documentation-governance goal records the prior audit contract.
The active VALUE-TOKEN-1 goal records the remaining frontier-token evidence
gap and its acceptance criteria.
