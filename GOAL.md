# Goal: clinician-first healthspan research tool and public evidence showcase

**Date:** 2026-09-10
**Primary audience:** clinicians and clinical research collaborators
**Secondary audience:** investors evaluating scientific discipline, product value,
and execution quality
**Publication posture:** public GitHub Pages showcase; proprietary distribution
decision retained. GitHub currently reports a public source repository. IR0 must
reconcile visibility, licensing and public wording; private source is not verified.
**Current intended use:** research and wellness development only

## Active execution goal

[T1: a trustworthy published measurement-review showcase](goals/active/trustworthy-research-showcase/GOAL.md)
is the single active execution contract, shaped with goal-driven-engineering.
It makes the IR0-IR3 reviewer-package milestone actionable through visual,
editorial, workflow, claim-traceability and published-release acceptance.
The [maturity and trust audit](docs/PROJECT_MATURITY_AND_TRUST_REVIEW.md)
records direct visual inspection of live/local pages, comparable practices and
remaining gaps. This root file retains the broader product and scientific
requirements; no IR or clinical gate is closed by creating T1.

## Release decision from the 2026-09-10 review

Current status: **research prototype; the dirty-checkout software gate and a
local Windows 3.11 installed-wheel/HTTP smoke now pass, full release
verification remains incomplete, and clinical production is blocked by E-005**.
The local evidence now includes a temporary clean candidate verification and a
desktop capture of the currently published Pages surface. That capture still
shows the older `120 / 120 passing` and `v0.1.0 · draft` presentation, so it
does not establish a published candidate, remote CI and Pages publication, or
the deployed Pages identity for the current checkout.

The next deliverable is a focused, useful measurement-review research release,
not a broader collection of age estimates. Start with one clinician/researcher
workflow and a musculoskeletal-focused report: inspect observed measurements,
units and provenance; identify missing inputs; explain FI and its denominator;
export a concise report. Keep partial measurement preview separate from the
MVV-gated assessment. Numeric ages remain research-only and withheld wherever
their approval gate is absent. Additional system-age work is deferred until the
first domain proves incremental value over simpler alternatives.

The baseline review found failed remote CI/Pages, untracked release
dependencies, stale public test claims, contradictory licensing/visibility
language, an absent research report and a reproducible comparison artifact
caused by changing the FI denominator. The current checkout now contains the
clinician-first research report and comparison-eligibility repair, while the
stale count and local verification issues remain unpushed changes rather than a
published candidate release. The default predictor is an integration fixture. Neither
clinician utility nor clinical model validity has been demonstrated.

Read [the critical review](docs/INDUSTRY_READINESS_REVIEW.md) for source evidence,
the observed comparison reproduction, design direction and review limitations.
Sections 1-6 retain the long-term intent and scientific boundary. The ordered
IR0-IR7 plan below supersedes the previous G0-G5 sequencing and any historical
completion claim contradicted by fresh release evidence.

### Worker completion review, 2026-09-10

**Decision: accept the local software repair milestone only. The overall goal
is not complete, and no IR gate is promoted by this review.** An independent
rerun of `uv run python scripts/verify_project.py --json` passed all 20 checks,
including Python and Node tests, generated artifacts and real loopback serving.
It still returned `clinical_gate: E-005 blocked`.

The following findings remain release blockers:

