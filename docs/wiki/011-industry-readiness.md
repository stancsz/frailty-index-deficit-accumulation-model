# 011 - Industry readiness and next release

Status: current planning decision, 2026-09-10. IR0 is in progress; no release
gate is complete.

The project remains a research prototype. The earlier remote CI and Pages
failure remains attached to `2f1218b9d20b61ee9682cdae0a5a74dd79a7f653`, while
later remote verify run `34548964641` and Pages run `34548964642` succeeded for
`7fc8fca`. A 2026-09-10 local dirty-checkout verification now passes all 20
software checks with 146 Python and 28 Node
tests, while a Windows 3.11 installed-wheel/HTTP smoke and local Pages
failure harness also pass. A temporary clean snapshot at
`0385ece0d3e65006cc1c58da6b2b015f2e1cd416` also passes locked installation and
all 20 checks; the receipt is recorded in
[`docs/ir0-clean-candidate-verification-2026-09-10.json`](../ir0-clean-candidate-verification-2026-09-10.json).
The same candidate also passes installed-wheel and real loopback HTTP smokes on
Windows and WSL Ubuntu.
The current temporary clean candidate
`5dd24112f6582c211b4c93b505db61c2c1e66b26` also passes the locked Windows
installation, all 20 verifier checks, documentation checks and installed-wheel/
loopback HTTP smoke; its receipt is
[`docs/ir0-current-candidate-verification-2026-09-10.json`](../ir0-current-candidate-verification-2026-09-10.json).
It remains local-only and does not establish publication.
The local Pages contrast repair also has an automated light-theme sweep with no
failures across 977 visible leaf-text nodes; human contrast and non-color review
remain open.
The retained desktop capture in
[`docs/reviews/trust-maturity-2026-09-10/`](../reviews/trust-maturity-2026-09-10/)
shows the published surface still reporting `120 / 120 passing` and
`v0.1.0 · draft`; this reinforces the open live-identity and publication-
reconciliation requirement and is not a current release receipt.
An `ir0-failure-demo` branch derived from the same candidate also returned
pytest exit 1 before publication; its local receipt is
[`docs/ir0-publication-failure-candidate-2026-09-10.json`](../ir0-publication-failure-candidate-2026-09-10.json).
E-005 remains blocked. The local result and later remote workflow success do
not establish that the current dirty checkout is the published candidate. The
live audit found superseded confidence/test-receipt wording and a 404 for the
current claim inventory, so current publication reconciliation and clinical
readiness remain open.

Prioritize one measurement-review workflow. Preserve observed data, provenance,
missingness, transparent FI and safe comparison. Numeric system ages remain
withheld pending their separate evidence gate. Defer broad domain expansion.

The review reproduced an FI change from adding a normal lab value while all
overlapping values stayed fixed. The local comparison repair now withholds the
unsupported aggregate delta and labels the coverage change; statistical review
is still required before IR2 can close.
The public site also differs from the dirty local draft, and local license
metadata conflicts with the proprietary decision. GitHub currently reports a
public repository; this does not establish an open-source license. IR0 requires
owner reconciliation, not an automatic repository visibility change.

The dependency/runtime review was refreshed for temporary candidate
`5dd24112f6582c211b4c93b505db61c2c1e66b26`: the installed-wheel and loopback
smoke passed on Python 3.13.11, and the current ephemeral `pip-audit 2.10.1`
run reported no known third-party Python vulnerabilities. This remains local
engineering evidence; the project distribution, JavaScript surface, SBOM and
hosted deployment are outside that audit.

Execution order: IR0 release integrity; IR1 workflow proof; IR2 comparison
integrity; IR3 site and documentation; IR4 protocol and data; IR5 independent
model validation; IR6 operational evidence; IR7 governed pilot and release.
The clinician-first research report and study protocol now exist, but the user
study and browser evidence are still open. The synthetic operations review is
recorded in [`docs/IR6_SYNTHETIC_OPERATIONS_REVIEW_2026-09-10.md`](../IR6_SYNTHETIC_OPERATIONS_REVIEW_2026-09-10.md),
but staging and governance evidence remain open. Synthetic operational work can proceed before clinical approval. The local Pages workflow now executes the full Python suite before evidence and deploy checks. Real clinical
deployment cannot. Named role owners remain to be assigned.

The complete acceptance criteria below are mirrored from GOAL.md. ROADMAP.md
owns statuses and dependencies; Project #4 records the same workflow. This entry
supersedes older Wiki completion claims wherever current evidence contradicts them.

