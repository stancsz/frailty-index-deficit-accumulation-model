# IR4 musculoskeletal protocol skeleton

**Status:** planning artifact only. This is not an approved protocol, statistical
analysis plan, clinical study plan, model, reference panel, or evidence of
clinical validity. No NHANES files are stored in this repository, no model is
fit by this document, and no numeric system age is authorized.

**Protocol ID:** `ir4-msk-almi-reference-v1`

**Decision owner:** clinical/data lead and statistician, both pending assignment

**Review state:** not reviewed or approved

Documentation authority: this dated planning artifact follows
[`PRODUCT_INTENT.md`](product-specs/PRODUCT_INTENT.md),
[`ARCHITECTURE.md`](../ARCHITECTURE.md), and [`GOAL.md`](../GOAL.md). It does
not authorize validation, numeric ages, clinical use, or E-005 closure.

## 1. Research question and boundary

Can a reproducible, age- and sex-stratified reference profile for appendicular
lean-mass index (ALMI) be assembled from a specified public NHANES examination
release, while preserving DXA quality flags, survey weights, missingness, and
the limits of the public-use files?

This protocol targets a measurement reference profile, not an outcome predictor.
It does not estimate lifespan, mortality risk, treatment effect, clinical risk,
or a person's system-specific age. Any future age-equivalent model would require
a separate target, reference panel, uncertainty method, external validation,
and qualified approval.

The first planned construct is **appendicular lean-mass index**:

```text
ALMI_kg_m2 =
  (left_arm_lean_excl_BMC_g + right_arm_lean_excl_BMC_g
   + left_leg_lean_excl_BMC_g + right_leg_lean_excl_BMC_g) / 1000
  / (standing_height_cm / 100)^2
```

The formula is a planned derivation. It must be checked against the selected
cycle codebooks, units, invalidity flags, and the public data before any result
is calculated.

## 2. Intended research use and population

- **Intended use:** research-only description of the distribution and observed
  measurement coverage of ALMI in the selected public survey cycle. Results may
  inform a future measurement-review protocol. They must not be used as a
  clinical cutoff, diagnosis, treatment recommendation, or patient-facing age.
- **Population:** noninstitutionalized NHANES participants aged 20 through 59
  years who are eligible for the selected 2011-2012 whole-body DXA component,
  have a valid cycle-reviewed height measure, and satisfy the approved quality
  and exclusion rules. The age range follows the DXX_G adult coverage and must
  be reconfirmed from the codebook before analysis.
- **Primary analysis unit:** one participant identified internally by `SEQN`.
  `SEQN` must never appear in a committed receipt, report, screenshot, or
  public artifact.
- **Primary target:** ALMI in `kg/m^2`, summarized by the prespecified age and
  sex strata. This is a measurement target, not a clinical endpoint.
- **Context measures:** combined grip strength in `kg`, height in `cm`, weight
  in `kg`, BMI in `kg/m^2`, DXA exam status, and component invalidity flags.
- **Optional structural context:** selected DXA BMD variables may be retained
  only as separately labeled measurements. They must not be merged into an
  ALMI score or relabeled as bone age.

## 3. Sources and access terms

The exact source files, URLs, expected units, missingness fields, weights, and
hash placeholders are recorded in
[`IR4_PUBLIC_DATA_MANIFEST_2026-09-10.json`](IR4_PUBLIC_DATA_MANIFEST_2026-09-10.json).
The selected release is NHANES 2011-2012. CDC documentation identifies DXX_G
as whole-body DXA, MGX_G as the grip test, BMX_G as body measures, and DEMO_G as
demographics and sample weights. The CDC data-user agreement and component
codebooks must be reviewed before any local retrieval.

Public release does not remove the need for governance. The manifest must be
populated with SHA-256 hashes, retrieval dates, codebook decisions, permitted
use, and local access controls before data are used. Raw files remain outside
the repository unless a separate terms and privacy review authorizes storage.

## 4. Eligibility and exclusions to review

The reviewer must approve the final cycle-specific rules before analysis:

1. Include adults in the stated age range with `RIDSTATR=2` and a valid DXX_G
   examination status.
2. Exclude pregnancy and every DXX_G exclusion or invalidity condition
   specified by the official cycle documentation.
3. Require finite, positive `BMXHT` and all four ALMI lean-mass components,
   unless a separately approved partial-measurement analysis is declared.
