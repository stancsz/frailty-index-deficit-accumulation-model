# 019 - Real data category coverage intake

On 2026-09-11 the repository retrieved and inspected public CDC NHANES files
for body composition, BIA, muscle, joints, bone, skin, blood, cardiovascular,
cardiorespiratory, immune/inflammatory, brain/cognitive, metabolic, kidney,
liver, sleep/recovery, lifestyle/function, and mental-health history coverage.

The source hashes and field identities are in
[`REAL_DATA_INTAKE_RECEIPT_2026-09-11.json`](../REAL_DATA_INTAKE_RECEIPT_2026-09-11.json).
The executable aggregate mapper is
[`scripts/build_category_data_receipt.py`](../../scripts/build_category_data_receipt.py),
and the privacy-safe observed-count summary is
[`CATEGORY_DATA_RECEIPT_2026-09-11.json`](../CATEGORY_DATA_RECEIPT_2026-09-11.json).
The privacy-safe numeric source summary is
[`CATEGORY_NUMERIC_SUMMARY_2026-09-11.json`](../CATEGORY_NUMERIC_SUMMARY_2026-09-11.json).

The local run verified 17 of 17 current categories have at least one observed
real source field or measured proxy. The joint and lifestyle/function mappings
also include the official Physical Functioning file's adult walking, standing,
work-limitation, and equipment variables. Cardiorespiratory coverage also includes
the official spirometry file's baseline FVC, FEV1, flow, quality, and
acceptable-curve fields. Lipid laboratory fields, sleep duration/disorder
fields, the full DPQ depression-screener item set, and objective wrist-monitor
day summaries are also represented. Joint coverage includes arthritis/gout history
and adult functional-difficulty items. The modern cycle has direct spinal-
mobility examination data but no knee radiograph. It also includes the official NHANES III `xr.dat`
fixed-width knee-radiograph source, with 2,589 records and bilateral
Kellgren-Lawrence, osteophyte, sclerosis, chondrocalcinosis, and replacement
fields. That source is from the 1991–1994 age-eligible radiograph sample and
must not be silently treated as a 2011–2012 measurement. The receipt distinguishes repeated day rows
from unique participants. This is source-coverage evidence only. It
does not establish a category construct, validated reference band, clinical
cutoff, category age, clinical reference interval, or E-005 approval. Numeric
category ages remain withheld.

Joint coverage also includes the official 2009–2010 `ARX_F.XPT` arthritis
body-measures file, with 5,001 records containing occiput-to-wall distance,
chest expansion, and lumbar-flexion measurements for the documented 20–69
eligible sample. CDC describes these as clinical spinal-mobility tests. The
source strengthens contemporary direct measurement coverage but does not
establish a harmonized joint construct or clinical cutoff.

Mental-health coverage now also maps the 2011–2012 Current Health Status file:
general health, recent physical-health days, recent mental-health days,
activity-limitation days, pain interference, anxiety days, and the source of
the interview response. These fields complement the full PHQ-9 screener but
remain questionnaire evidence rather than diagnosis or treatment outcome.

Immune/inflammatory coverage also includes the official 2009–2010 CRP file
(`CRP_F.XPT`) with `LBXCRP`, alongside the 2011–2012 CBC differential fields.
The CRP value is retained as an inflammatory biomarker and is not treated as a
disease diagnosis or clinical cutoff.

Cardiovascular and blood coverage also includes 2011–2012 apolipoprotein B
(`APOB_G.XPT`, `LBXAPB`, `LBDAPBSI`) as a distinct lipid-particle measure. It
is retained with its laboratory subsample boundary and is not interpreted
without the corresponding weight and survey-design review.

Cardiorespiratory coverage also includes the official 2011–2012 exhaled nitric
oxide file (`ENX_G.XPT`), with exam status, attempt count, trial values, and
the mean of two reproducible FENO measures. CDC documents this as an airway
inflammation marker for participants aged 6–79. It is not treated as an asthma
or COPD diagnosis.

Kidney coverage also includes the official 2011–2012 urine albumin/creatinine
component (`ALB_CR_G.XPT`), with albumin and creatinine in reported units plus
the albumin-to-creatinine ratio. These fields complement serum creatinine, BUN,
and uric acid, while detection-limit and survey-design handling remain open.

