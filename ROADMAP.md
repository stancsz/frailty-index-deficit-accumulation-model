# Production roadmap

This roadmap turns the repository goal into the shortest safe path to a
clinician-first, investor-visible research product. It is ordered by
dependency: later stages must not be treated as complete because an earlier
software check is green.

## Current position

**Current execution priority: VALUE-TOKEN-1, active (frontier-token value measurement).**
Owner: implementation agent with project-owner acceptance. The superseded T1
showcase contract is retained at
`goals/completed/trustworthy-research-showcase/GOAL.md`; the completed
documentation-governance contract is at
`goals/completed/documentation-governance/GOAL.md`; the current active contract
is `goals/active/frontier-value-measurement/GOAL.md`.
The [audit](docs/PROJECT_MATURITY_AND_TRUST_REVIEW.md) and root goal retain
the underlying product and release evidence.
Documentation authority: this roadmap is ordered project guidance below
[`PRODUCT_INTENT.md`](docs/product-specs/PRODUCT_INTENT.md),
[`ARCHITECTURE.md`](ARCHITECTURE.md), and the active execution contract in
[`goals/active/frontier-value-measurement/GOAL.md`](goals/active/frontier-value-measurement/GOAL.md).
It records sequencing and exit evidence; it does not redefine product intent
or clinical approval.
The dated production/value evidence package is
[`docs/PRODUCTION_VALUE_EVIDENCE_2026-09-11.md`](docs/PRODUCTION_VALUE_EVIDENCE_2026-09-11.md).
It records 20/20 canonical software checks, 176 Python tests, 28 Node tests,
and a passing loopback smoke, while explicitly leaving clinical readiness,
intended-user value, and frontier-token savings unverified.
The independent 2026-09-11 review added durable open outcomes to `GOAL.md`.
The immediate VALUE-TOKEN-1 order is: keep the measurement contract
reproducible; obtain owner-supplied matched frontier-run exports; adjudicate
quality and retries; then report a bounded result or a verified no-go. The
local synthetic receipt verifies mechanics only. Clinical-review readiness,
scientific validation, human acceptance, staging, and clinical approval retain
their existing IR dependencies and are not advanced by this token measurement.
Order: reconcile public claims and candidate identity; implement a measurement-first
experience; verify visual/behavior states and human comprehension; publish and
inspect the actual URL. T1 closes only with T1.1-T1.8 evidence and IR0-IR3
acceptance. It operationalizes the existing milestone and preserves IR4-IR7.
M1 is the local reviewer candidate; M2 is verified publication; M3 is human
acceptance. Q0-Q4 and the measurement table in T1 define checkpoint evidence.
All milestones remain open.
The live page was visually inspected and differs materially from local work;
the latest local canonical verifier passes all required software checks, but
neither fact establishes T1 completion.
The local slice now fronts purpose, intended user, synthetic scope, research-only
status and the primary example action, then leads the selected report with an
observed measurement ledger. Local Chromium captures and the current public
claim inventory are retained under `docs/reviews/`; cross-engine reruns and
human acceptance remain open. The per-check local record is
`docs/reviews/trust-maturity-2026-09-10/t1-local-qa-receipt.json`.
After the fresh-preview QA receipt update, the current dirty checkout reran
`uv run python scripts/verify_project.py --json`: all 20 checks passed and
`clinical_gate` remains `E-005 blocked`. This is current local verification,
not same-SHA remote or publication evidence.
The security route and dependency/runtime boundary are now recorded in
`docs/reviews/trust-maturity-2026-09-10/dependency-security-review-2026-09-10.md`;
private GitHub vulnerability reporting is confirmed disabled.
The live publication audit at
`docs/reviews/trust-maturity-2026-09-10/live-publication-audit-2026-09-10.json`
records successful remote workflows for `7fc8fca`, but also records the stale
published wording and missing live claim inventory. T1.6 remains open.
The fresh temporary clean candidate `5dd24112f6582c211b4c93b505db61c2c1e66b26`
also passes locked installation, all 20 verifier checks, documentation checks,
and installed-wheel/loopback HTTP smoke on Windows; the bounded receipt is
`docs/ir0-current-candidate-verification-2026-09-10.json`, with the prepared
freeze record at
`docs/reviews/trust-maturity-2026-09-10/candidate-freeze-manifest-2026-09-10.json`.
The snapshot predates final candidate-reference reconciliation and is not
pushed, published or remotely verified.

The repository is a substantial research-use-only engineering prototype. The
following surfaces have implementation or historical engineering evidence.
This inventory is not a current release pass:

- 35-feature input contract, minimum viable vector (MVV), deterministic
  deficit-accumulation/FI calculation, BIA calibration plumbing, and a
  biological-age response contract;
- optional native XGBoost survival adapter, explicit feature-vector manifest,
  missingness and training-quality receipts, patient-level split controls, and
  external-validation engineering harness;
- local SECA TableView parsing, synthetic Pages examples, wellness report,
  local MVV-gated assessment overlay, and stateless progress comparison;
