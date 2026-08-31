# Local NHANES intake review

`scripts/review_nhanes_intake.py` is a bounded, local-only audit of the
existing non-imputing NHANES adapter. It checks that an operator's explicit
cycle map can join local SAS transport components to the CDC public-use
linked-mortality file and produce the engine's canonical row shape. It does
not download data, train a model, validate clinical performance, estimate
lifespan, or approve a production release.

## Inputs and command

Install the optional data dependency before reading real SAS transport files:

```powershell
uv sync --extra data
```

The mortality parser follows the CDC fixed-width public-use `.dat` contract
(including `LRECL=61`) and does not assume a header row. Supply a local
component file for each XPT input, the matching mortality file, and a
cycle-specific JSON map:

```powershell
uv run python scripts/review_nhanes_intake.py `
  --cycle 2003-2004 `
  --xpt .\data\BIX_C.XPT `
  --xpt .\data\DEMO_C.XPT `
  --mortality .\data\NHANES_2003_2004_MORT_2019_PUBLIC.dat `
  --column-map .\data\nhanes-2003-2004-column-map.json `
  --output .\artifacts\nhanes-intake-receipt.json
```

The map must explicitly define the `SEQN`, `age`, `sex`, and `bmi` source
columns, and `duration_unit` plus `missing_values` must be explicit even when
the missing-value list is empty. Additional canonical or raw BIA columns may
be added only when the operator has checked the official cycle codebook.
`duration_unit` must be `years` when linked mortality is supplied because the adapter normalizes
`PERMTH_EXM` to years:

```json
{
  "columns": {
    "seqn": "SEQN",
    "age": "RIDAGEYR",
    "sex": "RIAGENDR",
    "bmi": "BMXBMI"
  },
  "duration_unit": "years",
  "missing_values": [".", 9999]
}
```

Use `--check` with `--output` in CI or an operator handoff to prove that a
stored receipt is byte-for-byte reproducible without rewriting it.

## Receipt boundary

The receipt records the selected cycle, SHA-256 and byte size for each input,
source-column names, row/column counts, mortality event/censor counts, and
aggregate canonical feature presence. It intentionally excludes local paths,
SEQN values, patient IDs, durations, measurements, and raw rows. No network
client is used by the command.

`outcome.status=passed` means only that the local intake shape and mechanical
join contract passed, including at least one eligible mortality row with a
positive follow-up value and one XPT/mortality join. The receipt keeps these
reviewer obligations explicit:

- verify the cycle-specific map against the official codebooks;
- verify laboratory/questionnaire missing-value sentinels;
- verify BIA fit-quality and measurement acceptance rules;
- review weights, complex-survey variance, disclosure control, and linkage
  policy;
- separately approve the cohort, reference panel, clinical cutoffs,
  uncertainty, and production release under E-005.

Exit codes are `0` for a passed mechanical review, `1` for an input or review
failure, `2` for CLI usage errors, and `3` when `--check` finds receipt drift.
This command is not a substitute for the [training manifest](TRAINING_MANIFEST_TEMPLATE.json),
the [external-validation protocol](EXTERNAL_VALIDATION_PROTOCOL.md), or the
[operations boundary](OPERATIONS.md).
