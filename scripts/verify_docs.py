"""Check that the public evidence pages agree with the current checkout."""

from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any
from urllib.parse import urlparse

from attestation import verify_sidecar


def _load_test_receipt(root: Path) -> dict[str, Any]:
    path = root / "docs" / "test-receipt.json"
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing test receipt: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid test receipt JSON: {exc}") from exc
    if not isinstance(receipt, dict):
        raise ValueError("test receipt must be a JSON object")
    for key in ("python_tests_collected", "node_tests_collected"):
        value = receipt.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"test receipt field {key} must be a positive integer")
    return receipt


def _failures(root: Path, test_count: int, node_test_count: int) -> list[str]:
    html = (root / "docs" / "index.html").read_text(encoding="utf-8")
    evaluation = (root / "EVAL.md").read_text(encoding="utf-8")
    model_card = (root / "docs" / "MODEL_CARD.md").read_text(encoding="utf-8")
    model_approval = (root / "docs" / "MODEL_APPROVAL.md").read_text(encoding="utf-8")
    operations_path = root / "docs" / "OPERATIONS.md"
    operations = operations_path.read_text(encoding="utf-8")
    overlay_doc_path = root / "docs" / "ASSESSMENT_OVERLAY.md"
    overlay_doc = (
        overlay_doc_path.read_text(encoding="utf-8")
        if overlay_doc_path.is_file()
        else ""
    )
    nhanes_intake_doc_path = root / "docs" / "NHANES_INTAKE.md"
    nhanes_intake_doc = (
        nhanes_intake_doc_path.read_text(encoding="utf-8")
        if nhanes_intake_doc_path.is_file()
        else ""
    )
    threat_model_path = root / "docs" / "PRIVACY_THREAT_MODEL.md"
    threat_model = (
        threat_model_path.read_text(encoding="utf-8")
        if threat_model_path.is_file()
        else ""
    )
    security_path = root / "SECURITY.md"
    security = (
        security_path.read_text(encoding="utf-8") if security_path.is_file() else ""
    )
    readme = (root / "README.md").read_text(encoding="utf-8")
    contributing_path = root / "CONTRIBUTING.md"
    contributing = (
        contributing_path.read_text(encoding="utf-8")
        if contributing_path.is_file()
        else ""
    )
    protocol_path = root / "docs" / "EXTERNAL_VALIDATION_PROTOCOL.md"
    protocol = (
        protocol_path.read_text(encoding="utf-8") if protocol_path.is_file() else ""
    )
    crosswalk_path = root / "docs" / "CLINICAL_ML_EVIDENCE_CROSSWALK.md"
    crosswalk = (
        crosswalk_path.read_text(encoding="utf-8") if crosswalk_path.is_file() else ""
    )
    credibility_wiki_path = root / "docs" / "wiki" / "001-model-credibility.md"
    credibility_wiki = (
        credibility_wiki_path.read_text(encoding="utf-8")
        if credibility_wiki_path.is_file()
        else ""
    )
    wiki_entry_path = root / "docs" / "wiki" / "003-clinical-ml-evidence-standards.md"
    wiki_entry = (
        wiki_entry_path.read_text(encoding="utf-8") if wiki_entry_path.is_file() else ""
    )
    workflow = (root / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    pages_workflow = (root / ".github" / "workflows" / "pages.yml").read_text(
        encoding="utf-8"
    )
    ci_workflow = (root / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )
    site_js = (root / "docs" / "site.js").read_text(encoding="utf-8")
    seca_parser = (root / "docs" / "seca-parser.js").read_text(encoding="utf-8")
    intake_form = (root / "docs" / "intake-form.js").read_text(encoding="utf-8")
    mvv = (root / "src" / "frailty_engine" / "mvv.py").read_text(encoding="utf-8")
    seca = (root / "src" / "frailty_engine" / "seca.py").read_text(encoding="utf-8")
    cli = (root / "src" / "frailty_engine" / "__main__.py").read_text(encoding="utf-8")
    intake_overlay = (root / "src" / "frailty_engine" / "intake_overlay.py").read_text(
        encoding="utf-8"
    )
    api = (root / "src" / "frailty_engine" / "api.py").read_text(encoding="utf-8")
    pipeline = (root / "src" / "frailty_engine" / "pipeline.py").read_text(
        encoding="utf-8"
    )
    release_receipt = (
        root / "src" / "frailty_engine" / "release_receipt.py"
    ).read_text(encoding="utf-8")
    release_provenance = (
        root / "src" / "frailty_engine" / "release_provenance.py"
    ).read_text(encoding="utf-8")
    model_release = (root / "scripts" / "validate_model_release.py").read_text(
        encoding="utf-8"
    )
    serving_smoke = (root / "scripts" / "run_serving_contract_smoke.py").read_text(
        encoding="utf-8"
    )
    validation = (root / "src" / "frailty_engine" / "validation.py").read_text(
        encoding="utf-8"
    )
    project_verify_path = root / "scripts" / "verify_project.py"
    project_verify = (
        project_verify_path.read_text(encoding="utf-8")
        if project_verify_path.is_file()
        else ""
    )
    engine_tests = (root / "tests" / "test_engine.py").read_text(encoding="utf-8")
    training = (root / "src" / "frailty_engine" / "training.py").read_text(
        encoding="utf-8"
    )
    survey_design = (root / "src" / "frailty_engine" / "survey_design.py").read_text(
        encoding="utf-8"
    )
    nhanes = (root / "src" / "frailty_engine" / "nhanes.py").read_text(encoding="utf-8")
    progress = (root / "src" / "frailty_engine" / "progress.py").read_text(
        encoding="utf-8"
    )
    public_seca_sample_path = root / "docs" / "example-seca-tableview.csv"
    manifest_path = root / "docs" / "TRAINING_MANIFEST_TEMPLATE.json"
    demo_path = root / "docs" / "demo-data.json"
    receipt_path = root / "docs" / "test-receipt.json"
    external_fixture_path = root / "examples" / "external_validation_synthetic.json"
    external_report_path = (
        root / "examples" / "external_validation_validation_report.json"
    )
    overlay_fixture_path = root / "examples" / "assessment_overlay_synthetic.json"
    nhanes_intake_script_path = root / "scripts" / "review_nhanes_intake.py"
    nhanes_intake_script = (
        nhanes_intake_script_path.read_text(encoding="utf-8")
        if nhanes_intake_script_path.is_file()
        else ""
    )
    failures: list[str] = []
    expected_count = f"{test_count} / {test_count}"
    expected_node_count = f"{node_test_count} Node Pages/parser tests"
    if f"Tests: {expected_count} passing" not in html:
        failures.append("docs/index.html has a stale status-ribbon test count")
    if f'<dt>Tests</dt><dd class="ok">{expected_count} passing</dd>' not in html:
        failures.append("docs/index.html has a stale at-a-glance test count")
    if f">{test_count} passed<" not in html:
        failures.append("docs/index.html has a stale automated receipt")
    if f"`py -3 -m pytest`: {test_count} passed" not in evaluation:
        failures.append("EVAL.md has a stale pytest receipt")
    if (
        f"The current checkout collects {test_count} Python tests and "
        f"{node_test_count} Node Pages/parser tests." not in evaluation
    ):
        failures.append("EVAL.md has a stale Node test count")
    if f"{test_count}-test suite" not in model_card:
        failures.append("MODEL_CARD.md has a stale test count")
    if expected_node_count not in html:
        failures.append("docs/index.html has a stale Node test count")
    if f"{test_count}-test suite plus {expected_node_count}" not in model_card:
        failures.append("MODEL_CARD.md has a stale Node test count")
    if '<a href="test-receipt.json">test-receipt.json</a>' not in html:
        failures.append("Pages is missing the public test-receipt link")
    eval_ids = re.findall(r"(?m)^\| (E-\d+) \|", evaluation)
    status_ids = re.findall(r'\{ id: "(E-\d+)", verdict:', site_js)
    if eval_ids != status_ids:
        failures.append("site.js status rows drift from EVAL.md criterion IDs")
    if eval_ids:
        expected_asset_token = f"e{max(int(item[2:]) for item in eval_ids) + 1:03d}"
        for asset_name in ("seca-parser.js", "intake-form.js", "site.js"):
            if f'src="{asset_name}?v={expected_asset_token}"' not in html:
                failures.append(
                    f"Pages asset token for {asset_name} must be {expected_asset_token}"
                )
    eval_statuses = dict(
        re.findall(r"(?m)^\| (E-\d+) \|.*\| (passing|blocked) \|$", evaluation)
    )
    site_statuses = dict(
        re.findall(r'\{ id: "(E-\d+)", verdict:\s+"(passing|blocked)"', site_js)
    )
    if eval_statuses != site_statuses:
        failures.append("site.js status verdicts drift from EVAL.md")
    if not operations_path.is_file():
        failures.append("docs/OPERATIONS.md is missing")
    if not overlay_doc_path.is_file():
        failures.append("docs/ASSESSMENT_OVERLAY.md is missing")
    if not nhanes_intake_doc_path.is_file():
        failures.append("docs/NHANES_INTAKE.md is missing")
    if not nhanes_intake_script_path.is_file():
        failures.append("scripts/review_nhanes_intake.py is missing")
    if not threat_model_path.is_file():
        failures.append("docs/PRIVACY_THREAT_MODEL.md is missing")
    if not security_path.is_file():
        failures.append("SECURITY.md is missing")
    if not contributing_path.is_file():
        failures.append("CONTRIBUTING.md is missing")
    if not crosswalk_path.is_file():
        failures.append("clinical-ML evidence crosswalk is missing")
    if not project_verify_path.is_file():
        failures.append("scripts/verify_project.py is missing")
    if not wiki_entry_path.is_file():
        failures.append("clinical-ML evidence wiki entry is missing")
    for marker in (
        "actions/upload-pages-artifact@v4",
        "actions/configure-pages@v5",
        "actions/deploy-pages@v4",
        "needs: verify",
        "if: github.ref == 'refs/heads/main'",
        "pages: write",
        "id-token: write",
        "name: github-pages",
        "path: docs",
        "uv run python scripts/build_demo_data.py --check",
        "uv run python scripts/build_external_validation_fixture.py --output examples/external_validation_synthetic.json --check",
        "uv run python scripts/run_external_validation_report.py --check",
        "uv run python scripts/build_test_receipt.py --check",
        "node --check docs/intake-form.js",
        "node --test tests/site_parser.test.cjs",
    ):
        if marker not in pages_workflow:
            failures.append(f"pages workflow is missing guard: {marker}")
    for marker in (
        "test-windows:",
        "runs-on: windows-latest",
        "shell: pwsh",
        "uv build --wheel",
        "scripts/validate_training_manifest.py docs/TRAINING_MANIFEST_TEMPLATE.json",
        "scripts/build_test_receipt.py --check",
        "scripts/run_external_validation_report.py --check",
        "node --check docs/intake-form.js",
        "review_nhanes_intake.py --help",
        "run_serving_contract_smoke.py",
    ):
        if marker not in ci_workflow:
            failures.append(f"CI workflow is missing Windows release guard: {marker}")
    for marker in (
        "_run_software_gate_contract",
        "FRAILTY_MODEL_APPROVAL_PATH",
        "FRAILTY_REQUIRE_PRODUCTION",
        "loaded_production_ready",
        "production_software_gate",
        "TemporaryDirectory",
        '"clinical_use": "forbidden"',
    ):
        if marker not in serving_smoke:
            failures.append(
                f"serving contract smoke is missing strict-stage marker: {marker}"
            )
    for marker in (
        "build_checks",
        "--skip-serving",
        "--json",
        "Clinical gate: E-005 remains separate and blocked",
        "software verification",
    ):
        if marker not in project_verify:
            failures.append(f"project verifier is missing marker: {marker}")
    for marker in (
        "SubgroupSupportWarning",
        "subgroup_support_warnings",
        '"no_events"',
        '"no_comparable_pairs"',
        '"insufficient_valid_replicates"',
        "OutcomeMetricName",
        "outcome_metric_status",
        '"not_implemented_pending_sap"',
        '"none_withheld"',
        '"review_gate": "E-005"',
    ):
        if marker not in validation:
            failures.append(
                f"validation report is missing subgroup-support marker: {marker}"
            )
    if "uv export --locked --extra ml --no-dev" not in ci_workflow:
        failures.append("CI wheel smoke is missing the locked ML extra")
    eval_ids = re.findall(r"^\| (E-\d{3}) \|", evaluation, flags=re.MULTILINE)
    latest_eval_id = max(eval_ids, key=lambda value: int(value[2:])) if eval_ids else ""
    if latest_eval_id:
        for label, document in (
            ("clinical-ML crosswalk", crosswalk),
            ("model-credibility research entry", credibility_wiki),
        ):
            if latest_eval_id not in document:
                failures.append(
                    f"{label} is stale: it does not mention latest {latest_eval_id}"
                )
    if (
        "E-001 through E-004 and E-006 through E-064" in crosswalk
        or "E-001 through E-004 and E-006 through E-064" in credibility_wiki
    ):
        failures.append("research documentation contains stale E-064 ledger coverage")
    for marker in (
        "FRAILTY_REQUIRE_PRODUCTION=true",
        "GET /health",
        "GET /readyz",
        "rollback",
        "body-free structured request logs",
        "assessment_readiness",
        "readiness.blockers",
        "64 KiB",
        'strata=("sex", "age_band")',
        "PRIVACY_THREAT_MODEL.md",
        "Cache-Control: no-store",
        "X-Content-Type-Options: nosniff",
        "X-Frame-Options: DENY",
    ):
        if marker not in operations:
            failures.append(f"OPERATIONS.md is missing runbook marker: {marker}")
    for marker in (
        "predict_for_assessment(age, encoded_vector)",
        "clinical-use: forbidden",
        "Pages and receipts",
        "PRIVACY_THREAT_MODEL.md",
    ):
        if marker not in contributing:
            failures.append(f"CONTRIBUTING.md is missing contributor marker: {marker}")
    if 'name="viewport"' not in html or "data-status-rows" not in html:
        failures.append("Pages shell is missing required metadata or status hook")
    if "verification receipts in EVAL.md" not in html:
        failures.append("Pages shell is missing the live verification-receipt pointer")
    if 'href="PRIVACY_THREAT_MODEL.md"' not in html:
        failures.append("Pages source map is missing the privacy threat model")
    if (
        'href="https://github.com/stancsz/frailty-index-deficit-accumulation-model/blob/main/SECURITY.md"'
        not in html
    ):
        failures.append("Pages source map is missing the stable SECURITY.md link")
    for marker in (
        "# Privacy and Security Threat Model",
        "FileReader",
        "_RequestMetrics",
        "FRAILTY_API_KEY",
        "E-005",
        "compliance attestation",
        "No real patient",
        "[OPERATIONS.md](OPERATIONS.md)",
        "[GOAL.md](../GOAL.md)",
        "scripts/validate_model_release.py",
        "incident log or issue tracker",
    ):
        if marker not in threat_model:
            failures.append(f"privacy threat model is missing marker: {marker}")
    for marker in (
        "# Security Policy",
        "private vulnerability reporting",
        "patient data",
        "FRAILTY_REQUIRE_PRODUCTION=true",
        "PRIVACY_THREAT_MODEL.md",
        "OPERATIONS.md",
        "E-005",
        "Invalid or oversized supplied `X-Request-ID` values remain replaced",
        "No real patient export",
    ):
        if marker not in security:
            failures.append(f"SECURITY.md is missing marker: {marker}")
    if "Status / action" not in html:
        failures.append("Pages wellness table is missing action semantics")
    if (
        'href="MODEL_APPROVAL.md"' not in html
        or "reference_panel_sha256" not in model_approval
    ):
        failures.append(
            "Pages is missing the reference-panel approval-sidecar link/schema"
        )
    for marker in (
        "expected at least one non-empty dated column",
        "extra non-empty columns",
        'replace(/\\u2212/g, "-")',
        "Copy failed — select text manually",
        "var segmentLabels = Object.keys(scan.segments)",
        'id: "E-012"',
        'id: "E-013"',
        'id: "E-014"',
        'id: "E-015"',
        'id: "E-016"',
        'id: "E-017"',
        'id: "E-018"',
        'id: "E-019"',
        'id: "E-020"',
        'id: "E-021"',
        'id: "E-022"',
        'id: "E-023"',
        'id: "E-024"',
        'id: "E-025"',
        'id: "E-026"',
        'id: "E-027"',
        'id: "E-028"',
        'id: "E-030"',
        'id: "E-031"',
        'id: "E-032"',
        'id: "E-036"',
        'id: "E-037"',
        'id: "E-038"',
        'id: "E-039"',
        'id: "E-040"',
        'id: "E-041"',
        'id: "E-042"',
        'id: "E-043"',
        'id: "E-044"',
        'id: "E-045"',
        'id: "E-047"',
        'id: "E-048"',
        'id: "E-049"',
        'id: "E-050"',
        'id: "E-051"',
        'id: "E-052"',
        'id: "E-053"',
        'id: "E-054"',
        'id: "E-055"',
        'id: "E-056"',
        'id: "E-057"',
        'id: "E-058"',
        'id: "E-059"',
        'h1 class="brand"',
        "brand-sub",
        '<details class="status-reveal" open>',
        "isSecureContext === true",
        "<noscript>",
        "MAX_SECA_BYTES",
        "dated columns must contain parseable dates",
        "Single scan only — trend comparison requires two dated scans.",
        "Biological-age readout",
        "uncertainty not validated",
        "ci_95: null",
        'response.headers["Connection"] = "close"',
        "TRAINING_MANIFEST_TEMPLATE.json",
        "uv sync --locked",
        "verify_package_install.py",
        'id="seca-download"',
        'id="seca-load-sample"',
        "example-seca-tableview.csv",
        "Synthetic sample:",
        "downloadNormalizedSecaSummary",
        "seca-tableview-normalized-v1",
        "seca-normalized-summary.json",
        'id="demo-download"',
        'id="demo-print"',
        'id="demo-copy-focus"',
        'id="demo-report"',
        "downloadWellnessReport",
        "printWellnessReport",
        "assessmentReadiness",
        "assessment_readiness",
        "SECA-only preview is not assessment-ready",
        "wellness-improvement-report-v1",
        "wellness-improvement-report-v1-development.json",
        "wellness-focus-areas-v2",
        "copyWellnessFocus",
        "publicFocusAreas",
        "top_interventions: result.top_interventions || []",
        "Normalized age-equivalent difference",
        "data-demo-deviation-uncertainty",
        "report-print-banner",
        "target_range_label",
        'id: "E-060"',
        'id: "E-061"',
        "shipped development fixture bands",
        "is_development_fixture_content",
        "model_boundary",
        "data-demo-panel-boundary",
        "reference_panel_readiness",
        "Local-only preview",
        "OPERATIONS.md",
        "FRAILTY_REQUIRE_PRODUCTION=true",
        "body-free structured",
        "rollback",
        "pages.yml",
        "actions/deploy-pages@v4",
        "bootstrap_replicates",
        "concordance_ci_95",
        "concordance_ci_status",
        "concordance_ci_construction",
        "concordance_comparable_pairs",
        "rows_excluded",
        "row_exclusion_counts",
        "support-aware",
        "fixture_only",
        "reference_panel_fixture_only",
        "clinical-use-forbidden",
        "run_external_validation_smoke.py",
        "build_external_validation_fixture.py",
        "run_training_split_smoke.py",
        "split_survival_rows",
        "patient_id_sha256_event_stratified",
        "deployment_fingerprint",
        "model_artifact_sha256",
        "reference_panel_sha256",
        "capture_release_receipt.py",
        "health_to_receipt",
        "receipt_matches_health",
        "runtime_provenance",
        "package_tree_sha256",
        "package_installation_mode",
        "dependency_set_sha256",
        "configuration_sha256",
        "provenance_is_well_formed",
        "provenance_is_ready_for_strict_admission",
        "provenance_is_installed",
        "auth_required_for_v1",
        "source_field_set_sha256",
        "Runtime release receipt",
        "validate_model_release.py",
        "MODEL_VECTOR_SOURCE_FEATURE_NAMES",
        "ModelAdapterProtocol",
        "predictor must implement predict_for_assessment",
        "test_readiness_matrix_consistent_with_health_receipt",
        "healthspan-model-release-preflight",
        "clinical_status",
        "action_effect_estimated",
        "clinical_or_lifespan_claim",
        "Age-equivalent wellness estimate",
        "assessment-comparisons",
        "AssessmentComparisonRequest",
        "AssessmentComparisonResponse",
        "build_progress_report",
        "wellness-progress-report-v1",
        "data-demo-progress",
        "moved_into_reference_range",
        "comparison_basis",
        "same_model_and_reference_panel",
        "same reference_panel_sha256",
        "fi_denominator_strength",
        "denominator_strength_caveat",
        "data-demo-coverage",
        "data-demo-measured",
        "data-demo-missing",
        "data-demo-focus-count",
        "data-demo-fi-strength",
        "Missing values are not fabricated",
        "segmental_trend_latest_minus_previous",
        "unmappedLabels",
        "unmapped_labels",
        "Segment trends (latest",
        "descriptive equipment trends",
        "ready health response must include model and reference-panel SHA-256 identities",
        "health response cannot mark a reference panel both production-ready and fixture-only",
        "ready health response must not contain readiness blockers",
        "inconsistent reference-panel fixture-only state",
        "duration_unit must be 'years' when mortality_records are supplied",
        "already normalized to years",
        "EXTERNAL_VALIDATION_PROTOCOL.md",
        "7.2.1 Prespecified minimum support fields",
        "RECORD_AFTER_STATISTICAL_REVIEW",
        "7.4.1 Outcome-level performance metrics",
        "calibration-in-the-large",
        "net-benefit",
        "CLINICAL_ML_EVIDENCE_CROSSWALK.md",
        "Framework coverage is selective",
        "TRIPOD+AI",
        "PROBAST+AI",
        "E-005 remains blocked",
        "clinical-ml-evidence-standards",
        "coverage_for",
        "clinical-healthspan-metrics-v1",
        "request_size_rejections",
        "Bounded runtime metrics",
        "reference_panel_band_span_years_for_age",
        "age outside reference-panel band coverage",
        "explicit supplied Gompertz mapper provenance",
        "mapper_source",
        "assessment_payload_overlay",
        "evaluate_mvv",
        "assess-overlay",
        "load_overlay",
        "merge_with_seca",
        "require_overlay_mvv",
        "--patient-id",
        "MAX_PATIENT_ID_LENGTH",
        "SECA input validation failed",
        'id="intake-patient-id"',
        'id="intake-preview"',
        "previewOverlay",
        "Confirm and download overlay",
        "ASSESSMENT_OVERLAY.md",
        "Exit code",
        "must match the observed latest SECA value",
        "FrailtyIntakeForm",
        'id="seca-intake"',
        'id="intake-fields"',
        'id="intake-mvv"',
        'id="intake-download"',
        "frailty-engine-assessment-overlay-v1",
        "frailty-assessment-overlay.json",
        "No scan or measurement data was uploaded",
        "review_nhanes_intake.py",
        "nhanes-intake-review-v1",
        "NHANES_INTAKE.md",
        "--column-map",
        "--cycle",
        "duration_unit",
        "--check",
        "no header row assumed",
        "not a downloader",
        "reviewer_obligations",
        "class SurveyDesign",
        "weight_kind",
        "weighting_applied",
        "design_reviewed",
        "survey_design",
        "raw sample_weight values require",
        "missing an explicit survey_design declaration",
        "complex-survey variance estimation",
    ):
        if marker not in (
            site_js
            + seca_parser
            + intake_form
            + mvv
            + seca
            + cli
            + intake_overlay
            + html
            + api
            + pipeline
            + release_receipt
            + release_provenance
            + model_release
            + validation
            + engine_tests
            + training
            + survey_design
            + nhanes
            + progress
            + operations
            + readme
            + workflow
            + pages_workflow
            + ci_workflow
            + protocol
            + crosswalk
            + wiki_entry
            + overlay_doc
            + nhanes_intake_doc
            + nhanes_intake_script
        ):
            failures.append(f"public parser/serving surface is missing guard: {marker}")
    if not protocol_path.is_file():
        failures.append("external-validation protocol template is missing")
    else:
        for marker in (
            "TEMPLATE — not an approved protocol",
            "## 3. Data-source identity",
            "## 4. Cohort eligibility, index date, endpoint, censoring, and horizon",
            "## 5. Patient-level leakage checks",
            "## 6. Feature contract and missingness rules",
            "## 7. Reporting obligations",
            "## 8. Reproducibility artifact checklist",
            "## 10. Reviewer, sign-off, and stop / rollback conditions",
            "## 12. What this template does **not** prove",
            "satisfy `E-005`",
            "subgroup_support_warnings",
            "no_comparable_pairs",
            "insufficient_valid_replicates",
            "outcome_metric_status",
            "not_implemented_pending_sap",
            "none_withheld",
            'review_gate: "E-005"',
        ):
            if marker not in protocol:
                failures.append(
                    f"external-validation protocol is missing marker: {marker}"
                )
    if not (root / "uv.lock").is_file():
        failures.append("uv.lock is missing from the reproducible project surface")
    if (root / "docs" / ".nojekyll").exists() is False:
        failures.append("docs/.nojekyll is missing")
    if not public_seca_sample_path.is_file():
        failures.append("docs/example-seca-tableview.csv is missing")
    else:
        public_seca_sample = public_seca_sample_path.read_text(encoding="utf-8")
        if not public_seca_sample.startswith('"Value","Unit",'):
            failures.append("public synthetic SECA sample has an invalid header")
        if "Micheal" in public_seca_sample or "Lau" in public_seca_sample:
            failures.append(
                "public synthetic SECA sample contains patient-specific text"
            )
    if not overlay_fixture_path.is_file():
        failures.append("synthetic assessment overlay fixture is missing")
    else:
        try:
            overlay_fixture = json.loads(
                overlay_fixture_path.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"synthetic assessment overlay fixture is invalid: {exc}")
        else:
            if overlay_fixture.get("format") != "frailty-engine-assessment-overlay-v1":
                failures.append("synthetic assessment overlay has the wrong format")
            if overlay_fixture.get("patient_id") != "demo-overlay":
                failures.append("synthetic assessment overlay has an unsafe identifier")
            if "Micheal" in overlay_fixture_path.read_text(encoding="utf-8"):
                failures.append(
                    "synthetic assessment overlay contains patient-specific text"
                )
    if re.search(r'href=["\']\.\./', html):
        failures.append("Pages contains a parent-relative link that breaks at /docs")
    for raw_target in re.findall(r'(?i)(?:href|src)=["\']([^"\']+)["\']', html):
        if raw_target.startswith(("#", "http:", "https:", "mailto:", "javascript:")):
            continue
        relative_target = urlparse(raw_target).path
        target = (root / "docs" / relative_target).resolve()
        try:
            target.relative_to((root / "docs").resolve())
        except ValueError:
            failures.append(f"Pages asset escapes docs/: {raw_target}")
            continue
        if not target.is_file():
            failures.append(f"Pages local asset is missing: {raw_target}")

    if not external_fixture_path.is_file():
        failures.append("synthetic external-validation fixture is missing")
    else:
        try:
            external_fixture = json.loads(
                external_fixture_path.read_text(encoding="utf-8")
            )
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            failures.append(
                f"synthetic external-validation fixture is invalid: {error}"
            )
        else:
            provenance = external_fixture.get("provenance", {})
            if external_fixture.get("fixture_type") != "synthetic_external_validation":
                failures.append("synthetic external-validation fixture type is invalid")
            if (
                provenance.get("kind") != "synthetic"
                or provenance.get("clinical_use") != "forbidden"
                or provenance.get("row_count") != len(external_fixture.get("rows", []))
            ):
                failures.append(
                    "synthetic external-validation fixture provenance is invalid"
                )
            if not (root / "scripts" / "run_external_validation_smoke.py").is_file():
                failures.append("synthetic external-validation smoke runner is missing")

    for target in (
        demo_path,
        external_fixture_path,
        receipt_path,
        external_report_path,
    ):
        ok, message = verify_sidecar(target, root=root)
        if not ok:
            failures.append(message)
    if not (root / "scripts" / "run_external_validation_report.py").is_file():
        failures.append("synthetic external-validation report writer is missing")
    elif external_report_path.is_file():
        try:
            external_report = json.loads(
                external_report_path.read_text(encoding="utf-8")
            )
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            failures.append(f"synthetic external-validation report is invalid: {error}")
        else:
            if external_report.get("clinical_status") != (
                "requires_e005_external_validation_and_clinical_review"
            ):
                failures.append(
                    "synthetic external-validation report has unsafe clinical status"
                )
            report_provenance = external_report.get("fixture_provenance", {})
            if (
                report_provenance.get("kind") != "synthetic"
                or report_provenance.get("clinical_use") != "forbidden"
                or not re.fullmatch(
                    r"[0-9a-f]{64}", str(report_provenance.get("fixture_sha256", ""))
                )
            ):
                failures.append(
                    "synthetic external-validation report provenance is invalid"
                )

    if (
        "research-use-only" not in html.lower()
        or "not for clinical use" not in html.lower()
    ):
        failures.append("Pages is missing explicit research-use-only boundary copy")
    if "does not satisfy E-005" not in cli:
        failures.append("CLI is missing explicit E-005 boundary copy")
    if "does not satisfy" not in readme or "E-005" not in readme:
        failures.append("README is missing explicit E-005 boundary copy")
    if (
        "cannot satisfy E-005" not in html
        or "external_validation_validation_report.json" not in html
    ):
        failures.append("Pages is missing the synthetic report boundary link copy")

    if not (root / "scripts" / "verify_package_install.py").is_file():
        failures.append("installed-wheel smoke runner is missing")

    manifest_check = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "validate_training_manifest.py"),
            str(manifest_path),
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if manifest_check.returncode:
        failures.append(
            "training-manifest template failed validation: "
            + (manifest_check.stderr.strip() or manifest_check.stdout.strip())
        )

    demo = json.loads((root / "docs" / "demo-data.json").read_text(encoding="utf-8"))
    if not str(demo.get("privacy_note", "")).startswith("Synthetic"):
        failures.append("demo-data.json is missing its synthetic privacy note")
    if any(
        not str(example.get("payload", {}).get("patient_id", "")).startswith("demo-")
        for example in demo.get("examples", [])
    ):
        failures.append("demo-data.json contains a non-demo patient identifier")
    if any(
        item.get("action_type") not in {"lifestyle", "review"}
        for example in demo.get("examples", [])
        for item in example.get("result", {})
        .get("wellness_report", {})
        .get("ranges", [])
    ):
        failures.append("demo-data.json contains an invalid wellness action type")
    for example in demo.get("examples", []):
        progress_report = example.get("progress", {}).get("report", {})
        if progress_report.get("format") != "wellness-progress-report-v1":
            failures.append("demo-data.json is missing a typed progress report")
        if (
            progress_report.get("action_effect_estimated") is not False
            or progress_report.get("clinical_or_lifespan_claim") is not False
        ):
            failures.append("demo-data.json progress report has unsafe claim flags")
        if "measurements" in progress_report:
            failures.append(
                "demo-data.json progress report echoes the raw input payload"
            )

    forbidden_tokens = (
        "Mi" + "cheal",
        "L" + "au",
        "TableView_" + "2026-06-05",
    )
    for relative in ("docs", "examples", "scripts", "src", "tests"):
        for path in (root / relative).rglob("*"):
            if (
                not path.is_file()
                or path.name == "verify_docs.py"
                or path.suffix == ".pyc"
            ):
                continue
            text = path.read_text(encoding="utf-8")
            if any(token.lower() in text.lower() for token in forbidden_tokens):
                failures.append(f"patient-specific export text found in {path}")
    return failures


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        test_receipt = _load_test_receipt(root)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    test_count = test_receipt["python_tests_collected"]
    node_test_count = test_receipt["node_tests_collected"]
    failures = _failures(root, test_count, node_test_count)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    print(
        "docs verification passed: "
        f"{test_count} Python + {node_test_count} Node tests in receipt"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