| Gate | Observed gap | Required closeout evidence |
|---|---|---|
| IR0 | Required release files remain modified or untracked; latest remote CI and Pages runs failed at `2f1218b9d20b61ee9682cdae0a5a74dd79a7f653`. A temporary local clean snapshot at `0385ece0d3e65006cc1c58da6b2b015f2e1cd416` passed locked installation and all 20 software checks on Windows and WSL Ubuntu. Installed-wheel and real loopback HTTP smokes also pass on both platforms; the complete receipt is [`docs/ir0-clean-candidate-verification-2026-09-10.json`](docs/ir0-clean-candidate-verification-2026-09-10.json). | One candidate SHA with locked fresh-clone installation, passing Linux/Windows and wheel/HTTP checks, successful publication and verified live identity. Reconcile licensing and visibility wording. The temporary candidate is not pushed or published, and Linux CI has not run. |
| IR0 | The local Pages workflow now executes `uv run python -m pytest -q` before its evidence and deploy checks. The exact temporary candidate and an isolated `ir0-failure-demo` branch derived from it verify pytest exit 1 with the publication step unreached, recorded in [`docs/ir0-publication-failure-candidate-2026-09-10.json`](docs/ir0-publication-failure-candidate-2026-09-10.json). Remote Pages and candidate-branch execution remain unverified. The checked-in receipt remains a count receipt, not a substitute for execution. | Verify the executed-test dependency and isolated failing-test demonstration on the exact published candidate path through remote Actions. Collection counts are not pass receipts. |
| IR2 | The regression remains reproducible, but the local comparison layer now withholds the unsupported aggregate change and discloses coverage; statistical review is absent. | Retain the coverage-only regression, complete the section 7 test matrix, and record qualified review sign-off. |
| IR1 and IR3 | `docs/RESEARCH_REPORT.md`, the study protocol, and the manual accessibility checklist now exist; local Chrome, Firefox, and WebKit QA cover the three target widths, keyboard focus, light/dark modes, effective 2x layout containment, print-to-PDF flow, malformed-import rejection, and page-origin network privacy. Headed Chrome accessibility-tree review found 119 of 119 interactive controls named, four landmarks, and five polite live regions. An automated light-theme computed-style sweep found no failures across 977 visible leaf-text nodes with a 4.55 minimum ratio. Human screen-reader review, actual browser 200% zoom UI evidence, human light/dark contrast and non-color review, and the required user study remain outstanding. | Retain the report, browser QA receipt, manual checklist, cross-browser findings, accessibility-tree evidence, and results meeting the IR1/IR3 acceptance thresholds. |
| IR4-IR7 | Approved protocol/data, independent validation, operational controls and governed pilot evidence remain incomplete. | Supply each gate's required evidence and qualified review. Keep E-005 blocked until approval is recorded. |

IR2 regression case: start from the balanced synthetic demo, set BMI to 31,
then add only creatinine 0.9 in the canonical input unit. The review observed
the FI denominator change from 13 to 14, FI from 0.0769 to 0.0714, and
development age from 44.0 to 43.9. The previous comparison reported
`same_model_and_reference_panel` with both movements `lower`. The repaired
comparison now withholds that unsupported aggregate change, reports matched
coverage and blockers, and keeps the case as a regression test. Adding data
must not be presented as evidence of improved health; unknown provenance must
not silently establish eligibility.

Follow the ordered IR0-IR7 plan in section 7. Completion reports must identify
the milestone reviewed, candidate identity, executed checks and unresolved
gates. A local test pass alone cannot close the research showcase, model,
hosted-service or clinical-production goals in section 8.

## 1. The outcome we are building

Build a trustworthy, practical healthspan assessment tool that helps a clinician
understand a person's measured health profile, current deficit load, data quality,
and safe next discussion points. Surround the tool with a concise, inspectable
research report and a public GitHub Pages experience that let a clinician or investor
inspect the method, run a synthetic demonstration, understand the evidence, and
see exactly what remains before clinical deployment.

The product is successful when a busy clinician can answer four questions without
guessing:

1. What was actually measured, using which source, unit, date, and protocol?
2. What does the engine calculate deterministically, and what is only a
   development-stage model output?
3. Which values, missing inputs, or reference-band differences deserve a safer
   follow-up discussion?
4. What evidence is complete, what is still unverified, and what would be
   required for clinical production use?

The product is also successful when an investor can see a coherent path from
reproducible engineering to governed clinical evidence without mistaking a
passing software test, a synthetic cohort, or a polished interface for clinical
validation.

## 2. Non-negotiable truth boundary

This repository must remain honest about evidence strength.

- The current release is research-use-only and wellness-oriented.
- It is not a diagnostic device, treatment recommender, mortality predictor,
  lifespan estimator, or approved clinical decision-support system.
- A public GitHub Pages site may publish documentation, synthetic examples,
  public-data receipts, and reproducible instructions. It must never publish
  patient exports, identifiers, credentials, restricted cohort rows, model
  artifacts, or an assessment API.
