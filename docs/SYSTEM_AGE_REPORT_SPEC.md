# System-specific age-equivalent report

This is the target presentation and evidence contract for the finished
healthspan product. It is a product specification, not a claim that the
current development model can produce all of these numbers.

## 1. The language the product must use

### Chronological age

Chronological age is the person's age calculated from date of birth and the
assessment reference date. The report must show the reference date and the
precision used (completed years or decimal years). It is an input/context
field, not a biomarker and not a measure of health.

### Biological age

"Biological age" is an umbrella concept, not a universally standardized test.
There is no accepted gold-standard assay that captures the aging of the whole
person. Different systems can age at different rates, and an aging clock's
output depends on its inputs, target, reference population, and model.

The product should therefore use the more precise label **system-specific
age-equivalent estimate** whenever it presents a number. The display may use
“biological age” as a short product term only when the card also names the
system, method, reference population, uncertainty, and validation status.

An age-equivalent estimate is not a literal age of an organ. It is the age in a
specified reference population whose modeled measurement or outcome is
similar. It is not a diagnosis, life-expectancy estimate, treatment-effect
estimate, or promise that a behavior will make a person younger.

## 2. Final report layout

The final report is a profile, not a leaderboard or a single composite score.
It should render in this order:

1. **Assessment context** — assessment date, chronological age, source and
   date of each measurement, protocol/device, units, and data-quality flags.
2. **Headline summary** — overall age-equivalent estimate only when the
   approved model and uncertainty are available; current deficit load (FI),
   measurement completeness, and homeostatic-deviation context.
3. **System cards** — one card per supported system, with the same schema for
   measured, incomplete, and unavailable systems.
4. **Prioritized focus areas** — measured values outside an approved reference
   band, missing inputs that materially limit interpretation, and a
   conservative next step for discussion with a qualified professional.
5. **Methods and limitations** — model/panel versions, uncertainty method,
   reference population, validation state, missingness, and the explicit
   research-use/wellness boundary.

Every card must answer four separate questions:

| Field | Meaning |
|---|---|
| `measurement_profile` | What was actually measured, on what date, with which protocol and units? |
| `reference_interpretation` | How does each observed value compare with the declared reference band? |
| `age_report` | Is a validated system-specific age-equivalent model available? |
| `next_step` | What safe, non-prescriptive follow-up is reasonable, without claiming an effect? |

## 3. Card contract

The stable shape should be equivalent to:

```json
{
  "system": "musculoskeletal",
  "display_name": "Muscle and structural health",
  "status": "partial",
  "measured_count": 3,
  "expected_count": 6,
  "measurement_profile": [
    {
      "name": "grip_strength",
      "value": 32.0,
      "unit": "kg",
      "measured_at": "2026-08-31",
      "protocol": "approved_protocol_id",
      "source": "clinic_measurement"
    }
  ],
  "missing_measurements": ["appendicular_lean_mass", "areal_bmd"],
  "reference_interpretation": {
    "status": "mixed",
    "basis": "age_sex_protocol_specific_reference_panel",
    "direction": "higher_is_not_universally_better"
  },
  "age_report": {
    "status": "withheld_unvalidated",
    "label": "system_specific_age_equivalent",
    "point_estimate": null,
    "delta_from_chronological_age": null,
    "interval": null,
    "interval_type": null,
    "model_id": null,
    "reference_panel_id": null,
    "uncertainty_validated": false
  },
  "interpretation": "Measurement profile only; no validated muscle age is available.",
  "next_step": "Discuss the measured findings and missing assessment inputs with a qualified professional."
}
```

When a category-specific model is approved, `age_report` may contain a
numeric estimate only if it also carries:

- the exact target and horizon (for example, a functional or clinical outcome);
- model, feature, protocol, and reference-panel identifiers;
- point estimate, unit (`years`), and a clearly named uncertainty interval;
- calibration and transportability results for the intended population;
- subgroup support and missingness support;
- repeatability/measurement-error information; and
- the human approval record and report date.

If any of those are absent, the estimate is withheld. A z-score, percentile,
commercial score, overall age, or FI value must never be relabeled as a system
age.

## 4. Recommended measurement map

These are evidence-informed inputs for a future report. They are not a promise
that every input is in the current feature contract or that any input alone
creates a valid age.

