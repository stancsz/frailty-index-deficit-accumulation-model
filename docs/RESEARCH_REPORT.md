# Research report: clinician-first measurement review

**As of:** 2026-09-10  
**Status:** research-use-only prototype  
**Audience:** clinicians, clinical research collaborators, statisticians, and
investors evaluating the evidence path

**Documentation authority:** This reader-facing report follows
[`PRODUCT_INTENT.md`](product-specs/PRODUCT_INTENT.md),
[`ARCHITECTURE.md`](../ARCHITECTURE.md), and the active goal recorded in
[`GOAL.md`](../GOAL.md). It does not override them.

**Measured:** This report describes the current working tree, not a clean
release candidate or a deployed service. The local software gate is being
repaired and checked in the repository. Remote CI and Pages publication still
have unresolved failures, the reference panel is synthetic, the predictor is a
development fixture, and E-005 remains blocked.

**Boundary:** The tool is not a diagnostic device, treatment recommender,
mortality predictor, lifespan estimator, or approved clinical decision-support
system. A passing software test is evidence about software behavior only.

## How to read this report

Every substantive statement uses one of the following labels:

- **Measured:** directly observed in source, a test, a generated artifact, or a
  reproducible receipt in this repository.
- **Method:** an implemented or proposed algorithm, contract, workflow, or
  design choice.
- **Evidence-informed:** supported by a cited external source, but not thereby
  demonstrated for this implementation or population.
- **Unverified:** an open hypothesis, user-study result, clinical claim, or
  future obligation.

## 1. Executive summary

**Measured:** The repository contains a Python assessment engine, a local SECA
TableView parser, a typed API, a CLI, an agent skill, and a static GitHub Pages
showcase. The engine accepts a canonical 35-feature vector, preserves missing
values, enforces a minimum viable vector, calculates a Rockwood-style
deficit-accumulation FI, and returns a bounded measurement-review report.

**Method:** The intended user value is a clinician or researcher being able to
inspect what was measured, see the FI numerator and denominator, identify
missing inputs and development reference-band states, and export a concise
review artifact before discussing context with the person. The workflow keeps a
partial SECA measurement preview separate from the MVV-gated assessment.

**Measured:** The current public synthetic artifact contains three synthetic
examples and withholds the numeric biological-age point estimate and interval.
The local development path can exercise the age-equivalent interface, but its
predictor and uncertainty are not validated. Category-specific ages remain
null or unavailable unless their independent evidence gate is complete.

**Unverified:** No clinician utility, interpretation safety, clinical validity,
transportability, treatment effect, mortality prediction, lifespan effect, or
commercial outcome has been demonstrated. The required five-user workflow
study, approved data protocol, independent validation, and qualified E-005
review remain open.

**Boundary sentence:** This release can support a transparent measurement and
development-review conversation; it cannot support a clinical decision or
claim that a person became biologically younger or healthier.

## 2. Clinical workflow

**Method:** The proposed first workflow is a musculoskeletal-focused review
with a broader deficit-accumulation context:

1. A clinician or researcher selects a local record and records the source,
   date, unit, and measurement protocol for available values.
2. A local SECA TableView-shaped CSV may be parsed in the browser or CLI. The
   parser exposes observed scan values, segment values, dates, unit warnings,
   and supported same-scan derivations. It does not upload the raw export.
3. The user completes the remaining demographic, blood, history, and
   functional fields required by the MVV. Missing age, sex, laboratory,
   history, or functional values are not inferred from the equipment export.
4. The engine validates the 35-feature contract and either returns a typed
   missing-requirements response or produces the assessment report.
5. The report separates measured values, missing values, FI coverage, wellness
   reference-band context, model status, and unavailable category ages.
6. The clinician applies history, examination, repeat measurement, and
   professional judgment. The interface does not prescribe a treatment or
   estimate the effect of an action.

**Method:** The proposed alternative workflow for comparison is the clinic's
existing manual measurement review. The study protocol in
[`CLINICIAN_WORKFLOW_STUDY.md`](CLINICIAN_WORKFLOW_STUDY.md) defines a timed
task, interpretation checks, and a de-identified evidence form.

**Unverified:** The product has not yet completed the required five-intended-
user study. No patient recruitment is requested through the public demo, and
no usability threshold is treated as passed until the study is run and
reviewed.

