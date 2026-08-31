# Contributing

This repository is a wellness/healthspan engineering prototype. Changes must
keep the distinction between tested software behavior, synthetic fixtures,
and the clinical/model evidence gate in `EVAL.md`.

## Local checks

Use the locked environment and run the relevant checks before opening a
change:

```powershell
uv sync --locked --extra dev --extra ml
uv run ruff check src tests scripts
uv run ruff format --check src tests scripts
uv run pytest -q
node --test tests/site_parser.test.cjs
uv run python scripts/verify_docs.py
uv run python scripts/verify_project.py
```

The deterministic demo, external-validation fixture, training-split smoke,
and installed-wheel smoke are useful release checks. The external fixture is
synthetic and `clinical-use: forbidden`; a passing smoke does not satisfy
E-005.

## Evidence and privacy rules

- Do not commit patient exports, raw SECA scans, identifiers, or credentials.
  Public Pages assets must remain synthetic and privacy-safe.
- Keep `EVAL.md` explicit about whether a result is measured, inferred,
  synthetic, or still unknown. Do not turn development predictor output into
  a mortality, lifespan, diagnosis, or treatment claim.
- Keep model artifacts, reference panels, approval sidecars, and checksums
  immutable and bound together. `/readyz` must remain fail-closed when an
  identity, uncertainty, panel, or security requirement is missing.
- Preserve the 36-column encoded vector contract. Serving and external
  validation use `predict_for_assessment(age, encoded_vector)`; the legacy
  raw-component development method is retained only for compatibility and is
  deprecated.
- Do not weaken the SECA import boundary into an upload path or add estimated
  action effects without a separate privacy, clinical, and product review.
- Use [`docs/PRIVACY_THREAT_MODEL.md`](docs/PRIVACY_THREAT_MODEL.md) when
  reviewing changes to data flows, logs, metrics, release artifacts, or the
  deployment boundary. It describes implemented controls and residual risks;
  it is not a compliance or clinical-approval claim.
- Use [`SECURITY.md`](SECURITY.md) for private vulnerability reporting,
  security-sensitive release review, and the supported-surface boundary.

## Pages and receipts

When changing `docs/site.js`, `docs/seca-parser.js`, or the static HTML, bump
the shared query token in `docs/index.html` and update the parser-test
expectation. Keep the test receipt, status rows, source map, and evidence
links synchronized. The Pages workflow is a static documentation/demo
release; it does not deploy the API or model.

Changes to the local assessment intake form must keep the Python MVV evaluator
and the SECA assessment-payload overlay as the contract, and must preserve the
same field names, missing-value behavior, and no-upload boundary across the
intake form, CLI handoff, and Python assessor.

When changing `/health`, `/readyz`, or the release receipt projection, update
the readiness matrix and receipt tests together. Readiness carries non-secret
model/panel identity so operators can reconcile a probe with its release
receipt; readiness blockers remain safe to report, while payloads and secrets
must never enter the receipt or logs.

Keep unrelated workspace artifacts, including `.ableton-mcp/`, out of a
change. Do not rewrite history or push a release as part of local
verification unless the task explicitly asks for it.
