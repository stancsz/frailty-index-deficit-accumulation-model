# 020 - Frontier-token value measurement

Status: active execution evidence, 2026-09-11

The repository now has a deterministic, privacy-safe paired-run receipt for
measuring frontier tokens per successful task. The current receipt uses a
synthetic mechanics fixture and explicitly reports `real_paired_runs: false`.
It demonstrates aggregation and contradiction checks, not actual savings.

See [`FRONTIER_TOKEN_MEASUREMENT.md`](../FRONTIER_TOKEN_MEASUREMENT.md), the
[receipt](../FRONTIER_TOKEN_VALUE_RECEIPT_2026-09-11.json), and the active
[`VALUE-TOKEN-1` goal](../../goals/active/frontier-value-measurement/GOAL.md).

Real evidence requires owner-supplied, request-correlated baseline/candidate
exports containing provider token counts, calls, retries, latency, success, and
independently adjudicated quality. Prompts, outputs, credentials, identifiers,
and raw provider logs must remain outside committed artifacts.

The synthetic example reports a mechanics-only 35.203366% matched-token
difference. It is not a production, billing, clinical, or frontier-provider
claim. E-005 remains blocked.
