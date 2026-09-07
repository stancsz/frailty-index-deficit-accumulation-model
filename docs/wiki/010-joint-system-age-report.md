# 010 — Joint-health age-equivalent report planning

- **scope:** planning for a future joint-health card and any later named
  age-equivalent estimate.
- **status:** measurement-only planning; no numeric joint age is approved.
- **decided:** 2026-09-04
- **decision owner:** repository owner and qualified clinical/statistical
  reviewers

## Decision

Add `joint_health` as a separate measurement-only card under the existing
musculoskeletal-first strategy. Do not rename or replace `muscle_health`, and
do not emit a numeric joint age from the current feature set.

The current 35-feature contract provides only an `osteoarthritis` history flag
and `chair_rise_time`, which are insufficient to define a validated joint-age
construct. The new card therefore reports the available context, marks the
age-equivalent estimate as `withheld_unvalidated`, and makes the measurement
gap visible.

## Construct to resolve

Before collecting or modeling data, the project must decide whether “joint
age” means one of the following:

- joint function and mobility;
- osteoarthritis burden or symptom severity;
- imaging-defined structural degeneration; or
- a governed composite of structure, symptoms, and function.

These are different constructs. A function score, imaging grade, or history
flag must not be relabeled as a universal joint age.

## Candidate measurement package

The clinical owner should select a repeatable, joint-specific protocol. A
future package might include, as appropriate to the chosen construct:

- validated patient-reported measures such as WOMAC, KOOS, or HOOS;
- standardized gait speed, timed-up-and-go, chair-rise, stair, balance, or
  walking tests;
- joint-specific range-of-motion or strength measurements;
- clinically governed imaging and grading, if structural disease is the target;
- joint location, laterality, pain context, injury history, treatment history,
  and assessment date.

These are candidates for protocol review, not current supported inputs or a
claim that any one test measures joint age.

## Evidence gate

A numeric `system_specific_age_equivalent` remains blocked until joint health
has its own:

1. prespecified construct and target;
2. standardized measurement protocol and repeatability evidence;
3. target-population reference panel with device, unit, age, sex, and relevant
   subgroup handling;
4. patient-level leakage-controlled model evaluation;
5. calibration, uncertainty, and measurement-error analysis;
6. independent validation with subgroup and missingness sensitivity;
7. evidence of useful information beyond chronological age and simpler measures;
8. qualified clinical, statistical, data-governance, and product approval.

The current card has none of these approvals. It must keep
`point_estimate`, intervals, model identifiers, and reference-panel
identifiers null.

## Data availability

No joint-specific clinical dataset or treadmill dataset has been supplied in
the current repository. Treadmill or cardiorespiratory data would not, by
itself, define joint age. A new data source must preserve provenance, protocol,
units, dates, consent or permitted-use basis, missingness, and disclosure
controls before it can enter development or validation.

## Safe product language

The product may say that joint-health measurements are unavailable or
incomplete, identify which inputs are missing, and suggest discussion or
repeat-measurement with a qualified professional. It must not claim that an
exercise, supplement, procedure, or treatment lowers joint age, reverses
degeneration, prevents disease, or extends life.

## Implementation status

`src/frailty_engine/body_reports.py` now exposes a `joint_health` shell using
the existing withheld-age contract. It is engineering scaffolding only. The
roadmap item belongs to P3 scientific/data provenance and remains downstream
of the E-005 clinical evidence gate.

## Public Pages behavior

The public synthetic demo may show the two currently supported joint-context
inputs when supplied: osteoarthritis history and chair-rise timing. It must
render `joint_health.age_report.point_estimate` as `null` and
`withheld_unvalidated`, not as a score, a functional age, or a joint-age test.
The R-087/E-087 trust pass makes that distinction explicit on the Pages site.
