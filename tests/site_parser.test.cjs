const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const { MAX_SECA_BYTES, parseSecaCsv } = require(path.join(
  __dirname,
  "..",
  "docs",
  "seca-parser.js",
));
require(path.join(__dirname, "..", "docs", "intake-form.js"));
const intakeForm = globalThis.FrailtyIntakeForm;
const mvvContract = globalThis.FrailtyMvvContract;

const fixture = fs.readFileSync(
  path.join(__dirname, "..", "examples", "seca_tableview_fixture.csv"),
  "utf8",
);
const publicSample = fs.readFileSync(
  path.join(__dirname, "..", "docs", "example-seca-tableview.csv"),
  "utf8",
);
const siteSource = fs.readFileSync(
  path.join(__dirname, "..", "docs", "site.js"),
  "utf8",
);
const intakeSource = fs.readFileSync(
  path.join(__dirname, "..", "docs", "intake-form.js"),
  "utf8",
);
const featuresSource = fs.readFileSync(
  path.join(__dirname, "..", "src", "frailty_engine", "features.py"),
  "utf8",
);
const siteCss = fs.readFileSync(
  path.join(__dirname, "..", "docs", "site.css"),
  "utf8",
);
const pageSource = fs.readFileSync(
  path.join(__dirname, "..", "docs", "index.html"),
  "utf8",
);
const pagesWorkflow = fs.readFileSync(
  path.join(__dirname, "..", ".github", "workflows", "pages.yml"),
  "utf8",
);
const demoData = JSON.parse(
  fs.readFileSync(path.join(__dirname, "..", "docs", "demo-data.json"), "utf8"),
);
const testReceipt = JSON.parse(
  fs.readFileSync(path.join(__dirname, "..", "docs", "test-receipt.json"), "utf8"),
);

test("Pages parser matches the local SECA fixture contract", () => {
  const parsed = parseSecaCsv(fixture);
  assert.equal(parsed.measuredAt, "Jan 2, 2025, 8:00 AM");
  assert.equal(parsed.trendAvailable, true);
  assert.equal(parsed.latest.values.bmi, 25.8);
  assert.ok(Math.abs(parsed.latest.values.fat_free_mass_kg - 56.8) < 1e-9);
  assert.ok(Number.isFinite(parsed.latest.values.estimated_height_cm));
  assert.equal(parsed.latest.values.height_cm, undefined);
  assert.ok(Number.isFinite(parsed.latest.values.ffmi));
  assert.equal(parsed.latest.derivations.length, 3);
  assert.equal(parsed.latest.segments["Left Arm"], 1.74);
  // The latest column is the maximum parsed date, matching the Python importer.
  assert.ok(Math.abs(parsed.trend.bmi + 0.6) < 1e-9);
  assert.ok(Math.abs(parsed.segmentalTrend["Left Leg"] - 0.05) < 1e-9);
  assert.ok(Math.abs(parsed.segmentalTrend["Right Arm"] - 0.04) < 1e-9);
  assert.equal(parsed.assessmentReadiness.assessmentReady, false);
  assert.match(parsed.assessmentReadiness.missingRequirements[0], /age and sex/);
  assert.match(parsed.assessmentReadiness.missingRequirements.join("; "), /blood-panel/);
  assert.match(parsed.assessmentReadiness.note, /not an assessment/);
});

test("Pages parser strips BOM and rejects unparseable dated columns", () => {
  assert.equal(parseSecaCsv("\uFEFF" + fixture).measuredAt, "Jan 2, 2025, 8:00 AM");
  const malformed = fixture.replace("Jan 2, 2025, 8:00 AM", "not-a-date");
  assert.throws(() => parseSecaCsv(malformed), /parseable dates/);
  const ambiguous = fixture.replace("Jan 2, 2025, 8:00 AM", "2025-01-02");
  assert.throws(() => parseSecaCsv(ambiguous), /parseable dates/);
  const extra = fixture.replace('"25.8","26.4"', '"25.8","26.4","unexpected"');
  assert.throws(() => parseSecaCsv(extra), /extra non-empty columns/);
  assert.equal(MAX_SECA_BYTES, 5 * 1024 * 1024);
});

