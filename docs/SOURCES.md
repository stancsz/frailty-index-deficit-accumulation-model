# Evidence and source boundary

This file keeps the implementation's evidence boundary visible. A citation
supports the general method or a published threshold; it does not prove that
the prototype is calibrated for a particular clinic, device, ethnicity, age
range, or use case.

## Privacy and security review boundary

The repository's implemented data-flow controls, residual deployment risks,
retention boundaries, and incident checklist are maintained in
[`PRIVACY_THREAT_MODEL.md`](PRIVACY_THREAT_MODEL.md). That document is an
engineering review artifact, not a compliance attestation or clinical evidence.
The contributor/operator policy is maintained in [`SECURITY.md`](../SECURITY.md)
and does not claim regulatory or clinical conformance.

## Deficit accumulation

- Searle et al., “A standard procedure for creating a frailty index,” *BMC
  Geriatrics* (2008), [open-access article](https://pmc.ncbi.nlm.nih.gov/articles/PMC2573877/).
  This supports the accumulated-deficit construction, 0-to-1 coding,
  intermediate 0.5 values, and the importance of using a sufficiently broad
  set of deficits. The implementation keeps missing variables out of the
  denominator and exposes that denominator in the response.
- Mitnitski et al., “Accumulation of Deficits as a Proxy Measure of Aging,”
  *The Scientific World Journal* (2001),
  [doi:10.1100/tsw.2001.58](https://doi.org/10.1100/tsw.2001.58). This supports
  the deficit-accumulation framing, not a claim that this particular 33-item
  FI is clinically validated.

## BIA transfer calibration

- Peine et al., “Generation of normal ranges for measures of body composition
  in adults based on bioelectrical impedance analysis using the seca mBCA,”
  *International Journal of Body Composition Research* (2013), listed in the
  [seca clinical studies reference page](https://www.seca.com/en_er/products/body-composition-analysis/clinical-studies.html).
- Bosy-Westphal et al., “Quantification of whole-body and segmental skeletal
  muscle mass using phase-sensitive 8-electrode medical bioelectrical
  impedance devices,” *European Journal of Clinical Nutrition* (2017),
  [doi:10.1038/ejcn.2017.27](https://doi.org/10.1038/ejcn.2017.27).

The code provides a versioned `ReferencePanel` loader and a synthetic fixture
only. It does not embed the published tables. A production panel must be
supplied with age/sex bands, units, provenance, and approval metadata.

## SECA TableView import

- A clinic-provided local TableView export supplied during development was
  used to verify the observed CSV shape: `Value`, `Unit`, dated columns, body
  composition rows, and segmental skeletal-muscle rows. The named/patient-
  specific file is intentionally not copied into this repository or its Pages
  artifact.
- `src/frailty_engine/seca.py` maps only observed values. It derives fat-free
  mass and FFMI only when same-scan weight, fat mass, and BMI are present, and
  retains the scan date, segment values, unit warnings, and latest-minus-
  previous trend. This is an import/provenance decision, not evidence that the
  export's measurements are clinical outcome predictors.

## NHANES data preparation

- CDC's [continuous NHANES examination data index](https://wwwn.cdc.gov/nchs/nhanes/search/datapage.aspx?Component=Examination&Cycle=2003-2004)
  publishes the 1999-2000, 2001-2002, and 2003-2004 BIA XPT files and their
  documentation. The BIA documentation identifies the legacy Xitron BIS
  measurements and quality-fit fields. The adapter uses only explicitly mapped
  raw columns and does not claim that they are equivalent to modern SECA
  outputs without transfer calibration.
- CDC's [National Death Index linkage page](https://www.cdc.gov/nchs/linked-data/mortality-files/index.html)
  documents the public-use NHANES linked-mortality release and its disclosure
  protections. The [public-use file directory](https://ftp.cdc.gov/pub/health_statistics/NCHS/datalinkage/linked_mortality/)
  lists the cycle files. The adapter follows CDC's supplied
  [SAS fixed-width reader](https://ftp.cdc.gov/pub/health_statistics/NCHS/datalinkage/linked_mortality/SAS_ReadInProgramAllSurveys.sas)
  for SEQN, eligibility, mortality status, and MEC follow-up positions.

Public-use data availability is not clinical approval. The linked-mortality
documentation notes that some follow-up or cause-of-death values were
perturbed for disclosure control; vital status was not perturbed. The cohort
provenance, versioned `SurveyDesign` declaration, survey-weighting/variance
plan, reference-panel approval, cutoff review, and external clinical validation
remain required before production use. The shipped adapter records this design
intent but does not implement complex-survey variance estimation.

## Cutoff boundary

The following sources are the review starting points for the explicit
engineering defaults in `fi.py`; they are not a completed clinical validation
package:

- BMI: [WHO BMI classification](https://www.who.int/data/gho/data/themes/topics/topic-details/GHO/body-mass-index).
- Blood pressure: Whelton et al., 2017 ACC/AHA guideline,
  [doi:10.1161/HYP.0000000000000065](https://doi.org/10.1161/HYP.0000000000000065).
- Waist circumference: International Diabetes Federation,
  [worldwide definition of the metabolic syndrome](https://idf.org/media/uploads/2023/05/attachments-30.pdf).
- Glycemia: American Diabetes Association, “2. Classification and Diagnosis
  of Diabetes,” [open-access Standards of Care chapter](https://diabetesjournals.org/care/article/47/Supplement_1/S20/153954/2-Diagnosis-and-Classification-of-Diabetes).
- eGFR categories: KDIGO 2012 CKD guideline,
  [KDIGO guideline PDF](https://kdigo.org/wp-content/uploads/2017/02/KDIGO_2012_CKD_GL.pdf).
- Grip strength: Cruz-Jentoft et al., EWGSOP2, [doi:10.1016/j.ageing.2018.05.003](https://doi.org/10.1016/j.ageing.2018.05.003).
- FIB-4: Sterling et al., [doi:10.1002/hep.22759](https://doi.org/10.1002/hep.22759).

The thresholds are intentionally easy to audit and replace. They should not be
described as sex-, age-, or ethnicity-validated until the external validation
work in `EVAL.md` is complete.

The FI denominator labels (low = 0–18, moderate = 19–27, high = 28–33)
are count-only engineering defaults for communicating how many of the 33
FI-eligible items were measured in one assessment. They are not completeness
cutoffs, clinical adequacy judgments, or patient targets, and remain pending
cohort review.

## Biological age

- Levine and Crimmins, “Is 60 the New 50? Examining Changes in Biological Age
  Over the Past Two Decades,” *Demography* (2018),
  [doi:10.1007/s13524-017-0644-5](https://doi.org/10.1007/s13524-017-0644-5).
  This supports the conceptual age-equivalent risk mapping. The prototype's
  Gompertz parameters are explicit software defaults and are not a substitute
  for fitting a baseline mortality curve to the approved training cohort.

## Prediction-model credibility and AI governance

- XGBoost's [parameter documentation](https://xgboost.readthedocs.io/en/latest/parameter.html)
  documents that `survival:cox` default predictions are on the exponentiated
  hazard-ratio scale. The adapter therefore requests `output_margin=True` for
  the raw linear predictor used by the Gompertz mapping; the repository locks
  this behavior with a native round-trip regression test. This documents the
  software output contract, not model validity.

- Collins et al., “TRIPOD+AI statement,” *BMJ* (2024),
  [doi:10.1136/bmj-2023-078378](https://doi.org/10.1136/bmj-2023-078378).
  This is a reporting checklist for developing and evaluating prediction
  models using regression or machine learning. It is used here as a reporting
  completeness reference, not as validation of the engine.
- Moons et al., “PROBAST+AI,” *BMJ* (2025),
  [doi:10.1136/bmj-2024-082505](https://doi.org/10.1136/bmj-2024-082505).
  This is the planned risk-of-bias and applicability review lens for the
  training and external-validation study.
- Tabassi, “Artificial Intelligence Risk Management Framework (AI RMF 1.0),”
  NIST (2023), [NIST AI 100-1](https://doi.org/10.6028/NIST.AI.100-1).
  This supplies a lifecycle trustworthiness vocabulary—validity/reliability,
  safety, security, transparency, explainability, privacy, and fairness—that
  informs the model-card and monitoring gates.
