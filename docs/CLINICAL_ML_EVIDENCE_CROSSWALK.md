# Clinical-ML evidence crosswalk (review artifact)

> **Status: additive review artifact.** This document maps the current
> repository to widely accepted clinical-ML reporting and governance
> frameworks so a reviewer can find what is already evidenced, what is
> only a template or deferred decision, and what is missing external
> evidence. **It does not claim that E-005 is satisfied.** It does not
> introduce new clinical evidence, regulatory conclusions, or numeric
> thresholds.

## Scope of this snapshot

- Repository at version v0.1.0 as observed on 2026-08-28.
- Development-only software posture: synthetic development predictor,
  synthetic BIA reference panel (`reference_panel_readiness:
  development_fixture_only`), and a Pages wellness handoff built from
  synthetic payloads.
- Deterministic Clinical Frailty Index (FI) with 0/0.5/1 deficit coding
  and explicit MVV enforcement at the API gateway.
- Synthetic external-validation fixtures (`examples/external_validation_synthetic.json`,
  `docs/demo-data.json`) and the deterministic
  `scripts/run_external_validation_smoke.py` runner, all
  `clinical_use: forbidden`.
- `docs/EXTERNAL_VALIDATION_PROTOCOL.md` and
  `docs/TRAINING_MANIFEST_TEMPLATE.json` are placeholders/templates
  (the manifest carries `status: "template"` and
  `production_ready: false`); they are specification skeletons, not
  evidence.
- Status of the [EVAL](../EVAL.md) ledger as observed: **E-005 is
  blocked**; E-001 through E-004 and E-006 through E-083 are software
  passing.
- The GitHub Pages publication path is a static documentation release;
  it does not deploy the assessment API or any model/patient artifact.

## How to read the rows

Every row splits the requested area into three labeled states so a
reviewer does not have to infer the boundary:

- **Software control** — a verified engineering behavior in the
  repository as of v0.1.0. Test or smoke evidence is cited.
- **Template / deferred decision** — a template, schema field, or
  reviewer obligation that intentionally contains placeholders or
  choices that are not yet made (for example
  [`EXTERNAL_VALIDATION_PROTOCOL.md`](EXTERNAL_VALIDATION_PROTOCOL.md)
  §7.2.1 or `MODEL_APPROVAL.md` approver fields).
- **Missing external evidence** — evidence that must come from outside
  this checkout: an approved cohort, a clinical reviewer, a real
  reference-panel file with documented device/population/units,
  external cohort access approvals, or a regulatory determination.

When the current repository already provides an artifact that covers a
framework line item, the cell links to that artifact instead of
duplicating the text.

## Framework sources

Primary sources cited verbatim as Markdown URLs:

- TRIPOD+AI, Collins et al., *BMJ* 2024 — <https://www.bmj.com/content/385/bmj-2023-078378>
- PROBAST+AI, Moons et al., *BMJ* 2025 — <https://www.bmj.com/content/388/bmj-2024-082505>
- External-validation guidance, Riley et al., *BMJ* 2024 — <https://www.bmj.com/content/384/bmj-2023-074820>
- Developing prediction models guide, Riley et al., *BMJ* 2024 — <https://www.bmj.com/content/386/bmj-2023-078276>
- GMLP, Health Canada / FDA / MHRA — <https://www.canada.ca/en/health-canada/services/drugs-health-products/medical-devices/good-machine-learning-practice-medical-device-development.html>
- Health Canada, *Pre-market guidance for machine learning-enabled medical devices* (page dated 2026-04-01) — <https://www.canada.ca/en/health-canada/services/drugs-health-products/medical-devices/application-information/guidance-documents/pre-market-guidance-machine-learning-enabled-medical-devices.html>
- Health Canada transparency principles for ML — <https://www.canada.ca/en/health-canada/services/drugs-health-products/medical-devices/transparency-machine-learning-guiding-principles.html>
- WHO, *Ethics and governance of artificial intelligence for health* (2021) — <https://www.who.int/publications/i/item/9789240029200>

> Framework coverage is selective. This crosswalk maps only the checklist and
> governance areas that this repository can currently evidence; it is not a
> substitute for the complete TRIPOD+AI or PROBAST+AI checklists.