**Unverified:** A clinician must decide whether a value is credible, whether a
repeat measurement is needed, whether a reference band applies to the person,
and whether any follow-up is clinically appropriate. The current software does
not replace those decisions.

## 3. Input and measurement contract

### 3.1 Canonical 35 features

**Measured:** `src/frailty_engine/features.py` defines 35 unique canonical
features. The units below are the current transport descriptions recorded by
the comparison contract. They are not proof that devices, laboratories, or
reference intervals have been harmonized.

| Group | Features and transport units | Typical status in this tool |
|---|---|---|
| Demographics and vital signs | `age` years; `sex` category; `bmi` kg/m²; `systolic_bp` mmHg; `diastolic_bp` mmHg; `resting_hr` bpm; `waist_circumference` cm | **Method:** supplied canonical values; source and protocol remain a user responsibility |
| BIA | `phase_angle` degrees; `ecw_tbw` ratio; `ffmi` kg/m²; `skeletal_muscle_mass` kg; `visceral_fat` L | **Method:** supplied values or supported same-scan derivation for selected SECA fields |
| Blood | `fasting_glucose` mg/dL; `hba1c` %; `hs_crp` mg/L; `albumin` g/dL; `creatinine` mg/dL; `egfr` mL/min/1.73m²; `alp` U/L; `wbc` 10⁹/L; `rdw` %; `fib_4` index | **Method:** supplied laboratory values; no laboratory value is inferred from SECA |
| History | `hypertension`, `t2d`, `osteoarthritis`, `sleep_apnea`, `cvd`, `copd`, `cancer`, `depression` as binary values | **Method:** supplied history values; no history is inferred from equipment data |
| Function and recovery | `grip_strength` kg; `chair_rise_time` seconds; `smoking_status` category; `alcohol_heavy_use` binary; `sleep_hours` hours | **Method:** supplied contextual or functional values; no functional value is inferred from SECA |

**Method:** The FI-eligible set is the 33 features other than `age` and
`sex`. A single assessment's FI denominator is the number of FI-eligible
features with valid values. Missing FI values are excluded from the
denominator, not imputed.

### 3.2 MVV and missingness

**Measured:** The MVV requires `age`, `sex`, `bmi`, `phase_angle`, and
`ecw_tbw`; at least six blood variables; either fasting glucose or HbA1c; and
at least four history variables. Failure returns a structured validation error
with missing requirements. The contract does not require all 35 features.

**Method:** Missingness is retained as missing through parsing, FI scoring,
category reports, training-frame construction, and public display. A sparse
denominator is shown with a count-only engineering strength label. That label
is not a clinical adequacy threshold.

### 3.3 Observed, derived, and provenance values

**Measured:** The SECA parser records scan dates, observed values, units,
segment values, unit warnings, and latest-minus-previous trends. It can derive
fat-free mass and FFMI only when the same-scan inputs required by the importer
are available. The normalized local handoff preserves derivation provenance.

**Method:** The assessment API validates normalized canonical values. Its
comparison context records feature names, transport units, protocol identity,
FI coding identity, cutoff identity, model identity, and reference-panel
identity, but it deliberately does not carry raw measurements.

**Unverified:** The repository has not established equivalence between a
clinic's device, laboratory method, or measurement protocol and the synthetic
development reference panel. A supplied value may be syntactically valid while
still being clinically unsuitable.

## 4. Methods

### 4.1 Deficit accumulation

**Method:** `src/frailty_engine/fi.py` applies explicit 0, 0.5, or 1 coding to
configured deficit features, averages valid coded items, and exposes numerator,
denominator, valid-variable names, and the denominator caveat. The engineering
cutoffs are versioned as `engineering-cutoff-set-v1`.

**Evidence-informed:** Searle et al. describe a standard accumulated-deficit
procedure and the use of intermediate coding values. That source supports the
general method, not clinical validation of this 33-item implementation. See
[`SOURCES.md`](SOURCES.md).

### 4.2 BIA transfer calibration

**Method:** The BIA path maps configured measurements to z-score-like
reference-panel values using the loaded panel's age and sex bands. The shipped
panel is a deterministic synthetic development fixture with an explicit
fixture-only status and digest.

**Evidence-informed:** Published BIA studies are used as design references for
measurement concepts and normal-range discussion. They do not establish that
the synthetic panel is valid for a clinic, device, population, or intended use.

### 4.3 Development predictor and age-equivalent mapping

