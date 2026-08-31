/* Clinical Healthspan Engine — site.js
   Progressive enhancement. No frameworks, no CDN, no analytics.
   Six small, accessible features:
     1. Evidence-section filter (chip toggles, multi-select, no-JS fallback).
     2. Copy-to-clipboard on every <pre data-copyable> block.
   3. Populated status table from EVAL.md criteria + a print-friendly verdict.
   4. Static example assessments with a privacy-safe progress report.
   5. Local-only SECA TableView parsing and normalized downloads.
   6. A copyable, privacy-safe focus-list handoff. */

(function () {
  "use strict";

  // ---------------------------------------------------------------
  // 1) Evidence filter — chips that hide <li> items with data-tags.
  //    No filter active = show everything.
  // ---------------------------------------------------------------
  function initEvidenceFilter() {
    var bar = document.querySelector("[data-filter-bar]");
    if (!bar) return;
    var targetSel = bar.getAttribute("data-target");
    var list = document.querySelector(targetSel);
    if (!list) return;
    var items = list.querySelectorAll("[data-tags]");
    var countEl = bar.querySelector("[data-filter-count]");

    function applyFilter(active) {
      var visible = 0;
      items.forEach(function (li) {
        var tags = (li.getAttribute("data-tags") || "").split(/\s+/);
        var show = active.size === 0 || tags.some(function (t) { return active.has(t); });
        if (show) {
          li.removeAttribute("hidden");
          visible++;
        } else {
          li.setAttribute("hidden", "");
        }
      });
      if (countEl) {
        countEl.textContent = visible + " of " + items.length + " shown";
      }
    }

    var active = new Set();
    var chips = bar.querySelectorAll(".filter-chip");
    chips.forEach(function (chip) {
      var tag = chip.getAttribute("data-tag");
      chip.setAttribute("aria-pressed", "false");
      chip.addEventListener("click", function () {
        var pressed = chip.getAttribute("aria-pressed") === "true";
        if (pressed) {
          chip.setAttribute("aria-pressed", "false");
          active.delete(tag);
        } else {
          chip.setAttribute("aria-pressed", "true");
          active.add(tag);
        }
        applyFilter(active);
      });
    });

    applyFilter(active);
  }

  // ---------------------------------------------------------------
  // 2) Copy-to-clipboard for <pre data-copyable> blocks.
  //    Falls back to a textarea+execCommand for very old browsers.
  // ---------------------------------------------------------------
  function initCopyButtons() {
    var blocks = document.querySelectorAll("pre[data-copyable]");
    blocks.forEach(function (pre) {
      // Inject the host once if the markup omitted it.
      var host = pre.querySelector(".copy-host");
      if (!host) {
        host = document.createElement("div");
        host.className = "copy-host";
        pre.appendChild(host);
      }
      var btn = host.querySelector(".copy-btn");
      if (!btn) {
        btn = document.createElement("button");
        btn.type = "button";
        btn.className = "copy-btn";
        btn.textContent = "Copy";
        btn.setAttribute("aria-label", "Copy code to clipboard");
        host.appendChild(btn);
      }
      btn.addEventListener("click", function () {
        var copy = pre.cloneNode(true);
        var copyHost = copy.querySelector(".copy-host");
        if (copyHost) copyHost.remove();
        var text = copy.textContent.trimEnd();
        var done = function (ok) {
          btn.setAttribute("data-copied", ok ? "true" : "false");
          btn.textContent = ok ? "Copied" : "Copy failed — select text manually";
          setTimeout(function () {
            btn.removeAttribute("data-copied");
            btn.textContent = "Copy";
          }, 1800);
        };
        if (navigator.clipboard && window.isSecureContext === true) {
          navigator.clipboard.writeText(text).then(function () { done(true); })
            .catch(function () { fallbackCopy(text, done); });
        } else {
          fallbackCopy(text, done);
        }
      });
    });
  }

  function fallbackCopy(text, cb) {
    try {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "absolute";
      ta.style.left = "-9999px";
      document.body.appendChild(ta);
      ta.select();
      var copied = document.execCommand("copy");
      document.body.removeChild(ta);
      cb(copied);
    } catch (e) {
      cb(false);
    }
  }

  // ---------------------------------------------------------------
  // 3) Status table — sourced from EVAL.md (E-001..E-083). Kept in
  //    the JS so the table reflects the source of truth exactly.
  // ---------------------------------------------------------------
  var STATUS_ROWS = [
    { id: "E-001", verdict: "passing",  area: "35-variable canonical matrix" },
    { id: "E-002", verdict: "passing",  area: "MVV rejection branches (API + tests)" },
    { id: "E-003", verdict: "passing",  area: "FI scoring + denominator caveat" },
    { id: "E-004", verdict: "passing",  area: "BIA calibration + CLI/API smoke" },
    { id: "E-005", verdict: "blocked",   area: "External cohort + clinical cutoff approval" },
    { id: "E-006", verdict: "passing",  area: "Calibration + subgroup harness + plots" },
    { id: "E-007", verdict: "passing",  area: "Public NHANES XPT + mortality ingestion" },
    { id: "E-008", verdict: "passing",  area: "GitHub Pages docs + browser/link review" },
    { id: "E-009", verdict: "passing",  area: "Operational skill-compatibility + serving gates" },
    { id: "E-010", verdict: "passing",  area: "SECA import + demo + wellness report" },
    { id: "E-011", verdict: "passing",  area: "Training missingness + artifact approval invariants" },
    { id: "E-012", verdict: "passing",  area: "Training quality and missingness evidence report" },
    { id: "E-013", verdict: "passing",  area: "Censoring-aware calibration + approval reset" },
    { id: "E-014", verdict: "passing",  area: "Pages parser/accessibility + API boundary hardening" },
    { id: "E-015", verdict: "passing",  area: "SECA parser parity + derivation provenance" },
    { id: "E-016", verdict: "passing",  area: "Training recipe metadata + CI ML gate" },
    { id: "E-017", verdict: "passing",  area: "Wellness direction + numeric range clarity" },
    { id: "E-018", verdict: "passing",  area: "Frozen training-manifest reproducibility shape" },
    { id: "E-019", verdict: "passing",  area: "Locked package + installed-wheel smoke path" },
    { id: "E-020", verdict: "passing",  area: "Privacy-safe normalized SECA handoff" },
    { id: "E-021", verdict: "passing",  area: "Downloadable wellness improvement report" },
    { id: "E-022", verdict: "passing",  area: "Explicit SECA assessment-readiness checklist" },
    { id: "E-023", verdict: "passing",  area: "Operations, monitoring, rollback, and privacy runbook" },
    { id: "E-024", verdict: "passing",  area: "External subgroup event/censoring support denominators" },
    { id: "E-025", verdict: "passing",  area: "Guarded static GitHub Pages publication workflow" },
    { id: "E-026", verdict: "passing",  area: "Support-aware bootstrap concordance uncertainty" },
    { id: "E-027", verdict: "passing",  area: "Reproducible synthetic validation smoke + fixture-only readiness" },
    { id: "E-028", verdict: "passing",  area: "Deterministic patient-level training split" },
    { id: "E-029", verdict: "passing",  area: "Safe runtime release identity and deployment fingerprint" },
    { id: "E-030", verdict: "passing",  area: "Allow-listed runtime release receipt capture and reconciliation" },
    { id: "E-031", verdict: "passing",  area: "Model/panel/approval release preflight and uncertainty lock" },
    { id: "E-032", verdict: "passing",  area: "Typed no-action-effect and no-clinical-claim boundary" },
    { id: "E-033", verdict: "passing",  area: "Stateless longitudinal wellness progress comparison" },
    { id: "E-034", verdict: "passing",  area: "Downloadable/loadable synthetic SECA sample" },
    { id: "E-035", verdict: "passing",  area: "Visible input completeness context" },
    { id: "E-036", verdict: "passing",  area: "Descriptive SECA segment trends" },
    { id: "E-037", verdict: "passing",  area: "Typed fixture-only assessment state" },
    { id: "E-038", verdict: "passing",  area: "Deterministic Pages demo artifact deploy gate" },
    { id: "E-039", verdict: "passing",  area: "Strict reference-panel approval flag parsing" },
    { id: "E-040", verdict: "passing",  area: "SECA preview error-state clearing" },
    { id: "E-041", verdict: "passing",  area: "SECA unmapped-row parser parity" },
    { id: "E-042", verdict: "passing",  area: "Hash-bound runtime readiness identity" },
    { id: "E-043", verdict: "passing",  area: "Single-source model-vector order" },
    { id: "E-044", verdict: "passing",  area: "Semantic release-receipt readiness invariants" },
    { id: "E-045", verdict: "passing",  area: "NHANES linked-duration unit boundary" },
    { id: "E-046", verdict: "passing",  area: "Pages handoff flags + EVAL status parity" },
    { id: "E-047", verdict: "passing",  area: "Complete wellness focus list + transparent Pages display" },
    { id: "E-048", verdict: "passing",  area: "External-validation and clinical-review protocol template" },
    { id: "E-049", verdict: "passing",  area: "Nullable uncertainty, nested receipt schema, and validation identity" },
    { id: "E-050", verdict: "passing",  area: "Reviewable validation exclusions and uncertainty status" },
    { id: "E-051", verdict: "passing",  area: "FI denominator label and panel digest binding" },
    { id: "E-052", verdict: "passing",  area: "Explicit predictor adapter contract and readiness matrix" },
    { id: "E-053", verdict: "passing",  area: "Readiness diagnostics and cohort-boundary support" },
    { id: "E-054", verdict: "passing",  area: "Explicit panel readiness and stable fixture identity" },
    { id: "E-055", verdict: "passing",  area: "Failure-safe accessible Pages and local SECA handoff" },
    { id: "E-056", verdict: "passing",  area: "Typed privacy-safe predictor failure envelope" },
    { id: "E-057", verdict: "passing",  area: "External-validation support and outcome metric obligations" },
    { id: "E-058", verdict: "passing",  area: "Windows-first CI and installed-wheel verification" },
    { id: "E-059", verdict: "passing",  area: "Clinical-ML credibility research crosswalk" },
    { id: "E-060", verdict: "passing",  area: "Typed Pages wellness focus-list handoff boundary" },
    { id: "E-061", verdict: "passing",  area: "Synthetic reference-panel promotion guard" },
    { id: "E-062", verdict: "passing",  area: "All-feature panel age-band coverage boundary" },
    { id: "E-063", verdict: "passing",  area: "Explicit supplied mapper provenance gate" },
    { id: "E-064", verdict: "passing",  area: "Explicit uncertainty construction labels" },
    { id: "E-065", verdict: "passing",  area: "Deterministic Python/Node test receipt" },
    { id: "E-066", verdict: "passing",  area: "Bounded privacy-safe runtime metrics" },
    { id: "E-067", verdict: "passing",  area: "Intervention and wellness-range context parity" },
    { id: "E-068", verdict: "passing",  area: "Local SECA assessment handoff and MVV overlay" },
    { id: "E-069", verdict: "passing",  area: "Versioned SECA handoff, preview, and typed CLI errors" },
    { id: "E-070", verdict: "passing",  area: "Privacy-safe local NHANES intake-shape receipt" },
    { id: "E-071", verdict: "passing",  area: "Typed survey-design and weight semantics" },
    { id: "E-072", verdict: "passing", area: "Selected next maturity tranche" },
    { id: "E-073", verdict: "passing", area: "Artifact attestations and E-005 boundary receipt" },
    { id: "E-074", verdict: "passing", area: "API response boundary and production maturity" },
    { id: "E-075", verdict: "passing", area: "Loopback HTTP serving contract" },
    { id: "E-076", verdict: "passing", area: "Runtime-process provenance and installed-build identity" },
    { id: "E-077", verdict: "passing", area: "Pages deploy guard and provenance admission semantics" },
    { id: "E-078", verdict: "passing", area: "Truthful Pages readout and complete wellness handoff" },
    { id: "E-079", verdict: "passing", area: "Real HTTP strict serving software gate" },
    { id: "E-080", verdict: "passing", area: "Independent next-tranche selection" },
    { id: "E-081", verdict: "passing", area: "External-validation subgroup support warnings" },
    { id: "E-082", verdict: "passing", area: "Typed withholding for future outcome metrics" },
    { id: "E-083", verdict: "passing", area: "Canonical software verification gate" },
  ];

  function initStatusTable() {
    var tbody = document.querySelector("[data-status-rows]");
    if (!tbody) return;
    var rows = "";
    STATUS_ROWS.forEach(function (r) {
      var v = r.verdict;
      var label = v.charAt(0).toUpperCase() + v.slice(1);
      rows += '<tr><td><code>' + r.id + '</code></td>'
            + '<td>' + escapeHtml(r.area) + '</td>'
            + '<td><span class="verdict ' + v + '">' + label + '</span></td></tr>';
    });
    tbody.innerHTML = rows;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c];
    });
  }

  // ---------------------------------------------------------------
  // 4) Static example assessments. The JSON is generated from the Python
  // pipeline, so this page never re-implements the scoring algorithm.
  // ---------------------------------------------------------------
  var selectedDemoExample = null;

  function initDemo() {
    var select = document.querySelector("#demo-select");
    if (!select) return;
    var downloadButton = document.querySelector("#demo-download");
    var printButton = document.querySelector("#demo-print");
    var copyFocusButton = document.querySelector("#demo-copy-focus");
    if (downloadButton) downloadButton.disabled = true;
    if (printButton) printButton.disabled = true;
    if (copyFocusButton) copyFocusButton.disabled = true;
    if (downloadButton) {
      downloadButton.addEventListener("click", function () {
        if (selectedDemoExample) downloadWellnessReport(selectedDemoExample);
      });
    }
    if (printButton) {
      printButton.addEventListener("click", function () {
        if (!selectedDemoExample) return;
        printWellnessReport();
      });
    }
    if (copyFocusButton) {
      copyFocusButton.addEventListener("click", function () {
        if (selectedDemoExample) copyWellnessFocus(selectedDemoExample);
      });
    }
    var placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "Demo data unavailable";
    placeholder.disabled = true;
    placeholder.selected = true;
    select.appendChild(placeholder);
    fetch("demo-data.json", { cache: "no-store" })
      .then(function (response) {
        if (!response.ok) throw new Error("demo-data.json returned " + response.status);
        return response.json();
      })
      .then(function (data) {
        var examples = data.examples || [];
        if (!examples.length) throw new Error("demo-data.json did not contain any examples");
        // Remove the placeholder before populating real options.
        while (select.firstChild) select.removeChild(select.firstChild);
        examples.forEach(function (example, index) {
          var option = document.createElement("option");
          option.value = String(index);
          option.textContent = example.label;
          select.appendChild(option);
        });
        select.addEventListener("change", function () {
          renderDemo(examples[Number(select.value)]);
        });
        select.value = "0";
        renderDemo(examples[0]);
      })
      .catch(function (error) {
        var flag = document.querySelector("[data-demo-flag]");
        if (flag) flag.textContent = "Demo data could not be loaded: " + error.message;
        var description = document.querySelector("#demo-description");
        if (description) {
          description.textContent = "Demo data could not be loaded: " + error.message
            + " The wellness report controls are disabled until the static JSON asset is restored.";
        }
        setDemoReportStatus("Demo data is unavailable — " + error.message, true);
      });
  }

  function renderDemo(example) {
    if (!example || !example.result) return;
    selectedDemoExample = example;
    var downloadButton = document.querySelector("#demo-download");
    var printButton = document.querySelector("#demo-print");
    var copyFocusButton = document.querySelector("#demo-copy-focus");
    if (downloadButton) downloadButton.disabled = false;
    if (printButton) printButton.disabled = false;
    if (copyFocusButton) copyFocusButton.disabled = false;
    var result = example.result;
    var metrics = result.metrics;
    var report = result.wellness_report;
    var panelReadiness = result.data_quality.reference_panel_readiness || "unknown";
    var age = metrics.biological_age;
    var ageEl = document.querySelector("[data-demo-biological-age]");
    var fiEl = document.querySelector("[data-demo-fi]");
    var fiDetail = document.querySelector("[data-demo-fi-detail]");
    var fiStrength = document.querySelector("[data-demo-fi-strength]");
    var deviationEl = document.querySelector("[data-demo-deviation]");
    var description = document.querySelector("#demo-description");
    if (ageEl) ageEl.textContent = Number(age.point_estimate).toFixed(1) + " years";
    var boundary = document.querySelector("[data-demo-boundary]");
    if (boundary) {
      boundary.textContent = (report.action_effect_estimated ? "Action effects estimated" : "Action effects are not estimated")
        + " · " + (report.clinical_or_lifespan_claim ? "clinical/lifespan claim present" : "no clinical or lifespan claim");
    }
    if (fiEl) fiEl.textContent = Number(metrics.current_deficit_load_fi).toFixed(3);
    if (fiDetail) fiDetail.textContent = metrics.current_deficit_load_fi_details.denominator + " valid FI variables";
    if (fiStrength) fiStrength.textContent = "Denominator band: "
      + humanize(metrics.current_deficit_load_fi_details.denominator_strength || "low")
      + " (engineering count label; not clinical adequacy)";
    if (deviationEl) deviationEl.textContent = signedPercent(result.trajectory.homeostatic_deviation_score);
    var deviationUncertainty = document.querySelector("[data-demo-deviation-uncertainty]");
    if (deviationUncertainty) {
      deviationUncertainty.textContent = Array.isArray(result.trajectory.score_ci_95)
        ? "Validated interval available: " + result.trajectory.score_ci_95.map(signedPercent).join(" to ")
        : "Uncertainty withheld; no validated interval ("
          + humanize(result.trajectory.uncertainty_construction || "none_withheld") + ")";
    }
    if (description) description.textContent = example.description;

    var flag = document.querySelector("[data-demo-flag]");
     if (flag) {
       flag.textContent = "Synthetic profile · " + result.model_metadata.model_id
         + " · panel: " + result.data_quality.reference_panel_id
        + " · panel state: " + humanize(panelReadiness)
        + " · panel digest: " + (result.data_quality.reference_panel_sha256
          || (result.data_quality.reference_panel_fixture_only ? "none (development fixture)" : "none"))
         + " · production-ready: " + String(result.model_metadata.production_ready)
         + " · fixture-only: " + String(result.data_quality.reference_panel_fixture_only)
         + " · uncertainty construction: "
         + humanize(age.uncertainty_construction || "none_withheld");
     }
    var panelBoundary = document.querySelector("[data-demo-panel-boundary]");
    if (panelBoundary) {
      panelBoundary.textContent = "Reference-panel state: " + humanize(panelReadiness)
        + ". The built-in panel is a software fixture; this readout is not ready for clinical use.";
    }
    var coverage = report.summary || {};
    var measuredEl = document.querySelector("[data-demo-measured]");
    var missingEl = document.querySelector("[data-demo-missing]");
    var focusCountEl = document.querySelector("[data-demo-focus-count]");
    var missingListEl = document.querySelector("[data-demo-missing-list]");
    if (measuredEl) measuredEl.textContent = String(coverage.measured_features ?? 0);
    if (missingEl) missingEl.textContent = String(coverage.missing_features ?? 0);
    if (focusCountEl) focusCountEl.textContent = String(coverage.focus_areas ?? 0);
    if (missingListEl) {
      var missing = report.missing_features || [];
      missingListEl.textContent = missing.length
        ? "Not measured in this example: " + missing.join(", ") + ". Missing values are not fabricated; complete the MVV through an approved workflow."
        : "No reportable features are missing in this example. Missing values are not fabricated.";
    }
    var focus = document.querySelector("[data-demo-focus]");
    if (focus) {
      focus.innerHTML = "";
      var areas = report.focus_areas || [];
      var countEl = document.querySelector("[data-demo-focus-shown]");
      var extraHost = document.querySelector("[data-demo-focus-extra]");
      var extraList = document.querySelector("[data-demo-focus-extra-list]");
      if (countEl) {
        countEl.textContent = areas.length
          ? "Showing " + Math.min(areas.length, 5) + " of " + areas.length + " measured focus areas."
          : "No measured focus areas in this example.";
      }
      if (!areas.length) {
        focus.innerHTML = "<li>No measured focus areas in this example. Keep monitoring trends and complete missing inputs when appropriate.</li>";
        if (extraHost) extraHost.hidden = true;
        if (extraList) extraList.innerHTML = "";
      } else {
        var visibleLimit = 5;
        var visibleAreas = areas.slice(0, visibleLimit);
        var remainingAreas = areas.slice(visibleLimit);
        visibleAreas.forEach(function (area) {
          var li = document.createElement("li");
          li.innerHTML = '<span class="focus-title">' + escapeHtml(area.focus) + "</span> <span class=\"focus-direction\">(" + escapeHtml(humanize(area.direction || "review")) + " · " + escapeHtml(humanize(area.action_type || "review")) + ")</span> — "
            + escapeHtml(area.recommendation);
          focus.appendChild(li);
        });
        if (extraHost && extraList) {
          if (remainingAreas.length) {
            extraHost.hidden = false;
            extraList.innerHTML = "";
            remainingAreas.forEach(function (area) {
              var li = document.createElement("li");
              li.innerHTML = '<span class="focus-title">' + escapeHtml(area.focus) + "</span> <span class=\"focus-direction\">(" + escapeHtml(humanize(area.direction || "review")) + " · " + escapeHtml(humanize(area.action_type || "review")) + ")</span> — "
                + escapeHtml(area.recommendation);
              extraList.appendChild(li);
            });
          } else {
            extraHost.hidden = true;
            extraList.innerHTML = "";
          }
        }
      }
    }
    var ranges = document.querySelector("[data-demo-ranges]");
    if (ranges) {
      ranges.innerHTML = "";
      (report.ranges || []).forEach(function (item) {
        var tr = document.createElement("tr");
        var targetRange = item.target_range || {};
        var numericRange = formatTargetRange(targetRange);
        var range = numericRange || targetRange.label || "reference band";
        if (numericRange && targetRange.label && numericRange !== targetRange.label) {
          range += " · " + targetRange.label;
        }
        var action = item.action_type ? " · " + humanize(item.action_type) : "";
        tr.innerHTML = "<td>" + escapeHtml(item.biomarker) + "</td>"
          + "<td>" + escapeHtml(formatValue(item.current_value)) + (item.unit ? " " + escapeHtml(item.unit) : "") + "</td>"
          + "<td>" + escapeHtml(range) + "</td>"
          + '<td class="range-status ' + escapeHtml(item.status) + '">' + escapeHtml(humanize(item.status) + action) + "</td>"
          + "<td>" + escapeHtml(item.recommendation) + "</td>";
        ranges.appendChild(tr);
      });
    }
    var payload = document.querySelector("[data-demo-payload] code");
    if (payload) payload.textContent = JSON.stringify(example.payload, null, 2);
    renderProgress(example.progress && example.progress.report);
    setDemoReportStatus("Showing " + example.label + " development report.", false);
  }

  function renderProgress(report) {
    var panel = document.querySelector("[data-demo-progress]");
    var summary = document.querySelector("[data-demo-progress-summary]");
    var changes = document.querySelector("[data-demo-progress-changes]");
    var boundary = document.querySelector("[data-demo-progress-boundary]");
    if (!panel || !summary || !changes || !boundary) return;
    if (!report) {
      panel.hidden = true;
      summary.textContent = "";
      changes.innerHTML = "";
      boundary.textContent = "";
      return;
    }
    panel.hidden = false;
    var counts = report.summary || {};
    summary.textContent = "Compared " + report.previous_assessed_at + " → " + report.current_assessed_at
      + ": " + counts.moved_into_reference_range + " measured item(s) moved into a development reference range, "
      + counts.moved_out_of_reference_range + " moved out, and "
      + counts.current_focus_areas + " remain current focus area(s).";
    changes.innerHTML = "";
    var changed = (report.range_changes || []).filter(function (item) {
      return item.value_change !== "unchanged" || item.status_transition !== "unchanged";
    });
    if (!changed.length) {
      changes.innerHTML = '<tr><td colspan="5">No measured range or status changes in this synthetic comparison.</td></tr>';
    } else {
      changed.forEach(function (item) {
        var tr = document.createElement("tr");
        var change = item.value_delta === null || item.value_delta === undefined
          ? humanize(item.value_change)
          : signedValue(item.value_delta);
        tr.innerHTML = "<td>" + escapeHtml(item.biomarker) + "</td>"
          + "<td>" + escapeHtml(formatValue(item.previous_value)) + "</td>"
          + "<td>" + escapeHtml(formatValue(item.current_value)) + "</td>"
          + "<td>" + escapeHtml(change) + "</td>"
          + "<td>" + escapeHtml(humanize(item.status_transition)) + "</td>";
        changes.appendChild(tr);
      });
    }
    boundary.textContent = report.summary.interpretation + " " + report.disclaimer;
  }

  function downloadWellnessReport(example) {
    if (!window.Blob || !window.URL || !window.URL.createObjectURL) {
      setDemoReportStatus("This browser cannot create a local report download.", true);
      return;
    }
    var result = example.result;
    var report = result.wellness_report;
    var summary = {
      format: "wellness-improvement-report-v1",
      source: "Synthetic GitHub Pages development example",
      profile_id: example.id,
      profile_label: example.label,
      readout: {
        chronological_age: result.metrics.chronological_age,
        biological_age: result.metrics.biological_age,
        current_deficit_load_fi: result.metrics.current_deficit_load_fi,
        current_deficit_load_fi_details: result.metrics.current_deficit_load_fi_details,
        homeostatic_deviation_score: result.trajectory.homeostatic_deviation_score
      },
      top_interventions: result.top_interventions || [],
      wellness_report: report,
      action_effect_estimated: false,
      clinical_or_lifespan_claim: false,
      progress_report: example.progress ? publicProgressReport(example.progress.report) : null,
      model_boundary: {
        model_id: result.model_metadata.model_id,
        production_ready: result.model_metadata.production_ready,
        reference_panel_id: result.data_quality.reference_panel_id,
        reference_panel_sha256: result.data_quality.reference_panel_sha256,
        reference_panel_production_ready: result.data_quality.reference_panel_production_ready,
        reference_panel_fixture_only: result.data_quality.reference_panel_fixture_only,
        reference_panel_readiness: result.data_quality.reference_panel_readiness,
        fi_denominator_strength: result.data_quality.fi_denominator_strength,
        action_effect_estimated: false,
        clinical_or_lifespan_claim: false
      },
      privacy_note: "This report contains only the selected synthetic example. No patient identifier, raw CSV, or uploaded data is included."
    };
    var blob = new Blob([JSON.stringify(summary, null, 2) + "\n"], { type: "application/json" });
    var url = window.URL.createObjectURL(blob);
    var anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "wellness-improvement-report-v1-development.json";
    anchor.hidden = true;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    window.setTimeout(function () { window.URL.revokeObjectURL(url); }, 0);
    setDemoReportStatus("Downloaded a local improvement report for " + example.label + ".", false);
  }

  function copyWellnessFocus(example) {
    if (!example || !example.result) return;
    var result = example.result;
    var report = result.wellness_report || {};
    var payload = {
      format: "wellness-focus-areas-v2",
      source: "Synthetic GitHub Pages development example",
      profile_id: example.id,
      profile_label: example.label,
      action_effect_estimated: false,
      clinical_or_lifespan_claim: false,
      model_boundary: {
        model_id: result.model_metadata.model_id,
        production_ready: result.model_metadata.production_ready,
        reference_panel_id: result.data_quality.reference_panel_id,
        reference_panel_sha256: result.data_quality.reference_panel_sha256,
        reference_panel_production_ready: result.data_quality.reference_panel_production_ready,
        reference_panel_fixture_only: result.data_quality.reference_panel_fixture_only,
        reference_panel_readiness: result.data_quality.reference_panel_readiness,
        fi_denominator_strength: result.data_quality.fi_denominator_strength,
        action_effect_estimated: false,
        clinical_or_lifespan_claim: false
      },
      focus_areas: publicFocusAreas(report),
      missing_features: report.missing_features || [],
      disclaimer: report.disclaimer,
      privacy_note: "This handoff contains only the selected synthetic example. No patient identifier, raw CSV, or uploaded data is included."
    };
    copyText(JSON.stringify(payload, null, 2), function (ok) {
      setDemoReportStatus(ok
        ? "Copied the complete measured focus list."
        : "Copy failed — select the focus list from the report download.", !ok);
    });
  }

  function publicFocusAreas(report) {
    return (report.focus_areas || []).map(function (area) {
      return {
        feature: area.feature,
        focus: area.focus,
        current_value: area.current_value,
        unit: area.unit,
        target_range: area.target_range,
        target_range_label: area.target_range_label,
        direction: area.direction,
        action_type: area.action_type,
        z_score: area.z_score,
        source: area.source,
        recommendation: area.recommendation
      };
    });
  }

  function copyText(text, done) {
    if (navigator.clipboard && window.isSecureContext === true) {
      navigator.clipboard.writeText(text).then(function () { done(true); })
        .catch(function () { fallbackCopy(text, done); });
    } else {
      fallbackCopy(text, done);
    }
  }

  function setDemoReportStatus(message, isError) {
    var status = document.querySelector("[data-demo-report-status]");
    if (!status) return;
    if (!status.dataset.sequence) status.dataset.sequence = "0";
    var sequence = Number(status.dataset.sequence) + 1;
    status.dataset.sequence = String(sequence);
    var prefix = "[demo-report " + sequence + "] ";
    var label = (isError ? "Error" : "Status") + " " + sequence + " · ";
    status.setAttribute("aria-label", label + message);
    status.textContent = prefix + message;
    status.style.color = isError ? "var(--accent)" : "var(--archive)";
  }

  function publicProgressReport(report) {
    if (!report) return null;
    var safe = JSON.parse(JSON.stringify(report));
    delete safe.patient_id;
    return safe;
  }

  function printWellnessReport() {
    var reportRegion = document.querySelector("#demo-report");
    if (!reportRegion || typeof window.print !== "function") {
      setDemoReportStatus("This browser cannot print the improvement report.", true);
      return;
    }
    var details = reportRegion.querySelectorAll("details");
    var openStates = [];
    details.forEach(function (detail) {
      openStates.push(detail.open);
      detail.open = true;
    });
    var finish = function () {
      document.body.classList.remove("print-report-mode");
      details.forEach(function (detail, index) { detail.open = openStates[index]; });
      window.removeEventListener("afterprint", finish);
    };
    document.body.classList.add("print-report-mode");
    window.addEventListener("afterprint", finish);
    setDemoReportStatus("Print dialog opened for the selected improvement report.", false);
    window.print();
  }

  function signedPercent(value) {
    var number = Number(value);
    if (!Number.isFinite(number)) return "—";
    var scaled = number * 100;
    return (scaled >= 0 ? "+" : "") + scaled.toFixed(1) + "%";
  }

  function formatTargetRange(target) {
    var hasLow = typeof target.low === "number";
    var hasHigh = typeof target.high === "number";
    if (hasLow && hasHigh) return formatValue(target.low) + "–" + formatValue(target.high);
    if (hasLow) return "≥ " + formatValue(target.low);
    if (hasHigh) return "≤ " + formatValue(target.high);
    return "";
  }

  function formatValue(value) {
    if (value === null || value === undefined) return "not measured";
    return typeof value === "number" ? String(Number(value.toFixed(2))) : String(value);
  }

  function signedValue(value) {
    var number = Number(value);
    return (number >= 0 ? "+" : "") + formatValue(number);
  }

  var ACRONYM_LABELS = {
    "ecw_tbw": "ECW/TBW (extracellular water to total body water ratio)",
    "ffmi": "FFMI (fat-free mass index)",
    "bmi": "BMI (body mass index)",
    "bia": "BIA (bioelectrical impedance analysis)"
  };

  function humanize(value) {
    var raw = String(value);
    if (Object.prototype.hasOwnProperty.call(ACRONYM_LABELS, raw)) return ACRONYM_LABELS[raw];
    if (Object.prototype.hasOwnProperty.call(ACRONYM_LABELS, raw.toLowerCase())) return ACRONYM_LABELS[raw.toLowerCase()];
    return raw.replace(/_/g, " ").replace(/\b\w/g, function (letter) { return letter.toUpperCase(); });
  }

  // ---------------------------------------------------------------
  // 5) Local-only SECA TableView preview and typed assessment overlay. The
  // overlay is a handoff builder only: no demographic or clinical values are
  // guessed and no payload is sent anywhere.
  // ---------------------------------------------------------------
  // Monotonic request token shared by the synthetic sample fetch and the
  // local FileReader path. A later click increments the counter, and any
  // async callback from an earlier request is ignored so a late success
  // cannot overwrite the latest error or a newer selection.
  var secaRequestToken = 0;
  var secaStatusSequence = 0;

  function initSecaAssessmentIntake() {
    var panel = document.querySelector("#seca-intake");
    var fields = document.querySelector("#intake-fields");
    var checklist = document.querySelector("#intake-mvv");
    var submit = document.querySelector("#intake-download");
    var status = document.querySelector("#intake-status");
    var patientId = document.querySelector("#intake-patient-id");
    var preview = document.querySelector("#intake-preview");
    var command = document.querySelector("#intake-command");
    if (!panel || !fields || !checklist || !submit || !status || !patientId
      || !preview || !command
      || !window.FrailtyIntakeForm) {
      return { setExport: function () {}, clear: function () {} };
    }
    var controller = null;
    var parsedExport = null;
    var previewed = false;

    function setStatus(message, isError) {
      status.textContent = message;
      status.style.color = isError ? "var(--accent)" : "var(--archive)";
    }

    function measured(value) {
      return value !== null && value !== undefined && value !== "";
    }

    function patientIdState() {
      var value = String(patientId.value || "").trim();
      if (!value) return { ok: false, value: value, message: "Enter a local pseudonym before continuing." };
      if (value.length > 128) return { ok: false, value: value, message: "The local identifier must be 128 characters or fewer." };
      return { ok: true, value: value, message: "" };
    }

    function resetPreview() {
      previewed = false;
      preview.hidden = true;
      preview.textContent = "";
      submit.textContent = "Preview CLI-ready assessment overlay";
      command.hidden = true;
      command.textContent = "";
    }

    function renderChecklist(values, mvv, validation) {
      var bloodCount = window.FrailtyIntakeForm.bloodFields.filter(function (name) {
        return measured(values[name]);
      }).length;
      var historyCount = window.FrailtyIntakeForm.historyFields.filter(function (name) {
        return measured(values[name]);
      }).length;
      var checks = [
        { ok: measured(values.age) && measured(values.sex), label: "Age + sex" },
        { ok: measured(values.bmi), label: "BMI" },
        { ok: measured(values.phase_angle), label: "Phase angle" },
        { ok: measured(values.ecw_tbw), label: "ECW/TBW" },
        { ok: bloodCount >= 6, label: "At least 6 blood variables (" + bloodCount + ")" },
        { ok: measured(values.fasting_glucose) || measured(values.hba1c), label: "Fasting glucose or HbA1c" },
        { ok: historyCount >= 4, label: "At least 4 history variables (" + historyCount + ")" }
      ];
      checklist.innerHTML = "<ul class=\"intake-checklist\">"
        + checks.map(function (item) {
          return "<li class=\"" + (item.ok ? "is-complete" : "is-pending") + "\">"
            + (item.ok ? "✓ " : "◯ ") + escapeHtml(item.label) + "</li>";
        }).join("")
        + "</ul>";
      if (validation && !validation.ok) {
        checklist.innerHTML += "<p class=\"field-note intake-error\">"
          + escapeHtml(validation.invalid.join(" ")) + "</p>";
      } else if (mvv && !mvv.ok) {
        checklist.innerHTML += "<p class=\"field-note\">"
          + escapeHtml(mvv.missing.join(" ")) + "</p>";
      }
    }

    function update() {
      if (!controller) {
        submit.disabled = true;
        return;
      }
      var values = controller.read();
      var mvv = controller.evaluateMvv();
      var validation = controller.validate();
      var identifier = patientIdState();
      renderChecklist(values, mvv, validation);
      if (!identifier.ok) {
        checklist.innerHTML += "<p class=\"field-note intake-error\">"
          + escapeHtml(identifier.message) + "</p>";
      }
      if (previewed) resetPreview();
      submit.disabled = !mvv.ok || !validation.ok || !identifier.ok;
      submit.setAttribute("aria-disabled", submit.disabled ? "true" : "false");
      if (!validation.ok) {
        setStatus("Fix the highlighted engineering-range values before downloading.", true);
      } else if (!identifier.ok) {
        setStatus(identifier.message, true);
      } else if (!mvv.ok) {
        setStatus("Complete the remaining MVV fields; nothing is inferred from the scan.", false);
      } else {
        setStatus("MVV complete. Preview the local overlay before downloading it.", false);
      }
    }

    function previewOverlay(values, measuredAt, identifier) {
      var overlay = window.FrailtyIntakeForm.buildOverlay(values, measuredAt, identifier);
      preview.textContent = JSON.stringify(overlay, null, 2);
      preview.hidden = false;
      previewed = true;
      submit.disabled = false;
      submit.setAttribute("aria-disabled", "false");
      submit.textContent = "Confirm and download overlay";
      command.hidden = true;
      command.textContent = "";
      setStatus("Review the overlay below. Confirm only after checking the local identifier and measurements.", false);
      preview.focus();
    }

    function downloadOverlay(overlay) {
      if (!controller || !parsedExport) return;
      if (!window.Blob || !window.URL || !window.URL.createObjectURL) {
        setStatus("This browser cannot create a local assessment overlay download.", true);
        return;
      }
      var url = window.URL.createObjectURL(
        new Blob([JSON.stringify(overlay, null, 2) + "\n"], { type: "application/json" })
      );
      var anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "frailty-assessment-overlay.json";
      anchor.hidden = true;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.setTimeout(function () { window.URL.revokeObjectURL(url); }, 0);
      command.hidden = false;
      command.textContent = "python -m frailty_engine assess-overlay <path-to-your-SECA.csv> --overlay frailty-assessment-overlay.json";
      setStatus("Downloaded the overlay locally. Run the canonical Python assessor with your original SECA CSV; no scan or measurement data was uploaded.", false);
    }

    function previewOrDownload() {
      if (!controller || !parsedExport) return;
      var values = controller.read();
      var mvv = controller.evaluateMvv();
      var validation = controller.validate();
      var identifier = patientIdState();
      if (!mvv.ok || !validation.ok || !identifier.ok) {
        update();
        return;
      }
      var overlay = window.FrailtyIntakeForm.buildOverlay(
        values, parsedExport.measuredAt, identifier.value
      );
      if (!previewed) {
        previewOverlay(values, parsedExport.measuredAt, identifier.value);
        return;
      }
      downloadOverlay(overlay);
      submit.textContent = "Download overlay again";
    }

    patientId.addEventListener("input", update);
    patientId.addEventListener("change", update);
    submit.addEventListener("click", previewOrDownload);

    return {
      setExport: function (exported, sourceLabel) {
        parsedExport = exported;
        panel.hidden = false;
        var initial = window.FrailtySecaParser.assessmentPayloadOverlay(
          exported.latest.values
        );
        controller = window.FrailtyIntakeForm.render(fields, initial, update);
        patientId.value = "local-seca-overlay";
        resetPreview();
        setStatus(
          (sourceLabel || "SECA export") + " mapped values are pre-filled. "
            + "Enter the remaining fields yourself; no missing value is inferred.",
          false
        );
        update();
      },
      clear: function () {
        parsedExport = null;
        controller = null;
        panel.hidden = true;
        fields.innerHTML = "";
        checklist.innerHTML = "";
        patientId.value = "local-seca-overlay";
        resetPreview();
        submit.disabled = true;
        submit.setAttribute("aria-disabled", "true");
        setStatus("", false);
      }
    };
  }

  function initSecaImport() {
    var input = document.querySelector("#seca-file");
    if (!input) return;
    var sampleButton = document.querySelector("#seca-load-sample");
    var downloadButton = document.querySelector("#seca-download");
    var sampleDownloadLink = document.querySelector('a[href="example-seca-tableview.csv"][download]');
    var intake = initSecaAssessmentIntake();
    var parsedExport = null;
    if (downloadButton) {
      downloadButton.hidden = true;
      downloadButton.addEventListener("click", function () {
        if (parsedExport) downloadNormalizedSecaSummary(parsedExport);
      });
    }
    if (sampleDownloadLink && !sampleDownloadLink.hasAttribute("aria-label")) {
      sampleDownloadLink.setAttribute(
        "aria-label",
        "Download the anonymized synthetic SECA TableView sample (not your file; software fixture, not patient data)"
      );
    }
    function consumeText(text, sourceLabel, token) {
      if (token !== secaRequestToken) return;
      try {
        parsedExport = window.FrailtySecaParser.parseSecaCsv(text);
        renderSecaPreview(parsedExport, sourceLabel, token);
        intake.setExport(parsedExport, sourceLabel);
        if (downloadButton) downloadButton.hidden = false;
      } catch (error) {
        parsedExport = null;
        intake.clear();
        if (downloadButton) downloadButton.hidden = true;
        clearSecaDetails(token);
        setSecaStatus("Could not parse this export: " + error.message, true, token);
      }
    }
    if (sampleButton) {
      sampleButton.addEventListener("click", function () {
        sampleButton.disabled = true;
        secaRequestToken += 1;
        var token = secaRequestToken;
        intake.clear();
        setSecaStatus("Loading the synthetic sample locally…", false, token);
        fetch("example-seca-tableview.csv", { cache: "no-store" })
          .then(function (response) {
            if (!response.ok) throw new Error("example-seca-tableview.csv returned " + response.status);
            return response.text();
          })
          .then(function (text) { consumeText(text, "Synthetic sample:", token); })
          .catch(function (error) {
            if (token !== secaRequestToken) return;
            clearSecaDetails(token);
            setSecaStatus("Synthetic sample could not be loaded: " + error.message, true, token);
          })
          .finally(function () { sampleButton.disabled = false; });
      });
    }
    input.addEventListener("change", function () {
      var file = input.files && input.files[0];
      if (!file) return;
      parsedExport = null;
      intake.clear();
      if (downloadButton) downloadButton.hidden = true;
      secaRequestToken += 1;
      var token = secaRequestToken;
      if (file.size > window.FrailtySecaParser.MAX_SECA_BYTES) {
        clearSecaDetails(token);
        setSecaStatus("This local export is larger than the 5 MB preview limit.", true, token);
        input.value = "";
        return;
      }
      var reader = new FileReader();
      reader.onload = function () {
        consumeText(String(reader.result), "Local export:", token);
      };
      reader.onerror = function () {
        if (token !== secaRequestToken) return;
        clearSecaDetails(token);
        setSecaStatus("The local file could not be read.", true, token);
      };
      reader.readAsText(file);
    });
  }

  function downloadNormalizedSecaSummary(exported) {
    if (!window.Blob || !window.URL || !window.URL.createObjectURL) {
      setSecaStatus("This browser cannot create a local normalized download.", true);
      return;
    }
    var latest = exported.latest || { values: {}, units: {}, segments: {}, warnings: [], derivations: [] };
    var summary = {
      format: "seca-tableview-normalized-v1",
      source_format: "SECA TableView CSV",
      measured_at: exported.measuredAt,
      latest_measurements: latest.values,
      units: latest.units,
      segmental_skeletal_muscle_mass: latest.segments,
      unmapped_labels: exported.unmappedLabels || [],
      derivations: latest.derivations,
      unit_warnings: latest.warnings,
      trend_available: Boolean(exported.trendAvailable),
      trend_latest_minus_previous: exported.trend || {},
      segmental_trend_latest_minus_previous: exported.segmentalTrend || {},
      assessment_readiness: exported.assessmentReadiness ? {
        assessment_ready: exported.assessmentReadiness.assessmentReady,
        missing_requirements: exported.assessmentReadiness.missingRequirements,
        note: exported.assessmentReadiness.note
      } : null,
      privacy_note: "Normalized locally from a SECA export. The original CSV and patient identifiers are not included."
    };
    var blob = new Blob([JSON.stringify(summary, null, 2) + "\n"], { type: "application/json" });
    var url = window.URL.createObjectURL(blob);
    var anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "seca-normalized-summary.json";
    anchor.hidden = true;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    window.setTimeout(function () { window.URL.revokeObjectURL(url); }, 0);
    setSecaStatus("Downloaded normalized summary locally. No scan data was uploaded.", false);
  }

  function renderSecaPreview(exported, sourceLabel, token) {
    var scan = exported.latest, canonical = ["bmi", "phase_angle", "ecw_tbw", "ffmi", "skeletal_muscle_mass", "visceral_fat"].filter(function (key) { return scan.values[key] !== undefined; });
    var readiness = exported.assessmentReadiness;
    var warningNote = scan.warnings.length ? " Review unit warnings." : "";
    var trendNote = exported.trendAvailable ? "" : " Single scan only — trend comparison requires two dated scans.";
    var readinessNote = " SECA-only preview is not assessment-ready; see remaining MVV inputs below.";
    setSecaStatus((sourceLabel ? sourceLabel + " " : "") + "Mapped " + canonical.length + " canonical fields from the latest dated scan. No upload occurred." + trendNote + readinessNote + warningNote, Boolean(scan.warnings.length), token);
    var details = document.querySelector("#seca-import-details");
    if (!details) return;
    var segmentLabels = Object.keys(scan.segments);
    var trendLabels = Object.keys(exported.segmentalTrend || {});
    var pairs = [
      ["Latest scan", exported.measuredAt],
      ["BMI", scan.values.bmi],
      ["Weight", scan.values.weight_kg],
      ["Height", scan.values.height_cm],
      ["Estimated height (derived)", scan.values.estimated_height_cm],
      ["Fat mass", scan.values.fat_mass_kg],
      ["Fat-free mass", scan.values.fat_free_mass_kg],
      ["FFMI (derived)", scan.values.ffmi],
      ["Skeletal muscle", scan.values.skeletal_muscle_mass],
      ["Visceral fat", scan.values.visceral_fat],
      ["Segments", "__SEGMENTS__"],
      ["Segment trends (latest − previous)", "__SEGMENT_TRENDS__"],
      ["Unmapped export rows", (exported.unmappedLabels || []).join(", ") || "none"],
      ["Derivations", scan.derivations.length ? scan.derivations.join(" | ") : "none"],
      ["Unit warnings", scan.warnings.length ? scan.warnings.join(" | ") : "none"],
      ["Trend status", exported.trendAvailable ? "latest minus previous" : "requires 2 dated scans"],
      ["BMI trend", exported.trend.bmi === undefined ? "not comparable" : formatDelta(exported.trend.bmi)],
      ["Muscle trend", exported.trend.skeletal_muscle_mass === undefined ? "not comparable" : formatDelta(exported.trend.skeletal_muscle_mass)],
      ["Assessment status", readiness && readiness.assessmentReady ? "ready" : "SECA preview only — MVV not met"],
      ["Remaining MVV inputs", readiness ? readiness.missingRequirements.join("; ") : "not available"],
      ["Safe next step", readiness ? readiness.note : "Complete the full MVV through an approved workflow."]
    ];
    var pairsHtml = "";
    pairs.forEach(function (pair) {
      if (pair[1] === "__SEGMENTS__") {
        pairsHtml += "<dt>" + escapeHtml(pair[0]) + "</dt><dd>";
        if (!segmentLabels.length) {
          pairsHtml += "none";
        } else {
          pairsHtml += '<ul class="seca-segment-list">'
            + segmentLabels.map(function (label) {
                return '<li>' + escapeHtml(label + ": " + formatValue(scan.segments[label])) + "</li>";
              }).join("")
            + "</ul>";
        }
        pairsHtml += "</dd>";
      } else if (pair[1] === "__SEGMENT_TRENDS__") {
        pairsHtml += "<dt>" + escapeHtml(pair[0]) + "</dt><dd>";
        if (!trendLabels.length) {
          pairsHtml += "not comparable";
        } else {
          pairsHtml += '<ul class="seca-segment-list">'
            + trendLabels.map(function (label) {
                return '<li>' + escapeHtml(label + ": " + formatDelta(exported.segmentalTrend[label])) + "</li>";
              }).join("")
            + "</ul>";
        }
        pairsHtml += "</dd>";
      } else {
        pairsHtml += "<dt>" + escapeHtml(pair[0]) + "</dt><dd>"
          + escapeHtml(pair[1] === undefined ? "not present" : formatValue(pair[1]))
          + "</dd>";
      }
    });
    details.innerHTML = pairsHtml;
  }

  function formatDelta(value) {
    return (value >= 0 ? "+" : "") + Number(value).toFixed(2);
  }

  function setSecaStatus(message, isError, token) {
    var status = document.querySelector("#seca-import-status");
    if (!status) return;
    if (token !== undefined && token !== secaRequestToken) return;
    // Prefix the sequence number so repeated updates remain distinguishable
    // for assistive technology and review.
    var sequence = ++secaStatusSequence;
    var prefix = "[seca " + sequence + "] ";
    var label = (isError ? "Error" : "Status") + " " + sequence + " · ";
    status.setAttribute("aria-label", label + message);
    status.textContent = prefix + message;
    status.style.color = isError ? "var(--accent)" : "var(--archive)";
  }

  function clearSecaDetails(token) {
    var details = document.querySelector("#seca-import-details");
    if (!details) return;
    if (token !== undefined && token !== secaRequestToken) return;
    details.innerHTML = "";
  }

  // ---------------------------------------------------------------
  // Boot
  // ---------------------------------------------------------------
  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  ready(function () {
    initEvidenceFilter();
    initCopyButtons();
    initStatusTable();
    initDemo();
    initSecaImport();
  });
})();