- Publicly available data may support research-readiness and, when independently
  appropriate and clinically reviewed, parts of a clinical-readiness package.
  Public availability by itself does not establish clinical validity,
  transportability, fairness, safety, or approval.
- A numeric system-specific age-equivalent estimate is permitted only after that
  system has its own construct, target, measurement protocol, reference panel,
  repeatability evidence, uncertainty method, independent validation, subgroup
  and missingness review, and qualified approval.
- Until those gates are complete, category age estimates remain explicitly
  withheld or unavailable. A z-score, FI, commercial score, overall age, or
  illustrative number must never be relabeled as a system age.

## 3. Current product surface

The canonical engine and agent skill currently provide the following bounded
surfaces. Each must remain deterministic, versioned, privacy-safe, and covered
by tests.

### 3.1 Assessment engine

- A canonical 35-feature input matrix across demographics, BIA/SECA, blood,
  clinical history, and functional measures.
- An API-enforced Minimum Viable Vector that rejects incomplete assessments with
  structured errors and never fabricates missing values.
- A deterministic Rockwood-style accumulated-deficit FI using 0, 0.5, and 1
  coding, with the valid-variable denominator and completeness caveat visible.
- BIA transfer-calibration plumbing with an explicitly synthetic development
  panel until a reviewed panel is supplied.
- A development-only biological-age interface backed by the current surrogate
  predictor and explicitly labeled uncertainty and readiness state.
- A full-body category report that shows measured, missing, partial, and
  unavailable states. Category ages remain null unless their independent gate is
  complete.
- A range-based wellness report that identifies measured focus areas, missing
  inputs, reference-band direction, practical discussion prompts, and the fact
  that action effects are not estimated.
- A descriptive longitudinal comparison for dated assessments. It must not
  infer causality or claim that a change altered biological age or outcome.

### 3.2 SECA-to-assessment workflow

- Parse a local SECA TableView-shaped CSV without uploading it.
- Preserve scan date, source, units, observed values, segment values, and
  derivation provenance.
- Derive only supported same-scan fields, such as FFMI when its required inputs
  are present.
- Never infer age, sex, laboratory values, clinical history, or functional
  measurements from an equipment export.
- Keep observed SECA fields read-only in the assessment handoff and collect the
  remaining MVV inputs explicitly.
- Produce a versioned local overlay that can be passed to the canonical CLI or
  API path.

### 3.3 Public GitHub Pages showcase

The public site is a clinician- and investor-facing evidence surface, not a
patient portal. It must provide:

- A concise first screen explaining the purpose, current status, and evidence
  boundary in plain language.
- A synthetic example that can be selected and inspected without a backend.
- Visible FI, development age-equivalent interface, homeostatic-deviation
  context, measurement completeness, category reports, wellness focus areas,
  and withheld/unavailable states.
- A local-only SECA sample workflow using a synthetic downloadable fixture.
- Clear method cards for the feature contract, FI, BIA calibration, model
  boundary, data quality, and serving path.
- A research evidence ledger connected to repository files and cited sources.
- A compact readiness view separating engineering production-shaped status from
  clinical production-ready status.
- Accessible keyboard navigation, readable tables, responsive layout, print or
  export support where useful, no analytics, no remote fonts, and no CDN
  dependency required for the core demonstration.
- A visible invitation for qualified clinical, statistical, data-governance, and
  investment conversations without implying that the product is already cleared
  for patient care.

## 4. World-class research report

Create and maintain a standalone report at
`docs/RESEARCH_REPORT.md`. It should be readable by a
clinician first, technically inspectable by a researcher, and concise enough for
an investor to navigate. The report must be bounded, source-linked, and explicit
about confidence.

Required structure:

1. **Executive summary**: the problem, the tool, the current user value, and
   the one-sentence clinical boundary.
2. **Clinical workflow**: who uses it, what inputs are available, what the
   clinician sees, and where professional judgment remains required.
3. **Input and measurement contract**: the 35 features, MVV, units, provenance,
   missingness, SECA limitations, and the difference between observed and
   derived values.
