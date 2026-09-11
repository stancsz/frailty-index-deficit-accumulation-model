# 008 — Product and release decisions

- **scope:** product posture, distribution, first system-age domain, and data
  strategy for this repository.
- **status:** current decision baseline
- **decided:** 2026-08-31
- **updated:** 2026-09-01
- **decision owner:** repository owner, pending legal/entity confirmation

## Decisions

1. **Distribution:** private/proprietary for now. The repository grants no
   open-source or external-use license; external distribution requires a
   separate written agreement. See [`LICENSE.md`](../../LICENSE.md).
2. **Intended use:** research and wellness/healthspan development only. The
   project is not a diagnostic device, treatment recommender, mortality
   predictor, or approved clinical decision-support system.
3. **Delivery sequence:** expose measurement-only full-body cards now, then
   validate and release one system-age model at a time. Do not attempt to
   release all numeric system ages simultaneously.
4. **First domain:** musculoskeletal/structural health. The first governed
   panel should combine appendicular lean mass and areal bone mineral density
   from DXA with standardized grip strength and chair-rise or gait-speed
   performance, plus the required context fields.
5. **Follow-on domains:** cardiorespiratory first, then metabolic, followed by
   immune/inflammatory, cognitive, kidney, liver, sleep/recovery, skin, and
   other domains only when each has its own protocol and evidence package.
6. **Age meaning:** use a named `system_specific_age_equivalent` and begin
   with a normative reference-population model. An outcome-linked model may be
   added later as a separately labeled output; it must not be conflated with
   the normative estimate.
7. **Data strategy:** use synthetic/public data for development and software
   testing. Use a separately governed, permitted external cohort for held-out
   validation. Never place raw patient exports or restricted cohort data in
   the repository.
8. **Approval:** numeric system ages remain withheld until the domain has a
   prespecified target, repeatable protocol, reference panel, model,
   uncertainty, held-out/external validation, subgroup and missingness
   review, and qualified clinical/statistical approval.
9. **Public showcase:** GitHub Pages is public and clinician-first, with
   investors as a secondary audience. It may expose only static documentation,
   synthetic examples, reproducible instructions, and privacy-safe public-data
   receipts. This public showcase does not change the private/proprietary
   source or product distribution decision and does not publish an assessment
   API, patient data, restricted cohort rows, or model artifacts.

## Consequences

- P0 is complete for the private source/product distribution decision and the
  public-safe Pages boundary.
- P1 and P2 are complete.
- P3 remains in progress because approved domain protocols, licensed inputs,
  and reference panels are not yet supplied.
- P4 and P5 remain blocked by P3 and E-005 respectively; P6–P8 remain
  downstream work.
- The current API, Pages demo, and agent skill continue to report measured
  values and explicit withheld/unavailable states. They must not emit a
  numeric domain age merely because this decision record exists.

## Revisit triggers

Reopen this decision before external distribution, a clinical pilot, adding a
new measurement modality, changing the intended population, or displaying a
numeric system age. Any such change requires a new protocol and the relevant
roadmap/evidence updates.

## Changelog

- 2026-09-01: added the public GitHub Pages showcase boundary and clinician-first,
  investor-visible audience while retaining private/proprietary source and
  product distribution.