Repository artifacts are linked with relative paths so the crosswalk
stays valid for the current checkout (e.g. `../MODEL_CARD.md` is
[`MODEL_CARD.md`](MODEL_CARD.md) at this depth).

---

## 1. Intended use, population, and the decision to be made

- **TRIPOD+AI Items 1 (title/abstract) and 3a (intended use).**
  - *Software control:* [`MODEL_CARD.md`](MODEL_CARD.md) "Intended
    use" section and [`GOAL.md`](../GOAL.md) §4 ("Regulatory framing"
    and "JSON API Schema") record the engine as a wellness / healthspan
    summary with neutral language and stripped prognostic terminology.
  - *Template / deferred decision:* [`EXTERNAL_VALIDATION_PROTOCOL.md`](EXTERNAL_VALIDATION_PROTOCOL.md)
    §1.2 ("Intended use (placeholder, to be re-stated by the clinical
    reviewer)") holds the placeholder for the populated intended-use
    statement, target population, target device/measurement setting,
    target use setting, and the one-sentence decision to be made.
  - *Missing external evidence:* a clinical reviewer–approved intended
    use statement, target population definition, and explicit
    approved / conditional / not-approved decision recorded against
    the frozen artifact/panel/uncertainty method.

- **TRIPOD+AI Item 3b (study type / role in clinical pathway).**
  - *Software control:* [`GOAL.md`](../GOAL.md) §5 product-surface
    scope and [`OPERATIONS.md` §6](OPERATIONS.md) bound the SECA preview,
    wellness report, and longitudinal comparison to local review and
    clinician discussion; they are not decision-support calls.
  - *Missing external evidence:* a clinical-roles review documenting
    how the engine would (or would not) be used in the intended
    pathway.

- **GMLP / Health Canada pre-market / WHO — intended purpose and
  scope.** All three frameworks call for an explicit, plain-language
  intended purpose that the label and documentation can be reconciled
  against. The repository's "wellness and healthspan prototype, not a
  diagnostic device" framing in [`GOAL.md`](../GOAL.md) and
  [`MODEL_CARD.md`](MODEL_CARD.md) is the in-house analogue; the
  populated form lives in §1.2 of the protocol template.

## 2. Predictor and outcome definitions

- **TRIPOD+AI Items 5–7 (predictors and outcomes) and PROBAST+AI
  predictor / outcome domain.**
  - *Software control:* the 35-variable matrix and 36-column model
    feature manifest are enforced by
    [`GOAL.md`](../GOAL.md) §2 and verified by E-001/E-002/E-043;
    [`MODEL_CARD.md`](MODEL_CARD.md) "Model and data contract" names
    the exact column order and the `ModelAdapterProtocol` contract.
    The outcome (time-to-event all-cause mortality via NHANES linked
    files, Gompertz inversion per Levine 2018) is named in
    [`GOAL.md`](../GOAL.md) §3 Pipeline B and
    [`SOURCES.md`](SOURCES.md) ("Biological age").
  - *Template / deferred decision:* the external-cohort primary
    endpoint, event-indicator mapping, censoring rule, duration unit,
    follow-up horizon, and second (sensitivity) horizon are placeholders
    in [`EXTERNAL_VALIDATION_PROTOCOL.md`](EXTERNAL_VALIDATION_PROTOCOL.md)
    §4.3 and §4.4.
  - *Missing external evidence:* a frozen endpoint and censoring rule
    with code lists, ICD mapping versions, and disclosure-control
    review; an approved device, population, age bands, units, and
    provenance record for the deployed reference panel
    ([`SOURCES.md`](SOURCES.md) "BIA transfer calibration").

## 3. Data provenance and source identity