4. **Methods**: FI construction, BIA transfer calibration, development predictor,
   age-equivalent mapping, category reports, wellness ranges, and progress
   comparison.
5. **What the current tool can show**: an example report with every numeric
   value labeled as synthetic or development-only where applicable.
6. **Evidence ledger**: software tests, reproducibility receipts, packaging,
   serving, privacy, accessibility, public-data intake, and Pages checks.
7. **Public-data proof ladder**: what can be demonstrated with permitted public
   data, how independence and leakage are controlled, and which claims remain
   unproven.
8. **Limitations and failure modes**: reference-panel drift, missing-not-at-
   random assumptions, survey design, measurement error, subgroup support,
   uncertainty, transportability, and intended-use limits.
9. **Readiness gates**: engineering production-shaped versus clinical
   production-ready, with evidence and owner for every gate.
10. **Practical usage**: local installation, CLI, API, SECA preview, overlay
    handoff, test commands, and safe interpretation guidance.
11. **Roadmap and investment case**: the next bounded tranche, why it matters,
    dependencies, and what would increase clinical and commercial confidence.
12. **References and appendices**: source map, response schema, data dictionary,
    report status vocabulary, and reproducibility commands.

Every substantive claim in the report must be one of:

- **Measured**: directly verified in source, tests, or a reproducible receipt.
- **Method**: a declared design choice or documented algorithm.
- **Evidence-informed**: supported by a cited external source but not yet
  demonstrated for this product or population.
- **Unverified**: a hypothesis or future obligation, labeled as such.

The report must never turn a citation into proof that this repository's model is
valid. Public-data results must include dataset identity, access terms, cohort
definition, feature and endpoint mapping, split boundary, missingness, survey
design, uncertainty construction, subgroup support, and reproducible commands.

## 5. Public-data evidence strategy

Use permitted public data to build a transparent evidence ladder. Keep raw data
outside the repository unless its terms explicitly allow redistribution and the
privacy review permits it.

### Level 0: provenance and intake

Record the source release, access date, license or permitted-use basis, file
hashes, cycle-specific maps, units, sentinels, linkage rules, and disclosure
limitations. Preserve fixed-width and mortality contracts exactly when required.

### Level 1: deterministic data preparation

Show that the public files can be parsed into canonical rows without invented
headers, fabricated measurements, silent imputation, or identifier leakage.
Emit privacy-safe aggregate receipts with counts, missingness, exclusions, and
schema identity only.

### Level 2: development reproducibility

Run the feature mapping, FI calculation, BIA normalization, training frame
construction, model fit, artifact generation, and report regeneration from a
locked environment. Persist the feature order, recipe, random seeds, mapper
provenance, survey-design declaration, and artifact hashes.

### Level 3: internal holdout and leakage control

Use patient-level separation, explicit tuning boundaries, duplicate rejection,
event/censoring accounting, and sensitivity analyses. Report this as internal
development evidence, not external validation.

### Level 4: independent public replication

Evaluate an independently sourced and permitted public cohort, or a separately
governed cohort when public data cannot support the intended population. Freeze
the analysis protocol before evaluation. Report discrimination, censoring-aware
calibration, uncertainty, missingness sensitivity, subgroup support, and
transportability limitations with transparent denominators.

### Level 5: clinical and product review

Qualified reviewers determine whether the evidence supports the intended use,
reference panel, cutoffs, patient-facing language, uncertainty, monitoring,
rollback, and deployment. A public-data result can contribute to this package,
but it cannot replace clinical review, measurement repeatability work, target
population suitability, or governance approval.

## 6. Two meanings of production ready

### 6.1 Engineering production-shaped

This status may be claimed only when the repository can demonstrate, with fresh
receipts:

- locked installation and reproducible dependency resolution;
- complete Python and browser/static test suites;
- canonical CLI and typed API behavior, including invalid-input handling;
- installed-wheel and real loopback HTTP smoke tests;
- fail-closed readiness and hash-bound release identity;
- privacy-safe logs, bounded responses, security headers, and no patient data in
  public artifacts;
