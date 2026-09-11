# Industry readiness review

Reviewed 2026-09-10. Decision: research prototype; not a production release.
This is a source, live-site, CI, and targeted behavior review, not clinical
validation or a comprehensive penetration/accessibility audit.

Documentation authority: This dated review follows
[`PRODUCT_INTENT.md`](product-specs/PRODUCT_INTENT.md),
[`ARCHITECTURE.md`](../ARCHITECTURE.md), and the active evidence contract in
[`GOAL.md`](../GOAL.md). It records evidence and gaps; it does not override
the authority layers or establish production readiness.

## Verdict and release strategy

The useful core is structured measurement review: preserve observations, expose
missing data, explain deficit coding, and produce a readable report. The project
has substantial engineering scaffolding, but it has not demonstrated clinician
utility, a validated age model, or a reproducible current public release.
More badges, body-system cards, and standards references will not resolve this.

Release a bounded research workflow first. A clinician should inspect a synthetic
musculoskeletal-focused measurement profile and its provenance, identify missing
inputs, and print a concise report. Keep the full 35-feature assessment behind its
existing MVV contract. A partial measurement preview must not silently become an
assessment. Numeric age development belongs in a separate research surface.
Defer additional domain ages until one domain earns its evidence and utility case.

## Evidence inspected

The reviewed checkout HEAD was `2f1218b9d20b61ee9682cdae0a5a74dd79a7f653`,
with extensive pre-existing modified and untracked files. Local changes are not
released evidence. No existing code or site changes were committed by this review.