- **TRIPOD+AI Items 8a–c (data sources) and PROBAST+AI
  participants/data-source domain.**
  - *Software control:* the cycle file URLs, documentation links, and
    role tags in [`TRAINING_MANIFEST_TEMPLATE.json`](TRAINING_MANIFEST_TEMPLATE.json)
    enumerate the supported NHANES BIX/mortality sources; the fixed
    parameter `RECORD_AFTER_DOWNLOAD` for source SHA-256 and
    `YYYY-MM-DD` for `retrieved_at` is the explicit "not yet
    populated" boundary. [`SOURCES.md`](SOURCES.md) "NHANES data
    preparation" quotes the CDC linkage page and disclosure-control
    note.
  - *Template / deferred decision:* the populated version of the
    training manifest must replace every `RECORD_AFTER_DOWNLOAD`/
    placeholder field with checksum, retrieval date, DUA reference,
    and IRB identifier. The protocol template mirrors this in
    [`EXTERNAL_VALIDATION_PROTOCOL.md`](EXTERNAL_VALIDATION_PROTOCOL.md)
    §3.
  - *Missing external evidence:* real data-access approvals / DUAs /
    IRBs; real source checksums; documented SECA device-family and
    reference-panel provenance for the deployed panel.

## 4. Leakage control and split design

- **External-validation guidance (§3 patient-level splits) and
  PROBAST+AI analysis-domain leakage review.**
  - *Software control:* E-028/E-053 cover `split_survival_rows` with a
    seeded SHA-256 patient-level fit/holdout partition and event/censor
    stratification (with optional `sex`/`age_band` strata); E-052
    forces assessment and external-validation paths through
    `ModelAdapterProtocol.predict_for_assessment` with the persisted
    36-column order. The protocol §5 enumerates patient-id, household,
    site, time, feature-derivation, and split-helper overlap checks.
  - *Template / deferred decision:* the clinical reviewer must freeze
    the prespecified clinical split and tuning boundary that the
    engineering split helper cannot substitute for; the
    external-validation report must attach Appendix A (patient-overlap
    receipt, no identifiers).
  - *Missing external evidence:* real external-cohort participant
    overlap report, signed by the data-governance reviewer, against
    the approved training cohort.

## 5. Missingness handling

- **TRIPOD+AI Items 13a–c, PROBAST+AI missing-data domain.**
  - *Software control:* missing optional values remain `NaN` for
    XGBoost's native `missing` parameter (E-011); MVV failure returns
    `InsufficientDataError` (E-002); FI excludes missing variables
    from its denominator (E-003, [`MODEL_CARD.md`](MODEL_CARD.md));
    the per-feature missing-count and per-feature missing-rate fields
    in `SurvivalTrainingFrame.quality` and
    `validate_external_cohort` are engineering support fields.
  - *Software boundary:* the versioned `SurveyDesign` declaration preserves
    weight kind, strata, PSU, and replicate-pattern intent in training
    artifacts and validation reports. It does not implement complex-survey
    variance; `weighting_applied` and `design_reviewed` remain explicit flags.
  - *Template / deferred decision:* the protocol §7.1 lists the
    denominators each metric must report (rows received / evaluated /
    excluded, aggregated exclusion reasons, MVV pass/fail,
    per-feature missing counts and rates overall and by subgroup).
  - *Missing external evidence:* an external cohort that exercises
    the real missingness patterns in the target deployment, plus the
    reviewer-approved sensitivity runs (native missing vs complete
    case, FI denominator strata, alternative reference panel).

## 6. Performance reporting

### 6.1 Discrimination, calibration, utility, and uncertainty

