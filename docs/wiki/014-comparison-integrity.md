# 014 - Comparison integrity and coverage disclosure

**Status:** current local software evidence, 2026-09-10  
**Decision:** aggregate longitudinal readouts must be withheld when the
measurement contract is not comparable

## Observed regression

**Measured:** In the balanced synthetic case, adding only a normal creatinine
value changed the FI denominator from 13 to 14, FI from 0.0769 to 0.0714, and
development age from 44.0 to 43.9. The overlapping values did not change.

**Method:** A denominator change is a coverage change, not evidence of health
improvement. The regression remains in `tests/test_engine.py`.

**Measured:** The focused matrix also adds an abnormal `cancer=1` item and
checks the reverse removal path. Both normal and abnormal coverage changes
withhold aggregate readouts and expose the added or removed FI feature.

## Implemented contract

**Measured:** Each assessment now carries a comparison context with versioned
feature, measurement-protocol, FI-coding, and cutoff identities; measured and
FI-valid feature names; transport units and protocols; model identity and
artifact hash; and reference-panel identity and hash. The context does not
contain raw measurements.

**Method:** Aggregate deltas are eligible only when the FI item set, coding,
cutoff, units, protocols, model artifact hash, and reference-panel hash are
compatible. Unknown hashes withhold aggregate deltas. Added or removed items,
changed units, and changed protocols are listed explicitly.

**Measured:** The API and Pages report use `matched_items_only` with an explicit
`comparison_eligibility` object when a blocker exists. Pages displays matched,
added, and removed FI coverage and says that a coverage change alone does not
establish health improvement.

## Evidence and remaining review

**Measured:** Focused Python tests, the full local Python suite, the 28-test
Pages/parser suite, and the generated synthetic artifact cover the repaired
behavior. E-033 in `EVAL.md` records the current criterion evidence.

**Unverified:** A qualified statistical reviewer has not yet signed off the
contract, and IR1 user comprehension evidence remains outstanding. This repair
does not establish clinical validity or a causal interpretation.

See [`GOAL.md`](../../GOAL.md), [`ROADMAP.md`](../../ROADMAP.md),
[`RESEARCH_REPORT.md`](../RESEARCH_REPORT.md), and
[`progress.py`](../../src/frailty_engine/progress.py).