**Method:** The local development predictor provides an integration path for a
development-stage hazard/readout mapping. A fitted release would require a
hash-bound artifact, feature manifest, reference panel, mapper provenance,
uncertainty method, and approval sidecar.

**Measured:** The current public artifact sets the age-equivalent point estimate
and interval to null, and the response states that the development predictor
and uncertainty method are not validated. The public artifact does not publish
a model artifact or an assessment API.

**Unverified:** No mortality, lifespan, clinical outcome, or biological-age
validity claim is supported. The cited aging-clock literature informs the
terminology boundary only.

### 4.4 Category reports

**Method:** The category report groups available measurements into body
composition, fluid/cellular, muscle, blood, cardiovascular, metabolic,
kidney, liver, sleep/recovery, lifestyle/function, mental-health history,
cardiorespiratory, immune/inflammatory, brain/cognitive, skin, and bone
sections. It exposes measured, missing, partial, and unavailable states.

**Measured:** Category ages are withheld. A z-score, FI, commercial score,
overall age, or illustrative number is not relabeled as a system-specific age.

### 4.5 Wellness reference ranges

**Method:** The wellness report exposes measured values, development reference
bands, direction, a discussion prompt, and an action type limited to lifestyle
or review. It carries `action_effect_estimated: false` and
`clinical_or_lifespan_claim: false`.

**Unverified:** A reference-band movement does not establish benefit, treatment
effect, risk reduction, or a change in biological age.

### 4.6 Progress comparison integrity

**Measured:** The comparison route now returns a versioned comparison context
with feature contract, measurement protocol, FI coding, cutoff, measured
features, FI-valid features, units, protocols, model identity, model artifact
hash, and reference-panel identity.

**Method:** Aggregate readout deltas are eligible only when the item set,
coding, cutoff, units, protocols, model artifact hash, and reference-panel hash
are compatible. If a normal added measurement changes the FI denominator, or a
hash is unknown, the report uses `matched_items_only`, lists matched/added/
removed features and blockers, and withholds aggregate readout deltas. The
range-transition section may still show measured item changes. This prevents a
coverage change from being presented as health improvement.

**Measured:** Focused tests cover added and removed FI items, changed units,
changed protocols, changed cutoff identity, unknown panel hash, and unknown
development model artifact hash. The generated synthetic Pages artifact shows
the withheld state rather than a false aggregate improvement.

## 5. What the current tool can show

**Measured:** `docs/demo-data.json` is generated from three deterministic
synthetic profiles. It contains no patient export and no patient identifier.
The current public artifact uses the following safe display pattern:

| Report element | Current example state | Label required for interpretation |
|---|---|---|
| FI numerator and denominator | A synthetic profile can show a deterministic FI ratio and its valid-item denominator | **Synthetic; software behavior only** |
| Biological-age point estimate | `null` in the public artifact | **Withheld; development predictor and uncertainty are unvalidated** |
| Biological-age interval | `null` | **Withheld; no validated uncertainty method** |
| Category age | `null` or unavailable | **Withheld until the category gate is complete** |
| Measured reference-band values | Synthetic profile values and development bands can be displayed | **Synthetic/development reference context; not clinical targets** |
| Progress aggregate deltas | Withheld when the comparison context is incomplete | **Matched-items-only; coverage and blockers must be read first** |
| Action-effect and clinical flags | Both are `false` | **No treatment-effect or clinical claim** |

**Method:** A clinician can use the artifact to inspect layout, missing-input
disclosure, denominator context, category states, report export, and the
comparison warning. A local API or CLI can exercise the typed contract with
explicitly synthetic or locally supplied input.

**Unverified:** The synthetic artifact does not demonstrate that a clinician
will interpret the report safely, that the workflow is faster than a manual
review, or that any numeric output improves care.

## 6. Evidence ledger

**Measured:** The current working tree provides the following software
evidence. Counts are recorded in [`test-receipt.json`](test-receipt.json), and
the collection receipt is not treated as a substitute for executed tests.

