# 004 — Current implementation status and remaining release gates

- **scope:** the repository roadmap, evaluation contract, and intended GitHub
  Project board, reviewed 2026-09-07.
- **status:** historical snapshot, superseded by wiki 011 and 012
- **decision it feeds:** what remains before the engineering prototype can be
  considered ready for an approved production deployment.

## Answer

The repository is a substantial research-use-only engineering prototype. The
deterministic FI engine, MVV/API contract, BIA plumbing, SECA importer, Pages
demo, wellness/progress reports, agent skill, serving boundary, reproducibility
checks, and synthetic validation harness are implemented and covered by
engineering evidence.

The remaining work is gated rather than a missing feature list. The agent
contract and fresh-install path are complete: `skills/frailty-engine/SKILL.md`
documents the supported invocation, and the isolated wheel smoke covers the
installed CLI/API, comparison, SECA, invalid-input, metrics, and provenance
paths.

1. Freeze reviewed scientific and data provenance, including approved inputs,
   reference-panel provenance, cutoff review, survey-design semantics, and
   reproducible training details.
2. Train and package a hash-bound candidate model release with an approved
   reference panel, uncertainty method, and human approval sidecar.
3. Complete E-005 using an approved external cohort, stratified validation,
   calibration, uncertainty and sensitivity analyses, clinical-utility review,
   and qualified clinical/statistical sign-off.
4. After E-005, implement the production deployment boundary, controlled pilot,
   and ongoing release, monitoring, revalidation, and change-control process.

The intended work tracker was and remains [GitHub Project #4 — longevity](https://github.com/users/stancsz/projects/4/views/1).
It was reconciled on 2026-08-31 after project scope was restored: P1 and P2 are
`Done`, P0 and P3 are `In Progress`, and P4–P8 are `Todo`. The board has no
dedicated blocked state, so `ROADMAP.md` remains the source of dependency
detail. Project #5 is the unrelated `hgrid` board.

E-005 remains blocked. Synthetic fixtures, passing software checks, and a
working serving contract do not establish clinical validity, production model
approval, or permission to make real-person longevity decisions.

The 2026-09-10 follow-up is recorded in wiki 012. It found a passing local
dirty-checkout verifier after receipt and documentation repair, while the
remote CI/Pages failure and the remaining IR0 clean-candidate requirements
remain open.

## Pages trust-pass

R-087/E-087 changes only the public presentation. The Pages front page now
uses CI-injected source-build metadata, reports test counts as a receipt rather
than a clinical result, labels the synthetic biological-age display as withheld,
and moves the long criterion index behind its source links. It also names the
unreviewed panel, cutoff, parameter, subgroup, and joint-age assumptions.
This is not new clinical evidence and does not change E-005.
