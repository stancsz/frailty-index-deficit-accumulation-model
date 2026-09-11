# Clinician workflow study protocol

**Status:** protocol artifact only; no sessions completed  
**Purpose:** prepare the IR1 usability and interpretation study without
recruiting through the public demo

## Study question

**Unverified:** Can an intended clinician or clinical researcher use the
measurement-review report safely and efficiently compared with the current
manual review, while recognizing that numeric ages, clinical advice, and
treatment effects are unvalidated?

## Participants and safeguards

**Method:** Recruit at least five intended users who routinely review body
composition, laboratory, functional, or frailty-related measurements. Record
role and relevant experience without collecting patient identifiers. Do not use
real patient exports in the public Pages demo. Use the frozen synthetic task
bundle or a separately approved de-identified study fixture.

## Task script

**Method:** Each participant receives the same synthetic case and is asked to:

1. select the appropriate example or load the approved local fixture;
2. identify what was measured and which inputs are missing;
3. locate the FI numerator, denominator, and denominator caveat;
4. explain whether the age-equivalent value is clinically validated;
5. inspect the musculoskeletal-focused measurement and reference-band context;
6. export the report; and
7. explain what they would and would not discuss with a person.

**Method:** Time the task for five minutes, record assistance requests, and
score the required interpretation checks. Compare the same participant's task
time and interpretation errors with the existing manual workflow or its
closest approved analogue.

## Pass criteria from GOAL.md

**Method:** At least four of five participants must complete sample selection,
find missing inputs, interpret FI correctly, and export the report without
assistance in five minutes. All participants must recognize that ages and
clinical advice are unvalidated. These are proposed product gates, not
scientific thresholds.

## De-identified evidence form

**Method:** Store one row per session with:

| Field | Allowed content |
|---|---|
| session_id | Random study identifier, not a patient identifier |
| participant_role | Broad role category only |
| workflow | `tool` or `manual` |
| completion_seconds | Numeric duration or `not_recorded` |
| assistance_count | Integer |
| found_missing_inputs | `yes`, `no`, or `partial` |
| interpreted_fi_correctly | `yes`, `no`, or `partial` |
| recognized_age_boundary | `yes`, `no`, or `partial` |
| exported_report | `yes`, `no`, or `blocked` |
| safety_issue | De-identified description or `none_observed` |
| reviewer_notes | No patient data or free-text identifiers |

## Current result

**Measured:** No participant sessions, comprehension scores, task times, or
manual-workflow comparison are recorded in this repository. IR1 remains open.

**Method:** A future result must include the frozen task version, participant
count, de-identified rows, protocol deviations, reviewer, date, and pass/fail
decision. A failed threshold should narrow the product scope rather than be
hidden by changing the task retrospectively.
