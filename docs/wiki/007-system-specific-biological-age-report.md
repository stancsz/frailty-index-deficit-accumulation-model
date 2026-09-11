# 007 — What is a scientifically defensible system-specific biological-age report?

- **scope:** adult longevity/healthspan wellness reporting for this repository,
  with a 2026-08-31 evidence check; not a diagnosis or clinical device claim.
- **status:** current
- **verified:** 2026-08-31
- **decision it feeds:** the final report shape, terminology, measurement map,
  and evidence gate for showing system-specific age-equivalent estimates.

## Gap statement

Entry 005 covered the engineering category schema and the rule that category
ages are withheld. It did not define the scientific meaning of chronological
age, distinguish a system age from a universal biological age, specify the
measurement/provenance fields that a finished card needs, or correct the
strength of the example's claims about DXA, VO2 max, immune markers, and
commercial panels. This entry addresses that gap.

## Answer

Chronological age should be calculated from date of birth and the assessment
reference date, and displayed as context. Biological age has no accepted
universal gold-standard test. A system-specific age is best presented as a
**named age-equivalent estimate**: the output of a specified model for a
specified system, measurement protocol, target, reference population, and
uncertainty method.

The final product should show a profile with:

- assessment date, chronological age, measurement dates, source, units, and
  protocol/device;
- current measurements and missing measurements for each system;
- reference-band direction and a conservative interpretation;
- a numeric system age only when the system has its own validated model and
  approval record; otherwise a typed `withheld_unvalidated` age report;
- uncertainty, model/panel identifiers, subgroup support, and completeness;
  and
- a non-prescriptive next step that does not promise a lower age, longer life,
  disease prevention, or treatment effect.

The example's direction is useful as a user-interface metaphor, but its exact
values must remain mock data. DXA is useful for areal bone mineral density and
body-composition compartments, but it is not an exact universal measure of
muscle age or visceral fat. Direct VO2peak testing is an important
cardiorespiratory-fitness measure, but it is not by itself a whole-body age.
hs-CRP and T-cell ratios are context-dependent markers, not standalone immune
age tests. Cognitive performance and MRI volumetrics are different constructs.
Commercial laboratory panels may provide measurements, but a proprietary score
is not validated merely because a company calls it biological age.

For this repository, the recommended final shape is recorded in
[`SYSTEM_AGE_REPORT_SPEC.md`](../SYSTEM_AGE_REPORT_SPEC.md). The current
implementation should continue to show category coverage and reference
interpretation while keeping unvalidated numeric category ages null.

The implementation sequence is: freeze card identifiers and safe withheld
output; approve each domain's protocol, provenance, reference panel, and
repeatability plan; fit and package one model per approved domain; validate
each domain independently for calibration, uncertainty, subgroup support, and
missingness; then release only the cards with complete evidence and human
approval. The illustrative 45-year-old values are mock presentation values,
not defaults, normative values, or evidence for this repository.

The machine-readable starting point for that review is
[`SYSTEM_AGE_MODEL_MANIFEST_TEMPLATE.json`](../SYSTEM_AGE_MODEL_MANIFEST_TEMPLATE.json).
It is deliberately a non-approving template: `numeric_allowed` is false,
`point_estimate` and `interval` are null, and approval remains
`not_submitted`/`production_ready: false` until a real domain evidence package
is reviewed.

## Receipts

- CDC defines reported age as completed years calculated from date of birth and
  a reference date — [CDC Health, United States age definition](https://www.cdc.gov/nchs/hus/sources-definitions/age.htm),
  accessed 2026-08-31 — confidence: high.
- Reviews and consensus reports state that no single gold-standard biomarker
  or consensus biological-age method has been established — [Biomarkers of
  Aging: From Function to Molecular Biology](https://pmc.ncbi.nlm.nih.gov/articles/PMC4924179/),
  [2025 systematic review](https://pubmed.ncbi.nlm.nih.gov/39938306/), accessed
  2026-08-31 — confidence: high.
- Aging-clock outputs should be described by their input domain or clock name,
  rather than conflated with whole-body biological age — [Contextualizing aging
  clocks](https://pmc.ncbi.nlm.nih.gov/articles/11634725/), accessed 2026-08-31 —
  confidence: high.
- Aging biomarkers require reliability, outcome relevance, appropriate
  predictive/clinical validation, and diverse-population evidence before
  translation — [Validation of biomarkers of aging](https://pmc.ncbi.nlm.nih.gov/articles/PMC11090477/),
  [TAME Biomarkers Workgroup framework](https://pmc.ncbi.nlm.nih.gov/articles/PMC6294728/),
  accessed 2026-08-31 — confidence: high for the framework; project-specific
  sufficiency remains unverified.
- System-level age modeling exists as an active research direction, including
  an 11-system methylation model, but that publication does not validate this
  project's model or authorize copying its estimates — [Systems Age](https://pubmed.ncbi.nlm.nih.gov/40954326/),
  accessed 2026-08-31 — confidence: medium for the research example.
- DXA BMD interpretation belongs to an explicit clinical measurement standard;
  body-composition and visceral-fat estimates have modality and algorithm
  limitations — [ISCD 2023 Adult Positions](https://iscd.org/wp-content/uploads/2024/03/2023-ISCD-Adult-Positions.pdf),
  [body-composition imaging review](https://pmc.ncbi.nlm.nih.gov/articles/PMC7378094/),
  accessed 2026-08-31 — confidence: high for the measurement boundary.
- Muscle assessment should combine muscle quantity, strength, and physical
  performance — [EWGSOP2 consensus](https://doi.org/10.1093/ageing/afy169),
  accessed 2026-08-31 — confidence: high for the assessment framework.
- Cardiorespiratory fitness is strongly associated with health outcomes and
  mortality, but association does not make VO2peak a universal biological-age
  test — [AHA scientific statement](https://doi.org/10.1161/CIR.0000000000000461),
  [2024 overview of meta-analyses](https://pmc.ncbi.nlm.nih.gov/articles/PMC11103301/),
  accessed 2026-08-31 — confidence: high.
- Standardized cognitive batteries cover executive function, memory, attention,
  and processing speed — [NIH Toolbox cognition domain](https://nihtoolbox.org/domain/cognition/),
  accessed 2026-08-31 — confidence: high for the assessment-domain description.
- HbA1c reflects average glycemia over roughly three months and has known
  accuracy limitations in some conditions — [CDC A1C guidance](https://www.cdc.gov/diabetes/diabetes-testing/prediabetes-a1c-test.html),
  accessed 2026-08-31 — confidence: high.
- hs-CRP is a useful but nonspecific inflammatory marker whose interpretation
  depends on clinical context and biological variability — [CDC/AHA background
  paper](https://pubmed.ncbi.nlm.nih.gov/15611384/), accessed 2026-08-31 —
  confidence: high.

## Changelog

- 2026-08-31: created from targeted review of the existing category contract
  and current biological-age measurement literature.
