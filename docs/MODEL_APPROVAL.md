# Model approval sidecar

An XGBoost artifact is executable software, not a clinical approval record.
When the API loads a native artifact, `FRAILTY_MODEL_APPROVAL_PATH` may point to
a separate JSON sidecar. The loader verifies that the sidecar matches the exact
artifact bytes and the persisted feature manifest before it applies any
production or uncertainty flags.

The sidecar must contain exactly these fields:

```json
{
  "schema_version": "1",
  "model_id": "xgb-survival-cox-v1",
  "artifact_sha256": "<64 lowercase hexadecimal characters>",
  "feature_names": ["<the exact 36 names in artifact order>"],
  "reference_panel_id": "<approved panel id>",
  "reference_panel_sha256": "<64 lowercase hexadecimal characters>",
  "uncertainty_method": "<cohort-reviewed method>",
  "log_hazard_se": 0.11,
  "production_ready": false,
  "uncertainty_validated": false,
  "approved_by": "<named reviewer or review board>",
  "approved_at": "2026-08-27",
  "evidence_refs": ["E-005/<review record>"]
}
```

The placeholder example is intentionally not loadable. Generate both digests
from the final artifact and reference-panel file, copy the exact
`MODEL_VECTOR_FEATURE_NAMES` order, and
replace the evidence references with the external-cohort, cutoff, uncertainty,
and panel-review records that a human reviewer has actually approved. Keep the
sidecar protected alongside the deployment configuration; the digests prevent
accidental artifact or reference-panel substitution, while the evidence and
reviewer fields are not a substitute for clinical governance.

For a configured service:

```powershell
$env:FRAILTY_MODEL_PATH = "models/healthspan-cox.json"
$env:FRAILTY_MODEL_APPROVAL_PATH = "models/healthspan-cox.approval.json"
$env:FRAILTY_REFERENCE_PANEL_PATH = "config/seca-reference-panel.json"
$env:FRAILTY_API_KEY = "<deployment-secret>"
$env:FRAILTY_REQUIRE_PRODUCTION = "true"
py -3 -m uvicorn frailty_engine.api:app --app-dir src
```

The API fails startup in strict mode, or reports actionable blockers from
`/readyz`, when the artifact, sidecar, uncertainty state, reference panel, or
API-key boundary is not ready. A matching sidecar can make the software
configuration internally consistent; only approved external validation and
clinical review can satisfy `E-005`.