Liver coverage also includes the official 2017–March 2020 pre-pandemic
transient-elastography file (`P_LUX.XPT`), with 10,409 records containing exam
status, retained-measure count, liver stiffness, stiffness-quality, and
controlled-attenuation measurements. This later-cycle direct FibroScan source
is retained separately from the 2011–2012 enzyme cohort.

The same cycle also contributes `ARQ_F.XPT`, with 5,106 adult records covering
chronic back or neck pain, inflammatory back-pain indicators, heel or tendon
symptoms, and related inflammatory conditions. These are kept as questionnaire
context and are not substituted for the direct mobility measurements.

Skin coverage also includes the official 2003–2004 `DEX_C.XPT` dermatology
examination file: 2,992 records with image-capture status and consensus
dermatologist readings for Fitzpatrick skin type, hand dermatitis, psoriasis,
and affected locations. CDC documents four standardized digital images and
two-reader consensus review for adults aged 20–59. This strengthens source
reality, but does not create a validated skin-health score or remove the cycle,
age, missingness, and clinical-review boundaries.

## Participant-level overlap evidence

The companion [`CATEGORY_OVERLAP_RECEIPT_2026-09-11.json`](../CATEGORY_OVERLAP_RECEIPT_2026-09-11.json)
reports unique participant coverage and pairwise overlap among mapped
categories within each NHANES cycle. It covers 1991-1994, 2003-2004,
2009-2010, 2011-2012, and 2017-March 2020 pre-pandemic sources. The
2011-2012 intake has mapped participant coverage for 16 categories. The receipt
does not join people across cycles and contains no participant identifiers,
raw rows, or measurements. It is evidence that real category sources can be
related within their source cycles, not evidence of harmonized constructs,
representative overlap, clinical validity, or a fitted model.

For the 2011–2012 cycle, the receipt uses 9,756 DEMO_G participants as a
descriptive public-use denominator. Category coverage ranges from 17.292% for
cognitive testing to 95.972% for metabolic data. The intersection of all 16
mapped categories is 0 participants. This makes the missingness and subsample
boundary measurable and prevents the source catalog from being mistaken for a
complete all-category cohort.

## Additional 2013–2014 cycle

[`REAL_DATA_INTAKE_2013_2014_RECEIPT_2026-09-11.json`](../REAL_DATA_INTAKE_2013_2014_RECEIPT_2026-09-11.json)
adds 17 official BMX, DXA, CFQ, DPQ, SLQ, PAXDAY, PFQ, CBC, BIOPRO, BPX,
TCHOL, TRIGLY, GLU, GHB, ALB_CR, MCQ, and DEQ files. This gives a second cycle
for 15 categories. Fluid/BIA and direct liver elastography are not present in
this cycle. The files remain cycle-separated and do not change the 2011–2012
denominator or establish harmonized clinical constructs.

## Additional 2015–2016 cycle

[`REAL_DATA_INTAKE_2015_2016_RECEIPT_2026-09-11.json`](../REAL_DATA_INTAKE_2015_2016_RECEIPT_2026-09-11.json)
adds 15 official files with field-level counts for 15 categories: body,
muscle, bone, joint history, skin, blood, cardiovascular, cardiorespiratory,
immune, metabolic, kidney, laboratory liver, sleep, lifestyle/function, and
mental health. The receipt explicitly records that no BIA fluid or CFQ
cognitive source was identified in this cycle, and that liver coverage is
laboratory-only rather than elastography. It emits no raw rows, measurements,
or participant identifiers.

## Additional 2017–2018 category cycle

[`REAL_DATA_INTAKE_2017_2018_CATEGORY_RECEIPT_2026-09-11.json`](../REAL_DATA_INTAKE_2017_2018_CATEGORY_RECEIPT_2026-09-11.json)
adds 18 official files covering 15 categories with field-level counts and
source hashes. BIA fluid and CFQ cognitive sources are explicitly absent from
the mapped intake. Direct liver elastography remains separately represented by
`LUX_J.XPT`, so this receipt does not merge laboratory and elastography claims.

