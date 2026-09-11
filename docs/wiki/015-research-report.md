# 015 - Clinician-first research report

**Status:** current report artifact, 2026-09-10  
**Decision:** publish the bounded measurement-review narrative while keeping
clinical and production claims blocked

## What was delivered

**Measured:** [`docs/RESEARCH_REPORT.md`](../RESEARCH_REPORT.md) now contains
the required executive summary, clinical workflow, 35-feature input contract,
methods, synthetic example boundary, evidence ledger, public-data proof ladder,
limitations, readiness gates, practical usage, roadmap, references, response
schema, status vocabulary, and reproducibility commands.

**Measured:** [`docs/CLINICIAN_WORKFLOW_STUDY.md`](../CLINICIAN_WORKFLOW_STUDY.md)
records the IR1 task script, pass criteria, de-identified evidence form, and
the fact that no participant sessions have been completed.

**Measured:** [`browser-qa-2026-09-10.json`](../browser-qa-2026-09-10.json) records
local Chrome QA at 360, 768, and 1440 pixel viewports, one document heading,
synthetic profile switching, the matched-items-only comparison warning, an
eight-step keyboard focus pass, light/dark modes, effective 2x layout
containment, print-to-PDF flow, malformed-import rejection, and no non-local
page-origin HTTP requests. Local Firefox 144.0.2 and WebKit 26.0 checks add
the same responsive, print, failed-import, local-network, and page-error
evidence. Headed Chrome accessibility-tree review found 119 of 119 interactive
controls named, four landmarks, and five polite live regions. Human
screen-reader and actual browser 200% zoom UI checks remain open.

The retained manual review checklist is
[`ACCESSIBILITY_MANUAL_CHECKLIST_2026-09-10.md`](../ACCESSIBILITY_MANUAL_CHECKLIST_2026-09-10.md).
It records the human rows separately from automated accessibility-tree and
layout evidence; no human sign-off is claimed yet.

**Measured:** [`ir0-wheel-smoke-2026-09-10.json`](../ir0-wheel-smoke-2026-09-10.json)
records a fresh Windows 3.11 installed-wheel and real loopback HTTP smoke from
the current dirty working tree. Health, metrics, assessment, comparison,
invalid-input, local SECA, installed-distribution provenance, development
fail-closed readiness, and the temporary software-gate HTTP contract passed.
This is not a clean candidate or publication receipt.

The local Pages workflow now runs the full Python suite before its evidence and
deploy checks. The local negative-test receipt records pytest exit 1 with the
publication step unreached. Remote execution on a clean candidate and a
candidate-branch failure demonstration remain open.

Current tracking status: IR3 is in progress with the report/static boundary and
Chrome, Firefox, and WebKit rendering and keyboard journeys delivered.
Screen-reader review, actual browser zoom, and the IR1 comprehension study
remain open.

## Evidence boundary

**Method:** The report labels claims as Measured, Method, Evidence-informed, or
Unverified. It identifies the synthetic panel, development predictor, withheld
public age output, local-only SECA path, and E-005 boundary.

**Unverified:** The report does not close IR0, IR1, IR3, IR4, IR5, IR6, IR7, or
E-005. Clean-candidate publication, browser matrix evidence, intended-user
comprehension, approved data, independent validation, and qualified review
remain required.

See [`GOAL.md`](../../GOAL.md), [`ROADMAP.md`](../../ROADMAP.md),
[`EVAL.md`](../../EVAL.md), and the [Project #4 board](https://github.com/users/stancsz/projects/4/views/1).
