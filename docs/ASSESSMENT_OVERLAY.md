# Local SECA assessment overlay

Status: development-only operator handoff. This document defines the JSON
file produced by the GitHub Pages SECA intake form and consumed by the local
`assess-overlay` command. It is not a clinical record, a prediction result, or
approval evidence.

## Contract

The overlay is a versioned JSON object:

```json
{
  "format": "frailty-engine-assessment-overlay-v1",
  "source_format": "SECA TableView CSV",
  "measured_at": "Jan 2, 2025, 8:00 AM",
  "patient_id": "local-seca-overlay",
  "measurements": {
    "age": 45,
    "sex": "female",
    "bmi": 25.8,
    "phase_angle": 6.1,
    "ecw_tbw": 0.39
  },
  "privacy_note": "Built locally from a SECA preview and user-entered values. No scan or measurement data was uploaded."
}
```

`measurements` uses the canonical feature names in `src/frailty_engine/features.py`.
Missing values are omitted or represented as `null`; they are never guessed.
The Pages form pre-fills only values observed in the latest SECA scan and keeps
those controls read-only. Age, sex, phase angle, ECW/TBW, blood, history, and
other missing fields must be supplied explicitly before the form enables its
preview.

The overlay loader requires the exact `format` value and a nested
`measurements` object. Unknown feature names and engineering-range violations
are rejected by the canonical Python parser. If the overlay repeats a
non-null SECA value, it must match the observed latest-scan value; the local
handoff refuses a conflicting replacement.

## Local identifier

`patient_id` is retained only in the locally downloaded file and the local
assessment response. Use a clinic-controlled pseudonym, not a name, health-card
number, or other direct identifier. The Pages site does not upload this value.
If the overlay omits the field, the CLI uses `local-seca-overlay` unless
`--patient-id` supplies a non-empty local identifier. An existing overlay
identifier takes precedence over that optional fallback.

## CLI handoff

Run the original SECA CSV and overlay together so the parser can verify the
observed scan values and the assessment can use the canonical Python pipeline:

```powershell
frailty-engine assess-overlay <path-to-your-SECA.csv> --overlay frailty-assessment-overlay.json
```

For a non-patient smoke test, the repository includes
`examples/assessment_overlay_synthetic.json` alongside
`examples/seca_tableview_fixture.csv`.

The command writes a successful JSON assessment to stdout and structured error
JSON to stderr. Exit codes are stable for scripting:

| Exit code | Meaning |
|---:|---|
| `0` | Assessment completed and passed the MVV. |
| `2` | MVV shortfall; inspect `error.missing_requirements`. |
| `3` | Overlay, SECA input, or measurement validation failure; inspect `error.field_errors`. |
| `4` | Other expected engine failure; no clinical result should be admitted. |

The command is a local handoff convenience. The development predictor and
reference panel remain unapproved, and a successful software run does not
establish clinical validity, lifespan benefit, diagnosis, treatment effect, or
E-005 approval.