- deterministic full-body category coverage reports with explicit measured,
  missing, and unavailable states. The target system-age profile is specified
  separately, but numeric domain ages are not yet implemented or validated;
- typed agent skill instructions, CLI/API serving, fail-closed readiness,
  release identity, runtime provenance, security headers, bounded metrics,
  installed-wheel HTTP smoke, Windows/Linux CI, and privacy/security guidance;
- public evidence documents, model-approval and external-validation templates,
  synthetic fixtures, reproducible artifact checks, and a canonical
  `scripts/verify_project.py` gate;
- a clinician-first public GitHub Pages showcase and research report scope,
  with a public-data proof ladder and separate engineering and clinical
  readiness statuses.
- an evidence-informed final report specification for a system-specific
  age-equivalent profile, including chronological-age context, measurement
  provenance, reference-band interpretation, withheld-age behavior, and the
  per-system evidence gate for any future numeric age.
- a recorded product decision baseline: private/proprietary distribution,
  research/wellness use, musculoskeletal-first validation, normative
  age-equivalent semantics, and governed external validation.

The critical limitation is intentional: `E-005` remains blocked. No real
external cohort, clinically reviewed cutoffs/reference panel, validated
uncertainty analysis, or human production-model approval is present. The
development predictor and reference panel must not be used for clinical or
real-person longevity decisions. Public Pages publication is limited to
documentation, synthetic examples, and privacy-safe public-data receipts.

On 2026-09-11, the four planned NHANES 2011-2012 intake files were retrieved
outside the repository and hashed in
`docs/REAL_DATA_INTAKE_RECEIPT_2026-09-11.json`. This makes real source fields
available for reviewed body-composition and muscle/function mapping; it does
not complete IR4 or validate any category. A follow-up intake added real DXA
bone-density, cognitive-testing, full dermatology-questionnaire fields, and a
2003-2004 direct dermatology image-reading file, so every
current category now has a real source field or measured proxy. Joint coverage now
includes arthritis/gout history and adult functional-difficulty items plus an
official 2009-2010 clinical spinal-mobility source with 5,001 records and an
NHANES III fixed-width knee-radiograph source with 2,589 age-eligible records
and bilateral radiographic fields. The source cycles and eligibility boundaries
are explicit rather than silently combined. The same 2009-2010 cycle now also
includes 5,106 ARQ questionnaire records for chronic back or neck pain and
inflammatory-back-pain context. Cycle harmonization,
joint-specific protocols, reference bands, and qualified review remain missing
or unapproved.
The new `scripts/build_category_data_receipt.py` performs the local mapping
check without emitting raw rows or measurements; its 2026-09-11 run verified
17/17 current categories with observed source fields or proxies. The follow-up
mapping adds the official Physical Functioning file's adult walking, standing,
work-limitation, and equipment fields to joint and lifestyle/function coverage,
and adds repeated systolic/diastolic examination readings to cardiovascular and
cardiorespiratory coverage. The latter also now includes baseline spirometry
volume, flow, quality and acceptable-curve fields. Lipid laboratory fields,
sleep duration/disorder fields, and the full depression screener item set have
also been added to their respective categories. Objective wrist-monitor day
summaries are now included for lifestyle/function and sleep, with separate row
and unique-participant counts because each participant can contribute multiple
days. This is source coverage evidence, not clinical validity or category-age
evidence. The companion `scripts/build_category_overlap_receipt.py` now
reports privacy-safe unique-participant coverage and pairwise category overlap
within each survey cycle in
`docs/CATEGORY_OVERLAP_RECEIPT_2026-09-11.json`. It covers five cycles,
including 16 categories with mapped participants in 2011-2012, and deliberately
performs no cross-cycle joins or identifier/measurement emission. This
strengthens participant-level data evidence without claiming a harmonized
clinical cohort. In the 2011-2012 denominator of 9,756 participants, mapped
category coverage ranges from 17.292% to 95.972%, and the all-16-category
intersection is 0 participants. The next data tranche therefore requires
explicit missingness, subsample, and eligibility handling rather than treating
the source catalog as a complete patient dataset.
An additional cycle-specific receipt now covers 17 official 2013–2014 files
for 15 categories, including body, muscle, bone, cognitive, mental-health,
sleep, function, blood, cardiovascular, immune, metabolic, kidney, joint
history, and skin questionnaire data. The category catalog exposes those
sources separately from the 2011–2012 counts. Its receipt records CDC URLs,
hashes, field identities, rows, and participant counts without committing raw
data; fluid/BIA and direct liver elastography remain absent from this cycle.
The primary intake now also has a non-destructive quality receipt for all 17
categories, counting missing rows and candidate special codes without
filtering values. This is the evidence base for the next codebook and
eligibility tranche.
An additional 2015–2016 receipt now covers 15 official files and 15 categories,
including direct body, bone, muscle, skin, blood, cardiovascular, kidney,
metabolic, laboratory liver, sleep, function, and mental-health fields. It
explicitly records the absence of BIA fluid, CFQ cognitive testing, and direct
liver elastography in that cycle. The codebook receipt now covers 81 official
CDC documentation/layout sources across seven source cycles.
The additional 2017–2018 category receipt now covers 18 official files and 15
categories, with BIA fluid and CFQ cognition explicitly absent and direct
liver elastography kept in its separate `LUX_J.XPT` receipt. The full codebook
receipt now covers 96 mapped official documentation/layout sources.
The additional 2021–2023 receipt adds 15 official files for 12 categories and
declares the absent BIA, DXA, grip, cognition, blood-pressure, spirometry, PFQ,
and objective-monitor sources. The full codebook receipt now covers 99 official
documentation/layout sources across eight source cycles.
The recent-cycle overlap receipt reports mapped all-category intersections of
0 across 15 categories in 2013–2014, 1,095 across 15 categories in 2015–2016,
873 in 2017–2018, and 1,360 across 12 categories in 2021–2023,
without emitting identifiers or performing cross-cycle joins.
The new `CATEGORY_NUMERIC_COVERAGE_RECEIPT_2026-09-11.json` verifies
non-missing numeric source fields and positive unique-participant counts for
all 17 categories. Sparse categories remain visible through their minimum
field-level counts; this is source-data coverage, not a harmonized cohort or
clinical validation.
The cycle matrix at `docs/CATEGORY_CYCLE_MATRIX_2026-09-11.json` makes the
boundary auditable: the primary multi-cycle package has all 17 categories,
2013–2014, 2005–2006, 2015–2016, and 2017–2018 have 15 each, 2007–2008 has 13, and 2021–2023 has 12. Declared absences
remain explicit and no cross-cycle joins are performed.
The quality summary at `docs/CATEGORY_QUALITY_SUMMARY_2026-09-11.json` adds
per-category missingness ranges and candidate special-code counts without
filtering values. It makes sparse and dirty fields measurable rather than
presenting source availability as data completeness.
The runtime catalog now exposes `cycle_coverage` for each category, with an
explicit `real_source_present` or `not_collected_in_cycle` state and reason.
This keeps the application from treating omitted source keys as unknown data.
The distribution receipt at `docs/CATEGORY_DISTRIBUTION_RECEIPT_2026-09-11.json`
adds quantiles and unique-participant counts for one real field in every
category. Coded fields remain labeled as source distributions, not reference
intervals.
Runtime category metadata now points each category to its representative
distribution receipt, source file, and field.

