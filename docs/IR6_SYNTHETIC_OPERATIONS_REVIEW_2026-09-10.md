# IR6 synthetic operations review

**Review date:** 2026-09-10  
**Scope:** local installed-wheel and loopback HTTP software boundary  
**Status:** development evidence only; IR6 staging and governance are not closed

This review records what the repository currently proves and what must still be
run by a deployment and governance owner. Local software evidence is not a
substitute for TLS, ingress, secret-management, infrastructure, or clinical
approval evidence.

| Control | Current observation | Closeout evidence still required |
|---|---|---|
| Deployment boundary | The API is exercised over loopback HTTP; the Pages surface is static and local-import oriented | Approved deployment diagram, trust boundaries, jurisdiction, intended-use, and data-flow review |
| TLS and ingress | Not exercised by the local smoke; response headers are checked | Staging TLS termination, certificate handling, ingress policy, and denial tests |
| Authentication | Strict software smoke observed HTTP 401 for unauthenticated `/metrics` and `/v1/assessments` | Staging identity, authorization roles, key provisioning, and access review |
| Request size | Configured body limit observed with typed 413 behavior | Deployment-level request, concurrency, and upstream timeout limits |
| Rate and time limits | No deployment rate-limit or timeout drill is claimed | Staging load/rate-limit evidence with approved thresholds and timeout behavior |
| Secret management | Production-like software smoke fails closed when API-key configuration is absent | Secret-manager integration, rotation drill, revocation, and audit evidence |
| Artifact admission | Temporary hash-bound model, panel, and approval sidecar reached `/readyz` 200 in the software gate; development fixture reached 503 | Immutable approved artifact, signed or retained release receipt, and deployment admission record |
| Dependency and SBOM | Locked resolution, wheel build, installed provenance, and package-tree digest pass locally | Generated SBOM, vulnerability review, patch policy, and retained scan receipt |
| Runtime support | Windows 3.11 installed-wheel and loopback evidence exists | Same candidate SHA on Linux and the supported Python matrix |
| Monitoring | Body-free logs and bounded process-local metrics expose status classes, latency, and oversize rejections | Infrastructure aggregation, alert ownership, retention policy, incident drill, and readiness-transition monitoring |
| Backup and restore | Rollback and restore procedure is documented in [`OPERATIONS.md`](OPERATIONS.md) | Timed restore drill against immutable artifacts and retained result |
| Capacity and availability | No approved service-level targets or load result is claimed | Prespecified capacity, latency, availability targets and a staging load receipt |
| Governance | Research and wellness development only; clinical use remains forbidden | Qualified security, privacy, data-governance, product, and clinical review for any broader use |

## Observed local receipt

[`ir0-wheel-smoke-2026-09-10.json`](ir0-wheel-smoke-2026-09-10.json) records the
dirty-working-tree Windows 3.11 installed-wheel smoke. It observed health,
metrics, valid and invalid assessment paths, comparison, local SECA handling,
installed-distribution provenance, development fail-closed readiness, and a
temporary software-gate readiness path. It does not establish a clean release,
TLS, staging, infrastructure rate limiting, SBOM approval, rollback drill, or
clinical readiness.

## Release boundary

Keep `clinical_gate: E-005 blocked` visible. Do not admit real-person traffic
or convert the temporary software-gate bundle into a clinical model. Any
deployment receipt must retain the candidate identity, artifact and panel
hashes, configuration identity, reviewer, date, observed results, and open
controls from this matrix.
