# Goal: measure frontier-token value without overclaiming

Status: active
Created: 2026-09-11
Goal ID: VALUE-TOKEN-1
Steward: project owner; contract prepared by Codex
Builder: next implementation agent

## Steward-owned contract

### Outcome

Create a reproducible, privacy-safe measurement package that can prove or
disprove whether this research workflow reduces frontier-model tokens per
successful task. The package must separate the local tool's software behavior
from the external frontier-model usage it may influence.

### Why

The repository currently proves source coverage and software behavior, but it
does not own frontier-provider billing or request accounting. A savings claim
requires matched tasks, a declared baseline, quality outcomes, retries, and
token measurements from the system that owns those calls.

### Source of truth

- [`docs/product-specs/PRODUCT_INTENT.md`](../../../docs/product-specs/PRODUCT_INTENT.md)
  defines the product boundary and evidence classes.
- [`ARCHITECTURE.md`](../../../ARCHITECTURE.md) defines the local system boundary.
- [`docs/PRODUCTION_VALUE_EVIDENCE_2026-09-11.md`](../../../docs/PRODUCTION_VALUE_EVIDENCE_2026-09-11.md)
  defines the current unverified token-savings claim and required measures.
- This file defines the measurement deliverables and their acceptance.

### Acceptance criteria

| ID | Required outcome | Evidence required to pass |
|---|---|---|
| V1 | A measurement schema captures matched task identity, baseline/candidate path, frontier input/output tokens, calls, retries, latency, quality, success, and failure reason. | Versioned schema, validator, and focused tests reject missing, contradictory, or identifying fields. |
| V2 | A local runner produces an aggregate receipt from redacted paired records without emitting prompts, outputs, identifiers, or credentials. | Deterministic fixture run, byte-stable receipt, privacy regression, and CLI `--check`. |
| V3 | Analysis reports frontier tokens per successful task, task success and quality, retries, latency, and uncertainty or a declared reason uncertainty is unavailable. | Executable aggregation with predeclared denominator and confidence-interval behavior. |
| V4 | The external integration boundary is explicit. | Documentation names the required request-correlated export from the frontier-token owner and does not modify sibling repositories or invent live results. |
| V5 | The package makes no savings claim without real paired runs. | Current receipt states `real_paired_runs: false` until owner-supplied data is ingested. |

### Constraints / invariants

- Do not fabricate frontier token counts, quality scores, cost savings, or
  production usage.
- Do not ingest prompts, model outputs, patient data, credentials, or raw
  provider logs into committed artifacts.
- Do not modify sibling repositories. The external integration is an input
  contract only.
- Preserve `clinical_use: forbidden` and `E-005` blocked status.
- A local synthetic fixture may verify mechanics, but cannot prove real value.

### Non-goals

This goal does not deploy a router, alter provider billing, run clinical
studies, claim clinical production readiness, or substitute synthetic tasks for
real frontier-model usage.

### Escalation conditions

Escalate only when real paired frontier-run exports, provider token fields, or
quality adjudication are required. Record the missing input and keep the
measurement status unverified.

## Builder-owned execution record

### Current approach

1. Define a redacted paired-run record and aggregate receipt.
2. Implement deterministic validation and analysis fixtures.
3. Document the request-correlated external export boundary.
4. Run local mechanical verification and retain the explicit real-data gap.

### Progress

- [x] Define and validate the paired-run schema.
- [x] Build the deterministic aggregate receipt and analysis runner.
- [x] Add privacy and contradiction regressions.
- [x] Document the real-run ingestion boundary and update reader guidance/Wiki.
- [x] Run fresh project verification and record the evidence.

### Validation

The schema, deterministic receipt, synthetic mechanics fixture, privacy tests,
and measurement documentation are implemented. The current repository
baseline passes the canonical 20/20 project checks with 176 Python tests and
28 Node tests. The receipt reports `real_paired_runs: false`, so frontier-token
savings remain unverified. The mechanics-only receipt reports five matched
successes from six synthetic tasks and a 35.203366% token difference; this is
not a real provider or production result.

### Remaining gap

Real paired frontier-model runs with provider-owned token accounting and a
predeclared task-quality rubric are still required before a savings result can
be reported.
