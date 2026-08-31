# 003 — What external standards should govern the credibility review of this clinical healthspan prediction engine?

- **scope:** This repository's v0.1.0 development-only FI, biological-age,
  SECA, and GitHub Pages surfaces, verified 2026-08-27.
- **status:** draft
- **verified:** 2026-08-27
- **decision it feeds:** Which evidence and governance work must be complete
  before the engine can be presented as clinically credible or production-ready.

## Answer

Use different standards for different questions. **TRIPOD+AI** is a reporting
completeness lens for development and evaluation studies; **PROBAST+AI** is a
risk-of-bias and applicability lens. The BMJ external-validation guidance
turns those lenses into a study workflow covering cohort identity, endpoint and
censoring, discrimination, calibration, uncertainty, subgroup support, and
clinical utility. None of these frameworks validates a model by themselves.

For the product lifecycle, use the joint **Good Machine Learning Practice**
principles, Health Canada's MLMD pre-market guidance and transparency
principles, and WHO's AI-health governance guidance. Together they make the
review broader than model accuracy: intended use, representative data,
reference standards, human-AI workflow, security, transparency, change
control, monitoring, and accountability must be explicit.

The repository's selective implementation map is
[`CLINICAL_ML_EVIDENCE_CROSSWALK.md`](../CLINICAL_ML_EVIDENCE_CROSSWALK.md).
It records which obligations are software controls, templates/deferred
decisions, or missing external evidence. The current conclusion is unchanged:
software evidence is substantial, but **E-005 remains blocked**. The default
model and reference panel are development fixtures, the protocol and training
manifest are templates, and no framework checklist, synthetic test, or
crosswalk is external clinical validation or regulatory clearance.

## Receipts

- TRIPOD+AI provides a structured reporting checklist for prediction-model
  development and evaluation studies using regression or machine-learning
  methods — [BMJ 2024](https://www.bmj.com/content/385/bmj-2023-078378) —
  confidence: high for the framework's reporting purpose.
- PROBAST+AI separates model-development quality from evaluation risk of bias
  and assesses applicability, including algorithmic bias and fairness —
  [BMJ](https://www.bmj.com/content/388/bmj-2024-082505) — confidence: high
  for the framework's appraisal purpose.
- External validation should report discrimination, calibration, uncertainty,
  support, and clinical utility when predictions inform decisions —
  [BMJ external-validation guidance](https://www.bmj.com/content/384/bmj-2023-074820)
  — confidence: high for the methodological guidance; target-cohort
  sufficiency remains unverified here.
- Model development requires a design and validation strategy that is
  appropriate to the available data and intended use; clinical utility is a
  separate question from predictive performance —
  [BMJ developing-models guide](https://www.bmj.com/content/386/bmj-2023-078276)
  — confidence: high for the methodological guidance.
- GMLP calls for multidisciplinary lifecycle expertise, good software and
  security practices, representative participants/data, independent test
  sets, reference datasets, and design matched to intended use —
  [Health Canada / FDA / MHRA GMLP](https://www.canada.ca/en/health-canada/services/drugs-health-products/medical-devices/good-machine-learning-practice-medical-device-development.html)
  — confidence: high for the published principles.
- Health Canada's current MLMD guidance treats lifecycle information,
  clinical validation, transparency, risk management, and post-market
  monitoring as part of evidence for safety and effectiveness —
  [Health Canada pre-market MLMD guidance](https://www.canada.ca/en/health-canada/services/drugs-health-products/medical-devices/application-information/guidance-documents/pre-market-guidance-machine-learning-enabled-medical-devices.html)
  — confidence: high for the guidance; regulatory applicability to this
  prototype is not decided here.
- Health Canada's transparency principles emphasize audience, intended use,
  workflow, performance, limitations, bias, monitoring, and change management
  — [Health Canada transparency principles](https://www.canada.ca/en/health-canada/services/drugs-health-products/medical-devices/transparency-machine-learning-guiding-principles.html)
  — confidence: high for the published principles.
- WHO guidance places ethics and human rights at the centre of AI-health
  design, deployment, and governance — [WHO Ethics and governance of AI for
  health](https://www.who.int/publications/i/item/9789240029200) — confidence:
  high for the published guidance.

## Changelog

- 2026-08-27: created as a draft research entry; linked to the selective
  repository crosswalk and kept E-005 explicitly blocked.
