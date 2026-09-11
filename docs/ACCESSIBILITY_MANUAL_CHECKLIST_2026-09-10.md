# IR3 accessibility and usability review checklist

**Review date:** 2026-09-10  
**Candidate:** local dirty checkout; no release SHA  
**Status:** partial evidence only; this checklist does not close IR3 or IR1

This checklist separates automated browser evidence from review that must be
performed by a human reviewer. A passing automated row is not a substitute for
the human review rows marked pending.

| Area | Evidence or review action | Current result | Reviewer / date |
|---|---|---|---|
| Responsive layout | Inspect Chromium, Firefox, and WebKit at 360, 768, and 1440 px; confirm no document overflow and one `h1` | Automated evidence recorded in [`browser-qa-2026-09-10.json`](browser-qa-2026-09-10.json). A separate 1440 × 1000 screenshot of the currently published, stale surface is retained in [`reviews/trust-maturity-2026-09-10/`](reviews/trust-maturity-2026-09-10/). | Automated receipt; human visual sign-off pending |
| Keyboard navigation | Tab through the page, confirm a named first focus target, visible focus, skip-link activation, and access to the core synthetic workflow | Automated focus journeys recorded; first focus is the skip link in Chrome and Firefox, and WebKit reaches the synthetic SECA control | Automated receipt; human keyboard sign-off pending |
| Browser zoom | Set the actual browser UI zoom to 200%, then repeat the core workflow and inspect clipping, reflow, focus, and export controls | Pending; effective 2x layout emulation passed, but actual browser zoom UI was not verified | Pending |
| Screen reader | Use a human-operated screen reader to traverse landmarks, headings, form labels, status messages, warnings, dialogs, and report export | Pending; headed Chrome accessibility-tree review found 119 of 119 interactive controls named, four landmarks, and five polite live regions | Pending |
| Color and contrast | Review light and dark modes with a WCAG 2.2 AA contrast tool and inspect meaning that is not conveyed by color alone | Automated light-theme computed-style sweep passed for 977 visible leaf-text nodes with no failures and a minimum ratio of 4.55; dark rendering and semantic token mapping are covered by source checks, but human contrast and non-color review remain pending | Pending |
| Print and export | Print the selected report and confirm report content remains readable and non-report controls are excluded | Automated print-to-PDF check passed | Automated receipt; human print review pending |
| Failed import recovery | Load the malformed synthetic import and confirm a clear status message, retained page usability, and cleared stale details | Automated check passed; no patient data used | Automated receipt |
| Network privacy | Inspect page-origin requests during synthetic import and manual form entry; confirm no measurement data leaves the browser | Automated local-network check passed; browser-extension traffic excluded | Automated receipt; reviewer confirmation pending |
| Core workflow comprehension | Have five intended users select a sample, find missing inputs, interpret FI safely, export the report, and identify unvalidated ages and clinical advice | No sessions recorded; IR1 remains Todo | Pending product owner and clinician reviewer |

## Required closeout record

Before IR3 can close, append the browser/version, operating system, assistive
technology, viewport and zoom settings, task result, defect severity, and
reviewer/date for every manual row. Record screenshots for any visual finding
and link the de-identified IR1 task rows separately. Do not record patient
measurements in this artifact.

## Reproduction references

- Automated receipt: [`browser-qa-2026-09-10.json`](browser-qa-2026-09-10.json)
- Workflow protocol: [`CLINICIAN_WORKFLOW_STUDY.md`](CLINICIAN_WORKFLOW_STUDY.md)
- Acceptance criteria: [`GOAL.md`](../GOAL.md), IR1 and IR3
- Research evidence ledger: [`RESEARCH_REPORT.md`](RESEARCH_REPORT.md)
- Published-surface mismatch artifact: [`reviews/trust-maturity-2026-09-10/README.md`](reviews/trust-maturity-2026-09-10/README.md)
