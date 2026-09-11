# Goal: a trustworthy published measurement-review showcase

Status: active  
Created: 2026-09-10  
Goal ID: T1  
Steward: project owner; contract prepared by Codex  
Builder: next implementation agent  
Acceptance reviewers: project owner plus clinician, statistical and accessibility reviewers; named assignments pending

## Steward-owned contract

### Outcome

Publish one coherent, measurement-first research demonstration that a clinician
can understand, inspect and use with synthetic examples. Its visual design,
copy, reports and evidence must communicate the same bounded capability.
Visitors must see the verified release, not a stale page behind a newer local
report. This goal establishes public research-showcase quality, not clinical
validity, a hosted patient service or general product-market fit.

### Why

The user wants a mature and trustworthy experience without generic AI-written
marketing or an overwhelming wall of qualifications. The baseline inspection
found an older live page, mobile overflow, prominent unsupported development
age output, and a local first screen dominated by citations and metadata.
Passing software tests did not detect or resolve these product problems.

### Source of truth

- [Root GOAL](../../../GOAL.md) retains the scientific and release invariants.
- [NORTHSTAR](../../../NORTHSTAR.md) defines the durable product direction.
- [ROADMAP](../../../ROADMAP.md) owns ordered project work and IR dependencies.
- [Maturity and trust audit](../../../docs/PROJECT_MATURITY_AND_TRUST_REVIEW.md)
  records current evidence, comparable references, screenshots and limitations.
