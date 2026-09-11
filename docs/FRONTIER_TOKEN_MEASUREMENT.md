# Frontier-token value measurement

Status: mechanics implemented; real paired-run evidence not supplied

This package defines the minimum evidence needed to claim that the workflow
saves frontier-model tokens. It measures tokens per successful task, success,
quality, calls, retries, and latency for matched baseline and candidate runs.

## Current receipt

[`FRONTIER_TOKEN_VALUE_RECEIPT_2026-09-11.json`](FRONTIER_TOKEN_VALUE_RECEIPT_2026-09-11.json)
was generated from the committed redacted mechanics fixture
[`frontier_token_pairs_synthetic.json`](../examples/frontier_token_pairs_synthetic.json).
It reports six synthetic paired tasks and five matched successes. The fixture
shows how the receipt computes a 35.203366% token difference on matched
successes, but the receipt sets `real_paired_runs: false` and
`claim_status: real_value_unverified`. This number is not a production or
provider result.

The receipt contains only aggregate counters. It emits no prompts, outputs,
credentials, patient data, or provider identifiers.

## Required real-run export

The frontier-token owner must provide a redacted record for each predeclared
task with:

- an opaque stable task ID and baseline/candidate labels;
- provider-reported input and output token counts;
- number of calls, retry count or enough data to derive it, and latency;
- success/failure and bounded failure reason;
- an independently adjudicated quality result using the same task rubric.

The export must be paired by task, exclude prompts and outputs, and identify
the exact candidate and baseline configuration. A provider billing dashboard,
cache-hit count, or synthetic replay alone is insufficient.

Run the local mechanics check with:

```powershell
uv run python scripts/build_token_value_receipt.py `
  --input examples/frontier_token_pairs_synthetic.json `
  --output docs/FRONTIER_TOKEN_VALUE_RECEIPT_2026-09-11.json --check
```

Until owner-supplied real paired runs are ingested, the project must describe
frontier-token savings as unverified. This evidence is separate from clinical
validity and does not change `E-005 blocked` or `clinical_use: forbidden`.
