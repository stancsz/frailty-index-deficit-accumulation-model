# Trust-maturity and T1 local review artifacts

Review date: 2026-09-10. This folder retains a desktop screenshot of the
published Pages surface for the release-identity and trust-maturity review.

Artifact: [`published-desktop.jpg`](published-desktop.jpg)

- Dimensions: 1440 × 1000 pixels, RGB
- SHA-256: `f27f7e6f336071d7b448c92868cc4c689721ac50440dc8706b4c412976f099`
- Observed status ribbon: wellness and healthspan prototype; research-use-only;
  synthetic reference panel; development surrogate
- Observed software badge: `Tests: 120 / 120 passing`
- Observed headline: `A deterministic scoring engine with a guarded
  biological-age model.`
- Observed header metadata: `v0.1.0 · draft`

This is visual evidence that the currently published surface differs from the
dirty local draft, which retains receipt metadata separately from the executed
verifier status and uses the withheld-age contract. It supports keeping IR0
open for candidate identity, publication reconciliation, and live metadata
verification.

## T1 local candidate captures

The following captures were taken from the dirty local static server after the
reviewer-first entry and measurement ledger changes. They are local Chromium
evidence, not a published-release receipt.

The per-check record for this slice is
[`t1-local-qa-receipt.json`](t1-local-qa-receipt.json). It separates local
passes from human, release, and owner actions that were not run.

| State | Dimensions | Artifact | SHA-256 | Observed result |
|---|---:|---|---|---|
| First screen, desktop | 1440 × 900 | [`local-desktop-t1.jpg`](local-desktop-t1.jpg) | `cd6e42a80b9d762f3e4b662f96ebc05eb43e8d6c708fbf712f8ef6eab9864353` | Purpose, intended user, synthetic scope, research-only boundary, and primary example action appear before technical appendices. |
| First screen, mobile | 390 × 844 | [`local-mobile-t1.jpg`](local-mobile-t1.jpg) | `3d3221d8f907bebb177fbae6cd9426ca209ad3dfb8e43ed0a1d8bdb39538215a` | The primary example action is visible in the viewport; document scroll width is 375 CSS px with a 390 CSS px viewport. |
| Selected report, clipped desktop view | 1440 × 900 crop | [`local-report-t1.jpg`](local-report-t1.jpg) | `94e2febfac96ced351eea52c235e04d3eb44139b8afc7d2c20945d55c3f3ded4` | Measurement ledger precedes derived cards and renders FI numerator/denominator, observed coverage, units, missing assessment date, and model/panel provenance. |

Additional state captures from the same local Chromium journey:

- [`local-selected-report-t1.jpg`](local-selected-report-t1.jpg), SHA-256
  `b9e2cf20defd11760714abe16527f0eb317561363f3365e4284682e6901cfc7c`, shows
  the full measurement ledger with the age output withheld.
- [`local-missing-data-t1.jpg`](local-missing-data-t1.jpg), SHA-256
  `08c5006a5edb15247c90fda49a53dcf39b0f1ea6acba6ff8cddc47569495548e`, shows
  the unavailable demo state with report actions disabled.
- [`local-failed-import-t1.jpg`](local-failed-import-t1.jpg), SHA-256
  `47062314a883354b054f4a06dd7c1a8ecd37bf03844ccd0fffcf40b482ef2e89`, shows
  malformed local import rejection with cleared details and an accessible error
  label.
- [`local-comparison-warning-t1.jpg`](local-comparison-warning-t1.jpg), SHA-256
  `d633ca2e19ade28620747527d1e2ccd540402d34cfd0ab25ab3503b4e92339c6`, shows
  the aggregate comparison withheld when model identity is unknown.
- [`local-evidence-t1.jpg`](local-evidence-t1.jpg), SHA-256
  `64d76c62f1a71a562f1481856f7b955ff9904d2d6e93ae2edfc37cc31c5fde41`, shows
  the concise evidence summary and claim-inventory link.

The local browser run also confirmed the page loaded only local assets from the
static server for this journey. A post-change Playwright rerun across Chromium
143, Firefox 144.0.2 and WebKit 26.0 at 360, 768 and 1440 px in light and dark
schemes found no document overflow, a visible primary action, a working demo
anchor and a rendered measurement ledger. Human screen-reader, actual browser
200% zoom, contrast/non-color review, and IR1 comprehension remain open. These
captures do not close T1.2 or T1.7.

The same rerun applied print media and generated
[`local-report-t1.pdf`](local-report-t1.pdf) at 1,172 bytes. The header and
non-report sections were hidden, the selected report remained visible, and the
measurement ledger stayed ahead of derived cards. This is local print evidence,
not a publication artifact.

## Prepared reviewer package

The synthetic reviewer package is ready for named human review but has no human
acceptance result. It includes the workflow protocol, manual accessibility
checklist, comparison worksheet, candidate and fixture identity, and a
de-identified result template:

- [`REVIEWER_PACKAGE.md`](REVIEWER_PACKAGE.md)
- [`comparison-review-worksheet.md`](comparison-review-worksheet.md)
- [`human-review-results-template.json`](human-review-results-template.json)

Automated evidence and software receipts do not substitute for the clinician,
statistical, accessibility, or owner reviews listed in those files.

The screenshot does not prove the deployed commit, current CI result, native
200% browser zoom, screen-reader behavior, contrast ratios, network privacy,
clinical validity, or production readiness. It is a review artifact, not a
release receipt.

## Current live publication audit

The current live URL was fetched after the local T1 wording changes. The latest
remote `main` commit is `7fc8fcab408fa755c9367e04867de0a39f31d98c`; its verify
run `34548964641` and Pages run `34548964642` both succeeded. The live URL
returned HTTP 200, but it is not reconciled with the current dirty checkout:
the deployed page still contains the old local software-receipt wording and
confidence slogans, and `CLAIM_INVENTORY_2026-09-10.md` returns HTTP 404.

The detailed HTTP, asset-hash, content-check, and mismatch receipt is
[`live-publication-audit-2026-09-10.json`](live-publication-audit-2026-09-10.json).
T1.6 therefore remains partial and open pending an owner-authorized candidate
freeze, publication, and live recheck.
**Package status:** retained dated review evidence; not a current release
decision, clinical approval, or active execution plan.