test("Pages parser ignores nonnumeric unmapped rows like the Python importer", () => {
  const withAuxiliaryRow = fixture.replace(
    '"Torso","kg","13.4","13.2"',
    '"Auxiliary note","","N/A","N/A"',
  );
  const parsed = parseSecaCsv(withAuxiliaryRow);
  assert.deepEqual(parsed.unmappedLabels, ["Auxiliary note"]);
  assert.equal(parsed.latest.segments.Torso, undefined);
  assert.equal(parsed.latest.values.bmi, 25.8);
});

test("Pages keeps development and single-scan limits visible", () => {
  assert.match(
    siteSource,
    /Single scan only — trend comparison requires two dated scans\./,
  );
  assert.match(pageSource, /Biological-age readout/);
  assert.match(pageSource, /uncertainty not validated/);
  assert.match(pageSource, /ci_95: null/);
  assert.match(pageSource, /Action effects are not estimated/);
  assert.equal(testReceipt.schema_version, 1);
  assert.ok(testReceipt.python_tests_collected > 0);
  assert.ok(testReceipt.node_tests_collected > 0);
  assert.equal(testReceipt.generated_by, "scripts/build_test_receipt.py");
  assert.match(testReceipt.node_command, /--test-reporter=tap/);
  assert.match(pageSource, /test-receipt\.json/);
  assert.match(pagesWorkflow, /scripts\/build_test_receipt\.py --check/);
  assert.match(pageSource, /seca-parser\.js\?v=e084/);
  assert.match(pageSource, /intake-form\.js\?v=e084/);
  assert.match(pageSource, /site\.js\?v=e084/);
  assert.match(pageSource, /subgroup_support_warnings/);
  assert.match(pageSource, /support warning/);
  assert.match(pageSource, /outcome_metric_status/);
  assert.match(pageSource, /not_implemented_pending_sap/);
  assert.match(pageSource, /verify_project\.py/);
});

test("Pages exposes the canonical SECA assessment overlay helper", () => {
  const parsed = parseSecaCsv(fixture);
  assert.deepEqual(parsed.assessmentPayloadOverlay, {
    bmi: 25.8,
    ffmi: parsed.latest.values.ffmi,
    skeletal_muscle_mass: 28.8,
    visceral_fat: 3.1,
  });
  assert.deepEqual(
    parsed.assessmentPayloadOverlay,
    parseSecaCsv(fixture).assessmentPayloadOverlay,
  );
  assert.match(intakeSource, /frailty-engine-assessment-overlay-v1/);
  assert.match(intakeSource, /No scan or measurement data was uploaded/);
});