4. Exclude duplicate `SEQN`, impossible units or values, and rows failing the
   documented component-quality flags. Do not silently repair or impute values.
5. Retain a missingness ledger for each source variable and each derived
   component. Complete-case ALMI is a declared analysis subset, not evidence
   that missingness is random.
6. Retain grip-strength rows separately when `MGDCGSZ` is missing or the grip
   status indicates a one-hand or incomplete test. Do not substitute a missing
   grip value with ALMI.

## 5. Measurement, units, and survey design

- DXX_G lean measurements are expected in grams. The four source fields and
  their DXA invalidity flags are listed in the manifest.
- BMX_G standing height is expected in centimeters. The conversion to meters
  must be performed once and recorded in the derived-variable receipt.
- MGX_G combined grip strength is expected in kilograms. The source status and
  effort fields must be preserved before accepting the combined value.
- DEMO_G `WTMEC2YR` is the planned examination weight. The analyst must verify
  that it is the correct weight for the joined DXX_G and MGX_G analysis and
  record any component-specific rule before use.
- `SDMVSTRA` and `SDMVPSU` must be retained for survey-design review. The
  current repository adapter does not provide a reviewed complex-survey
  variance estimator, so no inferential result may be presented as weighted
  population evidence until the variance method is approved.
- If weights or design fields cannot be reconciled across joined components,
  stop the analysis and report the failure rather than silently dropping the
  design.

## 6. Planned comparisons and metrics

The following are prespecified planning comparisons, not completed results:

- unweighted descriptive ALMI distributions versus the same summaries using
  the approved examination weights;
- age-and-sex-stratified reference summaries versus a simple age-only summary;
- complete ALMI coverage versus source-component coverage and missingness by
  age, sex, and survey status;
- ALMI and combined grip strength as separate, same-cycle descriptive measures;
  association is exploratory and does not establish clinical utility;
- a future reference model, if approved, must be compared with a simple
  age-and-sex reference baseline and must report error, calibration or coverage,
  subgroup support, missingness, and uncertainty.

For the primary descriptive estimates, report the denominator, valid numerator,
weighting state, design method, estimate, and 95% confidence interval or a
declared `not estimable` state. The planning precision target is a 95% interval
half-width of at most `0.5 kg/m^2` for the primary ALMI summaries when the
reviewed design and support permit it. This is a review threshold, not an
observed result. Failure to meet it means report the uncertainty and do not
promote the summary to a reference cutoff or age model.

## 7. Split, leakage, and sensitivity plan

- No participant may occur in more than one development, tuning, or holdout
  partition. `SEQN` is used only inside controlled local processing and is
  hashed or removed from receipts.
- A future reference-model fit must declare the cycle-level or participant-level
  split before looking at holdout outcomes. The current protocol does not fit a
  model.
- Required sensitivities are native missingness versus a prespecified
  complete-case analysis, approved versus unweighted summaries, component
  quality restrictions, age-band definitions, and the ALMI unit conversion.
- No cutoff, percentile, age-equivalent mapping, or performance claim is
  accepted from a sensitivity run alone.

## 8. Stop rules and approval gates

Stop before analysis if any of the following is unresolved:

- source URL, release, access terms, file hash, codebook version, or unit map;
- DXA eligibility, pregnancy, invalidity, grip status, or missingness rule;
- examination weight, strata, PSU, or variance method;
- participant-level split and leakage controls;
- qualified clinical/data/statistical review of the construct and intended use.

The protocol remains `not approved` until the clinical/data lead and statistician
sign a dated review record. A populated manifest, public-data receipt, or green
software test cannot satisfy E-005. Numeric system ages remain withheld.

## 9. Required future receipts

Before this protocol can feed IR5 or a product claim, retain:

1. the populated manifest and exact source hashes;
2. the codebook and unit/sentinel review;
3. an input receipt containing counts and missingness but no raw identifiers;
4. the approved survey-design and variance method;
5. the frozen split and sensitivity records;
6. descriptive and model results with denominators and uncertainty;
7. independent statistical and clinical review decisions; and
8. an explicit decision that the result does or does not justify any next
   product claim.

**Current decision:** preparation may continue. Data acquisition, fitting,
validation, numeric ages, clinical use, and E-005 closure are not authorized.