## Work-tracking synchronization

Project #4 is authoritative workflow metadata:
https://github.com/users/stancsz/projects/4/views/1

The 2026-09-10 review supersedes the historical P0/P1 completion labels.
Remote CI and Pages still fail at `2f1218b9d20b61ee9682cdae0a5a74dd79a7f653`.
A local dirty-checkout rerun of `uv run python scripts/verify_project.py --json`
now passes all required software checks and reports
`clinical_gate: E-005 blocked`; the linked receipt retains collection metadata
separately from executed-check status. A fresh Windows 3.11 installed-wheel and real
loopback HTTP smoke also passes, with its dirty-tree receipt at
`docs/ir0-wheel-smoke-2026-09-10.json`. A temporary clean snapshot at
`5dd24112f6582c211b4c93b505db61c2c1e66b26` also passes locked installation,
all 20 checks, documentation checks and installed-wheel/real loopback HTTP
smokes on Windows, recorded at
`docs/ir0-current-candidate-verification-2026-09-10.json`. The earlier
`0385ece0d3e65006cc1c58da6b2b015f2e1cd416` receipt retains the separate WSL
Ubuntu evidence. These are local evidence, not a published candidate or
publication result. P0/P1 are reopened for IR0; P2 records the existing contract only. P3/J1 are
constrained by IR4, P4/P5 by IR5, P6 by IR6, and P7/P8 by IR7. R-087 remains
unfinished and is absorbed by IR0/IR3. Board Todo includes blocked work because
the project has no Blocked option. Dependencies here explain the blockers.
The retained desktop publication capture shows the deployed surface still says
`120 / 120 passing` and `v0.1.0 · draft`; it is recorded in
`docs/reviews/trust-maturity-2026-09-10/README.md` and reinforces the open
candidate-identity and publication-reconciliation requirement.

## Current ordered plan, reviewed 2026-09-10

