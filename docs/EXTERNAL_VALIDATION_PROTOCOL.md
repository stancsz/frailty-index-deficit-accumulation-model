# External validation and clinical review protocol (template)

> **Status: TEMPLATE — not an approved protocol, not a clinical study plan, and not
> a claim of production readiness.** This file is a structured checklist and
> specification skeleton for the eventual external-validation and clinical-review
> work that will be required before any production or clinical use. It contains
> placeholders only. **No real external cohort, no real human subjects, no real
> review record, and no real results are included in this template.** A populated
> version of this template must not be treated as approved evidence and must not
> satisfy `E-005` in `EVAL.md` on its own.

---

## 1. Purpose, scope, and the decision to be made

### 1.1 Purpose

This template specifies the evidence a future external-validation and clinical-
review study must produce for the Clinical Frailty Index (FI) / biological-age
engine described in [`GOAL.md`](../GOAL.md) and [`docs/MODEL_CARD.md`](MODEL_CARD.md).
It separates the *software validation* already covered in `EVAL.md` (E-001
through E-059, with the exception of E-005) from the *clinical and model
approval* work that is still blocked (E-005).

### 1.2 Intended use (placeholder, to be re-stated by the clinical reviewer)

- **Intended use statement** (TBD by reviewer): _[Insert a one-paragraph
  intended-use statement in plain language. Example skeleton: "The engine is
  intended to be used as a wellness/age-equivalent summary for adult patients
  in <clinical setting>, with input from a <SECA mBCA device family> body-
  composition scan and a routine blood draw, to support a discussion between
  the patient and a qualified clinician. It is **not** intended to diagnose,
  screen for, or predict any specific disease, to estimate lifespan, to
  estimate treatment effect, or to replace professional judgment."]_
- **Target population** (TBD): _[e.g., community-dwelling adults aged 40–79
  with at least one routine annual health assessment in the cohort window.]_
- **Target device / measurement setting** (TBD): _[e.g., SECA mBCA 515/514
  with firmware <version>, taken in the morning after an overnight fast, in
  <clinic type>.]_
- **Target use setting** (TBD): _[e.g., adult wellness clinic; not
  emergency, inpatient, or pediatric settings.]_
- **Decision to be made** (TBD): _[The reviewer must state, in one sentence,
  whether a model with the frozen artifact, reference panel, and uncertainty
  method is **approved** for the stated intended use, **conditionally
  approved** with named conditions, or **not approved**. The decision must
  reference the external-cohort report, the cutoff review, and the uncertainty
  review by record id.]_

### 1.3 What this template is and is not

This template is **a checklist and specification skeleton**. It is not a study
protocol, not an IRB submission, not an SAP (statistical analysis plan), not a
clinical-investigation plan, not a regulatory submission, and not a clinical
recommendation. The populated version must be authored or co-authored by a
qualified clinical reviewer with statistical input.

---

## 2. Pre-conditions that must hold before external validation starts

The reviewer must confirm every box below before starting any external-cohort
analysis. A "no" answer is a blocker.

- [ ] The training cohort and training recipe are frozen in
      [`docs/TRAINING_MANIFEST_TEMPLATE.json`](TRAINING_MANIFEST_TEMPLATE.json)
      (or a successor populated manifest) with cycle versions, source SHA-256
      checksums, eligibility rules, missingness rules, BIA quality filters,
      survey-weighting plan, recipe parameters, and reproducibility hashes.
- [ ] The model artifact is hash-bound to its feature manifest and its
      reference-panel file via a populated
      [`docs/MODEL_APPROVAL.md`](MODEL_APPROVAL.md) sidecar. The reviewer must
      confirm that the **artifact SHA-256**, the **panel SHA-256**, the
      **exact 36 feature names** (35 inputs + calculated FI), the
      **reference-panel id**, the **uncertainty method/parameter**, the
      **approver field**, and the **evidence refs** all match the sidecar.
- [ ] The reference panel is **production-ready** (`production_ready: true`)
      and **not** `fixture_only`. A development fixture panel is not eligible
      for external validation.
- [ ] The intended use statement (Section 1.2) is approved and frozen before
      any cohort is unblinded against the model.
- [ ] The development/tuning cohort, the internal validation cohort, and the
      external evaluation cohort are disjoint at the patient level. Patient-
      level leakage checks are mandatory (Section 5).
- [ ] The endpoint, censoring rule, follow-up horizon, and analysis unit are
      frozen before analysis (Section 4).
- [ ] The age/sex/BMI training-anchor contract is preserved exactly as
      documented in `GOAL.md` §2 ("Notes"). The survival training frame
      continues to use only `age`, `sex`, and `bmi` as row-eligibility
      anchors, with optional missing values preserved as native `NaN` for
      XGBoost's sparsity-aware split finding. **This is a leakage-control
      contract for training, not a relaxation of the assessment MVV.** The
      assessment MVV enforced at the API gateway (age, sex, BMI, phase
      angle, ECW/TBW, ≥ 6 blood variables including glucose or HbA1c, ≥ 4
      history variables) remains in force at inference time.

---

## 3. Data-source identity (to be frozen in the populated manifest)

> The placeholders below mirror `docs/TRAINING_MANIFEST_TEMPLATE.json`. They
> must be replaced with the actual identifiers in the populated version. Do
> not invent numbers here.

| Field | Placeholder (replace in populated version) |
| :--- | :--- |
| External-cohort name / accession | _[e.g., CLSA Comprehensive cohort, DRUM data release <id>]_ |
| Data access approval / IRB reference | _[id]_, _[date]_ |
| Data-use agreement scope | _[Permitted use, redistribution, linkage]?_ |
| Cohort cycle / window | _[e.g., 2012–2018 baseline, follow-up through <date>]_ |
| Cohort sample size (N, after eligibility) | _N = ?_ |
| Cohort ethnicity strata available | _[list with definitions]_ |
| Cohort sex strata available | _[list with definitions]_ |
| Cohort age range available | _[min, max]_ |
| Cohort source SHA-256 / file manifest | _[list with checksums]_ |
| Cohort source retrieved at | _YYYY-MM-DD_ |
| BIA / body-composition device family in cohort | _[e.g., SECA mBCA 515, or device used to define the cohort's transfer panel]_ |
| Reference panel id used at inference | _[must match `MODEL_VECTOR_FEATURE_NAMES` panel id in sidecar]_ |
| Reference panel file SHA-256 | _[must match `reference_panel_sha256` in sidecar]_ |
| BIA transfer-panel identity (if cohort device ≠ SECA) | _[Record the transfer panel used to normalize the cohort to the same z-score space as the training anchor.]_ |

**BIA transfer-panel identity must be frozen before analysis.** The model
trains and infers strictly on SECA-anchor z-scores (Phase Angle, ECW/TBW,
FFMI) per `GOAL.md` §1. If the external cohort was collected on a different
device family, the reviewer must specify which published or licensed transfer
panel is used, how the device era is documented, and how units and age/sex
bands are reconciled. The published SECA reference panels (e.g., Peine et al.,
2013; Bosy-Westphal et al., 2017) listed in [`docs/SOURCES.md`](SOURCES.md)
are the current starting point; they are **not** an embedded table inside
this engine and must be supplied, hashed, and approved as part of the
production panel.

---

## 4. Cohort eligibility, index date, endpoint, censoring, and horizon

The reviewer must freeze each item below in writing before opening the
external-cohort dataset. Any post-hoc change is a protocol deviation and must
be re-reviewed.

### 4.1 Eligibility and exclusions

- [ ] **Inclusion rules** (frozen list, with cycle-specific notes): _[…]_
- [ ] **Exclusion rules** (frozen list): _[…]_
- [ ] **Duplicate-patient handling**: Reject duplicate `patient_id` /
      `SEQN` values; do not silently deduplicate.
- [ ] **Pregnancy / device-incompatible rules**: _[…]_
- [ ] **BIA quality filters** (e.g., `BIDFIT` accepted codes, if any): _[…]_
- [ ] **Survey / sampling design** (if applicable): _[Complex survey?
      Record strata, PSU, weight field, replicate method, software.]_
- [ ] **Patient-level fit/holdout** is disallowed for the external cohort:
      every external row is evaluated, never re-used for tuning.

The software declaration for this review is the versioned
`SurveyDesign` value object (`schema_version: "1"`, `weight_name`,
`weight_kind`, `strata`, `psu`, and `replicate_pattern`). `case_weight` may be
passed to the native development adapter as an XGBoost DMatrix case weight;
`replicate` and `stratum` are protocol metadata only until a reviewed complex-
survey adapter exists. External-validation metrics and calibration bins remain
unweighted in the shipped harness and must carry `weighting_applied: false`.
The reviewer must set `design_reviewed: true` only after confirming the
cycle-specific field mapping and approved variance method outside this adapter.

### 4.2 Index date

- [ ] **Index date definition**: _[e.g., date of MEC examination; date of
      consent; date of first valid SECA scan with complete MVV.]_
- [ ] **Index date for survival duration**: must match the source-defined
      duration field. NHANES uses the MEC examination as the anchor
      (`PERMTH_EXM`); if the cohort uses a different anchor, record it.

### 4.3 Endpoint and censoring

- [ ] **Primary endpoint** (TBD): _[e.g., all-cause mortality; composite
      of <events>; non-fatal <event>. State the code list / ICD mapping and
      version.]_
- [ ] **Event indicator mapping** (TBD): _[`1 = event`, `0 = censored`]_
- [ ] **Censoring rule** (TBD): _[e.g., administrative censoring at
      <date>; loss-to-follow-up at last known contact; competing-risk
      handling if applicable.]_
- [ ] **Duration unit** (TBD): _[Years. Must match the model's canonical
      year contract.]_
- [ ] **Disclosure-control review**: Public-use linked-mortality files may
      perturb follow-up or cause-of-death values (see `SOURCES.md`). The
      reviewer must document whether the chosen endpoint remains
      appropriate after disclosure control and whether the cohort source
      is public-use or restricted-access.

### 4.4 Follow-up horizon

- [ ] **Primary analysis horizon**: _[e.g., 5 years; 10 years.]_
- [ ] **Follow-up sufficiency guard**: Calibration bins must be estimable;
      an all-early-censored cohort at the requested horizon must block the
      horizon-level calibration report, not silently substitute a shorter
      horizon.
- [ ] **Second horizon (sensitivity)**: _[e.g., 3-year and 10-year]_ if
      follow-up supports it.

---

## 5. Patient-level leakage checks (mandatory)

The reviewer must run all of the following before any metric is reported.
A leakage finding is a stop-condition (Section 10).

- [ ] **Patient-id overlap**: Zero overlap between external-cohort
      `patient_id` values and any row in the training cohort, the internal
      validation cohort, the tuning cohort, and the deterministic
      `split_survival_rows` fit/holdout partitions used to produce the
      loaded artifact.
- [ ] **Household / family overlap** (if the cohort uses household ids):
      Zero overlap between external cohort and any training/validation
      household id.
- [ ] **Site / clinic overlap**: Document whether external-cohort sites
      overlap with training sites. If yes, justify or stratify.
- [ ] **Time overlap**: External cohort index dates must not pre-date the
      training cohort's last follow-up update for shared sites, unless
      explicitly justified.
- [ ] **Feature-derivation overlap**: If any feature in the model is
      derived from the same upstream source as a training feature, document
      the derivation path and confirm that no target leakage is possible
      (e.g., a feature derived from a future event is forbidden).
- [ ] **Split-helper provenance**: If `split_survival_rows` is used, record
      the seed, hash, partition sizes, and event/censor support. The
      `run_training_split_smoke.py` runner is a leakage-control aid; it is
      **not** the prespecified clinical split and must not be cited as
      external validation.
- [ ] **Receipt**: A signed patient-overlap report (no identifiers) is
      attached to this protocol as Appendix A.

---

## 6. Feature contract and missingness rules

The external-cohort feature contract must match the artifact's persisted
feature manifest exactly. The 36-column contract (35 named inputs plus
calculated FI) is generated from the single-source vector contract
`MODEL_VECTOR_SOURCE_FEATURE_NAMES` (see `MODEL_CARD.md`). Any column
mismatch is a stop-condition.

The serving adapter contract is equally fixed: validation calls
`ModelAdapterProtocol.predict_for_assessment(age, encoded_vector)` with the
same encoded 36-column order used by assessment serving. A predictor that only
exposes the legacy raw FI/z-score call is not an eligible validation adapter.

- [ ] **Feature manifest match**: The 36 names and their order match the
      model artifact and the approval sidecar byte-for-byte.
- [ ] **Unit normalization**: Document units per feature, conversion
      formulae, and reviewer for every mapped measurement.
- [ ] **Missingness sentinel audit**: List every cohort-specific missing-
      value sentinel and the recoding rule. Unlisted codes must be
      rejected, not silently coerced.
- [ ] **MVV enforcement at inference**: A row that fails the assessment MVV
      is rejected by the API with `InsufficientDataError`. The external
      cohort analysis must report how many rows were rejected for MVV
      failure, and must evaluate metrics only on MVV-passing rows unless
      a prespecified sensitivity analysis covers the MVV-failing subset.
- [ ] **Native NaN handling for optional features**: Optional features
      remain `NaN` for XGBoost's native `missing` parameter. No MICE or
      silent complete-case selection is permitted without a prespecified
      sensitivity run.
- [ ] **Per-feature missingness report**: Counts and rates per feature,
      overall and by subgroup (Section 7), are recorded.

---

## 7. Reporting obligations

The populated protocol must produce a written external-validation report
that includes every item below. The current software already implements
some of the engineering plumbing; this template does not pre-fill numbers
and does not invent thresholds.

### 7.1 Denominators (required for every metric)

- [ ] `rows_received`, `rows_evaluated`, `rows_excluded` and the aggregated,
      privacy-safe `row_exclusion_counts` reasons.
- [ ] Number of observed events, number of censored rows, event fraction,
      mean / median follow-up time (with unit).
- [ ] MVV-pass / MVV-fail counts and the missingness breakdown.
- [ ] Per-feature missing counts and rates (overall and by subgroup).
- [ ] Effective comparable-pair denominator for concordance (the
      implemented software already exposes
      `concordance_comparable_pairs`; the report must report it, because
      row count is not the same as evaluable survival-pair support).

### 7.2 Subgroup support (required, not optional)

- [ ] Standard sex strata (`female`, `male`, `unknown`/`other` if present).
- [ ] Standard age bands (`18–39`, `40–59`, `60–79`, `80+`).
- [ ] Standard ethnicity strata (cohort-specific; if the cohort uses
      different categories, extend the manifest and report them by name).
- [ ] Each subgroup row must report: row count, observed events, censored
      rows, event fraction, mean follow-up, and concordance **only when
      estimable**. Sparse strata (e.g., zero events, zero comparable
      pairs) must remain descriptive; they must not be hidden behind an
      aggregate score and must not be labeled "validated", "fair", or
      "safe".

#### 7.2.1 Prespecified minimum support fields (RECORD_AFTER_STATISTICAL_REVIEW)

> **Additive specification, future E-005 obligation.** This subsection
> does not invent clinical minimums. The current engineering harness
> (`validate_external_cohort` and the deterministic
> `scripts/run_external_validation_smoke.py` runner) **reports** support
> fields; it does **not** choose clinical minimums. Numeric thresholds
> below are placeholders to be replaced by the prespecified statistical
> analysis plan (SAP) after statistical review.

The prespecified SAP must record, for each reported subgroup, the
following minimum support fields before any subgroup metric is
interpreted. The checklist is a reporting obligation; the chosen minimums
themselves are a SAP decision and must not be inferred from the
engineering harness:

- [ ] **Minimum rows** per subgroup: _`RECORD_AFTER_STATISTICAL_REVIEW`_
      (placeholder; the SAP must state a numeric minimum or an explicit
      "no minimum").
- [ ] **Minimum observed events** per subgroup:
      _`RECORD_AFTER_STATISTICAL_REVIEW`_ (placeholder; the SAP must
      state a numeric minimum or an explicit "no minimum").
- [ ] **Minimum comparable pairs** (survival-pair support for concordance)
      per subgroup: _`RECORD_AFTER_STATISTICAL_REVIEW`_ (placeholder; the
      SAP must state a numeric minimum or an explicit "no minimum";
      the engineering harness already exposes
      `concordance_comparable_pairs`, which is the row-count-irreducible
      denominator).
- [ ] **Minimum valid bootstrap replicates** for any reported concordance
      interval per subgroup: _`RECORD_AFTER_STATISTICAL_REVIEW`_
      (placeholder; the SAP must state a numeric minimum or an explicit
      "no minimum"; the engineering harness already exposes
      `concordance_ci_valid_replicates` vs
      `concordance_ci_requested_replicates` and withholds the interval
      when sparse, with `concordance_ci_status` recording why).

The subgroup report (§9.2) must list, for every subgroup, the
prespecified minimums and the observed support, side-by-side, so that
sparse subgroups are visible by name and by number. A subgroup that
falls below any prespecified minimum is reported descriptively only;
its concordance cell remains `NA` and its bootstrap interval is
**withheld**, consistent with the sparse-stratum rule in §9.2.

**Engineering vs clinical boundary:** the shipped engineering harness
exposes row counts, observed events, comparable pairs, and valid
bootstrap replicates for every reported subgroup. It does **not**
implement clinical minimums and must not be cited as if it did. The SAP
is the only place where the numeric minimums above are set.

### 7.3 Discrimination

- [ ] Concordance index (Harrell's C) overall and by subgroup.
- [ ] **Support-aware bootstrap uncertainty** for concordance: report
      requested replicates, valid replicates, percentile interval, and
      the effective comparable-pair denominator. Also report
      `concordance_ci_status`, which distinguishes an emitted interval from
      no records, no comparable pairs, or insufficient valid replicates. The interval is withheld
      when resampling support is sparse (the implemented software already
      follows this rule). **This is an engineering review aid; it is not
      a calibrated clinical confidence interval without an approved SAP.**
      Record `concordance_ci_construction` as `bootstrap_percentile` only when
      the percentile interval is emitted, otherwise `none_withheld`.

The engineering report also serializes `subgroup_support_warnings` for each
observed sex, age-band, or ethnicity subgroup whose reported concordance
support is incomplete. Each entry contains a `dimension`, a `label`, and one
or more concrete reasons: `no_events`, `no_comparable_pairs`, or
`insufficient_valid_replicates`. This is an explicit review signal for why a
subgroup metric or interval is incomplete; it does not create a clinical
minimum, classify a subgroup as validated, fair, or safe, or replace the
prespecified SAP thresholds. An empty list means only that no enumerated
support warning was produced for the current computed groups.

### 7.4 Calibration

- [ ] Probability calibration (10-year mortality probability, or the
      chosen horizon): binned observed vs predicted, with a censoring-
      aware Kaplan–Meier horizon estimator. The implemented calibration
      bins fail closed when the horizon cannot be estimated; report
      `eligible_rows` and `calibration_rows` separately.
- [ ] Homeostatic-deviation-score calibration: same protocol, plus a
      plot artifact (the implemented `homeostatic_deviation_calibration.png`
      is the harness artifact; the populated report must use the
      approved cohort's plot).
- [ ] Biological-age calibration (if the biological-age mapping is
      reported): same protocol, plus a plot artifact
      (`biological_age_calibration.png`).
- [ ] FI denominator caveat: report FI score distribution by valid-
      variable count, because FI is sensitive to measurement completeness
      (see `GOAL.md` §3).

#### 7.4.1 Outcome-level performance metrics (future E-005 checklist)

> **Additive checklist, future E-005 obligation.** The metrics listed
> below are **not** computed, evidenced, or implied by the synthetic
> `examples/external_validation_synthetic.json` fixture or by the
> deterministic `scripts/run_external_validation_smoke.py` runner. The
> synthetic fixture exists only to exercise the engineering harness and
> is explicitly `clinical_use: forbidden`. The checklist below
> enumerates the outcome-level performance metrics the future
> external-validation report must include when they are claimed. It
> does not invent thresholds and does not pre-fill values.

When any of the following outcome-level performance metrics are claimed
in the populated external-validation report, the prespecified SAP and
the reviewer must satisfy every item below. A claim that omits any of
these items is incomplete and must not be presented as a complete
validation result.

- [ ] **Brier score (overall and by subgroup)** for the chosen primary
      horizon, reported with the same denominators (rows, observed
      events, valid bootstrap replicates where applicable) as the
      discrimination and calibration sections. **Survival analogue:**
      when the primary endpoint is right-censored, an approved survival
      analogue of the Brier score (e.g., a Graf–Schumacher or
      Gerds–Schumacher time-dependent Brier score, or another
      prespecified IPCW-weighted score) must be reported in place of a
      naive Brier score; the chosen analogue and its reference must be
      named by the SAP.
- [ ] **Calibration-in-the-large** for the chosen primary horizon,
      overall and by subgroup, with the eligible vs calibration-row
      denominators reported separately and a censoring-aware
      Kaplan–Meier horizon estimator (or an approved alternative named
      by the SAP) used where the endpoint is right-censored.
- [ ] **Calibration slope / Integrated Calibration Index (ICI)** for
      the chosen primary horizon, overall and by subgroup. The chosen
      slope estimator (logistic recalibration slope for binary
      endpoints; survival analogue for right-censored endpoints) must
      be named by the SAP. The reported slope is a calibration
      diagnostic, not a clinical-utility claim.
- [ ] **Decision-curve / net-benefit analysis** is reported **only**
      when both of the following hold:
    - The prespecified SAP names the target clinical decision (e.g.,
      "refer for further assessment at or above predicted probability
      `p*`").
    - The prespecified SAP names the threshold range over which net
      benefit is reported (e.g., `p* ∈ [_RECORD_AFTER_STATISTICAL_REVIEW_]`).
  This template does **not** invent thresholds. A decision-curve or
  net-benefit plot presented without a prespecified decision and
  prespecified thresholds is **not** an accepted outcome-level
  performance metric for this protocol and must be withheld from the
  populated report.

**Engineering vs clinical boundary:** the engineering harness
(`validate_external_cohort` and the deterministic
`scripts/run_external_validation_smoke.py` runner) reports
concordance, calibration bins, comparable-pair support, and
support-aware bootstrap intervals against the synthetic fixture. It
does **not** compute or evidence the Brier score (or its approved
survival analogue), calibration-in-the-large, calibration slope/ICI,
or decision-curve/net-benefit. These metrics are future E-005
obligations and are not computed or evidenced by the synthetic
fixture. The synthetic fixture's explicit `clinical_use: forbidden`
provenance must remain visible wherever a populated report cites
this protocol.

**Machine-readable withholding contract:** `ValidationReport` exposes
`outcome_metric_status` at the overall level and in every computed subgroup
record. Each named metric has `value: null`,
`status: "not_implemented_pending_sap"`, and
`construction: "none_withheld"`, plus a reason and `review_gate: "E-005"`.
This is an explicit absence marker, not a metric estimate. It prevents a
consumer from treating an omitted value as zero or interpreting the current
engineering harness as outcome-level clinical validation. The field may be
changed to an emitted numeric result only after the checklist above is frozen
in a prespecified SAP and run on an approved external cohort with reviewer
sign-off; no numeric thresholds are supplied by this repository.

### 7.5 Uncertainty

- [ ] Uncertainty method, parameter, and provenance are recorded and
      match the approval sidecar. The shipped development predictor
      sets `uncertainty_validated: false` and returns a nullable `ci_95` as
      `null`; a numeric interval is populated only for an approved predictor
      with cohort-validated uncertainty. **Do not represent an unvalidated
      interval as a clinical confidence interval.**
- [ ] Bootstrap interval reporting must follow the support-aware rules
      in §7.3.

### 7.6 Clinical-utility analysis (if claimed)

- [ ] Decision-curve analysis or net benefit at prespecified thresholds
      must be reported **only** if the prespecified SAP names the
      thresholds and the target decision. This template does **not**
      invent thresholds.

### 7.7 Sensitivity analyses (pre-specified obligations)

- [ ] Native missing-value handling vs a prespecified complete-case
      analysis.
- [ ] FI denominator strata (e.g., low / medium / high valid-variable
      count).
- [ ] Unweighted vs approved survey-weight analysis (if a survey weight
      is approved).
- [ ] Censoring-aware horizon calibration at the primary horizon and at
      a second horizon, if supported by follow-up.
- [ ] Reference-panel sensitivity: results when the cohort is normalized
      against the approved panel and against an alternative published
      panel, if available.
- [ ] Subgroup reweighting / transportability analysis, if the cohort
      population differs materially from the training population.

### 7.8 Limitations the current software cannot remove

These are limitations of the shipped implementation; the populated
report must acknowledge them, not paper over them:

- The default predictor and BIA panel are explicitly development
  fixtures; the populated report must reference the **approved**
  artifact and panel by SHA-256, not the development fixtures.
- Calibration bins use a Kaplan–Meier horizon estimator and fail closed
  on unestimable bins. This is a software safeguard, not proof that the
  censoring assumptions or the target-cohort calibration are valid.
- Survey-weight handling, where present, is pass-through to XGBoost
  DMatrix case weights; complex-survey variance estimation is **not**
  implemented by the adapter and must be supplied by the reviewer.
- The shipped biological-age and trajectory `ci_95` fields are nullable and
  remain `null` on unvalidated paths. A numeric interval is **not a calibrated
  clinical confidence interval until an approved uncertainty analysis is on
  file**.

---

## 8. Reproducibility artifact checklist

The populated release record must include every item below. A "no"
answer is a stop-condition.

- [ ] Frozen training manifest (cycle versions, source SHA-256 checksums,
      eligibility rules, missingness rules, BIA quality filters, weight
      plan, recipe, reproducibility hashes).
- [ ] Immutable model artifact and its SHA-256.
- [ ] Approved reference-panel file and its SHA-256.
- [ ] Approval sidecar (artifact hash, panel hash, 36 feature names, model
      id, uncertainty method/parameter, approver, evidence refs).
- [ ] External-cohort access approval, data-use agreement, and source
      file manifest with checksums.
- [ ] External-validation report (this protocol's §7) as a single signed
      document with appendices.
- [ ] Calibration plot artifacts (probability, homeostatic-deviation,
      biological-age) generated from the approved cohort.
- [ ] Subgroup-support table (sex, age band, ethnicity, plus any
      study-specific strata).
- [ ] Sensitivity-analysis reports.
- [ ] Patient-overlap leakage report (Appendix A; no identifiers).
- [ ] FI cutoff review record (per `GOAL.md` §3) by named reviewer.
- [ ] Uncertainty-method review record by named reviewer.
- [ ] Reference-panel approval record (device, population, units,
      provenance, license).
- [ ] Release-receipt capture from `scripts/capture_release_receipt.py`,
      reconciled against fresh `/health` metadata.
- [ ] `scripts/validate_model_release.py` preflight passing for the
      exact model/panel/sidecar trio, with `clinical_status` still
      `requires_e005_external_validation_and_clinical_review`.
- [ ] Versioned commit / release identifier that ties the artifacts to
      the report.

---

## 9. Reporting shells (table shells; no numbers invented)

### 9.1 Overall discrimination and calibration

| Metric | Value | Support (denominator) | Source field |
| :--- | :--- | :--- | :--- |
| Concordance index (overall) | _[value]_ | _[comparable pairs]_ | `concordance_index`, `concordance_comparable_pairs` |
| Concordance 95% interval (bootstrap) | _[lo, hi or null]_ | _[valid replicates / requested]_ | `concordance_ci_95`, `concordance_ci_status`, `concordance_ci_construction`, `concordance_ci_valid_replicates`, `concordance_ci_requested_replicates` |
| 10-year probability calibration (primary horizon) | _[table]_ | _[eligible / calibration rows]_ | `calibration.probability_bins` |
| Homeostatic-deviation calibration | _[table]_ | _[eligible rows]_ | `calibration.homeostatic_deviation_bins` |
| Biological-age calibration (if reported) | _[table]_ | _[eligible rows]_ | `calibration.biological_age_bins` |

### 9.2 Subgroup support (sex, age band, ethnicity)

| Subgroup | N rows | Events | Censored | Event fraction | Mean follow-up (years) | Concordance | Concordance 95% interval |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Sex: female | _[N]_ | _[k]_ | _[N−k]_ | _[k/N]_ | _[years]_ | _[C or NA]_ | _[lo, hi or withheld]_ |
| Sex: male | _[N]_ | _[k]_ | _[N−k]_ | _[k/N]_ | _[years]_ | _[C or NA]_ | _[lo, hi or withheld]_ |
| Age: 18–39 | _[N]_ | _[k]_ | _[N−k]_ | _[k/N]_ | _[years]_ | _[C or NA]_ | _[lo, hi or withheld]_ |
| Age: 40–59 | _[N]_ | _[k]_ | _[N−k]_ | _[k/N]_ | _[years]_ | _[C or NA]_ | _[lo, hi or withheld]_ |
| Age: 60–79 | _[N]_ | _[k]_ | _[N−k]_ | _[k/N]_ | _[years]_ | _[C or NA]_ | _[lo, hi or withheld]_ |
| Age: 80+ | _[N]_ | _[k]_ | _[N−k]_ | _[k/N]_ | _[years]_ | _[C or NA]_ | _[lo, hi or withheld]_ |
| Ethnicity: _[name]_ | _[N]_ | _[k]_ | _[N−k]_ | _[k/N]_ | _[years]_ | _[C or NA]_ | _[lo, hi or withheld]_ |
| _[Additional study-specific stratum]_ | _[…]_ | _[…]_ | _[…]_ | _[…]_ | _[…]_ | _[…]_ | _[…]_ |

**Sparse-stratum rule:** if a subgroup has zero events, zero comparable
pairs, or fewer than the prespecified minimum support, the concordance
cell is left as `NA` (not a number) and the interval is **withheld**. The
sparse subgroup is reported descriptively, never as a fairness or safety
claim.

### 9.3 Feature missingness (overall and by subgroup)

| Feature | Overall missing rate | Sex: female | Sex: male | Age: 18–39 | Age: 40–59 | Age: 60–79 | Age: 80+ | Ethnicity: _[…]_ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| _[feature name]_ | _[%]_ | _[%]_ | _[%]_ | _[%]_ | _[%]_ | _[%]_ | _[%]_ | _[%]_ |

### 9.4 Sensitivity runs

| Sensitivity | Primary metric | Sensitivity value | Δ vs primary | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Native missing-value handling (primary) | Concordance | _[…]_ | — | — |
| Prespecified complete-case analysis | Concordance | _[…]_ | _[…]_ | _[…]_ |
| FI denominator high-completeness stratum | Concordance | _[…]_ | _[…]_ | _[…]_ |
| FI denominator low-completeness stratum | Concordance | _[…]_ | _[…]_ | _[…]_ |
| Unweighted analysis | Concordance | _[…]_ | _[…]_ | _[…]_ |
| Approved survey-weight analysis (if any) | Concordance | _[…]_ | _[…]_ | _[…]_ |
| Alternative reference panel (if available) | Concordance | _[…]_ | _[…]_ | _[…]_ |
| Primary horizon vs second horizon | _[…]_ | _[…]_ | _[…]_ | _[…]_ |

---

## 10. Reviewer, sign-off, and stop / rollback conditions

### 10.1 Reviewer and sign-off fields

| Field | Value |
| :--- | :--- |
| Clinical reviewer (name, role, affiliation) | _[…]_ |
| Statistical reviewer (name, role) | _[…]_ |
| Data-governance reviewer (name, role) | _[…]_ |
| Reference-panel reviewer (name, role) | _[…]_ |
| FI cutoff reviewer (name, role) | _[…]_ |
| Uncertainty-method reviewer (name, role) | _[…]_ |
| Review date | _YYYY-MM-DD_ |
| Review record id (links to evidence refs) | _[…]_ |
| Decision (approved / conditional / not approved) | _[…]_ |
| Conditions / mitigations (if conditional) | _[…]_ |
| Reviewer signature (or equivalent record) | _[…]_ |

### 10.2 Explicit stop / rollback conditions

The reviewer, the operator, or the data-governance lead must halt the
validation work and (if a release is already in flight) roll back per
[`docs/OPERATIONS.md`](OPERATIONS.md) §5 if any of the following is true:

- [ ] Patient-level overlap between the external cohort and any
      training/tuning/validation cohort is non-zero.
- [ ] The model artifact or reference panel SHA-256 does not match the
      sidecar, or the 36-column feature manifest does not match the
      artifact byte-for-byte.
- [ ] The reference panel is `fixture_only` or `production_ready: false`,
      or its `production_ready` / `fixture_only` flags are not explicit
      booleans (string or other truthiness-coerced values are forbidden;
      see `EVAL.md` E-039 and E-042).
- [ ] The MVV pass rate is below the prespecified minimum, or a large
      undocumented missingness pattern is discovered after unblinding.
- [ ] The cohort is administratively censoring everyone before the
      primary horizon, making the horizon-level calibration unestimable
      and the report's headline metric unsupported.
- [ ] A subgroup has its metric suppressed at the aggregate level, or a
      sparse stratum is presented as if it were a validated fairness or
      safety claim.
- [ ] The uncertainty method or its parameter is changed after the report
      is drafted, without restarting the §7 reporting pass.
- [ ] The intended-use statement is changed after cohort unblinding.
- [ ] The `scripts/validate_model_release.py` preflight exits non-zero
      against the exact model/panel/sidecar trio used in the report.
- [ ] The release-receipt capture (or its `--check`) fails to reconcile
      against fresh `/health` metadata, indicating the running
      configuration is not the configuration the report claims.
- [ ] Any clinical, data-governance, or ethics approval lapses, is
      withdrawn, or is found to have been scoped incorrectly.
- [ ] `/readyz` reports a blocker during a production-mode smoke (per
      `OPERATIONS.md` §3): traffic must not be admitted.

---

## 11. Boundary links (do not duplicate citations here)

This protocol reuses, rather than re-cites, the following documents in
this repository. The populated version must keep these links intact and
must not move text out of those documents into this template:

- Project goal and acceptance contract: [`../GOAL.md`](../GOAL.md)
- Evaluation ledger (EVAL criteria, including the blocked E-005): [`../EVAL.md`](../EVAL.md)
- Model card (intended use, model contract, credibility gates, known
  limitations): [`MODEL_CARD.md`](MODEL_CARD.md)
- Evidence and source boundary (citations for deficit accumulation, BIA
  transfer, SECA import, NHANES, FI cutoffs, biological age, and AI
  governance): [`SOURCES.md`](SOURCES.md)
- Model approval sidecar contract: [`MODEL_APPROVAL.md`](MODEL_APPROVAL.md)
- Training manifest template (source-of-truth shape for frozen training
  provenance): [`TRAINING_MANIFEST_TEMPLATE.json`](TRAINING_MANIFEST_TEMPLATE.json)
- Operations runbook (fail-closed readiness, release receipts, rollback,
  monitoring boundary): [`OPERATIONS.md`](OPERATIONS.md)

---

## 12. What this template does **not** prove

A populated version of this template, on its own, does **not** prove any
of the following. Each item below must be established by a separate,
human-authored, externally reviewed record before any production or
clinical use.

- **Clinical effectiveness, safety, or benefit.** Public NHANES data,
  the synthetic `examples/external_validation_synthetic.json` fixture,
  the deterministic `scripts/run_external_validation_smoke.py` runner,
  the `scripts/run_training_split_smoke.py` leakage-control smoke,
  passing software tests, the model-release preflight, and a trained
  XGBoost artifact do **not** demonstrate clinical effectiveness,
  fairness, or safety. The synthetic fixture is explicitly
  `clinical_use: forbidden` and exists only to exercise the engineering
  harness.
- **Calibration of the `ci_95` interval.** The shipped predictors set
  `uncertainty_validated: false` and return `ci_95: null`; the nullable field
  is not an engineering or clinical confidence interval. A numeric interval
  requires an approved predictor and cohort-based uncertainty analysis.
- **Generalization across devices.** The published SECA reference panels
  (Peine et al., 2013; Bosy-Westphal et al., 2017) are the current
  starting points, not embedded tables; an approved panel file with
  documented device, population, age bands, units, and provenance is a
  separate prerequisite.
- **Generalization across populations.** Subgroup metrics in a populated
  report are descriptive; they do not establish fairness, equity, or
  transportability to a deployment population that was not studied.
- **Regulatory clearance.** This engine is framed as a wellness and
  healthspan prototype in `GOAL.md` and `MODEL_CARD.md`. Nothing in
  this template constitutes regulatory clearance, CE marking, FDA
  clearance, or any equivalent claim, regardless of how the populated
  report is signed.
- **Approval of `E-005`.** `EVAL.md` records that `E-005` requires an
  approved external cohort, a clinical cutoff review, and production
  model evidence. A populated external-validation report is one input
  into that decision; the decision itself is made by a qualified
  clinical reviewer with the supporting governance process.
- **A substitute for an IRB / ethics approval, a data-use agreement, or
  a prespecified statistical analysis plan.** These governance artifacts
  are separate prerequisites and must be in place before any external
  cohort is unblinded against the model.
- **Approval of the wellness report's recommendations.** The wellness
  report is an auditable interpretation layer that explicitly does not
  estimate whether a suggested action will change biological age,
  lifespan, or a clinical outcome (`MODEL_CARD.md`).
- **Approval of the longitudinal comparison.** The
  `/v1/assessment-comparisons` route is a stateless, descriptive
  follow-up view; it does not establish action effect, causality, or
  change in biological age (`MODEL_CARD.md`).

**Bottom line:** Public NHANES data, the committed synthetic engineering
fixtures, passing software tests, and a trained artifact alone do **not**
satisfy clinical approval. A populated version of this template, signed
by the reviewers named in §10.1, is the *minimum* specification for the
external-validation and clinical-review evidence the repository currently
treats as the E-005 gate; it is not, by itself, that evidence.

---

*This file is a documentation template only. It is not a study protocol,
not an SAP, not an IRB submission, not a regulatory submission, not a
clinical recommendation, and not a claim of production readiness. The
populated version must be authored by a qualified clinical reviewer and
must reference real, approved cohort, cutoff, panel, and uncertainty
records by id.*
