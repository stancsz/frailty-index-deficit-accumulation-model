/* Local-only SECA TableView parser shared by the Pages preview and Node tests. */
(function (root, factory) {
  var api = factory();
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.FrailtySecaParser = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  var MAX_SECA_BYTES = 5 * 1024 * 1024;
  var MONTHS = {
    Jan: 1, Feb: 2, Mar: 3, Apr: 4, May: 5, Jun: 6,
    Jul: 7, Aug: 8, Sep: 9, Oct: 10, Nov: 11, Dec: 12
  };
  var ASSESSMENT_OVERLAY_FIELDS = [
    "bmi", "phase_angle", "ecw_tbw", "ffmi",
    "skeletal_muscle_mass", "visceral_fat"
  ];

  function parseCsv(text) {
    var rows = [], row = [], cell = "", quoted = false;
    for (var i = 0; i < text.length; i++) {
      var char = text[i];
      if (char === '"') {
        if (quoted && text[i + 1] === '"') { cell += '"'; i++; }
        else quoted = !quoted;
      } else if (char === "," && !quoted) {
        row.push(cell); cell = "";
      } else if ((char === "\n" || char === "\r") && !quoted) {
        if (char === "\r" && text[i + 1] === "\n") i++;
        row.push(cell); cell = "";
        if (row.some(function (part) { return part.trim() !== ""; })) rows.push(row);
        row = [];
      } else cell += char;
    }
    if (cell || row.length) { row.push(cell); rows.push(row); }
    return rows;
  }

  function parseDateHeader(header) {
    var match = /^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),\s+(\d{4}),\s+(0?[1-9]|1[0-2]):([0-5]\d)\s+(AM|PM)$/.exec(header.trim());
    if (!match) throw new Error("dated columns must contain parseable dates");
    var year = Number(match[3]), month = MONTHS[match[1]], day = Number(match[2]);
    var hour = Number(match[4]) % 12 + (match[6] === "PM" ? 12 : 0);
    var minute = Number(match[5]);
    var date = new Date(0);
    date.setUTCFullYear(year, month - 1, day);
    date.setUTCHours(hour, minute, 0, 0);
    if (date.getUTCFullYear() !== year || date.getUTCMonth() !== month - 1 || date.getUTCDate() !== day || date.getUTCHours() !== hour || date.getUTCMinutes() !== minute) {
      throw new Error("dated columns must contain parseable dates");
    }
    return date.getTime();
  }

  function assessmentReadiness(values) {
    var missing = ["age and sex (not available in this SECA export; never inferred)"];
    if (values.bmi === undefined) missing.push("BMI (not present in the latest dated scan)");
    if (values.phase_angle === undefined) missing.push("phase angle (not present in the latest dated scan)");
    if (values.ecw_tbw === undefined) missing.push("ECW/TBW (not present in the latest dated scan)");
    missing.push("at least 6 blood-panel values, including fasting_glucose or hba1c");
    missing.push("at least 4 clinical-history values");
    return {
      assessmentReady: missing.length === 0,
      missingRequirements: missing,
      note: "SECA preview is not an assessment. Add the listed inputs through an approved clinical workflow; do not infer them from the scan."
    };
  }

  function assessmentPayloadOverlay(values) {
    var overlay = {};
    ASSESSMENT_OVERLAY_FIELDS.forEach(function (field) {
      if (values && values[field] !== undefined) overlay[field] = values[field];
    });
    return overlay;
  }

  function parseSecaCsv(input) {
    var text = String(input).replace(/^\uFEFF/, "");
    var rows = parseCsv(text);
    if (!rows.length || rows[0].length < 3 || rows[0][0].trim().toLowerCase() !== "value" || rows[0][1].trim().toLowerCase() !== "unit") {
      throw new Error("expected Value, Unit, and dated columns");
    }
    var headers = rows[0].slice(2).map(function (header) { return header.trim(); });
    if (!headers.length || headers.some(function (header) { return !header; })) {
      throw new Error("expected at least one non-empty dated column");
    }
    var scans = headers.map(function () { return { values: {}, units: {}, segments: {}, warnings: [], derivations: [] }; });
    var direct = {
      "Body Mass Index": ["bmi", "kg/m²"],
      "Height": ["height_cm", "cm"],
      "Weight": ["weight_kg", "kg"],
      "Skeletal Muscle Mass": ["skeletal_muscle_mass", "kg"],
      "Fat Mass": ["fat_mass_kg", "kg"],
      "Fat Free Mass": ["fat_free_mass_kg", "kg"],
      "Visceral Adipose Tissue": ["visceral_fat", "Liters"],
      "Phase Angle": ["phase_angle", "degrees"],
      "ECW/TBW": ["ecw_tbw", "ratio"]
    };
    var segments = { "Torso": true, "Left Arm": true, "Left Leg": true, "Right Arm": true, "Right Leg": true };
    var unmappedLabels = [];
    rows.slice(1).forEach(function (row, rowIndex) {
      var expectedColumns = headers.length + 2;
      if (row.length > expectedColumns && row.slice(expectedColumns).some(function (cell) { return cell.trim() !== ""; })) {
        throw new Error("row " + (rowIndex + 2) + " has extra non-empty columns");
      }
      var label = (row[0] || "").trim(), unit = (row[1] || "").trim();
      if (!label || label === "Segmental Skeletal Muscle Mass") return;
      if (!direct[label] && !segments[label]) {
        if (unmappedLabels.indexOf(label) === -1) unmappedLabels.push(label);
        return;
      }
      scans.forEach(function (scan, index) {
        var raw = (row[index + 2] || "").replace(/\u2212/g, "-").replace(/\u00a0/g, " ").trim();
        if (!raw) return;
        var value = Number(raw);
        if (!Number.isFinite(value)) throw new Error("non-numeric value for " + label);
        if (direct[label]) {
          scan.values[direct[label][0]] = value;
          scan.units[direct[label][0]] = unit;
          if (unit && unit.toLowerCase() !== direct[label][1].toLowerCase()) {
            scan.warnings.push(label + ": exported unit " + unit + "; expected " + direct[label][1]);
          }
        }
        else scan.segments[label] = value;
      });
    });
    scans.forEach(function (scan) {
      if (scan.values.weight_kg !== undefined && scan.values.fat_mass_kg !== undefined) {
        var fatFreeMass = scan.values.weight_kg - scan.values.fat_mass_kg;
        if (fatFreeMass < 0) throw new Error("SECA fat mass cannot exceed body weight");
        if (scan.values.fat_free_mass_kg === undefined) {
          scan.values.fat_free_mass_kg = Number(fatFreeMass.toFixed(6));
          scan.derivations.push("fat_free_mass_kg = weight_kg - fat_mass_kg");
        }
      }
      var heightForFfmi = scan.values.height_cm;
      if (heightForFfmi === undefined && scan.values.weight_kg > 0 && scan.values.bmi > 0) {
        heightForFfmi = Math.sqrt(scan.values.weight_kg / scan.values.bmi) * 100;
        scan.values.estimated_height_cm = Number(heightForFfmi.toFixed(4));
        scan.derivations.push("estimated_height_cm derived from weight_kg and bmi");
      }
      if (heightForFfmi > 0 && scan.values.fat_free_mass_kg !== undefined) {
        scan.values.ffmi = Number((scan.values.fat_free_mass_kg / Math.pow(heightForFfmi / 100, 2)).toFixed(6));
        scan.derivations.push("ffmi = fat_free_mass_kg / height_m²");
      }
    });
    var order = headers.map(function (header, index) {
      return { index: index, time: parseDateHeader(header) };
    });
    order.sort(function (a, b) { return a.time - b.time || a.index - b.index; });
    var previousIndex = order.length > 1 ? order[order.length - 2].index : null;
    var latestIndex = order[order.length - 1].index;
    var trend = {};
    var segmentalTrend = {};
    if (previousIndex !== null) {
      Object.keys(scans[latestIndex].values).forEach(function (key) {
        if (scans[previousIndex].values[key] !== undefined) {
          trend[key] = scans[latestIndex].values[key] - scans[previousIndex].values[key];
        }
      });
      Object.keys(scans[latestIndex].segments).forEach(function (key) {
        if (scans[previousIndex].segments[key] !== undefined) {
          segmentalTrend[key] = scans[latestIndex].segments[key] - scans[previousIndex].segments[key];
        }
      });
    }
    return { headers: headers, scans: scans, latest: scans[latestIndex], measuredAt: headers[latestIndex], trend: trend, segmentalTrend: segmentalTrend, trendAvailable: order.length > 1, unmappedLabels: unmappedLabels, assessmentReadiness: assessmentReadiness(scans[latestIndex].values), assessmentPayloadOverlay: assessmentPayloadOverlay(scans[latestIndex].values) };
  }

  return { MAX_SECA_BYTES: MAX_SECA_BYTES, parseSecaCsv: parseSecaCsv, assessmentPayloadOverlay: assessmentPayloadOverlay };
});