| Evidence area | Current observation | What it does not prove |
|---|---|---|
| Python behavior | The canonical project verifier executes the current Python suite; the retained receipt records 146 collected tests as metadata and is not a substitute for execution | Clinical validity, external performance, or reviewer approval |
| Pages and parser behavior | `node --test --test-reporter=tap tests/site_parser.test.cjs` passed 28 tests | Full browser coverage across Chromium, Firefox, and WebKit |
| Static quality | Ruff check and format check pass for the changed Python files; the project verifier covers the broader source tree | Absence of all deployment or governance risk |
| Generated artifacts | Demo and test receipts are generated by repository scripts and checked for drift | Publication of the current dirty checkout |
| Serving | The project verifier has a real loopback HTTP smoke and fail-closed readiness path | A hosted service, security review, or clinical approval |
| Public-data intake | CDC/NHANES parsing and synthetic validation fixtures have deterministic engineering smokes | External validation of the intended population or device equivalence |
| Rendered browser QA | [`browser-qa-2026-09-10.json`](browser-qa-2026-09-10.json) records local Chrome checks at 360, 768, and 1440 px with no document-level horizontal overflow, one `h1`, working synthetic profile switching, visible matched-items-only comparison warnings, an eight-step keyboard focus pass, light/dark modes, effective 2x layout containment, print-to-PDF flow, malformed-import rejection, and no non-local page-origin HTTP requests; an automated computed-style contrast sweep found no light-theme failures across 977 visible leaf-text nodes with a 4.55 minimum ratio; local Firefox 144.0.2 and WebKit 26.0 checks add the same responsive, keyboard, print, failed-import, local-network, and page-error evidence; headed Chrome exposes 119 named interactive controls, four landmarks, and five polite live regions; the 360 px check required responsive CSS repairs. The manual review protocol is [`ACCESSIBILITY_MANUAL_CHECKLIST_2026-09-10.md`](ACCESSIBILITY_MANUAL_CHECKLIST_2026-09-10.md). | Human screen-reader, actual browser 200% zoom UI, human contrast, and comprehension evidence remain open |
| Privacy boundary | Pages is static, synthetic, local-import oriented, and excludes raw input from progress reports | A complete deployed network, legal, or organizational privacy assessment |
| Clinical gate | E-005 remains blocked because approved cohort evidence and qualified review are absent | Any clinical or production claim |

**Measured:** The repository's canonical verifier is
`uv run python scripts/verify_project.py --json`. Its expected software result
is `status: "passed"` with `clinical_gate: "E-005 blocked"`. The verifier does
not promote a clinical gate.

**Unverified:** The latest remote CI and Pages runs failed at the recorded
candidate SHA in `GOAL.md` and `ROADMAP.md`. A clean candidate, fresh clone,
same-SHA Linux and Windows receipts, publication success, and live asset
identity have not been established by this report.

## 7. Public-data proof ladder

**Method:** The evidence ladder is deliberately cumulative. Each level below
must preserve provenance and state what it cannot prove.

| Level | Demonstration | Current status |
|---|---|---|
| 0. Provenance and intake | Release, access terms, hashes, units, sentinels, linkage, and disclosure limits | **Measured:** repository maps the intended CDC/NHANES and mortality contracts; cycle-specific governance remains to be completed |
| 1. Deterministic preparation | Parse permitted public files without fabricated headers, silent imputation, or identifier leakage; emit aggregate receipts | **Measured:** engineering parsers and receipts exist; no clinical claim |
| 2. Development reproducibility | Locked mapping, FI, BIA normalization, training frame, fit, artifact, and report regeneration | **Measured:** software paths and synthetic fixtures exist; the supplied predictor is not a production model |
| 3. Internal holdout and leakage control | Patient-level split, duplicate rejection, event/censor accounting, tuning boundary, and sensitivity plan | **Measured:** deterministic synthetic split behavior exists; approved study evidence is absent |
| 4. Independent replication | Frozen protocol, independent permitted cohort, calibration, uncertainty, missingness, subgroup support, and transportability review | **Unverified:** no approved independent evaluation has closed E-005 |
| 5. Clinical and product review | Qualified review of intended use, cutoffs, panel, language, monitoring, rollback, and deployment | **Unverified:** no qualified approval is recorded |

**Method:** Public availability is treated as an input to research readiness,
not as a substitute for clinical validity, fairness, repeatability,
transportability, governance, or approval.

## 8. Limitations and failure modes

**Unverified:** The synthetic reference panel may not transport across devices,
laboratory methods, populations, age ranges, sex strata, or protocols.

**Method:** Missing values are preserved, but the implementation does not make
a missing-not-at-random assumption safe. Sparse observations can change the FI
denominator and can make a longitudinal aggregate incomparable.

