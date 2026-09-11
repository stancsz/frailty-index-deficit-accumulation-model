# Product intent

Status: current product boundary
Owner: project steward
Execution contract: [`GOAL.md`](../../GOAL.md)
Architecture: [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
Durable direction: [`NORTHSTAR.md`](../../NORTHSTAR.md)

## Outcome

Build a clinician-first, measurement-first research demonstration that lets a
reviewer inspect synthetic assessments, observed measurements, FI denominator,
missing inputs, provenance, and safe next discussion points. The public surface
must communicate a bounded research prototype, not a clinical service.

## Primary users

Clinicians are the first users. Research collaborators and prospective partners
need an investor-readable evidence trail, but marketing language must not outrun
the evidence.

## Product boundary

The product currently supports deterministic measurement and report behavior,
local SECA parsing, synthetic examples, and a documented development interface.
It does not support diagnosis, treatment decisions, mortality or lifespan
prediction, validated biological age, numeric system ages, patient-data hosting,
or a clinically approved deployment.

## Evidence contract

Every public claim must identify its source, applicability, date or identity,
owner, and evidence class. Engineering checks, synthetic fixtures, public-data
templates, independent validation harnesses, and clinical evidence are separate
classes. Counts collected by a receipt are not a substitute for executed-test
results or human review.

## Definition of a trustworthy release

A release is trustworthy only when the exact published candidate is identified,
the relevant software and artifact checks pass, live assets reconcile to that
candidate, core links work, the research-only boundary is visible, human
accessibility review is recorded, intended-user review is complete, and every
remaining scientific gate is either satisfied by qualified evidence or clearly
blocked. E-005 remains blocked until its approved external-cohort and clinical
and statistical review requirements are met.

## Decision hierarchy

1. This product-intent document defines what the project is for.
2. `ARCHITECTURE.md` defines durable system boundaries and invariants.
3. Root `GOAL.md` defines the project-level evidence contract and ordered gates.
4. One active goal under `goals/active/` defines the current execution cycle.
5. Code, tests, receipts, screenshots, and runtime checks provide evidence.
6. Wiki pages and reports explain the same state for readers; they do not create
   a stronger claim than the source evidence.