Worker completion review: accept the local software repair milestone only.
An independent rerun passed all 20 verifier checks, but no IR gate is closed.
IR0 still lacks published-candidate and publication evidence. The local Pages
workflow now executes the full Python suite before its evidence and deploy
checks, while the checked-in receipt remains a count receipt rather than a
pass receipt. The current local candidate passes its Windows clean-checkout
gate, but remote verification on that exact candidate remains open. A local
candidate-derived failure branch now records pytest exit 1 with the publication
step unreached, but it is not a remote candidate-branch demonstration.
IR2 retains the denominator regression as a test, while the local comparison
layer now withholds the unsupported aggregate change and reports coverage.
IR1 user-study evidence, IR3 screen-reader/actual-zoom evidence, and IR4-IR7
evidence remain outstanding.
Local Chrome QA now also covers light/dark modes, effective 2x layout
containment, print-to-PDF flow, malformed-import rejection, and page-origin
network privacy. Headed Chrome accessibility-tree review found 119 of 119
interactive controls named, four landmarks, and five polite live regions. Local
Firefox and WebKit checks cover the three target widths,
profile switching, comparison warnings, print reflow, malformed-import
rejection, local-only requests, and page errors. An automated light-theme
computed-style sweep found no failures across 977 visible leaf-text nodes with
a 4.55 minimum ratio. Human screen-reader, actual browser 200% zoom UI,
human contrast/non-color, and IR1 comprehension evidence remain open. See
GOAL.md's worker completion review for the regression and closeout evidence.

This table is the canonical execution order. It supersedes the historical
showcase tranche and P0-P8 sequencing below, which remain background context.
No IR implementation gate was completed by the planning review.

### Next milestone and dependency clarification

Prepare one frozen measurement-only reviewer package under GOAL.md section 7.
Existing local report, comparison repair and receipts are subdeliverables; no
parent IR gate is promoted. Record the selected candidate and any differences
from the temporary snapshot before reusing evidence. Finish remote release
verification while named reviewers perform the five-user study, statistical
review and manual accessibility checks on the frozen local synthetic package.
Public deployment is not a prerequisite for beginning those reviews.

The current local implementation slice is recorded in
`docs/CLAIM_INVENTORY_2026-09-10.md` and
`docs/reviews/trust-maturity-2026-09-10/README.md`. It remains a dirty preview,
not a candidate SHA or published-release result.

For each external blocker, record the missing input, owner role, next action and
review date; named owners and dates remain unassigned until accepted. Continue
independent engineering work. IR4 protocol/data preparation can proceed, but
IR5 fitting and IR7 clinical pilot remain blocked. Defer broader age expansion
and hosted-service work beyond bounded synthetic IR6 preparation until workflow
utility is demonstrated. All original gate acceptance thresholds remain in force.

| ID | Priority | Status | Owner role | Depends on | Exit evidence |
|---|---|---|---|---|---|
| IR0 | 0 | In progress, local gate passes; release blocked | Maintainer | none | Clean candidate SHA passes full Linux/Windows tests, wheel HTTP smokes and publication gate; live identity verified; licensing/visibility wording reconciled. |
| IR1 | 1 | Todo | Product owner and clinician | Frozen local package to start; IR0 for release closeout | One workflow and five-user task study meet GOAL thresholds against current manual workflow. |
| IR2 | 1 | In progress, local contract implemented; reviewer sign-off absent | Engineering and statistician | Draft IR1 contract to start; frozen package for review; IR0 for release | Changing measurement coverage alone cannot imply health improvement; provenance and comparison eligibility tests pass and receive statistical review. |
| IR3 | 1 | In progress, report/static boundary, browser journeys, and manual checklist delivered; automated light-theme contrast sweep passes, human review and user evidence absent | Design and documentation | Draft IR1/IR2 contract to start; their review and IR0 to close | Focused site/report, real browser and accessibility evidence, network privacy checks and user comprehension pass. |
| IR4 | 2 | Todo, qualified owners/data needed | Clinical/data lead and statistician | IR1 | One domain protocol, permitted data, baselines, independent split and prespecified acceptance thresholds approved before fitting. |
| IR5 | 2 | Blocked | ML lead and independent reviewers | IR4 | Reproducible candidate and independent comparative validation; E-005 qualified review remains blocked until approved. |
| IR6 | 2 | In progress, synthetic local review recorded; staging and governance not started | Security/operations and governance | IR2; parallel IR4/IR5 | Staging auth, capacity, monitoring, supply-chain and rollback evidence; real use additionally requires applicable approvals. |
| IR7 | 3 | Blocked | Product, clinical and operations | IR3, IR5/E-005, IR6 | Governed pilot meets frozen utility/safety thresholds and release approval, then monitored release. |

### Next agent objectives, 2026-09-10

These are ordered implementation objectives under the existing single active
T1 contract and IR0-IR7 plan. They are not new clinical-validity claims or
parallel active GDE goals.