- deterministic synthetic Pages demo and local-only SECA workflow;
- generated report/demo/test receipts matching their source inputs;
- accessible public documentation with accurate claim labels;
- documented rollback, monitoring, incident, and data-retention boundaries; and
- a visible clinical gate that remains blocked when clinical evidence is absent.

Engineering production-shaped means the software can be responsibly handed to
reviewers and operators for the next evidence stage. It does not mean the model
is valid for patient care.

### 6.2 Clinically production-ready

This status requires all of the following for the exact intended use and each
numeric system-age output:

- a reviewed intended population, workflow, and risk assessment;
- an approved, permitted cohort with documented provenance and governance;
- a prespecified analysis plan and independent patient-level evaluation;
- validated measurement protocols, device/unit handling, repeatability, and
  reference-panel transportability;
- outcome-appropriate discrimination, calibration, uncertainty, and sensitivity
  evidence with transparent denominators;
- subgroup support and missingness analysis for relevant sex, age, ethnicity,
  and other clinically material strata;
- review of survey weights and complex-survey variance where applicable;
- evidence that the output adds useful information beyond age and simpler
  measures, where that is part of the intended use;
- clinical utility, workflow, human-factors, and patient-facing language review;
- cutoff, panel, model, uncertainty, monitoring, rollback, and change-control
  approval;
- qualified clinical, statistical, data-governance, security, and product
  sign-off; and
- deployment controls including authentication, authorization, TLS, secret
  management, rate limiting, network policy, retention, incident response, and
  an approved immutable release.

The clinical status remains **not ready** until the evidence package is approved.
Passing tests, a synthetic external-validation fixture, public-data parsing, a
high concordance on a development split, or a public Pages demo cannot change
that status by themselves.

## 7. Next steps and how to verify them

### Recommended next milestone: measurement-only reviewer package

The next milestone is a frozen, locally reproducible package for reviewing one
musculoskeletal measurement workflow. Include the synthetic demonstration,
concise research report, comparison warnings, export, evidence index and human
review checklist. This is an intermediate review deliverable, not a research
showcase release or clinical approval. Keep unsupported ages withheld.

The latest files record real progress: the report exists, comparison eligibility
is implemented locally, and clean-snapshot and browser receipts exist. These
are completed subdeliverables with bounded evidence. Their parent release gates
remain open because publication or qualified human review is still missing.
Do not redo completed work unless the candidate changes, a check fails, or a
review identifies a defect. Receipts cover their recorded source identity only;
the temporary snapshot does not automatically certify later working-tree edits.

| Work now | Owner role | Next action and exit evidence |
|---|---|---|
| Freeze the reviewer package | Maintainer | Select exact intended files, reconcile license/visibility wording, record one candidate SHA and hashes, and verify it from a clean checkout. Preserve unrelated changes. Record any source changes since the existing snapshot. |
| Finish remote release verification | Maintainer | For the selected candidate, obtain remote Linux/Windows CI and wheel/HTTP results plus the isolated failing-test publication check. After authorized publication, verify live metadata and assets. IR0 remains open until these pass. |
| Run human review in parallel | Product owner with clinician, statistical and accessibility reviewers | Assign named people and review dates. Use the frozen local synthetic package for the five-user study, comparison review and remaining manual accessibility checks. Record results against the unchanged IR1-IR3 thresholds. Public deployment is not required to begin this review. |
| Close findings and prepare showcase release | Engineering and documentation | Fix observed defects, rerun affected checks, and refresh receipts for the final candidate. Reconcile GOAL, ROADMAP, Wiki and Project #4 before declaring IR0-IR3 complete. |
| Prepare later evidence without fitting | Clinical/data lead | Identify permitted data and qualified reviewers, draft the domain protocol and list missing inputs. IR4 approval and IR5 fitting still require their original evidence gates. |

### Status and blocker rules

- **Complete subdeliverable:** the named artifact or check exists with its source
  identity and evidence. This does not mark its parent IR gate complete.
- **In progress:** an actionable engineering, documentation or review step
  remains. A missing external reviewer must not block independent local work.
- **Blocked:** name the exact missing input or decision, accountable owner role,
  next unblocking action and review date. If no person has accepted ownership,
  record that explicitly; do not invent an assignment or approval.