**Evidence-informed:** Complex survey weights and variance estimation matter for
public survey data. The repository records a survey-design contract and
disclosure boundary, but the shipped adapter does not establish a complete
complex-survey clinical analysis.

**Unverified:** Device repeatability, laboratory repeatability, temporal
stability, measurement error, subgroup support, uncertainty coverage,
transportability, and incremental utility over age, FI, and simpler domain
measures remain open.

**Measured:** The comparison layer withholds aggregate changes when coverage or
provenance is not stable. It does not make the remaining matched-item changes
causal or clinical.

**Method:** The public site is a documentation and synthetic-demonstration
surface. It must not receive patient exports, publish credentials or model
artifacts, or become an assessment API.

## 9. Readiness gates

**Measured:** The current ordered gates are:

| Gate | Current status | Required closeout |
|---|---|---|
| IR0 release candidate | In progress; local dirty-checkout software evidence exists | Clean candidate SHA, fresh-clone install, same-SHA Linux/Windows and wheel/HTTP receipts, executed-test publication gate, live identity, and licensing/visibility reconciliation |
| IR1 user workflow | Todo | Five intended-user sessions, de-identified task evidence, comprehension threshold, and comparison with the manual workflow |
| IR2 comparison integrity | In progress; local contract and focused tests pass | Statistical review and retained sign-off for eligibility, coverage disclosure, and interpretation wording |
| IR3 public experience | In progress; report/static boundary and Chrome, Firefox, and WebKit rendering and keyboard journeys delivered | Keyboard, zoom, screen reader, print, failed-import, responsive, privacy-network, and repeat comprehension evidence |
| IR4 protocol and data | Todo; qualified data owner needed | Frozen musculoskeletal construct, permitted data, repeatability, baseline, independent split, missingness, survey, and prespecified thresholds |
| IR5 independent model evidence | Blocked | Reproducible candidate, independent comparative validation, uncertainty, subgroup support, and qualified E-005 review |
| IR6 operations and governance | Synthetic local operations review recorded; staging and governance evidence not started | Auth, authorization, rate/time limits, secret/dependency controls, monitoring, incident ownership, restore and rollback drills, and governance review; see [`IR6_SYNTHETIC_OPERATIONS_REVIEW_2026-09-10.md`](IR6_SYNTHETIC_OPERATIONS_REVIEW_2026-09-10.md) |
| IR7 governed pilot | Blocked | Approved limited pilot, stop criteria, support and retention controls, safety monitoring, and recorded release approval |

**Measured:** E-005 is blocked. No status in this table should be read as
clinical readiness.

## 10. Practical usage

### Local installation and verification

**Method:** Use the locked environment and the canonical verifier:

```powershell
uv sync --locked --extra dev --extra ml
uv run frailty-engine sample
uv run python scripts/verify_project.py --json
```

**Measured:** A passing verifier is software evidence only. Keep the expected
`clinical_gate: E-005 blocked` result visible in receipts and release notes.

### CLI and API

**Method:** Run a local sample or start the development API:

```powershell
uv run frailty-engine sample
uv run uvicorn frailty_engine.api:app --app-dir src
```

**Method:** Send a typed `POST /v1/assessments` request with a local
`patient_id` and `measurements` object. A complete request returns metrics,
trajectory, wellness, category, data-quality, model, and comparison-context
fields. An incomplete MVV returns a structured HTTP 422 response.

### SECA preview and overlay

**Method:** Parse a local export without uploading it:

```powershell
uv run frailty-engine seca examples/seca_tableview_fixture.csv
uv run frailty-engine assess-overlay <path-to-SECA.csv> --overlay frailty-assessment-overlay.json
```

**Method:** Treat observed SECA values as read-only in the handoff. Supply age,
sex, blood, history, and functional fields explicitly. Do not infer a missing
clinical field from an equipment row.

### Comparison and safe interpretation

**Method:** Compare only dated assessments for the same person and inspect
`comparison_eligibility` before using any aggregate value. A
`matched_items_only` report is not evidence of improvement. If the denominator
or item set changes, report the coverage change and do not call the movement a
health improvement.

**Method:** Use `action_effect_estimated: false`,
`clinical_or_lifespan_claim: false`, `reference_panel_production_ready`, and
the model readiness fields as hard interpretation boundaries.

**Method:** Keep patient exports, credentials, restricted rows, model
artifacts, and transient directories outside the repository and outside the
static Pages artifact.

