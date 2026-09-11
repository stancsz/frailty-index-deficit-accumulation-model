# Goal: document the project using Goal-Driven Engineering

Status: done
Created: 2026-09-11
Goal ID: DOCS-GDE-1
Steward: project owner; contract prepared by Codex
Builder: next implementation agent

## Steward-owned contract

### Outcome

Make the entire project documentation set coherent under the
Goal-Driven Engineering model. Product intent, architecture, the project-wide
evidence contract, one active execution goal, implementation evidence, and
reader-facing guidance must have clear authority relationships and must not
make stronger scientific or release claims than the evidence supports.

### Why

The repository has substantial scientific, operational, release, Wiki, and
showcase documentation, but its higher-level product-spec and architecture
layers were implicit. A fresh agent or collaborator should be able to locate
what the project is for, how it is shaped, what is currently being executed,
and which evidence proves each claim without treating historical documents as
active plans.

### Source of truth

- [`docs/product-specs/PRODUCT_INTENT.md`](../../../docs/product-specs/PRODUCT_INTENT.md)
  defines product purpose, users, boundaries, and release meaning.
- [`ARCHITECTURE.md`](../../../ARCHITECTURE.md) defines system shape and durable
  engineering invariants.
- [`docs/DOCUMENTATION_CATALOG.md`](../../../docs/DOCUMENTATION_CATALOG.md)
  inventories the reader-facing and evidence documentation that must defer to
  these authority layers.
- [`GOAL.md`](../../../GOAL.md) defines project-wide evidence obligations.
- This file defines the documentation-governance execution contract.
- `README.md`, `docs/`, and `docs/wiki/` explain the same state to readers and
  may not override the higher authority layers.

### Acceptance criteria

| ID | Required outcome | Evidence required to pass |
|---|---|---|
| D1 | Product intent is explicit | Product spec names audience, outcome, boundaries, evidence classes, and definition of a trustworthy release. |
| D2 | Architecture is explicit | Architecture document records system layers, dependency direction, durable invariants, and verification anchors. |
| D3 | Goal authority is explicit | Root and active goals identify their authority zones, status, acceptance evidence, and remaining gaps; at most one active goal exists. |
| D4 | Reader docs are navigable | README, roadmap, reports, operational/security guidance, and Wiki identify the relevant authority layer and do not contradict it. |
| D5 | Scientific and release claims remain bounded | Documentation continues to distinguish engineering evidence, synthetic fixtures, external validation harnesses, human review, clinical evidence, and publication identity; E-005 remains blocked without approval. |
| D6 | Documentation is mechanically healthy | JSON and Markdown references validate, the canonical verifier and documentation checks pass, and the repository remains recoverable with unrelated work preserved. |

### Constraints and invariants

- Do not invent clinical validation, human review, ownership approval, or
  publication evidence.
- Preserve existing scientific, safety, licensing, privacy, and release
  boundaries.
- Do not create a second planning database below `GOAL.md`.
- Do not delete historical evidence solely to make the documentation appear
  cleaner; classify it as historical or retained evidence instead.
- Preserve user-owned dirty files and do not commit or publish without explicit
  authorization.

### Non-goals

This goal does not refit models, acquire clinical data, perform participant
studies, deploy Pages, change repository visibility, or rewrite scientific
results. It governs documentation structure and consistency around the real
project state.

### Escalation conditions

Escalate only for product-intent decisions, ownership/licensing decisions,
human review, or scientific approval that cannot be inferred from the existing
source of truth. Record the exact missing decision and leave documentation
truthful while it is pending.

## Builder-owned execution record

### Current approach

1. Establish product-intent and architecture authority layers.
2. Reclassify existing root, docs, Wiki, and evidence surfaces by role without
   erasing useful historical material.
3. Add navigation and contradiction checks where practical.
4. Run a fresh documentation and project verification pass.

### Progress

- [x] Read the GDE operating model and audit the existing documentation layout.
- [x] Add `docs/product-specs/PRODUCT_INTENT.md`.
- [x] Add `ARCHITECTURE.md`.
- [x] Add the matching Wiki authority-map entry.
- [x] Supersede the previous blocked showcase goal without deleting its history.
- [x] Complete the first repository-wide documentation authority and navigation
  inventory.
- [x] Reconcile current reader-facing docs, Wiki mirrors, `EVAL.md`, and
  Project #4, while labeling historical and retained evidence explicitly.
- [x] Run the final mechanical verification and acceptance audit for the current
  documentation set.
- [x] Add a dated, evidence-bounded production/value measurement package that
  separates software proof from clinical readiness, user value, and frontier
  token savings.

### Validation

The authority-layer documents are present and the stale root reference that
called the superseded T1 goal active is corrected. `EVAL.md`, reader guidance,
the Wiki mirror, and Project #4 now identify DOCS-GDE-1 as the active
documentation contract and keep T1 historical. The 2026-09-11 evidence package
records a fresh 20/20 canonical verifier pass, 173 Python tests, 28 Node tests,
and a real loopback serving smoke. It records no intended-user study or
frontier-token accounting, so those value claims remain unverified. Historical
receipts and captures retain their original counts but are labeled historical.

### Acceptance audit, 2026-09-11

| Criterion | Current evidence | Result |
|---|---|---|
| D1 Product intent | `docs/product-specs/PRODUCT_INTENT.md` names primary users, outcome, boundaries, evidence classes, and trustworthy-release meaning. | passed |
| D2 Architecture | `ARCHITECTURE.md` records layers, dependency direction, durable invariants, and verification anchors. | passed |
| D3 Goal authority | Exactly one goal file exists under `goals/active/`; root `GOAL.md`, the active goal, and Project #4 identify DOCS-GDE-1, while T1 is historical. | passed |
| D4 Reader navigation | `verify_docs.py` checks authority links and current reader surfaces; Wiki and Project #4 were reconciled. | passed |
| D5 Bounded claims | Current docs retain `clinical_gate: E-005 blocked`, research-use-only boundaries, and explicit missing intended-user and frontier-token evidence. | passed |
| D6 Mechanical health | `verify_docs.py`, its GDE regression, `build_test_receipt.py --check`, and `verify_project.py --json` pass; the latter reports 20/20 checks. | passed |

### Remaining gap

The remaining gaps are external or product-evidence obligations: exact
published-candidate identity, human accessibility review, intended-user study,
frontier-token accounting, and E-005 clinical approval. The underlying product
remains a research prototype and its E-005 clinical gate remains blocked.

### Completion summary

DOCS-GDE-1 is complete. The authority layers, reader guidance, Wiki mirror,
Project #4 record, current test receipt, and mechanical GDE contradiction check
were reconciled and freshly verified. The next execution goal must keep the
same evidence boundary and may not treat this documentation milestone as
clinical, publication, or frontier-token proof.
