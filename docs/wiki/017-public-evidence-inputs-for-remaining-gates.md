# 017 - Which remaining validation inputs can be obtained from public sources?

- **scope:** 2026-09-10 evidence intake for this repository's IR4-IR7 and remaining T1 review requirements. This records source availability and what each source can support. It does not validate the repository's model or authorize clinical use.
- **status:** draft
- **verified:** 2026-09-10
- **decision it feeds:** which remaining checks can begin with public material, and which need owner decisions, controlled access, primary data collection, or qualified human review.

## Answer

Public sources can support a reproducible data-intake and protocol package now: NHANES public files, their component documentation, survey-design guidance and public linked-mortality documentation are available. They can establish a versioned research data source, variable mapping, public-use restrictions, survey-design handling and disclosure limitations. They cannot establish that the resulting model is clinically valid, transportable, fair, calibrated for a chosen use, or approved.

The CLSA is a possible independent-cohort route, but it is not a public download. It requires an eligible primary applicant, Research Ethics Board approval, an approved application and a signed data-access agreement before release. It is therefore an IR4/IR5 input to pursue, not evidence already available to this repository.

Public guidance can also make the outstanding protocol and review work more concrete. ISCD positions give a defensible starting point for DXA precision and least-significant-change procedures. TRIPOD+AI gives a reporting checklist; PROBAST+AI gives a structured quality, bias and applicability appraisal. None of these standards substitutes for the frozen construct, local measurement repeatability evidence, independent evaluation, five-user study, accessibility review, security controls, or E-005 sign-off.

The repository now retains a non-approving protocol at
`docs/IR4_MUSCULOSKELETAL_PROTOCOL_2026-09-10.md` and a machine-checkable
planning manifest at `docs/IR4_PUBLIC_DATA_MANIFEST_2026-09-10.json`.
`scripts/validate_ir4_manifest.py` passes the manifest shape. The files keep
source hashes, sentinels, survey variance, reviewers, and approval unresolved;
this is preparation evidence only and does not authorize data acquisition or
fitting.

## Public inputs by remaining gate

| Gate or check | Publicly available input | What it can establish here | Still required before the check can pass |
|---|---|---|---|
| IR4 data provenance and protocol | NHANES public-use data, component documentation, codebooks, release/access policy, and analytic guidance | Exact source release, allowed statistical-analysis use, feature/unit mapping, sampling weights, clustering/stratification handling, and a public-data receipt | One frozen musculoskeletal construct and target; cycle-specific selection; permitted-use review; cohort eligibility; endpoint mapping; missingness policy; independent split; sample-size and CI rationale; prespecified thresholds; qualified protocol review |
| IR4 measurement repeatability | ISCD 2023 Adult Official Positions | A starting protocol for facility-specific DXA precision work. It specifies in-vivo precision assessment, repositioned repeated measurements and 95% LSC calculation | The actual device, software, operator and clinic-specific repeatability study; laboratory and functional-measure protocol/repeatability; proof that the selected construct is clinically meaningful |
| IR5 independent evaluation | CLSA data-access route and its protocols/resources | A controlled independent-cohort option with protocol, questionnaire, physical-assessment, data dictionary and sampling-weight resources | Eligible investigator/institution, REB approval, access agreement, approved analysis plan, data receipt, frozen model, leakage-free external evaluation and independent statistical/clinical review |
| IR5 reporting and appraisal | TRIPOD+AI and PROBAST+AI | A public reporting map and an appraisal checklist covering participants/data sources, predictors, outcomes, analysis, applicability, quality and bias | Actual model-development and evaluation results, uncertainty, subgroup and missingness analysis, comparator performance, and reviewer judgments. Checklists are not validation evidence |
| IR1/T1.7 workflow and comprehension | No public dataset can replace it | Public sources can inform a study protocol only | Five intended users completing the defined task, de-identified outcomes, manual-workflow comparator, and clinician review |
| IR3/T1.2 manual accessibility | WCAG 2.2 is public guidance | Target success criteria and a manual-review basis | Actual browser 200% zoom, screen-reader, contrast and non-color reviews on the frozen candidate, with defects resolved |
| IR6 operations and IR7 pilot | Public standards and vendor documentation may inform a future control design | A draft control matrix and test plan | A selected deployment boundary, staging evidence for auth/TLS/limits/SBOM/monitoring/rollback, governance review, and then a governed pilot. Public reading cannot prove deployed controls |
| E-005 clinical gate | Public literature and reporting guidance | The evidence package's required shape and its limits | Approved external-cohort evidence, clinical/statistical review, intended-use and cutoff/reference-panel decision, and recorded qualified approval |

