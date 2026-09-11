# 005 — Full-body category measurement and age-report contract

- **scope:** category-level assessment output and the agent/Pages handoff,
  reviewed 2026-08-31.
- **status:** current engineering contract; category-specific clinical age
  models are not approved.
- **decision it feeds:** what a caller can safely show for each body system.

## What the report contains

Every successful assessment returns `category_reports`. Each entry includes:

- a stable category id and display label;
- `chronological_age_context`, carrying the supplied assessment age and an
  explicit `supplied_not_recomputed` status because the current payload does
  not include date-of-birth/reference-date inputs;
- `status`: `complete`, `partial`, or `not_available`, based on measurement
  coverage rather than a health judgment;
- `measured_count` and `expected_count`;
- the measured values, units, engineering/reference-band status, direction, and
  source for that category, plus explicit `measurement_source`, `measured_at`,
  `protocol`, and `reference_source` fields;
- `missing_measurements` without guessed or imputed values;
- `reference_status`: `within_reference`, `attention`, `mixed`, or
  `not_available`;
- a typed `age_report` object.

The card also exposes the forward-compatible system-card fields
`system`/`display_name`, `measurement_profile`, `reference_interpretation`,
`next_step`, `action_effect_estimated`, and
`clinical_or_lifespan_claim`. These fields make the current measurement-only
response compatible with the final system-age layout without implying that a
system age is currently validated.

The current category set is:

| Category | Current measurements |
|---|---|
| Body composition | BMI, waist circumference, visceral fat |
| Fluid and cellular health | Phase angle, ECW/TBW |
| Muscle health | FFMI, skeletal muscle mass, grip strength, chair-rise time |
| Joint health | Osteoarthritis history and chair-rise time proxy; joint-specific measurements are not yet in the contract |
| Bone health | Not in the current contract |
| Skin health | Not in the current contract |
| Blood health | Glucose, HbA1c, hs-CRP, albumin, creatinine, eGFR, ALP, WBC, RDW, FIB-4 |
| Cardiovascular health | Blood pressure, resting heart rate, hs-CRP, selected history fields |
| Cardiorespiratory health | Blood pressure and resting heart rate; VO2 max is not in the current contract |
| Immune and inflammatory health | hs-CRP, WBC, and RDW context; immune-cell phenotyping is not in the current contract |
| Brain and cognitive health | Not in the current contract |
| Metabolic health | BMI, waist, visceral fat, glucose, HbA1c, T2D history |
| Kidney health | Creatinine, eGFR |
| Liver health | Albumin, ALP, FIB-4 |
| Sleep and recovery | Sleep duration, sleep-apnea history |
| Lifestyle and function | Grip, chair-rise, smoking, alcohol, sleep |
| Mental-health history | Reported depression history |

Categories intentionally overlap where a measurement informs more than one
body-system view. This is a reporting organization, not a second scoring
system and not independent clinical evidence.

## Age-report boundary

The finished product presentation and scientific terminology are specified in
[`SYSTEM_AGE_REPORT_SPEC.md`](../SYSTEM_AGE_REPORT_SPEC.md). It defines
chronological-age context, the distinction between a measurement profile and
an age-equivalent estimate, the per-card provenance fields, and the evidence
gate for any future numeric system age.

The overall biological-age field is the only age-equivalent interface currently
implemented. For a category with measured inputs, the category report returns:

```json
{
  "status": "withheld_unvalidated",
  "label": "system_specific_age_equivalent",
  "point_estimate": null,
  "delta_from_chronological_age": null,
  "ci_95": null,
  "interval": null,
  "interval_type": null,
  "model_id": null,
  "reference_panel_id": null,
  "method": "category_specific_model_not_available",
  "uncertainty_validated": false
}
```

For skin and bone, the report uses `status: "not_available"` and explains that
the required measurements are outside the current feature contract. A future
numeric category age would require, at minimum, a category-specific target and
model, exact measurement protocol, approved reference panel, uncertainty
construction, held-out validation, subgroup support, and human review. A
caller must not derive a category age by scaling a z-score or copying the
overall biological age.

## Agent behavior

An agent using [`skills/frailty-engine/SKILL.md`](../../skills/frailty-engine/SKILL.md)
should:

1. collect only supported measurements and preserve the source/unit;
2. present chronological-age context and category coverage before interpreting
   the readout;
3. show missing skin/bone measurements as unavailable, not normal or healthy;
4. treat `reference_status` as an engineering display state, not a diagnosis;
5. preserve `age_report.status` and `point_estimate: null` exactly;
6. recommend professional review for concerning values without claiming that an
   action will change biological age, lifespan, or treatment outcome.

## Files and verification

- `src/frailty_engine/body_reports.py` defines category membership and the
  withheld-age contract.
- `src/frailty_engine/pipeline.py` adds the report to each assessment.
- `src/frailty_engine/schemas.py` declares the typed API response.
- `docs/site.js` and `docs/index.html` render the synthetic full-body report.
- `scripts/build_demo_data.py` regenerates the privacy-safe Pages artifact.
- `scripts/validate_system_age_manifest.py` checks the non-approving domain
  model manifest shape.
- `tests/test_engine.py` and `tests/site_parser.test.cjs` cover API and Pages
  behavior.

Run the focused checks:

```powershell
uv run python -m pytest tests/test_engine.py
node --test tests/site_parser.test.cjs
uv run python scripts/build_demo_data.py --check
```

The implementation is engineering evidence only. The development predictor,
synthetic panel, category reference bands, and withheld age reports do not
satisfy E-005.