| Finding | Evidence and consequence |
|---|---|
| Current release is red | [Verify run 34148730824](https://github.com/stancsz/frailty-index-deficit-accumulation-model/actions/runs/34148730824) and [Pages run 34148730809](https://github.com/stancsz/frailty-index-deficit-accumulation-model/actions/runs/34148730809) failed at the reviewed SHA. Pages references two missing tracked system-age documents that exist only as untracked local files. The category-render assertion also fails in CI. P1 cannot remain unconditionally Complete. |
| Live site differs from local draft | Browser extraction of the [live Pages site](https://stancsz.github.io/frailty-index-deficit-accumulation-model/) shows 120/120 tests, the older guarded-age heading, and twelve technical navigation sections. The repaired local HTML now says 146 Python plus 28 Node tests and withheld age. No matching deployed release identity was established. |
| Visual and information hierarchy need replacement | The live content leads with package internals, a feature matrix, calibration and serving details before the demo. The retained [`published-desktop.jpg`](reviews/trust-maturity-2026-09-10/published-desktop.jpg) captures a 1440 × 1000 desktop surface with `Tests: 120 / 120 passing`, `v0.1.0 · draft`, and the older guarded-age headline. A clinical reviewer needs purpose, example output, limitations and method in that order. The screenshot does not establish native 200% zoom, screen-reader behavior, contrast ratios, print quality, or deployed commit identity. |
| Trust metadata contradicts product decisions | The repaired local `docs/index.html` JSON-LD and license chip now point to `LICENSE.md` and say proprietary distribution; Wiki 008 specifies the same terms. GitHub API reports `isPrivate: false`, so the public repository visibility still requires owner reconciliation. Proprietary licensing and repository visibility are different decisions. Do not change visibility automatically. |
| Test collection is presented as executed evidence | At the time of this review, `.github/workflows/pages.yml` did not require the full Python verification workflow and `scripts/build_test_receipt.py` collected Python tests. The dirty-tree follow-up now adds an executed `pytest` gate and a local negative failure harness; the exact candidate and remote dependency remain unverified. |
| Browser coverage is incomplete | `tests/site_parser.test.cjs` contains useful parser checks and source-string assertions. It does not establish rendered usability, accessibility, browser interoperability or network privacy. |
| Required narrative report is absent | `docs/RESEARCH_REPORT.md` does not exist. The growing EVAL ledger is historical evidence, not a concise current product verdict. |
| Predictor is an integration fixture | `src/frailty_engine/model.py:470-511` computes a deterministic log hazard from FI and BIA deviation. No approved trained model or reference panel is supplied. A Gompertz transformation does not itself validate an age construct. |
| Outcome validation is incomplete | `src/frailty_engine/validation.py:53-121` leaves Brier score, calibration slope, ICI and net benefit unimplemented pending a statistical analysis plan. An evaluation harness and synthetic receipts are not external validation. |
| Longitudinal comparison can confuse data coverage with change | `src/frailty_engine/progress.py:164-212` checks model/panel identity then subtracts aggregate values without requiring comparable FI item sets. In a synthetic balanced profile with BMI set to 31, adding only creatinine=0.9 changed denominator 13 to 14, FI 0.0769 to 0.0714 and development age 44.0 to 43.9. Overlapping measurements were identical. Output labeled the results lower under `same_model_and_reference_panel`. This was reproduced in the current uv environment without modifying source. |
| Product burden and benefit are untested | The MVV requires demographics, BIA, multiple blood tests and history before assessment, while the selected musculoskeletal-first strategy also needs protocols and measurements outside the existing contract. No completed usability or incremental-value evidence was found. |
| Operations remain a plan | P6-P8 are not complete. Operator-owned TLS, access control, retention, monitoring and rollback are documented, not demonstrated as a deployed service. Python >=3.10 support is broader than the 3.11 CI matrix. |

Follow-up verification on 2026-09-10 repaired the stale local receipt and public
count references. The local Pages workflow now executes the full Python suite
before its evidence and deploy checks. The synthetic operations review in
[`docs/IR6_SYNTHETIC_OPERATIONS_REVIEW_2026-09-10.md`](IR6_SYNTHETIC_OPERATIONS_REVIEW_2026-09-10.md)
records the local installed-wheel boundary and the staging controls that remain
open. A local isolated failure harness also
records pytest exit 1 with the publication step unreached. The dirty checkout now passes
`uv run python scripts/verify_project.py --json`: all 20 checks pass, with 146
Python tests, 28 Node tests, and `clinical_gate: E-005 blocked`. A temporary
clean snapshot at `0385ece0d3e65006cc1c58da6b2b015f2e1cd416` also passed
`uv sync --locked --extra dev --extra ml` and the same verifier; see
[`docs/ir0-clean-candidate-verification-2026-09-10.json`](ir0-clean-candidate-verification-2026-09-10.json).
The same candidate also passes installed-wheel and real loopback HTTP smokes on
Windows and WSL Ubuntu.
This does not close IR0. No published candidate, same-SHA Linux CI result,
remote candidate-branch execution, remote CI/Pages result, or live deployment
identity has been established. The local candidate-derived failure branch is
recorded in [`docs/ir0-publication-failure-candidate-2026-09-10.json`](ir0-publication-failure-candidate-2026-09-10.json).

The same dirty-tree follow-up also ran local Firefox 144.0.2 and WebKit 26.0
journeys at 360, 768, and 1440 px. Both engines passed rendering, profile
switching, comparison-warning visibility, light/dark modes, print-only report
output, malformed-import rejection, local-only request checks, and page-error
checks. WebKit headless default keyboard settings did not traverse the skip
link; full keyboard-access settings, screen-reader review, actual browser
200% zoom UI, human contrast review, and the IR1 user study remain open. The
manual checklist is retained in
[`docs/ACCESSIBILITY_MANUAL_CHECKLIST_2026-09-10.md`](ACCESSIBILITY_MANUAL_CHECKLIST_2026-09-10.md).

## Design direction

Use a restrained clinical document style: neutral background, system typography,
consistent spacing, clear table alignment, one accent color and plain status
labels. Reduce the first screen to the intended user, a concrete task, current
research status, and one primary action: view a synthetic example report.
Do not use standards names or test totals as decorative endorsements.

Separate the site into overview, example report, methods/evidence, and developer
documentation. Put file paths, algorithms, API schemas and historical receipts in
the latter two. State limitations once in a prominent summary and again only where
needed to interpret an output. Show unavailable measurements without filling the
main report with speculative body-system cards. Keep the complete coverage matrix
available as a secondary view. Every plotted or printed value needs its unit,
measurement date/source, missingness and interpretation boundary.

## Ordered verification contract

These IDs are shared by GOAL.md, ROADMAP.md and Project #4. Owners below are roles,
not claims that a qualified person has accepted responsibility. Assign named
owners before starting the corresponding gate. Thresholds for usability are
proposed product acceptance criteria, not scientific standards.

| ID | Owner and dependency | Required result and verification |
|---|---|---|
| IR0 | Maintainer; first | Reconcile tracked files, licensing/visibility wording and current status. Preserve unrelated work. From a fresh clone at one candidate SHA, install with `uv sync --locked --extra dev --extra ml`, run `uv run python scripts/verify_project.py --json`, and run both platform wheel/HTTP smokes. Linux, Windows and Pages must pass for the same SHA. Bind deploy to executed tests, then prove a deliberately failing Python test blocks publication on an isolated test branch. Verify live build metadata, asset hashes and links after an authorized deployment. E-005 remains blocked. |
| IR1 | Product owner plus clinician reviewer; IR0 | Define one user, setting, task, minimum available data, report and alternative workflow. Interview at least five intended users; record de-identified task evidence. At least four of five must complete sample selection, find missing inputs, interpret FI correctly and export the report without assistance in five minutes; all must recognize that ages and clinical advice are unvalidated. Compare task time and interpretation errors with their current manual report. Revise scope if utility is not demonstrated; do not recruit patient use through the public demo. |
| IR2 | Engineering plus statistical reviewer; IR0 and IR1 contract | Implement explicit comparison eligibility using item set, coding version, units/protocol, date and model/panel/artifact identity. Test unchanged overlapping values with added/removed normal and abnormal items, changed units/protocol, unknown hashes and changed cutoffs. Withhold unsupported aggregate change or show clearly labeled matched-item change and coverage difference. No improvement interpretation from coverage alone. Preserve MVV rejection and null unsupported ages. Retain reproducible tests and review sign-off. |
| IR3 | Product designer plus documentation owner; IR1 and IR2 report contract | Build the four-part site and research report; reconcile README, metadata, license text and all status claims. Test actual browser journeys in Chromium, Firefox and WebKit at 360, 768 and 1440 px, keyboard-only navigation, 200% zoom, screen reader, light/dark modes, print and failed imports. Target WCAG 2.2 AA; retain automated findings and manual checklist, with no unresolved serious/critical issues or blocked core task. Inspect network traffic for synthetic CSV import and form entry: no measurement data may leave the browser. Repeat IR1 comprehension test and retain screenshots. |
| IR4 | Clinical/data lead plus statistician; IR1 | Freeze one musculoskeletal construct and target before fitting. Distinguish normative age equivalence from outcome prediction. Supply permitted data identity/hashes, protocol, repeatability, cohort eligibility, sample-size rationale, survey design, missingness, independent split and leakage controls. Prespecify numerical acceptance thresholds and confidence interval precision with qualified reviewers before evaluation. Compare against chronological age, FI alone and a simple domain baseline. Use a TRIPOD+AI reporting map; it is a disclosure checklist, not approval. No fitting or performance claims from invented thresholds/data. |
| IR5 | ML lead plus independent statistician/clinical reviewer; IR4 | Train and package a reproducible candidate, then evaluate the frozen model on genuinely independent appropriate data. Report target-appropriate calibration/error, discrimination if outcome-linked, uncertainty coverage, repeatability, subgroup/event/sample denominators, missingness and incremental utility. Implement missing metrics before promising them. Apply prespecified pass/fail rules; retire used holdouts from future tuning claims. If the model does not outperform useful simpler alternatives or age equivalence adds confusion, release measurements only. E-005 requires qualified signed approval, not flags. |
| IR6 | Security/operations owner plus governance lead; IR2, with synthetic staging parallel to IR4/IR5 | Define deployment boundary and risk-based jurisdiction/intended-use review. Prove TLS/auth denial, authorization, request/rate/time limits, secret rotation, dependency scan/SBOM, supported Python matrix, monitoring and incident ownership in staging. Retain timed rollback and restore drills against immutable artifacts. Set capacity, latency and availability targets before load tests. Real-person use requires completed governance and relevant clinical gates; synthetic staging does not. |
| IR7 | Product/clinical/operations owners; IR3, IR5/E-005 and IR6 for clinical pilot | Run a governed limited pilot with predefined success and stop criteria, support ownership, access/retention controls, interpretation-error and workflow monitoring. Review every critical safety incident immediately; stop on material misleading output, data exposure or unapproved release identity. Release only after recorded approval and closeout of material defects. Any model, panel, cutoff or intended-use change reopens affected gates. |

Research showcase acceptance can complete after IR0-IR3 with explicit nonclinical
status. A hosted research deployment also requires IR6 and applicable governance.
Clinical production cannot complete until IR4-IR7 and E-005 are approved. Start
synthetic operational work early; do not leave security discovery until after
model validation. Do not imply that this review authorizes a deployment or patient
pilot.

## Reference basis

[WCAG 2.2](https://www.w3.org/TR/WCAG22/) supplies the accessibility target.
[TRIPOD+AI](https://www.tripod-statement.org/scope/) supplies reporting guidance
for prediction model studies. Neither establishes this product's conformity,
clinical value or regulatory approval. Performance acceptance thresholds require
an intended-use-specific protocol and qualified review.