## Immediate, bounded next actions

1. Create an IR4 protocol skeleton before downloading or fitting anything. It should name the construct, intended use, population, predictors, target, comparators, cohort eligibility, missingness rule, survey-design handling, split boundary, metrics, confidence-interval target and stop rule.
2. Build a versioned NHANES intake manifest from selected component documentation and record file URLs, release date, SHA-256, units, sentinel values and the matching analysis weights. Keep raw data outside the repository unless its terms and privacy review permit redistribution.
3. Ask an eligible institution-based investigator whether a CLSA application is justified after the construct and external-validation protocol are frozen. Do not represent the CLSA as available data until approval and agreement are complete.
4. Have the statistician use the TRIPOD+AI map and PROBAST+AI as independent review worksheets. Record every unanswerable item as open instead of treating checklist completion as a pass.
5. Assign clinician, accessibility and user-study reviewers for the existing synthetic T1 package. These checks require observed human work and cannot be filled with public research.

## Receipts

- NHANES says public datasets since the late 1990s are centrally released with component documentation covering protocol, QA/QC, processing and analytic recommendations; some data remain limited-access because of disclosure risk. [CDC NHANES datasets and documentation](https://wwwn.cdc.gov/nchs/nhanes/tutorials/datasets.aspx), accessed 2026-09-10. Confidence: high.
- Continuous NHANES public-use cycles are two-year releases and each is representative of the non-institutionalized US population. [CDC Continuous NHANES](https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/), accessed 2026-09-10. Confidence: high.
- NCHS limits public-use files to statistical analysis or reporting and applies confidentiality restrictions. [CDC Data User Agreement](https://www.cdc.gov/nchs/policy/data-user-agreement.html), accessed 2026-09-10. Confidence: high.
- NHANES analytic guidance documents sample design, weights and variance estimation; the variance tutorial states that weights and design variables are needed for unbiased estimates and accurate standard errors. [CDC survey methods and analytic guidance](https://wwwn.cdc.gov/nchs/nhanes/analyticguidelines.aspx), [CDC variance-estimation tutorial](https://wwwn.cdc.gov/nchs/nhanes/tutorials/varianceestimation.aspx/Weighting.aspx), accessed 2026-09-10. Confidence: high.
- The public-use linked mortality files cover adult participants and use disclosure-control perturbation for some follow-up time or cause-of-death values, while restricted-use versions are available through the RDC. [CDC linked-mortality readme](https://www.cdc.gov/nchs/data/datalinkage/public-use-linked-mortality-file-description.pdf), accessed 2026-09-10. Confidence: high.
- CLSA access is for approved public-sector researchers; the primary applicant needs an eligible appointment/institution and REB approval, and an approved application precedes a signed access agreement. [CLSA data access](https://www.clsa-elcv.ca/data-access/), accessed 2026-09-10. Confidence: high.
- ISCD says every technologist should perform an in-vivo precision assessment with representative patients; it specifies 15 people measured three times or 30 people twice with repositioning and an LSC at 95% confidence. [ISCD 2023 Adult Official Positions](https://iscd.org/official-positions-2023/), accessed 2026-09-10. Confidence: high.
- TRIPOD+AI is guidance for reporting studies that develop or evaluate clinical prediction models. [EQUATOR TRIPOD+AI](https://www.equator-network.org/reporting-guidelines/tripod-statement/), accessed 2026-09-10. Confidence: high.
- PROBAST+AI separates assessment of model-development quality from risk of bias in performance evaluation and examines applicability. [BMJ PROBAST+AI](https://www.bmj.com/content/388/bmj-2024-082505), accessed 2026-09-10. Confidence: high.
- WCAG 2.2 is the chosen accessibility target in the repository, but human review remains open. [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/), accessed 2026-09-10. Confidence: high.

## Changelog

- 2026-09-10: created after public-source intake; no gate status changed.