- **Deferred:** work deliberately outside the next milestone. Keep IR5 training
  and IR7 clinical pilot blocked by their evidence dependencies. Defer broader
  system-age expansion and hosted-service investment beyond bounded synthetic
  IR6 preparation until the measurement workflow demonstrates utility.

At the next planning review, assign people and dates to external blockers. If
reviewers or suitable data are unavailable, retain the package as a local
synthetic review build and continue only work that improves measurement
integrity or reviewability. Do not replace human evidence with more automated
checks, lower acceptance thresholds, or call the research showcase complete.

The dependency table below distinguishes when work can start from when a gate
can close. Existing scientific and release acceptance thresholds are unchanged.
Do not auto-promote a model or change repository visibility.

Each gate requires a named owner, candidate commit and artifact hashes,
environment/lock identity, test or study protocol, actual result, reviewer,
date, unresolved defects and a pass/fail decision. Missing required closeout evidence leaves the gate open,
not passed; independent work may continue. Role owners below are assignments still to be accepted by people.

| ID | Owner and dependency | Required result and verification |
|---|---|---|
| IR0 | Maintainer; first | Reconcile tracked files, licensing/visibility wording and current status. Preserve unrelated work. From a fresh clone at one candidate SHA, install with `uv sync --locked --extra dev --extra ml`, run `uv run python scripts/verify_project.py --json`, and run both platform wheel/HTTP smokes. Linux, Windows and Pages must pass for the same SHA. Bind deploy to executed tests, then prove a deliberately failing Python test blocks publication on an isolated test branch. Verify live build metadata, asset hashes and links after an authorized deployment. E-005 remains blocked. A temporary local clean snapshot at `0385ece0d3e65006cc1c58da6b2b015f2e1cd416` passed locked installation and all 20 software checks on Windows and WSL Ubuntu, and its isolated failure branch returned pytest exit 1 before publication. It is not pushed or published and does not satisfy Linux CI, remote, publication, live identity, or licensing/visibility reconciliation. |
| IR1 | Product owner plus clinician reviewer; start with frozen local package, release closeout requires IR0 | Define one user, setting, task, minimum available data, report and alternative workflow. Interview at least five intended users; record de-identified task evidence. At least four of five must complete sample selection, find missing inputs, interpret FI correctly and export the report without assistance in five minutes; all must recognize that ages and clinical advice are unvalidated. Compare task time and interpretation errors with their current manual report. Revise scope if utility is not demonstrated; do not recruit patient use through the public demo. |
| IR2 | Engineering plus statistical reviewer; draft IR1 contract for implementation, frozen package for review; release closeout requires IR0 | Implement explicit comparison eligibility using item set, coding version, units/protocol, date and model/panel/artifact identity. Test unchanged overlapping values with added/removed normal and abnormal items, changed units/protocol, unknown hashes and changed cutoffs. Withhold unsupported aggregate change or show clearly labeled matched-item change and coverage difference. No improvement interpretation from coverage alone. Preserve MVV rejection and null unsupported ages. Retain reproducible tests and review sign-off. |
| IR3 | Product designer plus documentation owner; start from draft IR1/IR2 contract, close after their review and IR0 | Build the four-part site and research report; reconcile README, metadata, license text and all status claims. Test actual browser journeys in Chromium, Firefox and WebKit at 360, 768 and 1440 px, keyboard-only navigation, 200% zoom, screen reader, light/dark modes, print and failed imports. Target WCAG 2.2 AA; retain automated findings and manual checklist, with no unresolved serious/critical issues or blocked core task. Inspect network traffic for synthetic CSV import and form entry: no measurement data may leave the browser. Repeat IR1 comprehension test and retain screenshots. |
| IR4 | Clinical/data lead plus statistician; IR1 | Freeze one musculoskeletal construct and target before fitting. Distinguish normative age equivalence from outcome prediction. Supply permitted data identity/hashes, protocol, repeatability, cohort eligibility, sample-size rationale, survey design, missingness, independent split and leakage controls. Prespecify numerical acceptance thresholds and confidence interval precision with qualified reviewers before evaluation. Compare against chronological age, FI alone and a simple domain baseline. Use a TRIPOD+AI reporting map; it is a disclosure checklist, not approval. No fitting or performance claims from invented thresholds/data. |
| IR5 | ML lead plus independent statistician/clinical reviewer; IR4 | Train and package a reproducible candidate, then evaluate the frozen model on genuinely independent appropriate data. Report target-appropriate calibration/error, discrimination if outcome-linked, uncertainty coverage, repeatability, subgroup/event/sample denominators, missingness and incremental utility. Implement missing metrics before promising them. Apply prespecified pass/fail rules; retire used holdouts from future tuning claims. If the model does not outperform useful simpler alternatives or age equivalence adds confusion, release measurements only. E-005 requires qualified signed approval, not flags. |
| IR6 | Security/operations owner plus governance lead; IR2, with synthetic staging parallel to IR4/IR5 | Define deployment boundary and risk-based jurisdiction/intended-use review. Prove TLS/auth denial, authorization, request/rate/time limits, secret rotation, dependency scan/SBOM, supported Python matrix, monitoring and incident ownership in staging. Retain timed rollback and restore drills against immutable artifacts. Set capacity, latency and availability targets before load tests. Real-person use requires completed governance and relevant clinical gates; synthetic staging does not. |
| IR7 | Product/clinical/operations owners; IR3, IR5/E-005 and IR6 for clinical pilot | Run a governed limited pilot with predefined success and stop criteria, support ownership, access/retention controls, interpretation-error and workflow monitoring. Review every critical safety incident immediately; stop on material misleading output, data exposure or unapproved release identity. Release only after recorded approval and closeout of material defects. Any model, panel, cutoff or intended-use change reopens affected gates. |


