# Statistical comparison review worksheet

**Status:** reviewer worksheet only; no statistical sign-off recorded

**Review package candidate:** temporary local candidate
`5dd24112f6582c211b4c93b505db61c2c1e66b26`

**Synthetic fixture:** `docs/demo-data.json`, SHA-256
`c2ff76eb5fd1d8eac7926d54a79959254ada7be13d4b7aac53820be4659f1e7d`

**Boundary:** this worksheet tests whether coverage and provenance changes are
reported honestly. It does not validate a clinical model, infer an intervention
effect, or approve any age output. A reviewer must use the frozen candidate and
record the actual observed response, not fill blanks from the expected result.

## Reviewer instructions

1. Use the same synthetic fixture and candidate identity for every case.
2. Record the exact input change, source units, protocol and artifact/panel
   identity before interpreting a comparison.
3. Mark a case `not_run` when the required reviewer or input is unavailable.
4. A changed denominator, item set, protocol, unit, cutoff, model hash, or
   reference-panel hash must block an aggregate health-improvement statement.
5. A passing software test is evidence of implementation behavior only. The
   statistician decides whether the comparison is interpretable.

## Case matrix

| Case | Input change | Required role | Expected safe behavior | Actual result | Status | Evidence / note |
|---|---|---|---|---|---|---|
| C-001 | Balanced synthetic baseline | Statistician | Record FI numerator, denominator, measured and missing items, units, model hash and panel hash before comparing |  | `not_run` |  |
| C-002 | Add only normal creatinine `0.9` in the canonical unit | Statistician | Denominator changes from 13 to 14 and FI changes from 0.0769 to 0.0714 in the known regression; aggregate comparison must be withheld or labeled coverage-only |  | `not_run` |  |
| C-003 | Add abnormal `cancer=1`, then remove it | Statistician | Show the changed item set and coverage; do not call the aggregate movement health improvement; reverse removal must remain explicit |  | `not_run` |  |
| C-004 | Change a shared measurement unit or protocol identity | Statistician and domain reviewer | Mark aggregate comparison ineligible until a reviewed conversion or protocol equivalence exists |  | `not_run` |  |
| C-005 | Change model artifact, reference-panel hash, or cutoff identity | Statistician and release reviewer | Withhold aggregate delta and expose the identity blocker; do not compare unlike releases |  | `not_run` |  |
| C-006 | Remove required inputs or submit malformed values | Clinician reviewer and statistician | Preserve missingness or reject the input; never fabricate a value or turn a partial preview into an assessment |  | `not_run` |  |

## Acceptance questions

The reviewer must answer each question in the result record:

- Were unchanged overlapping measurements identified separately from added or
  removed items?
- Were numerator, denominator, coverage, units, protocol, model identity,
  panel identity, and cutoff identity visible before interpretation?
- Did the output withhold an unsupported aggregate delta?
- Could a clinician mistake a coverage change for improved health?
- Were missing values preserved and malformed inputs rejected?
- Does the comparison remain descriptive and research-only?

## Closeout record

| Field | Entry |
|---|---|
| Reviewer role and name |  |
| Review date |  |
| Candidate SHA |  |
| Fixture SHA |  |
| Cases completed |  |
| Cases not run and why |  |
| Defects opened |  |
| Statistical decision | `not_submitted` |
| Clinical interpretation decision | `not_submitted` |

No row in this worksheet is evidence until a named reviewer records the actual
result and the candidate identity is confirmed unchanged.