- **TRIPOD+AI Items 16–18; external-validation guidance §§ on
  discrimination, calibration, and uncertainty; PROBAST+AI
  results-domain review.**
  - *Software control:* `validate_external_cohort` reports concordance
    with a support-aware deterministic percentile bootstrap interval
    (requested/valid replicates, comparable-pair denominator,
    `concordance_ci_status`); reports censoring-aware calibration
    bins on `eligible_rows` vs `calibration_rows`; emits
    homeostatic-deviation and biological-age calibration plots
    (E-006/E-013/E-026/E-050); serializes nullable `ci_95` with
    `uncertainty_validated` flag (E-049); preserves model id, panel
    id, available digests, readiness, and fixture state on the
    external-validation receipt (E-049).
    Survey-design metadata is carried into the report, subgroup records, and
    calibration bins, while the shipped validation calculations remain
    unweighted and emit `weighting_applied: false`.
  - *Template / deferred decision:*
    [`EXTERNAL_VALIDATION_PROTOCOL.md`](EXTERNAL_VALIDATION_PROTOCOL.md)
    §7.2.1 makes prespecified minimums explicit as
    `RECORD_AFTER_STATISTICAL_REVIEW` placeholders; §7.4.1 names
    Brier score (or approved survival analogue),
    calibration-in-the-large, calibration slope / ICI, and
    decision-curve / net-benefit as future E-005 obligations that
    require a prespecified decision and threshold range. The
    synthetic fixture and `scripts/run_external_validation_smoke.py`
    are explicitly `clinical_use: forbidden` and "exercise the
    engineering harness," not clinical performance.
  - *Missing external evidence:* numeric minimums set by the
    prespecified SAP; the named Brier / calibration / utility values
    on an approved cohort; an approved uncertainty method/parameter
    with cohort-validated bounds, with the corresponding artifact
    holding `uncertainty_validated: true`.

### 6.2 Outcome-level performance metrics checklist

- Same row family as §6.1; the populated report must include Brier
  (or approved survival analogue), calibration-in-the-large,
  calibration slope/ICI, and decision-curve/net-benefit only with
  prespecified decisions and thresholds (per protocol §7.4.1). The
  engineering harness does not compute these metrics; this row is a
  future E-005 obligation.
- The engineering report nevertheless exposes a stable
  `outcome_metric_status` map overall and per subgroup. Every named metric is
  serialized with `value: null`, `status: "not_implemented_pending_sap"`,
  `construction: "none_withheld"`, a reason, and `review_gate: "E-005"`.
  This is a typed absence contract for downstream consumers and reviewers; it
  is not evidence that any outcome-level metric has been calculated.

## 7. Subgroup applicability and equity

- **TRIPOD+AI Item 20 (subgroups); PROBAST+AI applicability domain;
  GMLP/WHO fairness considerations.**
  - *Software control:* training-quality and external-validation
    reports expose sex, age-band, and ethnicity (with `unknown`)
    slice row counts, events, censoring, event fraction, mean
    follow-up, and concordance when estimable (E-012/E-024/E-053);
    sparse strata stay descriptive, never labeled "validated" or
    "fair" (protocol §7.2 and §9.2 sparse-stratum rule).
  - *Template / deferred decision:* the populated external-validation
    report's §9.2 subgroup support table, plus any study-specific
    strata, must list both prespecified minimums and observed support
    side-by-side (protocol §7.2.1).
  - *Missing external evidence:* the cohort's ethnicity strata
    (definitions and counts); a fairness/equity review for cohorts
    and device populations not represented in the training data;
    subgroup performance in the deployment population.

## 8. Transparency and human-AI workflow

- **GMLP "human-AI configuration," Health Canada pre-market
  "transparency," Health Canada transparency principles, WHO
  governance principle 7.**
  - *Software control:* the API response carries a biological-age
    `interpretation` plus typed `action_effect_estimated: false` and
    `clinical_or_lifespan_claim: false` fields (E-032/E-046); the
    Pages improvement report and longitudinal comparison report
    carry the same top-level flags (E-046/E-033); biological-age and
    trajectory `ci_95` are nullable and ship `null` for unvalidated
    paths (E-049); the wellness report surfaces measured focus areas
    with direction (`below`/`above`), priority, action type, and a
    no-action-effect boundary.
  - *Template / deferred decision:*
    [`EXTERNAL_VALIDATION_PROTOCOL.md`](EXTERNAL_VALIDATION_PROTOCOL.md)
    §10.1 enumerates the named reviewer fields (clinical, statistical,
    data-governance, reference-panel, FI cutoff, uncertainty-method
    reviewers) and the conditions/mitigations for any conditional
    approval.
  - *Missing external evidence:* human-authored transparency summaries
    intended for the target user; reviewer-approved documentation for
    clinicians and patients; site- or context-specific deployment
    communication.

## 9. Cybersecurity, change control, and integrity