test("Pages provides a local MVV-gated SECA assessment handoff", () => {
  assert.match(pageSource, /id="seca-intake"/);
  assert.match(pageSource, /id="intake-fields"/);
  assert.match(pageSource, /id="intake-mvv"/);
  assert.match(pageSource, /id="intake-download"/);
  assert.match(pageSource, /id="intake-patient-id"[^>]*maxlength="128"/);
  assert.match(pageSource, /id="intake-preview"/);
  assert.match(pageSource, /CLI-ready assessment overlay/);
  assert.match(siteSource, /function initSecaAssessmentIntake/);
  assert.match(siteSource, /FrailtyIntakeForm\.render/);
  assert.match(siteSource, /controller\.evaluateMvv\(\)/);
  assert.match(siteSource, /submit\.disabled = !mvv\.ok \|\| !validation\.ok/);
  assert.match(siteSource, /intake\.setExport\(parsedExport, sourceLabel\)/);
  assert.match(siteSource, /intake\.clear\(\)/);
  assert.match(siteSource, /function previewOverlay/);
  assert.match(siteSource, /Confirm and download overlay/);
  assert.match(siteSource, /intake-patient-id/);
  assert.match(intakeSource, /function evaluateMvv\(values\)/);
  assert.match(intakeSource, /function buildOverlay\(values, measuredAt, patientId\)/);
  assert.match(intakeSource, /FrailtyMvvContract/);
  assert.match(intakeSource, /patient_id must be a non-empty/);
  assert.match(intakeSource, /dataset\.intakeSource = "seca"/);
  assert.match(intakeSource, /input\.readOnly = true/);
  assert.match(intakeSource, /input\.disabled = true/);
  assert.doesNotMatch(intakeSource, /fetch\s*\(/);
  assert.doesNotMatch(intakeSource, /XMLHttpRequest/);
});

test("Pages MVV contract agrees with canonical Python feature categories", () => {
  const pythonFeatures = (category) => Array.from(
    featuresSource.matchAll(
      new RegExp(`FeatureSpec\\("([^"]+)", "${category}"`, "g"),
    ),
    (match) => match[1],
  );
  assert.deepEqual(mvvContract.blood, pythonFeatures("blood"));
  assert.deepEqual(mvvContract.history, pythonFeatures("history"));
  assert.deepEqual(mvvContract.mandatory, [
    "age",
    "sex",
    "bmi",
    "phase_angle",
    "ecw_tbw",
  ]);

  const complete = {
    age: 45,
    sex: "female",
    bmi: 25.8,
    phase_angle: 6.1,
    ecw_tbw: 0.39,
    fasting_glucose: 92,
    hba1c: 5.3,
    hs_crp: 0.7,
    albumin: 4.2,
    creatinine: 0.9,
    egfr: 98,
    wbc: 6.0,
    hypertension: 0,
    t2d: 0,
    osteoarthritis: 0,
    sleep_apnea: 0,
  };
  assert.deepEqual(intakeForm.evaluateMvv(complete), { ok: true, missing: [] });
  const missingGlucose = { ...complete };
  delete missingGlucose.fasting_glucose;
  delete missingGlucose.hba1c;
  assert.equal(intakeForm.evaluateMvv(missingGlucose).ok, false);
  assert.match(
    intakeForm.evaluateMvv(missingGlucose).missing.join("; "),
    /fasting_glucose or hba1c is required/,
  );
  const overlay = intakeForm.buildOverlay(
    complete,
    "Jan 2, 2025, 8:00 AM",
    " clinic-42 ",
  );
  assert.equal(overlay.patient_id, "clinic-42");
  assert.equal(overlay.format, "frailty-engine-assessment-overlay-v1");
  assert.throws(
    () => intakeForm.buildOverlay(complete, null, ""),
    /patient_id must be a non-empty/,
  );
});

test("Pages exposes a privacy-safe normalized SECA download contract", () => {
  assert.match(pageSource, /id="seca-download"/);
  assert.match(pageSource, /original CSV or a patient identifier/);
  assert.match(siteSource, /downloadNormalizedSecaSummary/);
  assert.match(siteSource, /seca-tableview-normalized-v1/);
  assert.match(siteSource, /seca-normalized-summary\.json/);
  assert.match(siteSource, /assessment_readiness/);
  assert.match(siteSource, /reference_panel_fixture_only/);
  assert.match(siteSource, /segmental_trend_latest_minus_previous/);
  assert.match(siteSource, /unmapped_labels/);
  assert.match(siteSource, /Unmapped export rows/);
  assert.match(siteSource, /Segment trends \(latest/);
  assert.match(siteSource, /missing_requirements/);
  assert.match(siteSource, /original CSV and patient identifiers are not included/);
  assert.match(siteSource, /function clearSecaDetails\(token\)/);
  assert.equal((siteSource.match(/clearSecaDetails\(token\);/g) || []).length, 4);
});

test("Pages exposes a downloadable and loadable synthetic SECA sample", () => {
  const parsed = parseSecaCsv(publicSample);
  assert.equal(parsed.measuredAt, "Jan 2, 2025, 8:00 AM");
  assert.equal(parsed.trendAvailable, true);
  assert.equal(parsed.latest.values.bmi, 25.8);
  assert.equal(Object.keys(parsed.latest.segments).length, 5);
  assert.match(pageSource, /id="seca-load-sample"/);
  assert.match(pageSource, /example-seca-tableview\.csv/);
  assert.match(siteSource, /fetch\("example-seca-tableview\.csv"/);
  assert.match(siteSource, /Synthetic sample:/);
});

test("Pages deploy gate regenerates the committed synthetic demo artifact", () => {
  assert.match(pagesWorkflow, /uv run python scripts\/build_demo_data\.py --check/);
});

test("Pages exposes a privacy-safe wellness improvement report", () => {
  assert.match(pageSource, /id="demo-download"/);
  assert.match(pageSource, /id="demo-print"/);
  assert.match(pageSource, /id="demo-copy-focus"/);
  assert.match(pageSource, /id="demo-report"/);
  assert.match(pageSource, /role="region" aria-labelledby="demo-report-heading"/);
  assert.match(pageSource, /Normalized age-equivalent difference/);
  assert.match(pageSource, /data-demo-deviation-uncertainty/);
  assert.match(pageSource, /Research-use-only — synthetic development output/);
  assert.match(pageSource, /Download development wellness report/);
  assert.match(pageSource, /Print development wellness report/);
  assert.match(siteSource, /downloadWellnessReport/);
  assert.match(siteSource, /setDemoReportStatus\("Showing " \+ example\.label \+ " development report\./);
  assert.match(siteSource, /printWellnessReport/);
  assert.match(siteSource, /wellness-improvement-report-v1/);
  assert.match(siteSource, /wellness-improvement-report-v1-development\.json/);
  assert.match(siteSource, /action_effect_estimated: false/);
  assert.match(siteSource, /clinical_or_lifespan_claim: false/);
  assert.match(siteSource, /No patient identifier, raw CSV, or uploaded data is included/);
  assert.match(siteSource, /copyWellnessFocus/);
  assert.match(siteSource, /wellness-focus-areas-v2/);
  assert.match(siteSource, /reference_panel_readiness/);
  const focusStart = siteSource.indexOf("var payload = {");
  const focusEnd = siteSource.indexOf("copyText(JSON.stringify(payload", focusStart);
  assert.ok(focusStart >= 0 && focusEnd > focusStart);
  const focusPayload = siteSource.slice(focusStart, focusEnd);
  assert.match(focusPayload, /action_effect_estimated: false/);
  assert.match(focusPayload, /clinical_or_lifespan_claim: false/);
  assert.match(focusPayload, /model_boundary:/);
  assert.match(focusPayload, /production_ready:/);
  assert.match(focusPayload, /reference_panel_fixture_only:/);
  assert.match(focusPayload, /privacy_note:/);
  const reportStart = siteSource.indexOf("var summary = {");
  const boundaryStart = siteSource.indexOf("model_boundary:", reportStart);
  assert.ok(reportStart >= 0 && boundaryStart > reportStart);
  const reportBeforeBoundary = siteSource.slice(reportStart, boundaryStart);
  assert.match(
    reportBeforeBoundary,
    /top_interventions: result\.top_interventions \|\| \[\],[\s\S]*wellness_report: report,[\s\S]*action_effect_estimated: false,[\s\S]*clinical_or_lifespan_claim: false,[\s\S]*progress_report:/,
  );
});

test("Pages status rows cover every EVAL criterion", () => {
  const evaluation = fs.readFileSync(
    path.join(__dirname, "..", "EVAL.md"),
    "utf8",
  );
  const evalIds = [
    ...evaluation.matchAll(/^\| (E-\d+) \|/gm),
  ].map((match) => match[1]);
  const statusIds = [
    ...siteSource.matchAll(/\{ id: "(E-\d+)", verdict:/g),
  ].map((match) => match[1]);
  assert.deepEqual(statusIds, evalIds);
  const evalStatuses = Object.fromEntries(
    [
      ...evaluation.matchAll(
        /^\| (E-\d+) \|.*\| (passing|blocked) \|$/gm,
      ),
    ].map((match) => [match[1], match[2]]),
  );
  const siteStatuses = Object.fromEntries(
    [
      ...siteSource.matchAll(
        /\{ id: "(E-\d+)", verdict:\s+"(passing|blocked)"/g,
      ),
    ].map((match) => [match[1], match[2]]),
  );
  assert.deepEqual(siteStatuses, evalStatuses);
});

test("Pages shows input completeness context beside the readout", () => {
  assert.match(pageSource, /data-demo-coverage/);
  assert.match(pageSource, /data-demo-measured/);
  assert.match(pageSource, /data-demo-missing/);
  assert.match(pageSource, /data-demo-focus-count/);
  assert.match(siteSource, /coverage\.measured_features/);
  assert.match(siteSource, /Missing values are not fabricated/);
});

test("Pages labels the panel state and the SECA preview as local-only", () => {
  assert.match(pageSource, /Local only/);
  assert.match(pageSource, /the selected file never leaves this browser/);
  assert.match(pageSource, /research-use-only — not for clinical use/);
  assert.match(pageSource, /synthetic — clinical_use: forbidden — cannot satisfy E-005/);
  assert.match(pageSource, /external_validation_validation_report\.json/);
  assert.match(pageSource, /data-demo-panel-boundary/);
  assert.match(siteSource, /Reference-panel state:/);
  assert.match(siteSource, /reference_panel_readiness/);
});

test("Pages shows the FI denominator label and panel identity context", () => {
  assert.match(pageSource, /data-demo-fi-strength/);
  assert.match(siteSource, /denominator_strength/);
  assert.match(siteSource, /engineering count label; not clinical adequacy/);
  assert.match(siteSource, /reference_panel_sha256/);
  assert.match(pageSource, /fi_denominator_strength/);
});

test("Pages focus list agrees with the API list and uses a bounded visible display", () => {
  // The static markup must declare the count statement and the disclosure
  // element that hosts the remaining focus items.
  assert.match(pageSource, /data-demo-focus-shown/);
  assert.match(pageSource, /data-demo-focus-extra/);
  assert.match(pageSource, /data-demo-focus-extra-list/);
  assert.match(pageSource, /All remaining measured focus areas/);
  // The renderer must slice to at most five bullets, surface the count
  // statement, and emit the remaining list only when overflow exists.
  assert.match(siteSource, /visibleLimit = 5/);
  assert.match(siteSource, /Showing.*of.*measured focus areas/);
  assert.match(siteSource, /No measured focus areas in this example/);
  assert.match(siteSource, /extraHost\.hidden = true/);
  assert.match(siteSource, /remainingAreas/);
  // The downloadable report and JSON handoff must carry every measured
  // non-in-range focus item from the API, not a UI-bounded subset.
  assert.match(siteSource, /wellness_report: report,/);
  assert.match(siteSource, /target_range_label/);
  assert.match(siteSource, /focus_areas: publicFocusAreas\(report\)/);
  assert.match(siteSource, /source: area\.source/);
  assert.match(siteSource, /uncertainty construction/);
  // Every demo example's API focus list matches the live assess pipeline.
  for (const example of demoData.examples) {
    assert.equal(example.result.metrics.biological_age.ci_95, null);
    assert.equal(
      example.result.metrics.biological_age.uncertainty_construction,
      "none_withheld",
    );
    assert.equal(example.result.trajectory.score_ci_95, null);
    assert.equal(example.result.trajectory.uncertainty_construction, "none_withheld");
    const summaryCount = example.result.wellness_report.summary.focus_areas;
    const focusList = example.result.wellness_report.focus_areas;
    assert.equal(summaryCount, focusList.length);
    const nonInRange = example.result.wellness_report.ranges
      .filter((item) => item.status !== "in_range")
      .map((item) => item.biomarker);
    assert.deepEqual(
      [...focusList.map((item) => item.focus)].sort(),
      [...nonInRange].sort(),
    );
    for (const focus of focusList) {
      const range = example.result.wellness_report.ranges.find(
        (item) => item.feature === focus.feature,
      );
      assert.ok(range, `focus feature ${focus.feature} has a source range`);
      assert.equal(focus.focus, range.biomarker);
      assert.equal(focus.current_value, range.current_value);
      assert.equal(focus.unit, range.unit);
      assert.equal(focus.target_range_label, range.target_range.label);
      assert.equal(focus.direction, range.direction);
      assert.equal(focus.action_type, range.action_type);
      assert.equal(focus.z_score, range.z_score);
      assert.equal(focus.source, range.source);
      assert.equal(focus.recommendation, range.recommendation);
    }
  }
  const bmiFocus = demoData.examples
    .find((example) => example.id === "support")
    .result.wellness_report.focus_areas.find((item) => item.feature === "bmi");
  assert.ok(bmiFocus);
  assert.equal(bmiFocus.target_range_label, "18.5–24.9");
  assert.equal(bmiFocus.unit, "kg/m²");
  assert.match(bmiFocus.source, /WHO BMI/);
});

test("Pages exposes a descriptive longitudinal progress comparison", () => {
  assert.match(pageSource, /data-demo-progress/);
  assert.match(pageSource, /data-demo-progress-changes/);
  assert.match(siteSource, /renderProgress/);
  assert.match(siteSource, /progress_report/);
  assert.match(siteSource, /publicProgressReport/);
  assert.match(siteSource, /delete safe\.patient_id/);
  assert.equal(demoData.examples.length, 3);
  for (const example of demoData.examples) {
    assert.equal(example.progress.report.format, "wellness-progress-report-v1");
    assert.equal(example.progress.report.action_effect_estimated, false);
    assert.equal(example.progress.report.clinical_or_lifespan_claim, false);
    assert.match(
      example.progress.report.summary.interpretation,
      /Descriptive change between two assessments/,
    );
  }
});

test("Pages renders a visible placeholder and disabled report actions when demo-data is missing", () => {
  // The initDemo function must inject a disabled placeholder option before
  // the fetch resolves, and the demo report buttons must start disabled.
  const initDemoMatch = siteSource.match(/function initDemo\(\)\s*\{[\s\S]*?\n  \}/);
  assert.ok(initDemoMatch, "initDemo() must be defined in site.js");
  const initDemoBody = initDemoMatch[0];
  assert.match(
    initDemoBody,
    /placeholder\.disabled = true/,
    "initDemo must disable the placeholder option so the select is never silent",
  );
  assert.match(
    initDemoBody,
    /Demo data unavailable/,
    "initDemo must surface a visible placeholder label",
  );
  assert.match(
    initDemoBody,
    /downloadButton\.disabled = true[\s\S]*?printButton\.disabled = true[\s\S]*?copyFocusButton\.disabled = true/,
    "initDemo must start every report action button disabled",
  );
  // On failure the catch handler must publish the failure to the flag,
  // the description, and the report status — and leave the placeholder.
  assert.match(
    initDemoBody,
    /data-demo-flag[\s\S]*?demo-description[\s\S]*?setDemoReportStatus\("Demo data is unavailable/,
    "the failure branch must surface the error in three visible places",
  );
});

test("Pages protects the synthetic sample and local FileReader from stale async results", () => {
  // Both the sample fetch and the local FileReader must use a monotonic
  // token so a late success cannot overwrite a newer error or selection.
  assert.match(
    siteSource,
    /var secaRequestToken = 0/,
    "secaRequestToken must be declared at module scope so setSecaStatus can see it",
  );
  assert.match(
    siteSource,
    /secaRequestToken \+= 1/,
    "the synthetic sample fetch must increment the request token before the fetch",
  );
  assert.match(
    siteSource,
    /input\.addEventListener\("change"[\s\S]*?secaRequestToken \+= 1/,
    "the local FileReader path must also increment the request token",
  );
  assert.match(
    siteSource,
    /if \(token !== secaRequestToken\) return;/,
    "consumeText must guard against stale callbacks",
  );
  assert.match(
    siteSource,
    /function setSecaStatus\(message, isError, token\)/,
    "setSecaStatus must accept a token so it can skip stale writes",
  );
  assert.match(
    siteSource,
    /function clearSecaDetails\(token\)/,
    "clearSecaDetails must accept a token so it can skip stale clears",
  );
  // The existing clear-on-error contract must still be preserved.
  assert.match(
    siteSource,
    /clearSecaDetails\(token\);[\s\S]*?setSecaStatus\("Could not parse this export/,
    "consumeText must still clear on parse error",
  );
});

test("Pages renders SECA segment values and trends as individually navigable list items", () => {
  // The dl contract is preserved: each pair still emits a <dt>/<dd>.
  assert.match(siteSource, /"<dt>" \+ escapeHtml\(pair\[0\]\)/);
  // The two segment-shaped entries use an inner <ul> with one <li> per
  // segment so each value is independently copyable and navigable.
  const segmentListMatches = siteSource.match(/<ul class="seca-segment-list">/g) || [];
  assert.ok(
    segmentListMatches.length >= 2,
    "both Segments and Segment trends must use a seca-segment-list",
  );
  assert.match(
    siteSource,
    /segmentLabels\.map\(function \(label\)[\s\S]*?<li>/,
    "each segment value must be a discrete list item",
  );
  assert.match(
    siteSource,
    /trendLabels\.map\(function \(label\)[\s\S]*?<li>/,
    "each segment trend must be a discrete list item",
  );
});

test("Pages replaces misleading acronym humanization with stable labels", () => {
  // Each target acronym must map to a stable expanded label.
  assert.match(siteSource, /"ecw_tbw": "ECW\/TBW \(extracellular water to total body water ratio\)"/);
  assert.ok(
    demoData.examples.some((example) =>
      example.result.wellness_report.ranges.some(
        (item) => item.biomarker === "ECW/TBW",
      ),
    ),
    "the generated Pages artifact must use the readable ECW/TBW label",
  );
  assert.match(siteSource, /"ffmi": "FFMI \(fat-free mass index\)"/);
  assert.match(siteSource, /"bmi": "BMI \(body mass index\)"/);
  assert.match(siteSource, /"bia": "BIA \(bioelectrical impedance analysis\)"/);
  // The safe fallback path is preserved for any unknown token.
  assert.match(
    siteSource,
    /function humanize\(value\)[\s\S]*?replace\(\/_\/g, " "\)/,
    "humanize must still fall back to the original underscore-and-capitalize behaviour",
  );
  // signedPercent must return a visible em dash for non-finite input.
  assert.match(
    siteSource,
    /function signedPercent\(value\)[\s\S]*?if \(!Number\.isFinite\(number\)\) return "—";/,
  );
});

test("Pages exposes a visible :focus-visible rule for copy buttons and a printable report reflow", () => {
  // The dynamically-injected copy button must have a dedicated focus-visible
  // rule that survives the existing :hover/focus-visible combined selector.
  const focusMatches = siteCss.match(/\.copy-btn:focus-visible\s*\{/g) || [];
  assert.ok(
    focusMatches.length >= 1,
    "site.css must contain a .copy-btn:focus-visible rule",
  );
  // @media print must relax the scroll wrapper and the readout/demo grid
  // so the report's tables are not clipped and the cards reflow.
  assert.match(siteCss, /\.table-scroll\s*\{\s*overflow:\s*visible/);
  assert.match(siteCss, /\.wellness-table,\s*\.progress-table,\s*\.feature-table\s*\{/);
  assert.match(siteCss, /\.readout-grid\s*\{[\s\S]*?grid-template-columns:\s*1fr/);
  assert.match(siteCss, /\.demo-grid\s*\{[\s\S]*?grid-template-columns:\s*1fr/);
  assert.match(siteCss, /\.print-only\s*\{\s*display:\s*block/);
  assert.match(siteCss, /\.report-print-banner/);
  // Reduced-motion handling must remain in place.
  assert.match(siteCss, /@media \(prefers-reduced-motion: reduce\)/);
});

test("Pages prefixes SECA and demo status messages with a sequence counter", () => {
  // setSecaStatus must use its own monotonic update counter rather than the
  // async request token, because one request can publish multiple updates.
  assert.match(siteSource, /var secaStatusSequence = 0/);
  assert.match(
    siteSource,
    /function setSecaStatus\(message, isError, token\)[\s\S]*?var sequence = \+\+secaStatusSequence;[\s\S]*?"\[seca " \+ sequence \+ "\] "/,
  );
  assert.match(
    siteSource,
    /status\.setAttribute\("aria-label", label \+ message\)/,
    "setSecaStatus must publish an aria-label so screen readers can distinguish updates",
  );
  // setDemoReportStatus must do the same on the demo report status node.
  assert.match(
    siteSource,
    /function setDemoReportStatus\(message, isError\)[\s\S]*?status\.dataset\.sequence/,
  );
  assert.match(
    siteSource,
    /function setDemoReportStatus\(message, isError\)[\s\S]*?"\[demo-report " \+ sequence \+ "\] "/,
  );
  // The downloadable synthetic sample link gets an accessible label
  // clarifying it is anonymized and not the user's file.
  assert.match(
    siteSource,
    /sampleDownloadLink[\s\S]*?not your file; software fixture, not patient data/,
  );
});