## 11. Roadmap and investment case

**Method:** The next bounded tranche is a clinician/researcher measurement
review, not a new set of system-age numbers. It should complete IR0's clean
candidate work, run IR1 with the report contract, complete IR3 browser and
privacy evidence, and obtain statistical review of IR2.

**Method:** The musculoskeletal-first focus is intentional. The current
contract already contains phase angle, extracellular-water ratio, fat-free mass
index, skeletal muscle mass, grip strength, chair-rise time, BMI, waist, and
related FI items. A useful review of observed values and missingness can be
tested before investing in additional age models.

**Unverified:** The investment case improves only if intended users complete
the task safely, the report adds value over a manual review, and approved data
show that any model output adds useful information beyond simpler baselines.
If those tests fail, the stop rule is a measurement-only product rather than a
broader age-estimation surface.

**Method:** The durable work plan and owners are maintained in
[`ROADMAP.md`](../ROADMAP.md), the acceptance contract is in
[`GOAL.md`](../GOAL.md), and the criterion-level evidence is in
[`EVAL.md`](../EVAL.md).

## 12. References and appendices

### 12.1 Source map

**Measured:** The implementation and operational source map is:

- [`features.py`](../src/frailty_engine/features.py): canonical feature names,
  categories, and parser ranges.
- [`mvv.py`](../src/frailty_engine/mvv.py): assessment and training gates.
- [`fi.py`](../src/frailty_engine/fi.py): deficit coding and denominator.
- [`comparison.py`](../src/frailty_engine/comparison.py): versioned comparison
  context and unit/protocol identity.
- [`progress.py`](../src/frailty_engine/progress.py): comparison eligibility,
  matched-item coverage, and report construction.
- [`pipeline.py`](../src/frailty_engine/pipeline.py): assessment assembly.
- [`seca.py`](../src/frailty_engine/seca.py): local import and derivation
  provenance.
- [`MODEL_CARD.md`](MODEL_CARD.md), [`OPERATIONS.md`](OPERATIONS.md),
  [`PRIVACY_THREAT_MODEL.md`](PRIVACY_THREAT_MODEL.md), and
  [`SOURCES.md`](SOURCES.md): model, operations, privacy, and citation limits.
- [`INDUSTRY_READINESS_REVIEW.md`](INDUSTRY_READINESS_REVIEW.md): the critical
  readiness review and remaining evidence gaps.

**Evidence-informed:** The general method references, including accumulated
deficits, BIA measurement literature, public NHANES documentation, prediction
model reporting, and AI risk management, are listed in [`SOURCES.md`](SOURCES.md).
They support method selection and disclosure obligations, not validation of
this prototype.

### 12.2 Response schema and data dictionary

**Measured:** An assessment response contains `patient_id`, `metrics`,
`trajectory`, `wellness_report`, `category_reports`, `data_quality`,
`model_metadata`, and `comparison_context`. A progress response contains
`comparison_basis`, `comparison_eligibility`, matched-item range changes,
summary counts, and false action-effect/no-clinical-claim flags. Raw assessment
measurements are not echoed by the comparison report.

**Method:** `metrics.current_deficit_load_fi_details` is the authoritative place
for FI numerator, denominator, valid variables, and denominator strength.
`comparison_eligibility` is the authoritative place for item coverage,
changed units/protocols, blockers, and aggregate-readout eligibility.

### 12.3 Status vocabulary

**Method:** `Measured` means repository evidence, `Method` means design or
algorithm, `Evidence-informed` means cited but not product-proven, and
`Unverified` means open. `blocked` means required evidence is absent or failed;
it does not mean the underlying hypothesis is false. `development_fixture_only`
means software integration state, not clinical approval.

### 12.4 Reproducibility commands

**Method:** The minimum local receipt set is:

```powershell
uv run pytest -q
node --test --test-reporter=tap tests/site_parser.test.cjs
uv run ruff check src tests scripts
uv run ruff format --check src tests scripts
uv run python scripts/build_test_receipt.py --check
uv run python scripts/build_demo_data.py --check
uv run python scripts/verify_docs.py
uv run python scripts/verify_project.py --json
```

**Unverified:** These commands do not close IR1, IR3, IR4, IR5, IR6, IR7, or
E-005. They also do not by themselves prove that a clean candidate was
published or that the deployed Pages identity matches the reviewed source.