- **GMLP "cybersecurity," Health Canada pre-market, NIST AI RMF
  validity/reliability and security controls (referenced in
  [`SOURCES.md`](SOURCES.md)).**
  - *Software control:* [`OPERATIONS.md`](OPERATIONS.md) §1–§5 record
    fail-closed production admission, hash-bound model/panel/sidecar
    trios, deterministic `/health` deployment fingerprint, allow-listed
    release receipts (`capture_release_receipt.py`), body-free
    structured logs, 413 size controls, API-key rejection before body
    consumption (E-014), model-release preflight
    (`validate_model_release.py`, E-031/E-052), and immutable-artifact
    rollback steps; reference-panel approval flags are parsed strictly
    as booleans (E-039/E-042/E-044); Pages ships a synthetic SECA CSV
    sample that is local-only (E-034).
  - *Template / deferred decision:* deployment-boundary responsibilities
    (TLS termination, rate limiting, secret storage, network policy,
    key rotation) are explicitly out of the in-process software per
    [`OPERATIONS.md` §1/§5](OPERATIONS.md); the deployment-time
    controls belong at the deployment boundary, not in this
    repository.
  - *Missing external evidence:* deployment-boundary security review
    specific to the production environment; signed PCI/PHI/HIPAA
    artefacts for the deployment context; named security and privacy
    incident reviewers.

## 10. Monitoring, post-market surveillance, rollback

- **External-validation guidance §"performance over time"; GMLP
  post-market monitoring; Health Canada pre-market change-control;
  WHO governance principle 5.**
  - *Software control:* [`OPERATIONS.md` §4–§5](OPERATIONS.md) lists
    monitoring fields (missingness rates, FI distribution, BIA z-score
    warnings, biological-age uncertainty state, model/panel identity,
    and approved subgroup slices) without raw-payload retention and
    the rollback procedure (stop admission, restore last-known-good
    trio, restart under production settings, restore traffic
    gradually); protocol §10.2 enumerates stop / rollback conditions
    including patient-level overlap, sidecar mismatch, fixture-only
    panel, MVV pass-rate failures, all-early-censored primary horizon,
    and receipt/reconciliation failures.
  - *Template / deferred decision:* drift thresholds, alert limits,
    and subgroup monitoring minimums are explicitly not invented by
    this repository; they must be set in the approved monitoring
    protocol.
  - *Missing external evidence:* an approved monitoring protocol with
    numeric drift and equity limits, an on-call reviewer roster, a
    post-market data-use agreement, and an approved change-control
    process for artifact swaps.

## 11. Reviewer sign-off and decision recording

- **TRIPOD+AI Item 22; PROBAST+AI overall judgement; Health Canada
  pre-market decision documentation.**
  - *Software control:* the protocol §10 sign-off table and §10.2
    stop/rollback conditions record what a reviewer must supply.
  - *Template / deferred decision:* the populated protocol must record
    a named clinical reviewer, statistical reviewer, data-governance
    reviewer, reference-panel reviewer, FI cutoff reviewer,
    uncertainty-method reviewer, review date, review record id, and
    the explicit approved / conditional / not-approved decision.
  - *Missing external evidence:* the actual reviewer sign-off record
    against the frozen artifact/panel/uncertainty/cohort; the
    corresponding E-005 decision.

---

## 12. Per-framework quick index

This index lists where each framework's highest-priority obligations
land in this repository. Each entry links to the section above rather
than re-stating the obligations.

### 12.1 TRIPOD+AI — <https://www.bmj.com/content/385/bmj-2023-078378>

- Intended use, predictors, outcome, data sources → §1, §2, §3.
- Participants, missingness, split → §4, §5.
- Performance reporting → §6.
- Subgroups and limitations → §7.
- Transparency / interpretation boundary → §8.
- Reviewer sign-off → §11.

### 12.2 PROBAST+AI — <https://www.bmj.com/content/388/bmj-2024-082505>

- Participants and data sources → §3.
- Predictors and outcomes → §2.
- Analysis (leakage, missingness, split, calibration, uncertainty,
  utility, sensitivity) → §4, §5, §6, §6.2.
- Applicability (target population, transportability) → §1, §7.
- Risk-of-bias and overall judgement → §11.

