# Production and value evidence, 2026-09-11

## Decision

This repository is **software-production-shaped, but not production-ready as a
clinical product**. The exact reason is not a judgment call: E-005 remains
blocked because there is no approved external cohort, clinical cutoff review,
validated uncertainty analysis, qualified clinical/statistical sign-off, or
completed intended-user study.

The repository also does **not** prove that it saves frontier-model tokens for
other tasks. It contains a deterministic frailty engine and local/static
showcase, not a frontier-model router, provider billing integration, token
counter, or matched-task allocation experiment. Any token-saving percentage
would therefore be fabricated unless measured in the system that owns those
tokens.

The mechanics are now implemented in
[`FRONTIER_TOKEN_MEASUREMENT.md`](FRONTIER_TOKEN_MEASUREMENT.md) with a
redacted paired-run schema, deterministic aggregate receipt, privacy checks,
and a synthetic fixture. The current receipt explicitly reports
`real_paired_runs: false`; its mechanics-only synthetic percentage is not a
production or provider result. Real evidence still requires owner-supplied
request-correlated token counts and independent quality adjudication.

## Reproducible engineering measurements

The real-data package also includes
[`CATEGORY_OVERLAP_RECEIPT_2026-09-11.json`](CATEGORY_OVERLAP_RECEIPT_2026-09-11.json),
which reports same-cycle participant overlap for the mapped categories without
emitting identifiers, raw rows, or measurements.
The cycle-separated [`REAL_DATA_INTAKE_2013_2014_RECEIPT_2026-09-11.json`](REAL_DATA_INTAKE_2013_2014_RECEIPT_2026-09-11.json)
also adds 17 official files covering 15 categories, including cognitive,
mental-health, sleep, activity, body, bone, blood, cardiovascular, immune,
metabolic, kidney, joint-history, and skin-questionnaire sources without
merging them into the 2011–2012 denominator. Fluid/BIA remains absent from
this cycle. Liver coverage also has a separate 2017–2018 `LUX_J.XPT` receipt
with 6,401 direct-elastography records, kept separate from the 2017–March 2020
pre-pandemic source.
The primary category package also has a field-level
[`CATEGORY_QUALITY_RECEIPT_2026-09-11.json`](CATEGORY_QUALITY_RECEIPT_2026-09-11.json)
covering all 17 categories. It counts missingness and candidate source
special codes without filtering values or claiming clinical validity.
Cycle-specific quality receipts cover the 2013–2014 package and the
2017–2018 liver package as well.
The representative [codebook review](NHANES_CODEBOOK_REVIEW_2026-09-11.json)
prevents generic special-code filtering from corrupting valid monitor values.
The full [codebook receipt](NHANES_CODEBOOK_RECEIPT_2026-09-11.json) covers 99
official source documentation pages or layouts across eight NHANES cycles.
The separate [2015-2016 intake receipt](REAL_DATA_INTAKE_2015_2016_RECEIPT_2026-09-11.json)
adds 15 official files with field-level counts for 15 categories. Its explicit
absence section records that BIA fluid, CFQ cognitive testing, and direct liver
elastography were not part of this cycle's mapped intake. This is stronger
longitudinal source evidence, not a harmonized all-category cohort or clinical
validation.
The separate [2017-2018 category receipt](REAL_DATA_INTAKE_2017_2018_CATEGORY_RECEIPT_2026-09-11.json)
adds 18 official files for 15 categories and records the missing BIA/CFQ
coverage explicitly. The direct liver elastography source remains separately
receipted as `LUX_J.XPT`.
The separate [2021-2023 category receipt](REAL_DATA_INTAKE_2021_2023_CATEGORY_RECEIPT_2026-09-11.json)
adds 15 official files for 12 categories and declares the missing examination
and cognitive sources instead of treating the reduced cycle as complete.
The companion [recent overlap receipt](RECENT_CATEGORY_OVERLAP_RECEIPT_2026-09-11.json)
shows same-cycle mapped intersections of 0 across 15 categories in 2013–2014,
1,095 across 15 categories in 2015–2016, 873 across 15 categories in 2017–2018,
and 1,360 across 12 categories in 2021–2023. These
are privacy-safe joinability measurements, not harmonized clinical cohorts.
The [category numeric coverage receipt](CATEGORY_NUMERIC_COVERAGE_RECEIPT_2026-09-11.json)
now verifies that all 17 current categories have at least one non-missing real
numeric source field and a positive unique-participant count. It exposes the
minimum and maximum field-level counts for each category, including sparse
categories such as cognitive and skin fields. It contains no identifiers, raw
rows, or measurements, and remains source coverage rather than clinical
validation.
The [cycle matrix](CATEGORY_CYCLE_MATRIX_2026-09-11.json) reconciles that
coverage by cycle: 17/17 categories in the primary multi-cycle package,
15/17 in 2005–2006, 13/17 in 2007–2008, 15/17 in 2013–2014, 15/17 in 2015–2016, 15/17 in
2017–2018, and 12/17 in 2021–2023. Declared
absences remain explicit, with no cross-cycle joins.
The [category quality summary](CATEGORY_QUALITY_SUMMARY_2026-09-11.json)
adds field-level missingness ranges and candidate special-code counts for all
17 categories without filtering or classifying values. Observed maximum
missingness reaches 100% for some sparse skin fields, 98.5% for some joint
fields, and 96.5% for some cognitive fields. These are source-quality facts,
not clinical eligibility or validity claims.
For the 2011–2012 cycle, the public-use demographic denominator is 9,756
participants. Mapped category coverage ranges from 17.292% for cognitive
testing to 95.972% for metabolic data, and the intersection of all 16 mapped
categories is 0 participants. This is a hard missingness and subsample result,
not a complete cohort claim.