## 8. Definition of done and stop rules

1. **Research showcase release:** IR0-IR3 pass on the exact published version.
   The clinician workflow is understandable without assistance, the concise
   research report exists, and every public claim matches its evidence.
2. **Model candidate:** IR4-IR5 produce independently evaluated, reproducible
   evidence against prespecified baselines. A candidate is not clinical approval.
3. **Hosted research service:** IR6 and applicable governance pass before real
   user deployment. Static Pages never becomes a patient portal or assessment API.
4. **Clinical production:** all applicable IR gates, including IR7 and qualified
   E-005 approval, must pass for the exact intended use and immutable release.
5. GOAL, ROADMAP, Wiki and Project #4 agree. README, Pages metadata and release
   receipts must be reconciled before release; remaining contradictions are
   blockers rather than silently grandfathered claims.
6. Stop or narrow scope when users cannot interpret results safely, provenance
   or comparison eligibility is unknown, independent data are unavailable,
   simple baselines are as useful, or model/operational acceptance criteria fail.
   Preserve a measurement-only product when age estimates do not earn their cost.

Usability thresholds in IR1/IR3 are proposed product gates. Scientific thresholds
must be justified and frozen by qualified reviewers before evaluation, never
selected retrospectively to make a result pass. All current clinical claims
remain blocked. This planning update does not implement or satisfy the gates.

## Source of truth

- [`GOAL.md`](GOAL.md): product intent, scope, boundaries, readiness definitions,
  and definition of done.
- [`ROADMAP.md`](ROADMAP.md): ordered dependencies, owners, statuses, and exit
  evidence.
- [`EVAL.md`](EVAL.md): criterion-level engineering evidence and the E-005
  clinical gate.
- `docs/RESEARCH_REPORT.md`: current clinician-first research narrative and
  practical usage report.
- [`docs/SYSTEM_AGE_REPORT_SPEC.md`](docs/SYSTEM_AGE_REPORT_SPEC.md): target
  system-specific age-equivalent card and numeric-age evidence gate.
- [`docs/OPERATIONS.md`](docs/OPERATIONS.md): serving, monitoring, privacy,
  rollback, and release boundaries.
- [`docs/wiki/index.md`](docs/wiki/index.md): reusable research and decision
  entries.
- [GitHub Project #4](https://github.com/users/stancsz/projects/4/views/1):
  workflow tracking for this repository.
