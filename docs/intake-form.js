/* Local-only SECA-to-assessment overlay form.
 *
 * This file never reads a network response or sends a request. It renders a
 * typed overlay around the canonical assessment field names so a visitor can
 * complete an equipment preview and download a CLI/API-ready payload.
 */
(function (root) {
  "use strict";

  var GROUPS = [
    {
      key: "demographics",
      label: "Demographics and vital signs",
      fields: [
        { name: "age", label: "Age", unit: "years", kind: "numeric", min: 18, max: 120, step: 1 },
        { name: "sex", label: "Sex stratum", unit: "", kind: "sex" },
        { name: "bmi", label: "BMI", unit: "kg/m²", kind: "numeric", min: 5, max: 100, step: 0.1 },
        { name: "systolic_bp", label: "Systolic blood pressure", unit: "mmHg", kind: "numeric", min: 50, max: 300, step: 1 },
        { name: "diastolic_bp", label: "Diastolic blood pressure", unit: "mmHg", kind: "numeric", min: 30, max: 200, step: 1 },
        { name: "resting_hr", label: "Resting heart rate", unit: "bpm", kind: "numeric", min: 20, max: 250, step: 1 },
        { name: "waist_circumference", label: "Waist circumference", unit: "cm", kind: "numeric", min: 30, max: 250, step: 0.1 }
      ]
    },
    {
      key: "bia",
      label: "BIA / SECA",
      fields: [
        { name: "phase_angle", label: "Phase angle", unit: "degrees", kind: "numeric", min: 0, max: 20, step: 0.01 },
        { name: "ecw_tbw", label: "ECW/TBW", unit: "ratio", kind: "numeric", min: 0.1, max: 0.8, step: 0.001 },
        { name: "ffmi", label: "FFMI", unit: "kg/m²", kind: "numeric", min: 5, max: 60, step: 0.01 },
        { name: "skeletal_muscle_mass", label: "Skeletal muscle mass", unit: "kg", kind: "numeric", min: 1, max: 150, step: 0.01 },
        { name: "visceral_fat", label: "Visceral adipose tissue", unit: "L", kind: "numeric", min: 0, max: 100, step: 0.01 }
      ]
    },
    {
      key: "blood",
      label: "Blood panel",
      fields: [
        { name: "fasting_glucose", label: "Fasting glucose", unit: "mg/dL", kind: "numeric", min: 20, max: 1000, step: 0.1 },
        { name: "hba1c", label: "HbA1c", unit: "%", kind: "numeric", min: 2, max: 30, step: 0.01 },
        { name: "hs_crp", label: "hs-CRP", unit: "mg/L", kind: "numeric", min: 0, max: 1000, step: 0.01 },
        { name: "albumin", label: "Albumin", unit: "g/dL", kind: "numeric", min: 0.1, max: 8, step: 0.01 },
        { name: "creatinine", label: "Creatinine", unit: "mg/dL", kind: "numeric", min: 0.1, max: 20, step: 0.01 },
        { name: "egfr", label: "eGFR", unit: "mL/min/1.73m²", kind: "numeric", min: 0, max: 250, step: 0.1 },
        { name: "alp", label: "Alkaline phosphatase", unit: "U/L", kind: "numeric", min: 1, max: 2000, step: 1 },
        { name: "wbc", label: "White blood cell count", unit: "10⁹/L", kind: "numeric", min: 0.1, max: 200, step: 0.01 },
        { name: "rdw", label: "RDW", unit: "%", kind: "numeric", min: 5, max: 50, step: 0.01 },
        { name: "fib_4", label: "FIB-4", unit: "index", kind: "numeric", min: 0, max: 100, step: 0.01 }
      ]
    },
    {
      key: "history",
      label: "Clinical history",
      fields: [
        { name: "hypertension", label: "Hypertension", unit: "", kind: "binary" },
        { name: "t2d", label: "Type 2 diabetes", unit: "", kind: "binary" },
        { name: "osteoarthritis", label: "Osteoarthritis", unit: "", kind: "binary" },
        { name: "sleep_apnea", label: "Sleep apnea", unit: "", kind: "binary" },
        { name: "cvd", label: "Cardiovascular disease", unit: "", kind: "binary" },
        { name: "copd", label: "COPD", unit: "", kind: "binary" },
        { name: "cancer", label: "Cancer history", unit: "", kind: "binary" },
        { name: "depression", label: "Depression", unit: "", kind: "binary" }
      ]
    },
    {
      key: "functional",
      label: "Function and habits",
      fields: [
        { name: "grip_strength", label: "Grip strength", unit: "kg", kind: "numeric", min: 0, max: 150, step: 0.1 },
        { name: "chair_rise_time", label: "Chair-rise time", unit: "seconds", kind: "numeric", min: 0.1, max: 300, step: 0.1 },
        { name: "smoking_status", label: "Smoking status", unit: "", kind: "smoking" },
        { name: "alcohol_heavy_use", label: "Heavy alcohol use", unit: "", kind: "binary" },
        { name: "sleep_hours", label: "Sleep", unit: "hours/night", kind: "numeric", min: 0, max: 30, step: 0.1 }
      ]
    }
  ];

  var BLOOD_FIELDS = [
    "fasting_glucose", "hba1c", "hs_crp", "albumin", "creatinine",
    "egfr", "alp", "wbc", "rdw", "fib_4"
  ];
  var HISTORY_FIELDS = [
    "hypertension", "t2d", "osteoarthritis", "sleep_apnea",
    "cvd", "copd", "cancer", "depression"
  ];
  var MVV_CONTRACT = {
    mandatory: ["age", "sex", "bmi", "phase_angle", "ecw_tbw"],
    blood: BLOOD_FIELDS.slice(),
    history: HISTORY_FIELDS.slice()
  };

  function own(object, key) {
    return Object.prototype.hasOwnProperty.call(object || {}, key);
  }

  function measured(value) {
    return value !== null && value !== undefined && value !== "";
  }

  function allSpecs() {
    var specs = [];
    GROUPS.forEach(function (group) {
      group.fields.forEach(function (spec) { specs.push(spec); });
    });
    return specs;
  }

  function option(select, value, label) {
    var item = document.createElement("option");
    item.value = value;
    item.textContent = label;
    select.appendChild(item);
  }

  function makeInput(spec, initial, fromScan) {
    var input;
    if (spec.kind === "sex" || spec.kind === "smoking" || spec.kind === "binary") {
      input = document.createElement("select");
      if (spec.kind === "sex") {
        option(input, "", "Not measured");
        option(input, "female", "Female");
        option(input, "male", "Male");
      } else if (spec.kind === "smoking") {
        option(input, "", "Not measured");
        option(input, "never", "Never");
        option(input, "former", "Former");
        option(input, "current", "Current");
      } else {
        option(input, "", "Not measured");
        option(input, "0", "No / absent");
        option(input, "1", "Yes / present");
      }
    } else {
      input = document.createElement("input");
      input.type = "number";
      input.min = String(spec.min);
      input.max = String(spec.max);
      input.step = String(spec.step);
      input.inputMode = "decimal";
      input.placeholder = "Not measured";
    }
    input.id = "intake-" + spec.name;
    input.name = spec.name;
    input.dataset.intakeFeature = spec.name;
    input.dataset.intakeKind = spec.kind;
    if (initial !== undefined && initial !== null) {
      input.value = String(initial);
      if (fromScan) {
        input.dataset.intakeSource = "seca";
        input.setAttribute("aria-readonly", "true");
        if (input.tagName === "SELECT") input.disabled = true;
        else input.readOnly = true;
      }
    }
    return input;
  }

  function read(container) {
    var values = {};
    Array.prototype.forEach.call(
      container.querySelectorAll("[data-intake-feature]"),
      function (input) {
        var raw = String(input.value || "").trim();
        var name = input.dataset.intakeFeature;
        if (!raw) {
          values[name] = null;
        } else if (input.dataset.intakeKind === "numeric") {
          values[name] = Number(raw);
        } else if (input.dataset.intakeKind === "binary") {
          values[name] = Number(raw);
        } else {
          values[name] = raw;
        }
      }
    );
    return values;
  }

  function validate(values) {
    var invalid = [];
    allSpecs().forEach(function (spec) {
      var value = values[spec.name];
      if (value === null || value === undefined) return;
      if (spec.kind === "numeric") {
        if (!Number.isFinite(value) || value < spec.min || value > spec.max) {
          invalid.push(spec.label + " must be between " + spec.min + " and " + spec.max);
        }
      } else if (spec.kind === "binary" && value !== 0 && value !== 1) {
        invalid.push(spec.label + " must be No or Yes");
      }
    });
    return { ok: invalid.length === 0, invalid: invalid };
  }

  function evaluateMvv(values) {
    var missing = [];
    MVV_CONTRACT.mandatory.forEach(function (name) {
      if (!measured(values[name])) {
        missing.push(name + " is mandatory");
      }
    });
    var bloodMeasured = MVV_CONTRACT.blood.filter(function (name) {
      return measured(values[name]);
    }).length;
    if (bloodMeasured < 6) {
      missing.push("at least 6 blood variables are required (received " + bloodMeasured + ")");
    }
    if (!measured(values.fasting_glucose) && !measured(values.hba1c)) {
      missing.push("fasting_glucose or hba1c is required");
    }
    var historyMeasured = MVV_CONTRACT.history.filter(function (name) {
      return measured(values[name]);
    }).length;
    if (historyMeasured < 4) {
      missing.push("at least 4 history variables are required (received " + historyMeasured + ")");
    }
    return { ok: missing.length === 0, missing: missing };
  }

  function render(container, initial, onChange) {
    container.innerHTML = "";
    var inputs = [];
    GROUPS.forEach(function (group) {
      var fieldset = document.createElement("fieldset");
      fieldset.className = "intake-group";
      var legend = document.createElement("legend");
      legend.textContent = group.label;
      fieldset.appendChild(legend);
      group.fields.forEach(function (spec) {
        var row = document.createElement("div");
        row.className = "intake-field";
        var label = document.createElement("label");
        label.htmlFor = "intake-" + spec.name;
        label.textContent = spec.label + (spec.unit ? " (" + spec.unit + ")" : "");
        var hasInitial = own(initial, spec.name) && initial[spec.name] !== null && initial[spec.name] !== undefined;
        var input = makeInput(spec, hasInitial ? initial[spec.name] : null, hasInitial);
        input.addEventListener("input", function () {
          if (onChange) onChange(read(container), spec.name);
        });
        input.addEventListener("change", function () {
          if (onChange) onChange(read(container), spec.name);
        });
        row.appendChild(label);
        row.appendChild(input);
        fieldset.appendChild(row);
        inputs.push(input);
      });
      container.appendChild(fieldset);
    });
    return {
      read: function () { return read(container); },
      validate: function () { return validate(read(container)); },
      evaluateMvv: function () { return evaluateMvv(read(container)); },
      focusFirst: function () { if (inputs[0]) inputs[0].focus(); }
    };
  }

  function buildOverlay(values, measuredAt, patientId) {
    var identifier = patientId === undefined ? "local-seca-overlay" : String(patientId).trim();
    if (!identifier || identifier.length > 128) {
      throw new Error("patient_id must be a non-empty value no longer than 128 characters");
    }
    return {
      format: "frailty-engine-assessment-overlay-v1",
      source_format: "SECA TableView CSV",
      measured_at: measuredAt || null,
      patient_id: identifier,
      measurements: values,
      privacy_note: "Built locally from a SECA preview and user-entered values. No scan or measurement data was uploaded."
    };
  }

  root.FrailtyIntakeForm = {
    groups: GROUPS,
    bloodFields: BLOOD_FIELDS,
    historyFields: HISTORY_FIELDS,
    render: render,
    read: read,
    validate: validate,
    evaluateMvv: evaluateMvv,
    buildOverlay: buildOverlay
  };
  root.FrailtyMvvContract = MVV_CONTRACT;
})(typeof globalThis !== "undefined" ? globalThis : this);
