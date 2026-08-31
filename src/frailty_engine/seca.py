"""Typed import support for SECA mBCA TableView CSV exports.

The equipment export is useful for an anthropometry/BIA preview, but it is not
an assessment by itself. This module deliberately maps only values that are
actually present in the export and records derived values and unit warnings so
callers can decide whether to use them in a complete MVV payload. The
assessment_payload_overlay helper is the explicit bridge from a local SECA
preview to a caller-supplied assessment overlay; it never infers missing
demographics, blood, history, or functional values.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
import io
import math
from pathlib import Path
import re
from typing import TextIO


_DIRECT_FIELDS = {
    "Body Mass Index": ("bmi", "kg/m²"),
    "Height": ("height_cm", "cm"),
    "Weight": ("weight_kg", "kg"),
    "Skeletal Muscle Mass": ("skeletal_muscle_mass", "kg"),
    "Fat Mass": ("fat_mass_kg", "kg"),
    "Fat Free Mass": ("fat_free_mass_kg", "kg"),
    "Visceral Adipose Tissue": ("visceral_fat", "Liters"),
    "Phase Angle": ("phase_angle", "degrees"),
    "ECW/TBW": ("ecw_tbw", "ratio"),
}
_SEGMENT_LABELS = {"Torso", "Left Arm", "Left Leg", "Right Arm", "Right Leg"}
_TIMESTAMP_PATTERN = re.compile(
    r"^(?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    r"\s+(?P<day>\d{1,2}),\s+(?P<year>\d{4}),\s+"
    r"(?P<hour>0?[1-9]|1[0-2]):(?P<minute>[0-5]\d)\s+(?P<ampm>AM|PM)$"
)
_MONTHS = {
    name: index
    for index, name in enumerate(
        (
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ),
        start=1,
    )
}


def _timestamp_key(value: str, index: int) -> tuple[bool, datetime, int]:
    try:
        parsed = _parse_timestamp(value)
    except ValueError:
        return (False, datetime.min, index)
    return (True, parsed, index)


def _parse_timestamp(value: str) -> datetime:
    match = _TIMESTAMP_PATTERN.fullmatch(value.strip())
    if match is None:
        raise ValueError("SECA dated columns must use e.g. 'Jan 2, 2025, 8:00 AM'")
    try:
        return datetime(
            int(match["year"]),
            _MONTHS[match["month"]],
            int(match["day"]),
            int(match["hour"]) % 12 + (12 if match["ampm"] == "PM" else 0),
            int(match["minute"]),
        )
    except ValueError as error:
        raise ValueError("dated columns must contain parseable dates") from error


@dataclass(frozen=True)
class SecaScan:
    """One dated column from a TableView export."""

    measured_at: str
    measurements: dict[str, float]
    units: dict[str, str]
    segmental_skeletal_muscle_mass: dict[str, float]
    derivations: tuple[str, ...]
    unit_warnings: tuple[str, ...]

    def to_measurements(self) -> dict[str, float]:
        """Return only values that can seed the canonical 35-feature payload.

        Recorded anthropometry and derived support values remain available via
        ``all_measurements``; they are intentionally not mixed into a 35-field
        assessment payload because they are not canonical features.
        """

        return {
            key: value
            for key, value in self.measurements.items()
            if key
            in {
                "bmi",
                "phase_angle",
                "ecw_tbw",
                "ffmi",
                "skeletal_muscle_mass",
                "visceral_fat",
            }
        }

    def all_measurements(self) -> dict[str, float]:
        """Return all recorded and explicitly derived values for local review."""

        return dict(self.measurements)


@dataclass(frozen=True)
class SecaTableViewExport:
    """A parsed SECA TableView export with one or more dated scans."""

    columns: tuple[str, ...]
    scans: tuple[SecaScan, ...]
    unmapped_labels: tuple[str, ...]
    source_format: str = "seca-tableview-csv"

    @property
    def latest(self) -> SecaScan:
        if not self.scans:
            raise ValueError("SECA export contains no dated scans")
        index = max(
            range(len(self.scans)), key=lambda i: _timestamp_key(self.columns[i], i)
        )
        return self.scans[index]

    def latest_measurements(self) -> dict[str, float]:
        """Return canonical fields from the latest dated scan."""

        return self.latest.to_measurements()

    def latest_all_measurements(self) -> dict[str, float]:
        """Return all latest-scan values, including non-canonical support fields."""

        return self.latest.all_measurements()

    def assessment_payload_overlay(self) -> dict[str, float]:
        """Return only latest-scan values valid for an assessment overlay.

        The result contains the six canonical BIA/anthropometry keys that the
        export can actually provide: bmi, phase_angle, ecw_tbw, ffmi,
        skeletal_muscle_mass, and visceral_fat. Support values such as weight
        and estimated height remain available through latest_all_measurements
        but are not silently promoted into the 35-feature contract.
        """

        return self.latest_measurements()

    @property
    def trend_available(self) -> bool:
        """Whether a latest-minus-previous comparison can be computed."""

        return len(self.scans) >= 2

    @property
    def trend_note(self) -> str:
        """Explain why a trend is or is not available to a caller."""

        if self.trend_available:
            return "Latest minus previous dated scan."
        return "Trend unavailable: at least two dated scans are required."

    @property
    def assessment_readiness(self) -> dict[str, object]:
        """Explain which MVV inputs remain outside a SECA export.

        A body-composition scan is a useful source for a subset of the
        canonical vector, but it is never enough to run an assessment on its
        own. This explicit checklist prevents callers from mistaking a rich
        local preview for a complete clinical/wellness input record.
        """

        values = self.latest_measurements()
        missing: list[str] = [
            "age and sex (not available in this SECA export; never inferred)",
        ]
        if "bmi" not in values:
            missing.append("BMI (not present in the latest dated scan)")
        if "phase_angle" not in values:
            missing.append("phase angle (not present in the latest dated scan)")
        if "ecw_tbw" not in values:
            missing.append("ECW/TBW (not present in the latest dated scan)")
        missing.extend(
            (
                "at least 6 blood-panel values, including fasting_glucose or hba1c",
                "at least 4 clinical-history values",
            )
        )
        return {
            "assessment_ready": not missing,
            "missing_requirements": tuple(missing),
            "note": (
                "SECA preview is not an assessment. Add the listed inputs "
                "through an approved clinical workflow; do not infer them "
                "from the scan."
            ),
        }

    def trend(self) -> dict[str, float]:
        """Return latest-minus-previous values for comparable numeric fields."""

        if len(self.scans) < 2:
            return {}
        ordered = sorted(
            range(len(self.scans)), key=lambda i: _timestamp_key(self.columns[i], i)
        )
        previous = self.scans[ordered[-2]].measurements
        current = self.scans[ordered[-1]].measurements
        return {
            key: round(current[key] - previous[key], 6)
            for key in current.keys() & previous.keys()
            if math.isfinite(current[key]) and math.isfinite(previous[key])
        }

    def segmental_trend(self) -> dict[str, float]:
        """Return latest-minus-previous changes for recorded segment values."""

        if len(self.scans) < 2:
            return {}
        ordered = sorted(
            range(len(self.scans)), key=lambda i: _timestamp_key(self.columns[i], i)
        )
        previous = self.scans[ordered[-2]].segmental_skeletal_muscle_mass
        current = self.scans[ordered[-1]].segmental_skeletal_muscle_mass
        return {
            key: round(current[key] - previous[key], 6)
            for key in current.keys() & previous.keys()
            if math.isfinite(current[key]) and math.isfinite(previous[key])
        }


def _read_source(source: str | Path | TextIO) -> str:
    if hasattr(source, "read"):
        return str(source.read()).lstrip("\ufeff")
    if isinstance(source, Path):
        return source.read_text(encoding="utf-8-sig")
    if "\n" in source or "\r" in source:
        return source.lstrip("\ufeff")
    return Path(source).read_text(encoding="utf-8-sig")


def _number(raw: str) -> float | None:
    normalized = raw.replace("\u2212", "-").replace("\u00a0", " ").strip()
    if not normalized:
        return None
    value = float(normalized)
    if not math.isfinite(value):
        raise ValueError("SECA numeric values must be finite")
    return value


def _derive(values: dict[str, float]) -> tuple[str, ...]:
    derivations: list[str] = []
    weight = values.get("weight_kg")
    fat_mass = values.get("fat_mass_kg")
    bmi = values.get("bmi")
    if weight is not None and fat_mass is not None:
        fat_free_mass = weight - fat_mass
        if fat_free_mass < 0:
            raise ValueError("SECA fat mass cannot exceed body weight")
        if "fat_free_mass_kg" not in values:
            values["fat_free_mass_kg"] = round(fat_free_mass, 6)
            derivations.append("fat_free_mass_kg = weight_kg - fat_mass_kg")
    height_cm = values.get("height_cm")
    if (
        height_cm is None
        and weight is not None
        and bmi is not None
        and weight > 0
        and bmi > 0
    ):
        height_cm = math.sqrt(weight / bmi) * 100
        values["estimated_height_cm"] = round(height_cm, 4)
        derivations.append("estimated_height_cm derived from weight_kg and bmi")
    if height_cm is not None and height_cm > 0:
        height_m = height_cm / 100
        if "fat_free_mass_kg" in values:
            values["ffmi"] = round(values["fat_free_mass_kg"] / (height_m**2), 6)
            derivations.append("ffmi = fat_free_mass_kg / height_m²")
    return tuple(derivations)


def read_seca_tableview_csv(source: str | Path | TextIO) -> SecaTableViewExport:
    """Parse a SECA TableView CSV from a path, text, or readable text stream.

    The parser accepts the observed TableView shape with quoted timestamp
    headers. It does not infer patient demographics or fill missing values.
    """

    rows = list(csv.reader(io.StringIO(_read_source(source))))
    if not rows or len(rows[0]) < 3:
        raise ValueError("SECA CSV requires Value, Unit, and at least one date column")
    header = tuple(item.strip() for item in rows[0])
    if header[0].lower() != "value" or header[1].lower() != "unit":
        raise ValueError("SECA CSV must start with Value and Unit columns")
    columns = header[2:]
    if not columns or any(
        not column or _timestamp_key(column, 0)[0] is False for column in columns
    ):
        raise ValueError("SECA dated columns must use parseable dates")
    scans_data = [
        {"values": {}, "units": {}, "segments": {}, "warnings": []} for _ in columns
    ]
    unmapped: list[str] = []
    for row_number, row in enumerate(rows[1:], start=2):
        if len(row) > len(header) and any(cell.strip() for cell in row[len(header) :]):
            raise ValueError(f"SECA row {row_number} has extra non-empty columns")
        padded = list(row) + [""] * (len(header) - len(row))
        label = padded[0].strip()
        unit = padded[1].strip()
        if not label:
            continue
        if label == "Segmental Skeletal Muscle Mass":
            continue
        direct = _DIRECT_FIELDS.get(label)
        if direct is None and label not in _SEGMENT_LABELS:
            if label not in unmapped:
                unmapped.append(label)
            continue
        for index, scan in enumerate(scans_data):
            value = _number(padded[index + 2])
            if value is None:
                continue
            if direct is not None:
                field, expected_unit = direct
                scan["values"][field] = value
                scan["units"][field] = unit
                if unit and unit.lower() != expected_unit.lower():
                    scan["warnings"].append(
                        f"{label}: exported unit {unit!r}; expected {expected_unit!r}"
                    )
            else:
                scan["segments"][label] = value

    scans: list[SecaScan] = []
    for measured_at, scan in zip(columns, scans_data, strict=True):
        derivations = _derive(scan["values"])
        scans.append(
            SecaScan(
                measured_at=measured_at,
                measurements=dict(scan["values"]),
                units=dict(scan["units"]),
                segmental_skeletal_muscle_mass=dict(scan["segments"]),
                derivations=derivations,
                unit_warnings=tuple(dict.fromkeys(scan["warnings"])),
            )
        )
    return SecaTableViewExport(
        columns=columns,
        scans=tuple(scans),
        unmapped_labels=tuple(unmapped),
    )