- [Research report](../../../docs/RESEARCH_REPORT.md) describes the method.
- [Project #4](https://github.com/users/stancsz/projects/4/views/1) mirrors status.

This is the single active execution goal. It makes the existing IR0-IR3
reviewer-package milestone concrete; it does not replace or pass those gates.
IR4-IR7 remain separate scientific and operational obligations.

### Acceptance criteria

| ID | Required outcome | Evidence required to pass |
|---|---|---|
| T1.1 | One understandable first screen | At desktop 1440x900 and mobile 390x844, the purpose, intended user, research-only status and primary synthetic-example action are visible before technical appendices. No citation code block, test-count billboard or full evidence history precedes that explanation. A first-time reviewer can reach the example in one action. |
| T1.2 | A restrained, usable visual system | Personally inspect rendered overview, selected report, missing-data state, failed import, comparison warning, evidence view and print/export. Retain screenshots at 360, 768 and 1440 px for Chromium, Firefox and WebKit, with light/dark support where offered. No document-level horizontal overflow, clipped controls or unreadably compressed text. Wide tables may scroll inside labeled containers. Record keyboard, actual 200% browser zoom, screen-reader, contrast and non-color checks; meet the existing IR3 accessibility gate. |
| T1.3 | Every public claim is traceable and internally consistent | Maintain a current claim inventory with page/output, claim, source or receipt, applicability, source identity, date, owner and measured/method/evidence-informed/unverified status. Zero unresolved contradictions about ages, test passes, data provenance, license, readiness or deployment. Replace historical pass-count prose and self-assigned confidence slogans with concise current evidence. Archive history outside the main journey. Collection counts must never stand in for executed-test evidence. |
| T1.4 | The synthetic report earns its prominence | Put observed measurements, units, dates/provenance, FI numerator/denominator and missingness before optional technical details. Withhold unsupported ages in page, downloaded artifact and print. Do not make large unavailable-age cards the primary value proposition. Verify all profiles, SECA synthetic load, malformed import, MVV rejection, coverage-only comparison regression and export against the canonical output. Labels say synthetic, without suggesting anonymized patient provenance. |
| T1.5 | Evidence and ownership can be inspected | From the first screen, evidence and project ownership/contact are each reachable within two actions. The report, methods, limitations, evaluation terms and reporting route resolve successfully. Each clinical/method citation says what it supports here and what it does not. Verify the actual security-reporting route; do not imply GitHub private reporting is enabled when it is disabled. Do not invent credentials, affiliations, testimonials or approval. |
| T1.6 | The exact published release is verified | Preserve unrelated work, freeze intended files at one candidate SHA, run locked clean installation, full verifier, supported-platform wheel/HTTP checks and remote CI. Verify the deliberately failing test blocks the real publication path. After authorized deployment, record URL, timestamp, commit/build identity and asset hashes; check core links and visually inspect live desktop/mobile again. Existing snapshot receipts do not certify later edits. IR0 must pass before this criterion closes. |
| T1.7 | Intended users understand and complete the workflow | Retain the IR1 five-user study: at least four of five complete sample selection, missing-input identification, correct FI interpretation and export independently in five minutes; all five correctly identify that age outputs are unvalidated or withheld and the tool does not provide approved clinical advice. Compare time/errors with the manual workflow. Add a 30-second first-screen check: at least four of five identify purpose and intended user, and all five identify research-only status. Record misunderstandings and revise before accepting. These are product targets, not demonstrated results. |
| T1.8 | Repository handoff and claims match the product | README installation and example path work from the final clean candidate; documentation, package runtime-support claims, license/evaluation terms and published artifacts agree. Record a dependency/security review and supported-runtime evidence or narrow unsupported claims. Keep static-site checks distinct from future service controls. Root GOAL, ROADMAP, Wiki and Project #4 agree; no unresolved high-impact misleading claim or blocked core task remains. |

Visual acceptance includes human judgment. A reviewer records observations about
hierarchy, readability, consistency, information density and credibility, with
screenshots and concrete defects. A subjective "not AI-generated" score or an
automated screenshot/DOM pass alone cannot close T1.2 or T1.7. Do not infer how
a page was authored from its appearance.

### Achievable milestones and measurements

These are checkpoints inside this goal, not additional active goals. Complete
M1 without waiting for recruitment or clinical data; work on reviewer scheduling
in parallel. Missing M2/M3 evidence does not erase a verified M1 result.

| Milestone | Can proceed with | Exit measurement | State at goal creation |
|---|---|---|---|
| M1: reviewable local candidate | Current synthetic fixtures, source and local browser tools | T1.1, T1.3-T1.5 local implementation passes; automated and agent visual portion of T1.2 passes; every remaining human/release check listed explicitly. Retain candidate identity, claim inventory, screenshots and QA receipt. | Not passed; baseline audit only |
| M2: verified publication | M1, owner-approved terms/contact and authorized publish path | T1.6 passes; zero failed core links, live assets match approved hashes, no unsupported numeric ages in public outputs, no unresolved critical/high-impact defect in core tasks. | Not passed; current live version differs |
| M3: accepted research showcase | Frozen package, assigned reviewers and five intended users | T1.2 human checks, T1.7 and T1.8 pass; all T1 criteria and applicable IR0-IR3 closeout evidence approved. | Not passed; reviewers/results pending |

| Measure | Baseline from audit | Target and measurement method |
|---|---|---|
| Live source identity | HTML matches older `35e3e14`; no injected build identity | Candidate SHA and live metadata/hash agreement for all deployed core assets; save HTTP/hash receipt after release |
| Mobile page overflow | Published client width 390, scroll width 740 | `scrollWidth <= clientWidth + 1` at 360, 390, 768 and 1440 CSS px for core states; separately inspect nested-table scrolling |
| Time to first useful action | Local desktop demo begins around y=7704 | Primary synthetic-example action visible on first screen and usable in one action; screenshot plus click journey |
| Public claim contradictions | Age/export, test-count and provenance wording conflicts found | Zero unresolved contradictions in a reviewed claim inventory covering page, report, download, print and README |
| Evidence links | Live research report and linked main LICENSE return 404 | All core links return intended content, not merely HTTP 200; verify every method/report/contact/evaluation link and local anchor |
| Data/output integrity | Local guards exist; live age output differs | All three synthetic profiles and exported/printed fields match the canonical public artifact; unsupported ages remain null/withheld |
| Software regression | Baseline full local verifier 20/20 | Required verifier checks all pass on final candidate; record executed commands and exit codes, never only collected counts |
| Comprehension and task success | No participant outcomes recorded | Existing 4/5 within five minutes and 5/5 boundary recognition, plus T1.7 first-screen check; retain de-identified results |

### QA gates and retained checks

1. **Q0: candidate and claim freeze.** Record `git status --short`,
   `git rev-parse HEAD`, intended changed paths and SHA-256 hashes of core public
   assets. Distinguish dirty preview from immutable candidate. Enumerate public
   claims and known defects before implementation. Never stage unrelated files.
2. **Q1: deterministic software and artifact gate.** From the clean candidate,
   run `uv sync --locked --extra dev --extra ml`, then
   `uv run python scripts/verify_project.py --json`. Retain JSON and exit code.
   Require current docs, demo and receipt checks plus executed tests and serving
   smoke. The source defines the required checks; do not freeze a test count.
   Add focused regression coverage for changed behavior and broken links/claims
   when appropriate. Preserve `clinical_gate: E-005 blocked`.
3. **Q2: browser and visual gate.** Exercise each profile, load synthetic SECA,
   reject malformed CSV, inspect missing MVV and comparison warnings, download
   and print the report, open evidence and return. Capture browser/version,
   viewport, theme, state, source identity, screenshot path and actual finding.
   Inspect console errors and network during imports/forms; measurement data
   must not leave the browser. Inspect screenshots directly. Run the original
   IR3 cross-browser and accessibility checks; mark manual checks pending until
   actually performed. No broken core task or serious/critical accessibility
   finding may be waived by a passing screenshot comparison.
4. **Q3: publication gate.** Run remote candidate CI and platform wheel smokes;
   retain the failing-test publication-block proof. After authorized deployment,
   verify final URL, metadata, asset hashes, core links, local-only handling and
   desktop/mobile overview/report states again. A local screenshot is not live
   evidence. Any changed asset after sign-off reopens its affected checks.
5. **Q4: human acceptance and consistency.** Use the existing clinician study
   protocol and accessibility checklist. Record results, reviewer/date and
   defects, then obtain explicit acceptance for the final package. Reconcile
   root GOAL, ROADMAP, Wiki and board. Human thresholds cannot be satisfied by
   an agent simulating participants or by counting automated passes.

Keep a QA receipt under `docs/reviews/` with one record per check: ID, candidate,
environment, command or journey, expected result, actual result, pass/fail/not
run, evidence path, reviewer/date and remaining defect. A rerun is required
after a relevant change; do not repeatedly run unchanged green checks simply
to accumulate receipts. A blocked external check must name its unblocking action.

### Constraints and invariants

- Preserve MVV rejection, missing values, local-only measurement handling,
  comparison eligibility and null unsupported ages. Keep E-005 blocked.
- Only synthetic fixtures and public-safe evidence may appear in public output.
- Comparators inform presentation and evidence practices; their studies,
  customers, device validation and claims do not validate this software.
- Keep caveats beside affected results and provide one clear global boundary.
  Do not remove necessary limits to appear more trustworthy.
- Preserve user-owned dirty files. Do not change visibility, license ownership
  or publication settings by inference. Use existing authorized workflows.
- Root IR acceptance is unchanged. Missing reviewers keep human criteria open;
  independent implementation and local verification can continue.

### Non-goals

New biomarkers or system-age models, clinical validation, patient recruitment,
paid-service infrastructure, a new backend, competitor feature parity, decorative
redesign without utility, or an exhaustive security/clinical certification.

### Escalation conditions

Ask the owner for the specific missing ownership/evaluation-term decision,
reviewer assignment or publication authorization only when it blocks the next
dependent action. Record who must act and what evidence will unblock it.
Do not lower criteria or fabricate reviewer approval. If publication access is
unavailable, finish the reviewable candidate and retain the live gap explicitly.

## Builder-owned execution record

### Current approach

1. Inventory current claims and freeze the report contract; fix known false or
   stale statements before aesthetic work.
2. Reorganize around purpose, example, method/evidence and collaboration/contact.
   Keep deep engineering material available through progressive disclosure.
3. Exercise all required states, repair visual/behavior defects, and prepare
   the frozen synthetic package for human review alongside release verification.
4. Publish through the authorized gate, inspect the actual URL, and map every
   criterion to retained evidence. Close only when all criteria pass.

### Progress

- [x] Baseline source, receipt, live Actions and rendered-page audit recorded.
- [x] Official comparable evidence practices reviewed with applicability limits.
- [x] Goal contract and project tracking synchronized during planning.
- [ ] T1.1-T1.5: implement and verify presentation, claims and workflow.
- [ ] T1.6: verify the final candidate and published identity.
- [ ] T1.7: complete intended-user and qualified human review.
- [ ] T1.8: reconcile repository handoff and final status.

### Discoveries and decisions

The live HTML matches older commit `35e3e14b0acb5c80b1f46dbb9791439fbf4238c0`;
the failed `2f1218b` commit is not the observed deployed HTML. The current local
page withholds ages but still prioritizes technical material over the workflow.
Retain the existing measurement implementation; focus this goal on publication,
presentation, consistency and review. Do not broaden into clinical validation.

### Validation and runtime evidence

See the dated audit and six retained project screenshots. The local full verifier
passed 20/20 during the audit with `clinical_gate: E-005 blocked`. That baseline
is neither final-candidate evidence nor a pass for this goal. No redesign or
deployment was performed while authoring this goal.

### Remaining gap

All T1 acceptance criteria remain open pending implementation or final review.
Named human reviewers, final ownership/evaluation terms and release evidence
remain outstanding. The audit inspected selected rendered states and source
surfaces, not every line, browser state, dependency or scientific claim.