| Order | Objective | Agent-deliverable acceptance | Explicit boundary |
|---|---|---|---|
| A | Prepare an IR4 protocol and public-data manifest package | A reviewable, non-approving protocol names one musculoskeletal construct, intended research use, population, predictors, target, comparators, cohort eligibility, missingness, survey design, split boundary, metrics, CI precision and stop rule. A machine-checkable manifest records the chosen public files, release/access terms, URLs, hashes, units, sentinels and weights. | No raw cohort data, fitting, performance result, numeric age or approval claim. Protocol and manifest require clinical/data/statistical review before use. |
| B | Make the reviewer package executable | A prepared synthetic package contains the study script, accessibility checklist, statistical comparison-review worksheet, candidate and fixture identity, evidence links, de-identified result forms, and reviewer-role destinations. The package is ready for named review; release freezing and all human results remain open. | An agent may prepare materials but cannot simulate five users, a screen-reader reviewer, a statistician or a clinician. Missing reviews remain not run. |
| C | Reconcile a final public research release | One owner-authorized candidate SHA has clean-install, verifier, platform-smoke, remote CI, failing-test publication-block and post-deploy identity/hash/link/visual evidence. | This can close T1.6 and IR0 only when every receipt names the same candidate. It does not close E-005 or clinical production. |

The public sources, controlled-access boundary and immediate source-backed inputs
for objective A are recorded in [Wiki 017](docs/wiki/017-public-evidence-inputs-for-remaining-gates.md).
Objective A now has a reviewable, non-approving protocol at
`docs/IR4_MUSCULOSKELETAL_PROTOCOL_2026-09-10.md` and a machine-checkable
planning manifest at `docs/IR4_PUBLIC_DATA_MANIFEST_2026-09-10.json`.
`py -3 -X utf8 scripts/validate_ir4_manifest.py docs/IR4_PUBLIC_DATA_MANIFEST_2026-09-10.json`
passes. The files deliberately retain null source hashes, pending codebook and
survey-design decisions, no reviewers, and `E-005` blocked.
Objective B preparation is also indexed in
`docs/reviews/trust-maturity-2026-09-10/REVIEWER_PACKAGE.md`, with a comparison
worksheet and de-identified result template. The package is review-ready but
not frozen as a release and has no human results.