### 12.3 External-validation guidance — <https://www.bmj.com/content/384/bmj-2023-074820>

- Cohort identity, endpoint, censoring, horizon → §2, §3.
- Patient-level splits and overlap checks → §4.
- Missingness → §5.
- Discrimination, calibration, utility, uncertainty → §6.
- Subgroup denominators → §7.
- Reproducibility artifact checklist and stop/rollback conditions →
  §8, §10, §11.

### 12.4 Developing prediction models guide — <https://www.bmj.com/content/386/bmj-2023-078276>

- Study design and intended use → §1.
- Predictor and outcome definitions → §2.
- Sample size and missingness → §5.
- Model development, validation strategy, performance → §6.
- Subgroups and external validation → §7.
- Reporting and interpretation → §8, §11.

### 12.5 GMLP (Health Canada / FDA / MHRA) — <https://www.canada.ca/en/health-canada/services/drugs-health-products/medical-devices/good-machine-learning-practice-medical-device-development.html>

- Intended purpose and product description → §1.
- Patient-centric design and human-AI configuration → §8.
- Data and reference-panel quality → §3, §5.
- Model development, performance, and validation → §6.
- Cybersecurity and change control → §9.
- Monitoring and post-market → §10.
- Transparency / labeling → §8.

### 12.6 Health Canada pre-market MLMD guidance (page dated 2026-04-01) — <https://www.canada.ca/en/health-canada/services/drugs-health-products/medical-devices/application-information/guidance-documents/pre-market-guidance-machine-learning-enabled-medical-devices.html>

- Intended purpose, indication, target population → §1.
- Data provenance and reference-panel identity → §3.
- Leakage / split / training-versus-tuning separation → §4.
- Performance reporting by subgroup; calibration; uncertainty → §6,
  §7.
- Cybersecurity and integrity → §9.
- Change-control, monitoring, rollback → §10.
- Reviewer sign-off → §11.

### 12.7 Health Canada transparency principles — <https://www.canada.ca/en/health-canada/services/drugs-health-products/medical-devices/transparency-machine-learning-guiding-principles.html>

- Use-case documentation and intended purpose → §1.
- Model description and feature contract → §2.
- Performance and subgroup reporting → §6, §7.
- Limitations and uncertainty disclosure → §8.
- Monitoring and transparency over time → §10.

### 12.8 WHO AI health governance guidance — <https://www.who.int/publications/i/item/9789240029200>

- Roles of developers, deployers, and end users → §8, §11.
- Risk management throughout the lifecycle → §9, §10.
- Data and ecosystem integrity → §3, §4.
- Patient-centric design and human determination → §8.
- Transparency and explainability → §8.
- Continuous monitoring → §10.

---

## 13. What this crosswalk does not prove

- **It does not prove E-005 is satisfied.** The protocol template is a
  placeholder; the synthetic fixture is `clinical_use: forbidden`; the
  default model and reference panel are explicitly development
  fixtures; the cohort, cutoff, panel, and uncertainty reviews named
  in §10–§11 of the protocol are not on file.
- **It does not prove clinical effectiveness, fairness, transportability,
  or safety.** A passing test suite, a synthetic fixture, a model
  preflight that returns a passing software gate, and a populated
  protocol signature are not equivalence to a clinical trial or
  outcome study.
- **It does not prove calibration of the shipped `ci_95` interval.**
  Both `metrics.biological_age.ci_95` and `trajectory.score_ci_95`
  remain `null` for unvalidated paths (E-049); a numeric interval is
  reserved for an approved predictor with cohort-validated
  uncertainty. The typed `uncertainty_construction` field records
  `wald_1_96_se` only for an emitted approved-model interval and
  `none_withheld` otherwise. External-validation concordance uses the
  separate `concordance_ci_construction` field to distinguish an emitted
  `bootstrap_percentile` interval from `none_withheld`; neither label is a
  clinical calibration claim.
- **It does not generalize across devices or populations.** The
  published SECA reference panels listed in
  [`SOURCES.md`](SOURCES.md) are starting points, not embedded tables;
  an approved panel file with documented device, population, age bands,
  units, and provenance is a separate prerequisite.
