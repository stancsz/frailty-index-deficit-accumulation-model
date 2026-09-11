# 012 - IR0 local release verification checkpoint

- **scope:** the 2026-09-10 local repair and verification of the IR0 release gate
- **status:** historical checkpoint, superseded by wiki 014 and 015
- **decision it feeds:** whether the software portion of the candidate research release is reproducible

## Observed result

After formatting `scripts/verify_docs.py`, regenerating the checked-in test
receipt, and synchronizing the visible current test counts, the dirty checkout
passes:

```powershell
uv run python scripts/verify_project.py --json
```

The verifier reports `status: passed` for all 20 checks, with 141 collected
Python tests, 25 Node Pages/parser tests, and `clinical_gate: E-005 blocked`.
The passing checks include the documentation verifier, deterministic demo and
receipt checks, synthetic external-validation and training-split smokes, and
the real loopback serving contract.

## What this establishes

This is fresh engineering evidence for the current local working tree. It
shows that the repaired receipt, Pages counts, documentation checks, Python and
Node tests, generated synthetic artifacts, manifests, and serving smoke agree
with one another in this environment.

## What this does not establish

### Independent worker completion review

An independent rerun passed all 20 checks. Accept this as a local repair
milestone only; the overall GOAL.md requirements remain unmet and no IR gate
is closed. Pages checks a Python collection-count receipt without requiring
successful execution of the full Python suite before deployment. IR0 must bind
publication to executed tests for the exact candidate and prove a failing test
blocks publication.

At this checkpoint IR2 also remained open: starting with the balanced synthetic demo at BMI 31,
adding only normal creatinine 0.9 changed the denominator from 13 to 14, FI
from 0.0769 to 0.0714, and development age from 44.0 to 43.9. The comparison
reported both movements as lower despite unchanged overlapping measurements.
Retain this regression when implementing comparison eligibility and coverage
disclosure. Subsequent work added `docs/RESEARCH_REPORT.md`, a study protocol,
and the comparison-eligibility implementation; IR1/IR3 user-study and browser
evidence and IR4-IR7 evidence remain outstanding. The acceptance requirements
are recorded in GOAL.md sections 4, 7 and 8.

### Remaining release evidence

IR0 remains open. The checkout contains pre-existing modified and untracked
files and has no owner-approved candidate commit for this repair. A temporary
clean snapshot passed locked installation and local Windows and WSL Ubuntu
checks, while the earlier remote failure remains attached to commit
`2f1218b9d20b61ee9682cdae0a5a74dd79a7f653`. Later remote verify run
`34548964641` and Pages run `34548964642` succeeded for `7fc8fca`, but that is
not the current dirty candidate. The current temporary clean candidate
`5dd24112f6582c211b4c93b505db61c2c1e66b26` passes locked installation, all 20
verifier checks, documentation checks and installed-wheel/loopback HTTP smoke
on Windows; see
[`docs/ir0-current-candidate-verification-2026-09-10.json`](../../docs/ir0-current-candidate-verification-2026-09-10.json).
Remote same-SHA Linux evidence, an isolated remote deliberately failing
publication test, live build metadata and asset verification, and
licensing/visibility reconciliation remain open.

The live audit returned HTTP 200 but found superseded confidence/test-receipt
wording and a 404 for the current claim inventory. No current candidate
deployment was authorized or performed in this follow-up. E-005 remains
blocked, and the project remains research-use-only and not a clinical
decision-support release.

See [GOAL.md](../../GOAL.md), [ROADMAP.md](../../ROADMAP.md),
[the industry-readiness plan](011-industry-readiness.md), and [Project #4](https://github.com/users/stancsz/projects/4/views/1).
