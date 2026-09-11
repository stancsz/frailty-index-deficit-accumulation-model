# T1 reviewer package

**Package status:** prepared for named human review; no human review has been
completed and no acceptance decision is recorded.

**Software candidate used by the local receipt:** temporary candidate
`5dd24112f6582c211b4c93b505db61c2c1e66b26`.

This package is a synthetic, research-only review aid. It is not a clinical
study, patient workflow, production release, or substitute for IR0, IR1, IR2,
IR3, or E-005. Do not add patient exports, credentials, raw identifiers, or
unapproved cohort data.

## Start here

1. Read the active contract in
   [`goals/completed/trustworthy-research-showcase/GOAL.md`](../../../goals/completed/trustworthy-research-showcase/GOAL.md).
2. Use the synthetic fixture
   [`docs/demo-data.json`](../../demo-data.json) and verify its SHA-256 against
   `c2ff76eb5fd1d8eac7926d54a79959254ada7be13d4b7aac53820be4659f1e7d`.
3. Run the existing workflow protocol in
   [`docs/CLINICIAN_WORKFLOW_STUDY.md`](../../CLINICIAN_WORKFLOW_STUDY.md).
4. Complete the statistical comparison worksheet in
   [`comparison-review-worksheet.md`](comparison-review-worksheet.md).
5. Record only de-identified study observations in
   [`human-review-results-template.json`](human-review-results-template.json).
6. Complete the manual rows in
   [`docs/ACCESSIBILITY_MANUAL_CHECKLIST_2026-09-10.md`](../../ACCESSIBILITY_MANUAL_CHECKLIST_2026-09-10.md).

## Evidence already available

- Local browser and state receipt:
  [`t1-local-qa-receipt.json`](t1-local-qa-receipt.json)
- Cross-engine automated receipt:
  [`browser-qa-2026-09-10.json`](../../browser-qa-2026-09-10.json)
- Claim inventory:
  [`CLAIM_INVENTORY_2026-09-10.md`](../../CLAIM_INVENTORY_2026-09-10.md)
- Current local candidate software receipt:
  [`ir0-current-candidate-verification-2026-09-10.json`](../../ir0-current-candidate-verification-2026-09-10.json)
- Dependency and security boundary:
  [`dependency-security-review-2026-09-10.md`](dependency-security-review-2026-09-10.md)
- Live publication mismatch:
  [`live-publication-audit-2026-09-10.json`](live-publication-audit-2026-09-10.json)

These receipts separate automated local evidence from human review, publication
identity, owner decisions, and clinical approval. They do not turn a local
preview into a release.

## Required reviewer roles

| Review | Required role | Current state | Required evidence destination |
|---|---|---|---|
| Workflow and first-screen comprehension | Product owner plus clinician or intended-user reviewer | Not run | `human-review-results-template.json` and the study protocol |
| Comparison interpretation | Qualified statistician plus domain reviewer | Not run | `comparison-review-worksheet.md` and de-identified decision record |
| Keyboard and browser zoom | Accessibility reviewer | Automated evidence only; human review pending | `ACCESSIBILITY_MANUAL_CHECKLIST_2026-09-10.md` |
| Screen reader, contrast, and non-color meaning | Accessibility reviewer using assistive technology | Not run | `ACCESSIBILITY_MANUAL_CHECKLIST_2026-09-10.md` |
| Release terms and ownership | Project owner or maintainer | Not accepted | Root `GOAL.md`, `ROADMAP.md`, and Project #4 |

## Required closeout

The package is ready for review, not accepted. A reviewer must record the
candidate identity, environment, date, actual observation, defect severity,
decision, and follow-up owner. If the candidate or synthetic fixture changes,
discard the result rows and repeat the affected review. Human thresholds cannot
be met by automated screenshots, accessibility-tree counts, or software tests.
