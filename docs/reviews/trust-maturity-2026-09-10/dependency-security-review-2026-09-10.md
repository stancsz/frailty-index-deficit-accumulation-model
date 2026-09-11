# Dependency, runtime and security-route review

Review date: 2026-09-10. Owner: project maintainer. This is a local review
receipt, not a security certification or deployment approval.

## Observed repository and runtime evidence

- `uv lock --check` passed for the checked-in lock file.
- `uv run python --version` observed Python 3.13.11 in the current checkout and
  in the clean candidate wheel smoke. The current temporary candidate is
  `5dd24112f6582c211b4c93b505db61c2c1e66b26`; it is local-only and excludes
  its self-referential receipt and freeze manifest.
- The package declares Python `>=3.10` in `pyproject.toml`. The retained clean
  candidate receipt records successful locked wheel and HTTP smokes on Python
  3.11.14 on Windows and Python 3.12.3 under WSL Ubuntu. Python 3.10 and
  3.12 outside that receipt are not independently certified here.
- The static Pages surface has no Node package manifest or lockfile. Its parser
  and rendering code are exercised directly by the checked-in Node test suite.
- The current canonical verifier passed all required software checks and still
  reports `clinical_gate: E-005 blocked`.

## Dependency audit

On 2026-09-10, an ephemeral `pip-audit 2.10.1` environment was run against the
current locked environment with:

```powershell
uv run --with pip-audit pip-audit --format json --progress-spinner off
```

The command reported `No known vulnerabilities found` for the audited
third-party Python packages. The local project distribution was skipped because
it is not published on PyPI, so this result is not a source-code audit,
JavaScript audit, deployment scan, or guarantee against future advisories.

## GitHub reporting route

The repository is public, issues are enabled, Discussions are disabled, and
the GitHub API reports `private-vulnerability-reporting.enabled: false`.
Secret scanning and push protection are enabled; Dependabot security updates
are disabled. Therefore the project must not imply that private vulnerability
reporting is currently available. The documented fallback is a minimal,
non-revealing public issue asking for a secure maintainer channel, with no
patient data, credentials, raw scans, or exploit detail.

## Remaining review boundary

This receipt does not establish a supported hosted deployment, TLS, ingress,
identity, secret management, rate limiting, SBOM review, or clinical safety.
Those remain deployment-owner and E-005 obligations.
**Status:** dated dependency/security review evidence; not a security
attestation, production approval, or active execution plan.