- **It does not constitute regulatory clearance.** This repository is
  framed as a wellness and healthspan prototype per
  [`GOAL.md`](../GOAL.md) and [`MODEL_CARD.md`](MODEL_CARD.md); nothing
  in this crosswalk is a CE mark, FDA clearance, Health Canada
  pre-market decision, or equivalent.
- **It does not substitute for an IRB / ethics approval, a data-use
  agreement, or a prespecified statistical analysis plan.** Those
  governance artefacts are separate prerequisites before any external
  cohort is unblinded against the model.

---

## 14. Reviewer handoff checklist (no invented thresholds)

The handoff below restates the open obligations, each linked to the
existing artifact that records it. The reviewer is not asked to accept
new numbers; the only numbers to fill in live in artifacts already in
this repository (the protocol template, the training-manifest template,
and the model-approval sidecar).

- [ ] Confirm the intended-use statement has been re-stated in
      [`EXTERNAL_VALIDATION_PROTOCOL.md`](EXTERNAL_VALIDATION_PROTOCOL.md)
      §1.2 with population, device, use setting, and the decision to
      be made.
- [ ] Confirm the cohort identity, cycle range, source SHA-256s,
      retrieval dates, DUA reference, and BIA device family have
      replaced the placeholders in
      [`TRAINING_MANIFEST_TEMPLATE.json`](TRAINING_MANIFEST_TEMPLATE.json)
      and [`EXTERNAL_VALIDATION_PROTOCOL.md`](EXTERNAL_VALIDATION_PROTOCOL.md)
      §3.
- [ ] Confirm the patient-overlap report against the approved training
      cohort is attached as protocol §5 Appendix A (no identifiers).
- [ ] Confirm the primary endpoint, event-indicator mapping, censoring
      rule, duration unit, primary horizon, and second (sensitivity)
      horizon have been frozen in
      [`EXTERNAL_VALIDATION_PROTOCOL.md`](EXTERNAL_VALIDATION_PROTOCOL.md)
      §4.3 / §4.4 before cohort unblinding.
- [ ] Confirm the feature manifest and units match the artifact and
      sidecar byte-for-byte; confirm the MVV pass-rate, MVV-fail
      reason counts, and per-feature missing counts/rates overall and
      by subgroup will be reported per protocol §7.1.
- [ ] Confirm the prespecified SAP has set the §7.2.1 minimums (rows,
      observed events, comparable pairs, valid bootstrap replicates)
      and the §7.4.1 metrics (Brier or approved survival analogue,
      calibration-in-the-large, calibration slope / ICI, and
      decision-curve / net-benefit with prespecified decision and
      threshold range).
- [ ] Confirm the uncertainty method and parameter, the named cohort,
      and the supporting evidence refs are recorded in
      [`MODEL_APPROVAL.md`](MODEL_APPROVAL.md).
- [ ] Confirm the reference-panel file is non-fixture, hash-bound by
      sidecar, and documented with device, population, age bands,
      units, and provenance; confirm the panel SHA-256 identity is
      present in assessment / readiness / receipt fields.
- [ ] Confirm the §10.1 reviewer table is filled with named reviewers
      (clinical, statistical, data-governance, reference-panel, FI
      cutoff, uncertainty-method), review date, review record id, and
      the explicit approved / conditional / not-approved decision.
- [ ] Confirm the `scripts/validate_model_release.py` preflight returns
      a passing software gate for the exact artifact / panel / sidecar
      trio, with `clinical_status` still
      `requires_e005_external_validation_and_clinical_review`.
- [ ] Confirm the `scripts/capture_release_receipt.py` capture and
      `--check` reconcile against the running service, with the
      `readiness.blockers` field empty in the `--check` output.
- [ ] Confirm any stop / rollback condition from
      [`EXTERNAL_VALIDATION_PROTOCOL.md`](EXTERNAL_VALIDATION_PROTOCOL.md)
      §10.2 has been signed off in the populated report before this
      row is closed.

When every box above can be checked against a populated version of the
existing artifacts, E-005 is ready to be re-evaluated by the
qualification process defined in `EVAL.md`, not by this crosswalk.