The full executable acceptance contract is in [GOAL.md section 7](GOAL.md#7-next-steps-and-how-to-verify-them)
and the [industry readiness review](docs/INDUSTRY_READINESS_REVIEW.md).
Named owners remain unassigned; no clinical/statistical sign-off is implied.

## Documentation rule

### North Star alignment, 2026-09-10

- Deliverable: `NORTHSTAR.md`, the durable clinician-first direction and
  decision principles derived from GOAL.md.
- Owner: documentation contributor; dependency: current GOAL.md and IR0-IR7 plan.
- Status: drafted and checked for alignment; no IR gate promoted.
- Exit evidence: the document preserves the musculoskeletal-first workflow,
  IR1 usability targets, comparison integrity, evidence-gated ages, and E-005
  boundary. Wiki entry 013 and Project #4 IR1 carry the same direction.
- Research-release and clinical blockers remain those in the ordered plan above.

`README.md` is the short orientation and usage guide. Verbose operational,
scientific, evidence, and feature-contract material belongs in `docs/` and
`docs/wiki/`, with the README linking to it. New user-facing behavior must
update the relevant wiki entry and keep the README focused on what the project
is, what the model does, and how an agent uses the associated skill.

The public Pages site and research report must remain consistent with the goal,
roadmap, evaluation ledger, README, Wiki, and current product decision record.

## Goal-aligned showcase tranche

The 2026-09-01 goal adds a bounded public-facing tranche ahead of clinical
readiness work:

1. Write `docs/RESEARCH_REPORT.md` for clinicians, researchers, and investors.
   It must explain the workflow, current outputs, evidence, limitations,
   practical usage, public-data proof ladder, and both readiness definitions.
2. Refine `docs/` into a public static showcase with synthetic examples,
   local-only SECA demonstration, source-linked evidence, accessible controls,
   and an unmistakable research-use-only boundary.
3. Extend the evidence package around permitted public data: provenance,
   deterministic intake, reproducible development, patient-level holdout,
   independent public replication where appropriate, subgroup support, and
   uncertainty reporting.
4. Reconcile README, Wiki, EVAL, receipts, and Project #4 before publishing.

R-087 (Trust-pass Pages refresh, EVAL E-087): collapses the front-page evidence index, demotes the bioage readout to a `development only · withheld` disclosure, injects CI build metadata from the checked-in test receipt, corrects the joint description to limited measurement context with a null age, and adds five new unverified assumptions covering cutoff review, reference-panel age/sex banding, Gompertz parameter fitness, subgroup coverage, and the absent joint-specific validation. The clinical evidence gate (E-005) is unchanged; this is documentation-only.

Public-data evidence can advance research readiness and may contribute to a
clinical evidence package when it is independent and appropriate. It cannot by
itself establish clinical validity, transportability, safety, or approval.

## Ordered work plan

| ID | Workstream | Status | Depends on | Exit evidence |
|---|---|---|---|---|
| P0 | Publish a clean repository baseline and public-safe showcase boundary | In progress under IR0: local wording/artifact repair is present; candidate publication and licensing/visibility reconciliation remain open | none | Repository and Pages publication contain only intended source or public-safe static documentation, synthetic fixtures, receipts, and tests. No patient exports, credentials, restricted rows, model artifacts, or API deployment are published. `LICENSE.md` records the private/proprietary source decision; any external source/product use still requires written authorization. |
| P1 | Make the software gate fully green | In progress under IR0: dirty-checkout and temporary clean-candidate verifier plus local Windows wheel/HTTP smoke pass; Linux CI and Pages remain unverified | P0 | `uv run python scripts/verify_project.py --json` returns `status: passed`; Ruff format, Python/Node tests, receipts, docs, artifact checks, and real loopback serving all pass. The output still reports `clinical_gate: E-005 blocked`. |
| P2 | Freeze the agent-skill and full-body reporting contract | Complete for current measurement contract; final system-age shape documented; delivery deferred | P1 | `skills/frailty-engine/SKILL.md` documents the supported CLI/service path, current `category_reports`, uncertainty semantics, local-only SECA behavior, versioning, safe error handling, and withheld-age behavior. [`docs/SYSTEM_AGE_REPORT_SPEC.md`](docs/SYSTEM_AGE_REPORT_SPEC.md) defines the final system-specific age-equivalent profile. The typed API, Pages demo, and installed-wheel smoke expose deterministic measurement profiles, provenance/reference interpretation, safe next steps, and explicit unavailable skin/bone/brain-cognitive sections. Numeric system ages remain withheld until each domain has its own validated model and approval. |
| P3 | Freeze scientific/data provenance and domain measurement protocols | Partially implemented; clinician-first research report, public-data proof ladder, public-source intake map, and a non-approving IR4 protocol/manifest package now exist. No protocol, data manifest, or review is approved. | P1, P2, IR1, IR4 | A reviewed training manifest identifies exact NHANES/equivalent files, linkage and endpoint rules, units, quality filters, survey-design/weight semantics, split/tuning boundary, BIA transfer panel, mapper provenance, and checksums. The research report and public receipts explain what public data prove and do not prove. For each planned system age, add the construct/target, measurement protocol, repeatability plan, reference population, device/unit rules, and missingness policy; `scripts/validate_system_age_manifest.py` mechanically checks this release-review shape and fails closed on numeric-age or approval flags. Replace all development fixtures in the candidate release with approved/licensed inputs. See [Wiki 017](docs/wiki/017-public-evidence-inputs-for-remaining-gates.md), `docs/IR4_MUSCULOSKELETAL_PROTOCOL_2026-09-10.md`, and `docs/IR4_PUBLIC_DATA_MANIFEST_2026-09-10.json`; clinical/data/statistical review remains required. |
| P4 | Train and package candidate overall and system-specific model releases | Blocked by P3 | P3 | A reproducible native model artifact, 36-column feature manifest, supplied Gompertz mapper, and approved reference panel cover the overall model. Any offered system age additionally has a separate domain model, feature/protocol manifest, target, uncertainty method, model/panel hashes, and human-authored approval sidecar that pass `validate_model_release.py`. No artifact is promoted by changing flags alone. |
| P5 | Complete external validation and clinical review (`E-005`) | Blocked | P4 | An approved CLSA or equivalent held-out cohort is evaluated without leakage. The evidence package contains discrimination, censoring-aware horizon calibration, biological-age/homeostatic-deviation calibration, uncertainty, missingness sensitivity, FI denominator sensitivity, clinical utility, and sex/age/ethnicity subgroup support. A qualified clinical/statistical review signs off cutoffs, panel, intended use, limitations, rollback criteria, and production approval. |
| P6 | Harden the deployment boundary | Synthetic local operations review recorded; staging and governance evidence not started | P5 | The approved artifact is served only from an installed, immutable release. Deployment has TLS, authentication/authorization, secret management, rate limiting, network policy, backups/retention rules, and an operator-owned configuration. `/readyz` is HTTP 200 only for the approved artifact/panel/uncertainty/release receipt and complete runtime provenance. |
| P7 | Run a controlled pilot | Not started | P6 | A limited, consented pilot uses a written SOP, synthetic/non-patient smoke tests, support escalation, access controls, incident handling, monitoring, and rollback. Pilot outputs are framed as wellness/healthspan estimates unless the approved intended-use review says otherwise. No outcome or intervention effect is inferred from before/after changes. |
| P8 | Release and maintain | Not started | P7 | Versioned releases have signed/retained receipts, changelogs, model/data drift review, missingness and subgroup monitoring, periodic revalidation, security patching, and a documented change-control process. Any model, panel, cutoff, feature, or mapper change re-enters the relevant approval gates. |

## Detailed acceptance criteria

### P0 — Publish a clean repository baseline

1. Record the private/proprietary distribution terms in `LICENSE.md` and the
   product decision Wiki entry; obtain a separate written agreement before
   external reuse.
2. Stage only project files. Exclude `.venv`, build/wheel smoke directories,
   caches, `.ableton-mcp` failure logs, raw SECA exports, model artifacts,
   downloaded NHANES data, credentials, and patient identifiers.
3. Commit the repository on `main`, push it to
   `https://github.com/stancsz/frailty-index-deficit-accumulation-model`, and
   verify that the public tree contains `skills/frailty-engine/SKILL.md`.
4. Enable/verify Actions and GitHub Pages. Pages may publish only the static
   `docs/` surface and synthetic fixtures; it must never receive patient data
   or the assessment API.

### P1 — Make the software gate fully green

Historical local fixes do not establish current release readiness. The latest
reviewed CI and Pages runs failed. Restore the clean-checkout gate under IR0,
regenerate/check the privacy-safe test and demo receipts when inputs change,
then rerun the complete gate from the locked environment. Do not call an
isolated test rerun a full release result.

Required command:

```powershell
uv run python scripts/verify_project.py --json
```

Required interpretation:

- `status: passed` means the software contract is reproducible;
- `clinical_gate: E-005 blocked` must remain visible until P5 is complete;
- a synthetic external-validation report, passing model preflight, or green
  serving smoke is not clinical validation.

### P2 — Freeze the agent-skill contract

The client integration should have one supported path and one explicit
fallback:

- preferred local path: install the locked package and invoke
  `frailty-engine assess` with a JSON request;
- optional service path: call authenticated `POST /v1/assessments` over a
  private, TLS-protected deployment boundary;
- SECA path: parse locally, collect missing MVV values explicitly, and use the
  versioned overlay; never upload or infer missing age, sex, laboratory,
  history, or functional values;
- response path: consume `metrics.biological_age.point_estimate`, FI,
  `homeostatic_deviation_score`, data-quality fields, wellness ranges, model
  boundary, and uncertainty flags without treating them as lifespan, mortality,
  diagnostic, or treatment-effect predictions.

The agent skill must fail closed on missing MVV inputs, development fixtures,
unvalidated uncertainty, model/panel mismatch, and unsafe deployment
configuration. It must never silently substitute a legacy predictor call or
fabricate missing measurements.

The finished user-facing report is specified in
  [`docs/SYSTEM_AGE_REPORT_SPEC.md`](docs/SYSTEM_AGE_REPORT_SPEC.md). Its required
semantics are:

- chronological age is calculated from date of birth and the assessment
  reference date and is shown as context, not as a biomarker;
- every system card separates observed measurements/provenance,
  age-appropriate reference interpretation, age-report status, and the safe
  next step;
- the displayed number, when approved, is a named system-specific
  age-equivalent estimate with model, target, reference panel, uncertainty,
  repeatability, validation, subgroup, and approval metadata;
- `withheld_unvalidated` is the expected result when any numeric-age evidence
  gate is incomplete; missing measurements are never treated as normal; and
- illustrative values, vendor scores, z-scores, FI values, or a copied overall
  age cannot be relabeled as a system age.

This specification is an end-state product contract, not evidence that the
current development fixtures satisfy E-005.

### P3 — Freeze scientific/data provenance

The training and validation package must be reviewable without publishing raw
health data. Freeze:

- target population, inclusion/exclusion, age range, sex/ethnicity definitions,
  endpoint, censoring, follow-up unit, and disclosure-control limitations;
- exact source URLs/releases, retrieval dates, file hashes, cycle-specific
  column maps, BIA quality filters, units, derived fields, and missing-value
  sentinels;
- survey-design declaration, weighting and variance plan, optional-feature
  missingness handling, patient-level split, tuning boundary, and sensitivity
  analyses;
- modern SECA reference-panel provenance and transfer-calibration method;
- system-specific measurement protocols, domain targets, repeatability,
  reference populations, device/unit handling, and missingness rules for every
  future age card;
- joint-health tranche: confirm whether the intended construct is joint
  function, osteoarthritis burden, imaging severity, or a separately named
  composite; select a repeatable protocol and reference population; and keep
  the card measurement-only until the per-domain evidence gate is complete;
- all FI cutoff sources and each target-population review decision;
- the fixed XGBoost recipe, random seeds, mapper provenance, dependency
  versions, and artifact-generation command.

`docs/TRAINING_MANIFEST_TEMPLATE.json` and
`docs/EXTERNAL_VALIDATION_PROTOCOL.md` are templates and review aids. Filling
them with a plausible-looking value does not constitute approval.

`docs/SYSTEM_AGE_MODEL_MANIFEST_TEMPLATE.json` is the corresponding per-domain
review aid. Run `uv run python scripts/validate_system_age_manifest.py
docs/SYSTEM_AGE_MODEL_MANIFEST_TEMPLATE.json` to check its non-approving shape;
the command does not create evidence, approve a model, or permit numeric ages.

### P4 — Train and package a candidate release

The candidate release is one immutable unit:

```text
model artifact
  + exact 36-column feature manifest
  + supplied reference panel and file hash
  + supplied Gompertz mapper provenance
  + uncertainty method and validation state
  + training/data manifest
  + human approval sidecar
  + release receipt
```

The release preflight must reject development fixture content, missing or
contradictory booleans, unknown mapper provenance, incomplete runtime
provenance, absent hashes, and a sidecar that does not bind to the exact
artifact/panel/feature order. Numeric uncertainty intervals are allowed only
after the uncertainty review has approved their construction and validity.

### P5 — Complete external validation and clinical review

This is the principal production blocker. The reviewer-owned evidence package
must include:

1. cohort identity, governance/consent or permitted-use basis, endpoint and
   censoring definitions, follow-up sufficiency, and patient-level leakage
   checks;
2. model discrimination with uncertainty and transparent denominators;
3. censoring-aware calibration for the approved horizon and the biological-age
   mapping, with a prespecified statistical analysis plan;
4. outcome-level performance and clinical-utility analysis where the intended
   workflow requires it, including prespecified decisions and thresholds;
5. subgroup results for sex, age bands, and ethnicity, with support warnings,
   missingness, events, comparable pairs, and valid replicates reported;
6. sensitivity analyses for native missingness versus complete-case handling,
   FI denominator completeness, BIA transfer assumptions, cutoffs, survey
   weights/variance, and mapper uncertainty;
7. independent review and sign-off for intended use, patient-facing language,
   reference panel, FI cutoffs, uncertainty, failure modes, monitoring, and
   stop/rollback conditions.
8. domain-specific evidence for every system age displayed: construct and
   target, measurement repeatability, reference-panel transportability,
   uncertainty, subgroup support, and evidence that the system age adds useful
   information beyond chronological age and simpler measures.

Until this package is approved, the product remains research-use-only and the
development predictor/panel cannot produce a production or clinical claim.

### P6–P8 — Deploy, pilot, and maintain

The operations contract already defines readiness, body-free logs, privacy-safe
metrics, release receipts, rollback, and SECA boundaries. Production work adds
the deployment owner's infrastructure controls and a real change-management
process. At minimum, retain:

- immutable release bundles and reproducible environment locks;
- TLS, authenticated access, secret rotation, least privilege, rate limits,
  network allow-lists, and retention/deletion controls;
- aggregate monitoring for availability, latency, errors, oversize requests,
  MVV rejection, missingness, FI denominator, model/panel identity, and
  approved drift/subgroup measures;
- a canary/pilot plan, support and incident contacts, rollback drills, and
  revalidation triggers;
- public documentation that distinguishes software evidence, external clinical
  evidence, and production approval.

## Source-of-truth documents

- [`GOAL.md`](GOAL.md) — product scope, feature contract, safety boundaries,
  and required validation.
- [`docs/SYSTEM_AGE_REPORT_SPEC.md`](docs/SYSTEM_AGE_REPORT_SPEC.md) — target
  system-card format, measurement map, and numeric-age evidence gate.
- [`docs/SYSTEM_AGE_MODEL_MANIFEST_TEMPLATE.json`](docs/SYSTEM_AGE_MODEL_MANIFEST_TEMPLATE.json)
  — per-domain protocol, model, uncertainty, validation, subgroup, and approval
  manifest template; it is not a production approval.
- [`docs/wiki/008-product-decisions.md`](docs/wiki/008-product-decisions.md)
  — selected product, distribution, first-domain, measurement, model, and data
  decisions.
- [`LICENSE.md`](LICENSE.md) — private/proprietary distribution notice.
- [`EVAL.md`](EVAL.md) — criterion-by-criterion engineering evidence; `E-005`
  is the clinical approval gate.
- [`README.md`](README.md) — quick start and user-facing commands.
- [`skills/frailty-engine/SKILL.md`](skills/frailty-engine/SKILL.md) — agent
  operating contract.
- [`docs/MODEL_CARD.md`](docs/MODEL_CARD.md) — intended use, limitations, and
  current evidence.
- [`docs/EXTERNAL_VALIDATION_PROTOCOL.md`](docs/EXTERNAL_VALIDATION_PROTOCOL.md)
  — future external-validation and clinical-review template.
- [`docs/MODEL_APPROVAL.md`](docs/MODEL_APPROVAL.md) — artifact/panel/sidecar
  promotion gate.
- [`docs/OPERATIONS.md`](docs/OPERATIONS.md) — serving, monitoring, rollback,
  privacy, and SECA handoff.
- [`docs/CLINICAL_ML_EVIDENCE_CROSSWALK.md`](docs/CLINICAL_ML_EVIDENCE_CROSSWALK.md)
  — standards-to-artifact map.
- [`docs/SYSTEM_AGE_REPORT_SPEC.md`](docs/SYSTEM_AGE_REPORT_SPEC.md)
  — final system-specific age-equivalent report shape and evidence gate.

## Definition of production usable

The client can plug the skill into an agent, provide a validated assessment
payload, and receive a deterministic, versioned, privacy-safe age-equivalent
healthspan readout with FI, quality, uncertainty, and wellness context. The
service is reproducible from an immutable release, operationally protected,
documented in the public wiki, and supported by approved external evidence.

The definition is not met by passing software tests alone. It is not met until
P5/E-005 is approved and P6 deployment controls are in place.