| System card | Stronger measurement set | What it can support now | What remains unproven |
|---|---|---|---|
| Muscle and structural | DXA appendicular lean mass; standardized grip strength; five-repetition chair stand or gait speed; height/weight. | A body-composition and function profile; FI-related context. | A numeric “muscle age” requires its own target, reference panel, repeatability, validation, and approval. |
| Bone | DXA areal BMD interpreted with the applicable clinical reference standard; fracture history and risk context. | Bone measurement availability and clinician handoff. | DXA BMD is not a universal bone-aging clock; bone age and fracture risk are different constructs. |
| Cardiorespiratory | Directly measured VO₂peak/VO₂max from a standardized cardiopulmonary exercise test when appropriate; resting BP and HR. | Fitness and cardiovascular-health context. | VO₂peak is a strong health-outcome marker, but it is not by itself a whole-body or heart age. |
| Metabolic | HbA1c; fasting glucose when indicated; lipid profile including triglycerides/HDL and potentially ApoB; waist and blood pressure; medication and fasting context. | Glycemic/lipid/metabolic reference interpretation. | These are clinical risk and physiology measures, not a validated metabolic-age number without a model. |
| Immune and inflammatory | hs-CRP interpreted with recent infection/injury and other context; CBC with differential; specialized immune phenotyping only under a defined protocol. | Inflammation and blood-count context. | hs-CRP is nonspecific; a T-cell ratio or one blood draw is not an immune age. |
| Brain and cognition | Standardized, language/education-appropriate cognitive battery covering executive function, memory, attention, and processing speed; MRI only for a defined clinical/research question. | Cognitive performance profile. | Cognitive performance, MRI brain age, and neurodegenerative diagnosis are distinct outputs. |
| Kidney | Creatinine/eGFR, urine albumin-to-creatinine ratio, blood pressure, and medication/context review. | Kidney-health reference context. | eGFR is a kidney-function estimate, not a validated kidney-age clock. |
| Liver | ALT/AST, platelets, albumin, bilirubin as clinically indicated, and FIB-4 with its input/context fields. | Liver-risk and function context. | FIB-4 is a risk index; it must not be presented as liver age. |
| Sleep and recovery | Sleep duration/regularity and validated sleep questionnaire; actigraphy or polysomnography when clinically indicated. | Sleep/recovery context and missingness. | A sleep duration value cannot be converted to a biological age. |
| Blood/hematologic | CBC and differential, hemoglobin/hematocrit, RDW, and relevant clinical context. | Blood-health profile. | A blood age requires a separately validated model and should not duplicate inflammation or metabolic age. |
| Skin | Standardized dermatologic examination or validated image protocol with consent and bias review. | Explicit unavailable status until the protocol is supported. | Cosmetic “skin age” is not a clinical biological-age measure. |
| Mental and emotional health | Validated, appropriate questionnaires plus clinician context where indicated. | Self-reported wellbeing/history context. | Mental-health scores are not biological age and should not be used as a proxy for diagnosis. |

The product may group or rename these cards for the user interface, but the
underlying identifiers, units, source provenance, and withheld-age semantics
must remain stable. Overlapping measurements are allowed; they must not be
counted as independent evidence twice without an explicit model design.

## 5. Correct interpretation of the illustrative 45-year-old example

The following is a **mock display example only**, not a clinical result:

> Chronological age: 45 years. Cardiorespiratory age-equivalent: 38 years
> (illustrative only). Muscle/structural age-equivalent: 52 years (illustrative
> only). Metabolic age-equivalent: 41 years (illustrative only). Immune and
> inflammatory age-equivalent: 49 years (illustrative only). Cognitive
> age-equivalent: 45 years (illustrative only).

The production report must not attach those values to a real person unless
each value comes from its own approved model and evidence record. In the
current project, the correct rendering for these cards is generally:

> **Age-equivalent withheld — measurement profile available.** The available
> measurements and their reference-band direction are shown; the project does
> not yet have an approved system-specific age model for this card.

## 6. Evidence gate for a numeric system age

Before displaying a number, the project must document, for that system:

1. a prespecified construct and target that are not merely chronological age;
2. a standardized and repeatable measurement protocol;
3. a target-population reference panel with device, units, age/sex handling,
   and relevant population support;
4. an independently evaluated model with patient-level leakage controls;
5. calibration, discrimination or predictive validity appropriate to the
   target, uncertainty, and measurement error;
6. external validation, subgroup support, and missingness sensitivity;
7. evidence that the output adds useful information beyond chronological age
   and simpler clinical measures; and
8. qualified clinical, statistical, data-governance, and product approval.

The output must remain `withheld_unvalidated` when the gate is incomplete.
Passing software tests, a vendor's marketing label, a cross-sectional
chronological-age predictor, or an illustrative example cannot satisfy it.

## 7. Safe action language

The report can identify a measured focus area and suggest a next discussion or
repeat measurement. It must not say that a particular exercise, supplement,
drug, diet, or sleep change will reduce a system age, extend lifespan, prevent
disease, or change a treatment outcome. A before/after difference is
descriptive until a prespecified intervention study establishes an effect.

Commercial panels may be listed as possible sources of laboratory data only if
the report preserves the laboratory's method, date, units, and reference
context. A proprietary vendor score is not evidence of a validated system age
and is not a substitute for this contract.

## 8. Current project boundary

The current engine can provide an overall development age-equivalent readout,
FI context, and deterministic category coverage/reference summaries. It must
keep skin and bone unavailable where measurements are outside the canonical
input contract and must keep all unvalidated category ages null. This document
defines the final shape to build toward; it does not move the project past
`E-005` or its production-approval gate.
