# Current public claim inventory

Status: working inventory for T1, reviewed 2026-09-10. Owner: project
maintainer. This document records what the public showcase says, what supports
it, and where the claim stops. It is not clinical or regulatory approval.

| Surface or output | Claim as published | Source or receipt | Applicability and identity | Date | Owner | Evidence status |
|---|---|---|---|---|---|---|
| Pages overview and API contract | The engine accepts a canonical 35-feature contract and enforces an MVV before assessment. | `src/frailty_engine/features.py`, `src/frailty_engine/mvv.py`, EVAL E-001/E-002, `docs/test-receipt.json` | Software behavior in this repository; not evidence that every clinic collects equivalent variables. | 2026-09-10 | Maintainer | measured |
| Pages synthetic report | The example shows a deterministic FI with an explicit numerator, denominator, measured coverage, and missing-feature list. | `src/frailty_engine/fi.py`, `docs/demo-data.json`, `docs/site.js`, Node Pages tests | Synthetic public fixture only. Missing values are not imputed and the denominator is an engineering count label. | 2026-09-10 | Maintainer | measured |
| Pages biological-age area | Numeric biological-age and homeostatic-deviation outputs are withheld from the public artifact. | `src/frailty_engine/model.py`, `docs/demo-data.json`, EVAL E-049/E-054 | Development predictor, uncertainty method, and reference panel are not clinically validated. `ci_95` remains null. | 2026-09-10 | Maintainer | measured and unverified for clinical use |
| Pages reference-panel notice | The shipped panel is a synthetic development fixture and is not production-ready. | `src/frailty_engine/calibration.py`, `docs/demo-data.json`, EVAL E-037/E-054 | Panel identity is `seca-development-fixture`; it must not be treated as a licensed clinical reference panel. | 2026-09-10 | Maintainer | measured |
| Pages local SECA preview | A selected CSV can be parsed and normalized locally without uploading the raw file or inventing missing clinical inputs. | `docs/seca-parser.js`, `docs/site.js`, `tests/site_parser.test.cjs`, EVAL E-015/E-020/E-068 | Browser-local behavior only. The SECA scan alone is not an assessment and does not produce an age output. | 2026-09-10 | Maintainer | measured |
| Pages comparison report | A comparison can show matched measurement coverage and withhold aggregate change when eligibility is incomplete. | `src/frailty_engine/progress.py`, `src/frailty_engine/comparison.py`, EVAL E-051/E-055 | Descriptive engineering comparison, not causal improvement, treatment effect, or clinical utility. | 2026-09-10 | Maintainer | measured |
| Download and print report | Exported and printed reports retain the synthetic, research-only boundary and do not promote unavailable ages. | `docs/site.js`, `tests/site_parser.test.cjs`, EVAL E-021/E-046/E-078 | Public static report path only; browser output still requires state-by-state inspection after relevant edits. | 2026-09-10 | Maintainer | measured locally; live publication unverified |
| Public evidence register | Current entries use bounded evidence classes such as repository-observed, cited source, and explicitly unverified status; self-assigned confidence slogans are not used as claim support. | `docs/index.html`, `scripts/verify_docs.py`, this inventory | Public wording describes the evidence boundary and points to receipts; it is not a reviewer sign-off or clinical confidence estimate. | 2026-09-10 | Maintainer | measured locally |
| Software verification | The current dirty checkout passes the canonical local verifier and reports the executed receipt separately from the clinical gate. | `scripts/verify_project.py`, `docs/ir0-clean-candidate-verification-2026-09-10.json`, `docs/test-receipt.json` | Local or temporary clean-snapshot evidence, not proof of the deployed page or a clinical result. Do not treat collection counts as executed pass evidence. | 2026-09-10 | Maintainer | measured locally |
| Clinical readiness | E-005 remains blocked because approved external-cohort validation, clinical review, and production-model approval are absent. | Root `GOAL.md`, `EVAL.md`, `docs/INDUSTRY_READINESS_REVIEW.md`, Project #4 IR0/IR3 notes | Applies to clinical validity, prognostic use, calibration, and production promotion. | 2026-09-10 | Project owner and qualified reviewers | unverified and blocked |
| License and distribution | The repository uses private or proprietary distribution terms recorded in `LICENSE.md`. | `LICENSE.md`, `README.md`, Pages metadata and source map | Does not grant reuse rights for code, data, model artifacts, or third-party sources. | 2026-09-10 | Project owner | measured |
| Published identity | The retained published desktop capture is stale and shows `120 / 120 passing` and `v0.1.0 · draft`; it does not identify the current local candidate. | `docs/reviews/trust-maturity-2026-09-10/published-desktop.jpg`, its `README.md`, live audit | Historical live-surface evidence only. Candidate SHA, remote CI, deployment identity, and live asset hashes remain open. | 2026-09-10 | Maintainer and deployment owner | measured historical evidence; current deployment unverified |
| Security reporting | GitHub private vulnerability reporting is not enabled for the public repository; the documented fallback is a minimal non-revealing request for a private maintainer channel. | `SECURITY.md` section 2, `docs/reviews/trust-maturity-2026-09-10/dependency-security-review-2026-09-10.md`, GitHub API route check | Do not send patient data, raw scans, credentials, or exploit details to public issues. This does not establish deployment security. | 2026-09-10 | Project owner | route availability measured; private route unavailable |
| Dependency and runtime review | The lock is current, the local canonical verifier passes, the current temporary candidate passes an installed-wheel/HTTP smoke on Python 3.13.11, earlier clean-candidate receipts cover Python 3.11.14 and 3.12.3, and the current ephemeral pip-audit run found no known third-party Python vulnerabilities. | `uv.lock`, `docs/ir0-current-candidate-verification-2026-09-10.json`, `docs/ir0-clean-candidate-verification-2026-09-10.json`, `docs/reviews/trust-maturity-2026-09-10/dependency-security-review-2026-09-10.md` | This is repository and local-runtime evidence only. The local project was not auditable as a PyPI distribution, and hosted deployment, JavaScript, SBOM, and future advisory review remain outside this receipt. | 2026-09-10 | Maintainer and deployment owner | measured locally; deployment review open |

## Reconciliation notes

- The public journey leads with purpose, intended user, synthetic scope and the
  example action. Test receipts, citations and the historical live capture are
  available as evidence, not as the first-screen explanation.
- A test count is a receipt field. It does not by itself prove that the current
  deployed files, model, reference panel, or clinical claims are valid.
- The evidence register uses bounded evidence classes instead of confidence
  scores. Current verifier results remain linked to their receipts and are not
  presented as clinical confidence.
- The only numeric FI in the public example is a synthetic software output. An
  age-equivalent number is not a clinical result and remains withheld here.
- The next review pass must update this inventory after any candidate or deploy
  change. A changed asset, report field, or runtime identity reopens the related
  row rather than inheriting the previous status.