Run from the repository root on Windows with the locked environment:

```powershell
uv run python scripts/verify_project.py --json
uv run python -m pytest -q
node --test tests/site_parser.test.cjs
```

Observed on 2026-09-11 in the working checkout:

| Metric | Observed result | Evidence boundary |
|---|---:|---|
| Canonical verifier checks | 20/20 passed | Software and documentation checks only |
The new [2005–2006 cycle receipt](REAL_DATA_INTAKE_2005_2006_CATEGORY_RECEIPT_2026-09-11.json)
adds 15 official XPT files with positive non-missing and unique-participant
counts across 15 categories. Cognitive CFQ and BIA fluid files were not usable
for that cycle and remain explicitly absent.

The [2007–2008 cycle receipt](REAL_DATA_INTAKE_2007_2008_CATEGORY_RECEIPT_2026-09-11.json)
adds 13 official XPT files with positive non-missing counts across 13
categories. Bone, cognitive, BIA fluid, and skin sources are explicitly absent
for that cycle.
The runtime catalog now carries explicit cycle coverage states for every
category, distinguishing `real_source_present` from `not_collected_in_cycle`
with a reason. This makes the application metadata agree with the receipts.

The [category distribution receipt](CATEGORY_DISTRIBUTION_RECEIPT_2026-09-11.json)
adds n, unique participants, and q05/q25/median/q75/q95 summaries for one
representative real field in all 17 categories. The cognitive, joint,
lifestyle, mental-health, and skin examples include coded public-use values,
which are not clinical reference intervals.
The runtime catalog links each category to its representative distribution
receipt, source file, and field without embedding participant values.

| Python tests | 176 passed | Local test suite; not clinical evidence |
| Node tests | 28 passed, 0 failed | Pages/parser contract only |
| Real loopback serving smoke | Passed | Health, fail-closed readiness, metrics, valid/invalid HTTP paths, headers and identifier non-echo |
| Locked dependency resolution | Passed | `uv lock --check`; not a security or uptime guarantee |
| Static quality checks | Ruff and format checks passed | Current checkout only |
| Clinical gate | E-005 blocked | No clinical-production claim permitted |

The canonical JSON receipt is intentionally not copied into this document:
rerun the command above to regenerate the machine-readable evidence from the
current checkout. A green result is meaningful only together with the exact
candidate identity and publication reconciliation required by IR0.

## Value that is currently demonstrated

The measurable value is bounded to deterministic review support:

- the 35-feature contract, provenance fields, missingness and FI denominator
  are represented in typed software contracts;
- incomplete assessments are rejected by the minimum viable vector rather than
  silently completed;
- the serving smoke exercises real HTTP behavior, including typed invalid input
  and fail-closed readiness;
- Pages and local SECA parsing are covered by executable tests;
- unsupported clinical age claims and unsupported comparison changes are
  withheld by contract.

These facts show reduced software ambiguity and repeatable local execution.
They do not show that a clinician is faster, more accurate, or more likely to
change a safe decision than with a manual workflow.

## Hard value test still required

The next valid value claim is an intended-user comparison, not a proxy metric.
Use the protocol in `docs/CLINICIAN_WORKFLOW_STUDY.md` and record, for each
participant and matched case:

1. task completion within five minutes;
2. interpretation accuracy for missing inputs and FI denominator;
3. recognition that age estimates and clinical advice are unvalidated;
4. elapsed task time and errors with the tool versus the participant's manual
   workflow;
5. assistance requests, unsafe interpretations, and report-export success.

The pre-registered target is at least 4 of 5 users completing the required
tasks independently and all 5 recognizing the research-only boundary. No such
results are present in this repository as of this evidence date.

## Frontier-token savings claim

To prove that this tool saves frontier tokens, a separate matched-task study
must capture, for the same task set and model policy:

- task success and human-quality score;
- frontier input and output tokens, including retries and failed attempts;
- number of frontier calls and wall-clock latency;
- local/tool compute and any human intervention;
- a predeclared baseline and confidence intervals across tasks.

The primary metric should be frontier tokens per successful task, with quality
and rework as guardrails. This repository currently has no trace schema or
experiment receipt for those quantities. Status: **unverified, not zero**.

## Release interpretation

The evidence supports the phrase “research-use-only software prototype with a
passing local software gate and real loopback HTTP smoke.” It does not support
“clinical production-ready,” “validated,” “safe for patient care,” or “saves
frontier tokens.” The exact candidate SHA, clean-clone install, remote CI,
published URL identity, human accessibility review, and intended-user study
remain separate release obligations.