## Additional 2021–2023 cycle

[`REAL_DATA_INTAKE_2021_2023_CATEGORY_RECEIPT_2026-09-11.json`](../REAL_DATA_INTAKE_2021_2023_CATEGORY_RECEIPT_2026-09-11.json)
adds 12 official files covering 11 categories with current body, joint-history,
skin, blood, lipid cardiovascular, immune, metabolic, kidney, laboratory liver,
sleep, mental-health, alcohol, physical-activity, and smoking fields. It
explicitly records absent BIA, grip/DXA muscle, DXA bone, CFQ cognition,
BPX/spirometry, PFQ, and objective activity-monitor sources.

The [`RECENT_CATEGORY_OVERLAP_RECEIPT_2026-09-11.json`](../RECENT_CATEGORY_OVERLAP_RECEIPT_2026-09-11.json)
reports privacy-safe same-cycle overlap for the recent receipts. The mapped
all-category intersections are 0 across 15 categories in 2013–2014, 1,095
participants for 15 categories in 2015–2016, 873 for 15 categories in 2017–2018,
and 1,360 for 12 categories in 2021–2023. It emits no identifiers, raw rows, measurements, or cross-cycle
joins.

Liver health has a second direct source receipt for 2017–2018 `LUX_J.XPT`,
with 6,401 records and stiffness, quality, and controlled-attenuation fields.
It is deliberately kept separate from the 2017–March 2020 pre-pandemic
`P_LUX.XPT` source.

The [`CATEGORY_QUALITY_RECEIPT_2026-09-11.json`](../CATEGORY_QUALITY_RECEIPT_2026-09-11.json)
audits missing rows and candidate special-code counts for every primary
category. It is deliberately non-destructive: values are not removed or
classified as invalid. Codebook, eligibility, survey-design, and clinical
interpretation review remain open.
The [codebook receipt](../NHANES_CODEBOOK_RECEIPT_2026-09-11.json) records 99
official CDC documentation/layout URLs across eight source cycles with content
hashes. It verifies source traceability, not clinical approval.
Equivalent quality receipts cover the 2013–2014 package and the 2017–2018
liver package, preserving the same no-cleaning boundary across cycles.
The representative [codebook review](../NHANES_CODEBOOK_REVIEW_2026-09-11.json)
records official semantics for DPQ, PAM, chemistry, anthropometry, and liver
elastography fields; it is not a complete field-by-field approval.

The [`CATEGORY_NUMERIC_COVERAGE_RECEIPT_2026-09-11.json`](../CATEGORY_NUMERIC_COVERAGE_RECEIPT_2026-09-11.json)
now verifies non-missing numeric source coverage for all 17 current
categories. It records per-category field counts and minimum/maximum
participant counts while emitting no identifiers, raw rows, or measurements.
Sparse category fields remain visible, and the receipt is source coverage only,
not a harmonized cohort or clinical validation.

The [`CATEGORY_CYCLE_MATRIX_2026-09-11.json`](../CATEGORY_CYCLE_MATRIX_2026-09-11.json)
reconciles this by cycle: the primary multi-cycle package covers 17/17
categories, while 2005–2006, 2013–2014, 2015–2016, and 2017–2018 cover 15/17 each,
2007–2008 covers 13/17, and 2021–2023 covers 12/17. It records declared absences instead of silently treating them as
patient missingness, and performs no cross-cycle joins.

The [`CATEGORY_QUALITY_SUMMARY_2026-09-11.json`](../CATEGORY_QUALITY_SUMMARY_2026-09-11.json)
adds per-category missingness-rate ranges and candidate special-code counts.
Values are not filtered or classified. This makes sparse and dirty source
fields auditable without turning source quality into clinical validity.
The [`CATEGORY_DISTRIBUTION_RECEIPT_2026-09-11.json`](../CATEGORY_DISTRIBUTION_RECEIPT_2026-09-11.json)
adds q05, q25, median, q75, q95, and unique-participant counts for one real
field in each of the 17 categories. Coded public-use fields remain labeled as
source distributions, not clinical reference intervals.
The runtime category catalog now exposes the receipt, source file, and field
for each representative distribution without embedding participant values.
