# Project maturity and public trust review

Review date: 2026-09-10. Decision: credible engineering prototype, but published
research-showcase quality is not yet demonstrated. This is a bounded audit and
goal-setting document, not clinical, security or production certification.

The active execution contract is
[T1: trustworthy research showcase](../goals/completed/trustworthy-research-showcase/GOAL.md).
Root GOAL and IR0-IR7 remain authoritative for scientific and release boundaries.

## What was inspected

- Live [GitHub Pages](https://stancsz.github.io/frailty-index-deficit-accumulation-model/)
  and a separate local browser preview of the current `docs/` working tree.
- Rendered desktop overview and demo/report states at 1440x1000; mobile
  overview at 390x844. Screenshots were personally inspected, not merely saved.
- Page structure/text and local synthetic SECA-load action. The latter displayed
  four mapped canonical fields and an explicit incomplete-assessment message.
  Its no-upload message was observed; this audit did not independently capture
  a complete network trace for that interaction.
- GOAL, NORTHSTAR, ROADMAP, README, research report, Pages HTML, comparison and
  schema surfaces, CI workflows, package metadata, security/license documents,
  local verification/browser receipts, live Actions status and key live links.
- Full local `uv run python scripts/verify_project.py --json`: 20/20 passed,
  including executed Python/Node checks and serving smoke; E-005 stays blocked.
- Official seca, InsideTracker and Dalhousie pages. InsideTracker Science and
  Dalhousie FI public desktop pages were also visually inspected. No logged-in
  competitor workflow, clinical equivalence or outcome efficacy was evaluated.

Not inspected exhaustively: every source line or dependency, real patient
workflow, all rendered sections/states, physical mobile devices, screen-reader
operation, actual 200% browser UI zoom, final release network behavior,
penetration testing, independent clinical validity and full competitor products.
Earlier browser receipts are supporting local evidence, not new live passes.

## Current maturity by dimension

| Dimension | Observed strength | Remaining gap |
|---|---|---|
| Measurement integrity | Canonical inputs, MVV, comparison guard and explicit missingness have local checks. | Qualified interpretation review and final-candidate regression evidence. |
| Engineering | Full verifier passes locally; the fresh temporary current candidate `5dd24112f6582c211b4c93b505db61c2c1e66b26` also passes locked Windows installation, docs checks and installed-wheel/loopback HTTP smoke; Windows/Linux CI and wheel smokes are defined; local Pages now runs pytest. Remote verify run `34548964641` and Pages run `34548964642` succeeded for `7fc8fca`. | The candidate snapshot predates final reference reconciliation and is not owner-frozen, pushed or published; remote same-SHA Linux and final live identity evidence remain open. |
| User experience | Synthetic profiles, local preview, report and export controls exist. | Technical-first hierarchy; missing completed user study; visual review gaps. |
| Scientific transparency | Explicit synthetic panel/development predictor and blocked E-005. | Citations and fixtures do not establish model validity; some public copy conflicts. |
| Publication trust | Inspectable repository and evidence files; the live audit records HTTP 200 and successful Pages execution for `7fc8fca`. | The live HTML still has superseded wording, the current claim inventory returns 404, and live assets are not reconciled with the current dirty candidate. |
| Ownership/operations | Privacy and operational boundaries are documented. | Evaluation terms/owner clarity, working private reporting route, runtime-support evidence and later staging controls. |

The IR4 preparation subdeliverable is now explicit: the repository contains a
non-approving musculoskeletal protocol, a public-data manifest with pending
hashes and review fields, and a shape validator that passes. The T1 reviewer
package also contains executable human-review materials. These preparations do
not close qualified review, IR0-IR3, IR4-IR7, or E-005.

No aggregate maturity percentage is assigned. These dimensions have different
evidence requirements and cannot substitute for one another.

## Findings and priority

### P0: visitors receive an older and materially different page

Live HTML returned 200 and matched `docs/index.html` at commit
`35e3e14b0acb5c80b1f46dbb9791439fbf4238c0` byte-for-byte, with SHA-256
`718fb834d1a88a41fdfb0d3686a28c3ce4306a963258209263c2af682923fe96`.
Do not call failed commit `2f1218b9d20b61ee9682cdae0a5a74dd79a7f653` deployed.
No injected `__BUILD_META__` was found in the observed HTML. The live receipt
contained 120 collected Python tests and 23 Node tests; local counts were 146/28.
The live first screen advertised `Tests: 120 / 120 passing`.

The live balanced demo visibly showed biological age **42.9 years** and
homeostatic deviation **-4.7%**. The local corresponding cards showed withheld.
The live `/RESEARCH_REPORT.md` returned 404; the local report exists. The new local page targets
GitHub main `LICENSE.md`, which also returned 404. This publication gap directly affects
the truth of the visitor experience. T1.3 and T1.6 must close it.

### P1: the first screen prioritizes implementation over user value

The desktop typography and restrained colors are a usable starting point.
The problem is hierarchy and density, not evidence that AI authored the page.
The live page leads with a technical title, multiple status chips, a twelve-item
contents list, a developer-facing summary and a dense at-a-glance table.

The local draft adds a large citation/BibTeX panel and metadata before the
summary. In the inspected 1440px layout the summary began around y=789 and the
demo around y=7704. On mobile, citations and technical links occupied the entire
first screen before purpose or a usable primary action. Promote the measurement
workflow; move citation code, hashes and developer details into secondary views.

### P1: the published mobile layout overflows

With a 390px emulated viewport, live `documentElement.clientWidth` was 390 and
`scrollWidth` was 740. The screenshot showed compressed content occupying only
part of the screen. The local mobile first screen appeared improved, but a
single screenshot cannot certify all tables, forms or export states. Require
document-level containment on the final URL and real task-state inspection.

### P1: honest withholding still dominates the local report

The local report corrects the age output but gives two large withheld cards
prominence beside FI. It also displays technical field names and long hashes.
That communicates what the tool cannot do before what it can show. Lead with
measurements, coverage and denominator, then explain limits beside the affected
result. Withholding must remain accurate in the export as well as on screen.

### P1: current evidence and development history are mixed

`docs/index.html` retains a historical 56-Python/10-Node pass statement beside
newer 146/28 references and describes a public export as including an
age-equivalent readout. The research report says numeric public age is withheld.
The evidence history repeats self-assigned high-confidence labels. The fixture
label "anonymized synthetic" also obscures whether any real records are involved.
Create a concise current claim register and archive historical milestones.
Test counts support inventory, not an executed pass or clinical claim.

### P2: public accountability and repository handoff need closeout

LICENSE leaves final holder/terms to later agreement. SECURITY describes a
conditional private route; the GitHub private-vulnerability-reporting API
reported `enabled: false`. Establish an actual owner-approved reporting path
without sending a test report to anyone during this audit. `pyproject.toml`
declares Python >=3.10 while the CI matrix uses 3.11: retain evidence for the
claimed range or narrow support wording. SBOM/vulnerability and staging gaps
remain in IR6; do not make full patient-service infrastructure a prerequisite
for an honest static research page.

### P1: comprehension is still a hypothesis

The study protocol records no participant results. Manual screen-reader,
actual zoom, full keyboard journey, dark-mode/non-color and human print review
are still pending. A named accessibility tree or automated contrast sweep does
not replace those checks. Retain IR1/IR3 thresholds and test the final package.

## Comparable practices to adopt selectively

These are public evidence and workflow references, not a claim of competitive
parity or an endorsement. Checked on 2026-09-10.

| Reference | Observed practice | Apply here | Do not transfer |
|---|---|---|---|
| [seca clinical studies](https://www.seca.com/en_ph/products/body-composition-analysis/clinical-studies.html) | Separates validation publications from reference data and identifies methods/populations. | Link each interpretation to its method, applicable population and evidence status. | Device validation, correlation or vendor superlatives as validation of this engine. |
| [InsideTracker Science](https://www.insidetracker.com/science) | Dedicated science navigation and named research; public design separates navigation from content. | Keep a discoverable evidence destination connected to the user journey. | Its prominent study/customer/data-count marketing or outcome claims as a trust shortcut; no equivalent evidence exists here. |
| [Dalhousie Frailty Index](https://www.dal.ca/sites/gmr/our-tools/the-frailty-index.html) | Plain method explanation within an identifiable research group, with tool/contact navigation. | Explain deficit accumulation near the result and make accountable ownership easy to find. | Authority of the general FI concept as approval of this item set, cutoff choices, age transform or longitudinal output. |
| [Dalhousie Clinical Frailty Scale](https://www.dal.ca/sites/gmr/our-tools/clinical-frailty-scale.html) | Describes intended clinical context and provides references/permission guidance. | Clearly state user, setting, interpretation limits and evaluation terms. | Conflating CFS and FI, copying protected scale material, or implying a clinical endorsement. |

Recommended structure: purpose and current status; inspect a synthetic report;
method/evidence and limitations; ownership and collaboration/contact. Retain
the deeper developer documentation without forcing it into the primary journey.
Do not add stock clinical imagery, institutional-looking seals or invented
testimonials to compensate for missing evidence.

## Visual evidence

BrowserOS neo rendered the following project captures. Mobile means emulation,
not physical-device testing. The local server was `http://127.0.0.1:8773/`.
Screenshots show the baseline only and are not acceptance evidence for a redesign.

| Surface | Screenshot |
|---|---|
| Published overview, desktop | [Capture](reviews/trust-maturity-2026-09-10/published-desktop.jpg) |
| Published overview, mobile | [Capture](reviews/trust-maturity-2026-09-10/published-mobile.jpg) |
| Published demo, desktop | [Capture](reviews/trust-maturity-2026-09-10/published-demo.jpg) |
| Local overview, desktop | [Capture](reviews/trust-maturity-2026-09-10/local-desktop.jpg) |
| Local overview, mobile | [Capture](reviews/trust-maturity-2026-09-10/local-mobile.jpg) |
| Local demo, desktop | [Capture](reviews/trust-maturity-2026-09-10/local-demo.jpg) |

## Decision

Proceed with T1 as the next execution goal. Complete the claim inventory and
measurement-first page, verify a single release, and obtain human review.
Keep clinical validity, new models and broader service deployment outside this
goal. Creating this audit and goal does not repair or approve the published site.