| ID | Owner and dependency | Required result and verification |
|---|---|---|
| IR0 | Maintainer; first | Reconcile tracked files, licensing/visibility wording and current status. Preserve unrelated work. From a fresh clone at one candidate SHA, install with `uv sync --locked --extra dev --extra ml`, run `uv run python scripts/verify_project.py --json`, and run both platform wheel/HTTP smokes. Linux, Windows and Pages must pass for the same SHA. Bind deploy to executed tests, then prove a deliberately failing Python test blocks publication on an isolated test branch. Verify live build metadata, asset hashes and links after an authorized deployment. E-005 remains blocked. The fresh temporary clean candidate `5dd24112f6582c211b4c93b505db61c2c1e66b26` passes the locked Windows installation, all 20 checks, documentation checks and installed-wheel/HTTP smoke; its freeze manifest records that it predates final reference reconciliation and the candidate remains unauthorized. Remote verify and Pages later succeeded for `7fc8fca`, but remote same-SHA Linux evidence, remote failure-branch execution, authorized publication and live reconciliation remain open. |
| IR1 | Product owner plus clinician reviewer; IR0 | Define one user, setting, task, minimum available data, report and alternative workflow. Interview at least five intended users; record de-identified task evidence. At least four of five must complete sample selection, find missing inputs, interpret FI correctly and export the report without assistance in five minutes; all must recognize that ages and clinical advice are unvalidated. Compare task time and interpretation errors with their current manual report. Revise scope if utility is not demonstrated; do not recruit patient use through the public demo. |
| IR2 | Engineering plus statistical reviewer; IR0 and IR1 contract | Implement explicit comparison eligibility using item set, coding version, units/protocol, date and model/panel/artifact identity. Test unchanged overlapping values with added/removed normal and abnormal items, changed units/protocol, unknown hashes and changed cutoffs. Withhold unsupported aggregate change or show clearly labeled matched-item change and coverage difference. No improvement interpretation from coverage alone. Preserve MVV rejection and null unsupported ages. Retain reproducible tests and review sign-off. |
| IR3 | Product designer plus documentation owner; IR1 and IR2 report contract | Build the four-part site and research report; reconcile README, metadata, license text and all status claims. Test actual browser journeys in Chromium, Firefox and WebKit at 360, 768 and 1440 px, keyboard-only navigation, 200% zoom, screen reader, light/dark modes, print and failed imports. Target WCAG 2.2 AA; retain automated findings and manual checklist, with no unresolved serious/critical issues or blocked core task. Inspect network traffic for synthetic CSV import and form entry: no measurement data may leave the browser. Repeat IR1 comprehension test and retain screenshots. |
| IR4 | Clinical/data lead plus statistician; IR1 | Freeze one musculoskeletal construct and target before fitting. Distinguish normative age equivalence from outcome prediction. Supply permitted data identity/hashes, protocol, repeatability, cohort eligibility, sample-size rationale, survey design, missingness, independent split and leakage controls. Prespecify numerical acceptance thresholds and confidence interval precision with qualified reviewers before evaluation. Compare against chronological age, FI alone and a simple domain baseline. Use a TRIPOD+AI reporting map; it is a disclosure checklist, not approval. No fitting or performance claims from invented thresholds/data. |
| IR5 | ML lead plus independent statistician/clinical reviewer; IR4 | Train and package a reproducible candidate, then evaluate the frozen model on genuinely independent appropriate data. Report target-appropriate calibration/error, discrimination if outcome-linked, uncertainty coverage, repeatability, subgroup/event/sample denominators, missingness and incremental utility. Implement missing metrics before promising them. Apply prespecified pass/fail rules; retire used holdouts from future tuning claims. If the model does not outperform useful simpler alternatives or age equivalence adds confusion, release measurements only. E-005 requires qualified signed approval, not flags. |
| IR6 | Security/operations owner plus governance lead; IR2, with synthetic staging parallel to IR4/IR5 | Define deployment boundary and risk-based jurisdiction/intended-use review. Prove TLS/auth denial, authorization, request/rate/time limits, secret rotation, dependency scan/SBOM, supported Python matrix, monitoring and incident ownership in staging. Retain timed rollback and restore drills against immutable artifacts. Set capacity, latency and availability targets before load tests. Real-person use requires completed governance and relevant clinical gates; synthetic staging does not. |
| IR7 | Product/clinical/operations owners; IR3, IR5/E-005 and IR6 for clinical pilot | Run a governed limited pilot with predefined success and stop criteria, support ownership, access/retention controls, interpretation-error and workflow monitoring. Review every critical safety incident immediately; stop on material misleading output, data exposure or unapproved release identity. Release only after recorded approval and closeout of material defects. Any model, panel, cutoff or intended-use change reopens affected gates. |


See [review](../INDUSTRY_READINESS_REVIEW.md), [goal](../../GOAL.md), [roadmap](../../ROADMAP.md), and [Project #4](https://github.com/users/stancsz/projects/4/views/1).

## Next milestone: measurement-only reviewer package

Freeze a synthetic local package with the report, comparison warnings, export
and review checklist. The existing report, comparison repair and local receipts
are subdeliverables, not completed IR gates. Bind evidence to the selected
candidate; later edits are not certified by the temporary snapshot.

Run remote IR0 verification and human IR1-IR3 review in parallel. The five-user
study, statistical comparison review and manual accessibility checks can start
on the frozen local package before public deployment. Final showcase release
still requires IR0-IR3 to pass. Assign named reviewers and dates; for each
blocker record its missing input, owner role and next action. Assignments remain
unaccepted until confirmed. Prepare IR4 protocol/data work, retain IR5/IR7
blocks, and defer broader age expansion and hosted-service work beyond bounded
synthetic IR6 preparation until workflow utility is demonstrated. Preserve all
existing acceptance thresholds; missing human evidence cannot be replaced by
additional automated checks. GOAL.md section 7 and ROADMAP.md define the plan.

