# North Star

Help clinicians understand a person's measured health, see what is missing,
and discuss meaningful change with confidence in what the evidence supports.

## The future we want

A clinician should be able to turn fragmented body-composition, laboratory,
history, and functional measurements into a concise, traceable healthspan
report. The report should make the person's current deficit load understandable,
show the limits of the available data, and support a better-informed conversation
about what deserves follow-up.

Every result should be explainable from its measurements, method, and evidence.
When the data cannot support an answer, the product should make that gap useful
and visible. Over time, repeat assessments should help distinguish measured
change from differences in coverage, protocol, or calculation.

## Who we serve first

Our primary users are clinicians and clinical research collaborators reviewing
measurements. Start with one musculoskeletal-focused workflow: inspect observed
values and provenance, identify missing inputs, understand the frailty index
(FI) and its denominator, and export a concise report.

The public showcase lets clinicians, researchers, and investors inspect a
synthetic example, the method, and the evidence still needed. Its purpose is to
make the work assessable and support qualified collaboration.

## What success looks like

Our guiding measure is the proportion of intended users who can complete a
measurement review correctly, independently, and within a practical appointment
workflow. Speed matters only when interpretation remains accurate.

The first product gate, defined in GOAL.md, is a five-user study: at least four
users can select a sample, find missing inputs, interpret FI correctly, and
export the report without assistance within five minutes. All five must
recognize that age estimates and clinical advice are unvalidated. Compare task
time and interpretation errors with their current manual workflow. These are
acceptance targets, not demonstrated results.

Longer-term success means repeat use because the report adds useful information
and reduces interpretation burden. Any model must demonstrate incremental value
over chronological age, FI alone, and a simple domain baseline before its
complexity becomes part of the product promise.

## Principles that guide decisions

- **Measurements come first.** Preserve units, dates, sources, protocols, and
  derivations. Missing values remain missing. Partial previews remain distinct
  from assessments that meet the minimum input requirements.
- **Comparisons must be earned.** A change in measurement coverage must never
  imply improved health. Compare eligible measurements and disclose coverage
  differences; withhold unsupported aggregate changes.
- **Age estimates must earn their place.** Each system needs its own defined
  construct, repeatable measurements, reference population, uncertainty,
  independent validation, and qualified approval. Keep unsupported ages withheld.
  A measurement-only product is a valid outcome.
- **Evidence sets the claim.** Distinguish observed results, declared methods,
  development fixtures, and unverified hypotheses. Passing software tests does
  not establish clinical validity or approval.
- **Privacy is part of usefulness.** Keep local measurement workflows local.
  Public examples remain synthetic and evidence receipts privacy-safe. Real-person
  use requires the applicable governance and deployment controls.
- **Focus precedes expansion.** Prove one useful workflow and one domain before
  adding more system scores or a broader service.

## What we are not promising

The current project is a research and wellness development prototype. It is not
a diagnostic device, treatment recommender, mortality predictor, lifespan
estimator, or approved clinical decision-support system. Before-and-after
measurements do not establish intervention effects. The public site is not a
patient portal or assessment API.

## How this guides the work

Choose work that improves measurement integrity, user understanding, or the
evidence needed for the next justified claim. Narrow or stop work when users
cannot interpret it safely, suitable independent data are unavailable, or a
simpler approach is equally useful.

This document states the durable direction. [GOAL.md](GOAL.md) governs scope,
acceptance criteria, and evidence boundaries. [ROADMAP.md](ROADMAP.md) owns the
ordered plan, dependencies, owners, and status; [EVAL.md](EVAL.md) records
criterion-level evidence. The current clinical gate, E-005, remains blocked.
Writing this North Star does not close any release or clinical gate.
