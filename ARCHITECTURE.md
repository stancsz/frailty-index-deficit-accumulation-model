# Architecture

Status: current engineering boundary
Owner: project steward
Source of product intent: `docs/product-specs/PRODUCT_INTENT.md`
Source of execution acceptance: `GOAL.md` and `goals/active/*/GOAL.md`

## System shape

The project is a local-first, evidence-bounded research prototype with four
distinct layers:

1. **Measurement contract**: `src/frailty_engine/features.py` defines the
   canonical 35-feature input vector. `mvv.py` rejects incomplete requests
   before assessment.
2. **Deterministic assessment**: `fi.py`, `calibration.py`, `pipeline.py`,
   and `body_reports.py` calculate FI and measurement/category reports. Missing
   values remain missing and the denominator is exposed.
3. **Development prediction interface**: `model.py` exposes a deliberately
   withheld age-equivalent interface backed by a development surrogate. No
   committed survival model, approved reference panel, or clinical uncertainty
   estimate exists in this checkout.
4. **Evidence and delivery surfaces**: `src/frailty_engine/api.py` provides
   the local HTTP contract; `docs/` provides the synthetic public showcase,
   reports, release receipts, and evidence ledger.

## Dependency direction

```text
features / schemas
        ↓
      mvv → fi / calibration / seca
        ↓
     pipeline → model / body_reports / progress
        ↓
       api and docs showcase
```

Training and external-validation harnesses consume explicit manifests and
fixtures. They do not promote an artifact, panel, or clinical claim. Release
receipts and `/readyz` remain fail-closed when production controls are absent.

## Durable invariants

- Public examples contain synthetic data only.
- Unsupported biological-age and system-age claims stay withheld or nullable.
- `clinical_use: forbidden` and `E-005` remain explicit until qualified
  external evidence and approval exist.
- A passing software verifier proves software behavior only. It does not prove
  clinical validity, fairness, treatment effect, or production readiness.
- Local SECA files remain browser-local during the showcase workflow.
- Documentation must distinguish product intent, architecture, active execution
  work, and retained evidence. Historical receipts do not certify later edits.

## Change control

Product intent and durable invariants belong here or in the product spec.
Implementation progress and runtime evidence belong in the active `GOAL.md`.
Do not add a second planning database below the goal. A material product-intent
change requires steward or owner approval and a corresponding goal update.

## Verification anchors

- Software: `uv run python scripts/verify_project.py --json`
- Documentation: `uv run python scripts/verify_docs.py`
- Receipt: `uv run python scripts/build_test_receipt.py --check`
- Scientific and readiness status: `EVAL.md`, `GOAL.md`, and the dated evidence
  artifacts under `docs/reviews/`
