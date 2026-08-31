"""Explicit, non-imputing adapters for public NHANES source files.

The CDC publishes continuous-NHANES component files as SAS transport files
and the linked-mortality outcome as a fixed-width ASCII file.  This module
handles the mechanical parts of bringing those files into the engine's flat
row contract.  It deliberately does not guess cycle-specific questionnaire
codes, laboratory missing-value sentinels, or clinical definitions: callers
must provide an explicit column map and missing-value policy.

The resulting rows are still research inputs.  Public-use mortality files can
contain disclosure-protection perturbations, and an approved cohort,
reference panel, cutoff review, and clinical sign-off remain separate gates.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

from .calibration import ReferencePanel
from .derived import calculate_fib_4
from .exceptions import ModelUnavailableError, ValidationError
from .features import FEATURE_NAMES
from .training import build_survival_frame, SurvivalTrainingFrame
from .survey_design import SurveyDesign


@dataclass(frozen=True)
class NHANESCycleResource:
    """Official source locations for a continuous-NHANES BIA cycle."""

    cycle: str
    bia_url: str
    mortality_url: str


NHANES_BIA_CYCLES: dict[str, NHANESCycleResource] = {
    "1999-2000": NHANESCycleResource(
        cycle="1999-2000",
        bia_url="https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/1999/DataFiles/BIX.XPT",
        mortality_url=(
            "https://ftp.cdc.gov/pub/health_statistics/NCHS/datalinkage/"
            "linked_mortality/NHANES_1999_2000_MORT_2019_PUBLIC.dat"
        ),
    ),
    "2001-2002": NHANESCycleResource(
        cycle="2001-2002",
        bia_url="https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2001/DataFiles/BIX_B.XPT",
        mortality_url=(
            "https://ftp.cdc.gov/pub/health_statistics/NCHS/datalinkage/"
            "linked_mortality/NHANES_2001_2002_MORT_2019_PUBLIC.dat"
        ),
    ),
    "2003-2004": NHANESCycleResource(
        cycle="2003-2004",
        bia_url="https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2003/DataFiles/BIX_C.XPT",
        mortality_url=(
            "https://ftp.cdc.gov/pub/health_statistics/NCHS/datalinkage/"
            "linked_mortality/NHANES_2003_2004_MORT_2019_PUBLIC.dat"
        ),
    ),
}


@dataclass(frozen=True)
class NHANESColumnMap:
    """Raw-column map for one prepared cycle.

    Keys are canonical engine names plus optional ``patient_id``,
    ``duration``, ``event``, ``ethnicity``, ``sample_weight`` and raw BIA/FIB-4
    source names.
    Values are raw column names.  A map is required so that cycle-specific
    coding decisions are visible in the calling code rather than hidden in a
    broad alias table. ``duration_unit`` applies only when ``duration`` is
    mapped directly from the source row. Records returned by
    ``read_public_use_mortality`` already expose canonical duration in years.
    """

    columns: Mapping[str, str]
    duration_unit: str = "years"
    missing_values: frozenset[Any] = frozenset()

    def __post_init__(self) -> None:
        if self.duration_unit not in {"years", "months"}:
            raise ValueError("duration_unit must be 'years' or 'months'")
        invalid = set(self.columns) - (
            set(FEATURE_NAMES)
            | {
                "patient_id",
                "duration",
                "event",
                "ethnicity",
                "race_ethnicity",
                "ast",
                "alt",
                "platelets",
                "bia_resistance_50k",
                "bia_reactance_50k",
                "bia_ecf",
                "bia_tbw",
                "bia_fat_free_mass",
                "height_cm",
                "seqn",
                "sample_weight",
            }
        )
        if invalid:
            raise ValueError(f"unsupported NHANES map key(s): {sorted(invalid)}")
        if any(
            not isinstance(source, str) or not source.strip()
            for source in self.columns.values()
        ):
            raise ValueError("NHANES column-map values must be non-empty strings")


def cycle_resource(cycle: str) -> NHANESCycleResource:
    """Return an official BIA/mortality manifest entry for a supported cycle."""

    try:
        return NHANES_BIA_CYCLES[cycle]
    except KeyError as error:
        raise ValueError(
            f"unsupported BIA cycle {cycle!r}; choose one of {sorted(NHANES_BIA_CYCLES)}"
        ) from error


def read_xpt(path: str | Path) -> Any:
    """Read a CDC SAS transport file using the optional pandas dependency."""

    try:
        import pandas as pd
    except ImportError as error:
        raise ModelUnavailableError(
            "pandas is required for XPT ingestion; install the [data] extra"
        ) from error
    try:
        return pd.read_sas(path, format="xport", encoding="latin-1")
    except (OSError, ValueError) as error:
        raise ValidationError(f"could not read NHANES XPT file: {path}") from error


def merge_xpt_files(paths: Iterable[str | Path]) -> Any:
    """Outer-merge component XPT files on the NHANES ``SEQN`` identifier.

    Overlapping non-key columns are rejected.  This avoids silently choosing
    one cycle/component's version of a field when a source map is wrong.
    """

    path_list = list(paths)
    if not path_list:
        raise ValueError("at least one XPT path is required")
    frames = [read_xpt(path) for path in path_list]
    merged = frames[0]
    for frame in frames:
        frame.columns = [str(column).upper() for column in frame.columns]
    merged.columns = [str(column).upper() for column in merged.columns]
    if "SEQN" not in merged.columns:
        raise ValidationError("NHANES XPT file is missing SEQN")
    for frame in frames[1:]:
        if "SEQN" not in frame.columns:
            raise ValidationError("NHANES XPT file is missing SEQN")
        overlap = (set(merged.columns) & set(frame.columns)) - {"SEQN"}
        if overlap:
            raise ValidationError(
                "NHANES XPT files have overlapping non-key columns",
                field_errors={
                    column: "duplicate source column" for column in sorted(overlap)
                },
            )
        try:
            merged = merged.merge(frame, on="SEQN", how="outer", validate="one_to_one")
        except ValueError as error:
            raise ValidationError(
                "NHANES XPT files must have unique SEQN rows"
            ) from error
    return merged


def _fixed_width_value(line: str, start: int, end: int) -> str:
    return line[start - 1 : end].strip()


def _optional_int(raw: str) -> int | None:
    return int(raw) if raw and raw != "." else None


def read_public_use_mortality(
    path: str | Path, *, require_eligible: bool = True
) -> list[dict[str, Any]]:
    """Read a CDC 2019 public-use continuous-NHANES mortality ``.dat`` file.

    Positions follow CDC's supplied SAS reader: ``SEQN`` 1-6,
    ``ELIGSTAT`` 15, ``MORTSTAT`` 16, ``UCOD_LEADING`` 17-19,
    ``PERMTH_INT`` 43-45, and ``PERMTH_EXM`` 46-48.  The MEC follow-up
    duration is used because the BIA measurement is collected in the MEC.
    Duration is returned in both months and years; zero-month observations are
    retained and will be rejected later by the survival-frame contract rather
    than silently discarded.
    """

    source = Path(path)
    try:
        raw_lines = source.read_bytes().splitlines()
    except OSError as error:
        raise ValidationError(
            f"could not read NHANES mortality file: {path}"
        ) from error
    result: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(raw_lines, start=1):
        try:
            line = raw_line.decode("ascii")
        except UnicodeDecodeError as error:
            raise ValidationError(
                f"NHANES mortality file line {line_number} is not ASCII"
            ) from error
        if not line.strip():
            continue
        # The CDC SAS reader uses LRECL=61 PAD MISSOVER.  The downloaded ASCII
        # file may omit trailing blanks, so reproduce PAD before slicing.
        if len(line) < 19:
            raise ValidationError(
                f"NHANES mortality file line {line_number} is shorter than 19 characters"
            )
        line = line.ljust(61)
        seqn_raw = _fixed_width_value(line, 1, 6)
        eligstat_raw = _fixed_width_value(line, 15, 15)
        mortstat_raw = _fixed_width_value(line, 16, 16)
        cause = _fixed_width_value(line, 17, 19) or None
        int_months = _optional_int(_fixed_width_value(line, 43, 45))
        exm_months = _optional_int(_fixed_width_value(line, 46, 48))
        if not seqn_raw.isdigit():
            raise ValidationError(f"invalid SEQN on mortality line {line_number}")
        eligstat = _optional_int(eligstat_raw)
        mortstat = _optional_int(mortstat_raw)
        if require_eligible and eligstat != 1:
            continue
        if eligstat != 1:
            result.append(
                {
                    "seqn": int(seqn_raw),
                    "patient_id": f"nhanes-seqn-{int(seqn_raw):06d}",
                    "eligstat": eligstat,
                    "mortstat": mortstat,
                    "ucod_leading": cause,
                    "duration_interview_months": int_months,
                    "duration_months": exm_months,
                    "duration": (
                        float(exm_months) / 12.0 if exm_months is not None else None
                    ),
                    "event": bool(mortstat) if mortstat in {0, 1} else None,
                }
            )
            continue
        if mortstat not in {0, 1}:
            raise ValidationError(
                f"eligible mortality line {line_number} has invalid MORTSTAT"
            )
        duration_months = exm_months
        result.append(
            {
                "seqn": int(seqn_raw),
                "patient_id": f"nhanes-seqn-{int(seqn_raw):06d}",
                "eligstat": eligstat,
                "mortstat": mortstat,
                "ucod_leading": cause,
                "duration_interview_months": int_months,
                "duration_months": duration_months,
                "duration": (
                    float(duration_months) / 12.0
                    if duration_months is not None
                    else None
                ),
                "event": bool(mortstat),
            }
        )
    return result


def mortality_by_seqn(
    records: Iterable[Mapping[str, Any]],
) -> dict[int, Mapping[str, Any]]:
    """Index parsed mortality records and reject duplicate participant IDs."""

    indexed: dict[int, Mapping[str, Any]] = {}
    for record in records:
        try:
            seqn = int(record["seqn"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValidationError("mortality record requires integer seqn") from error
        if seqn in indexed:
            raise ValidationError(f"duplicate mortality record for SEQN {seqn}")
        indexed[seqn] = record
    return indexed


def _is_missing(value: Any, missing_values: frozenset[Any]) -> bool:
    if value is None:
        return True
    try:
        if value == "":
            return True
    except (TypeError, ValueError):
        pass
    try:
        if bool(value != value):  # NaN without requiring pandas.
            return True
    except (TypeError, ValueError):
        pass
    try:
        return value in missing_values
    except TypeError:
        return False


def _raw_value(
    row: Mapping[str, Any], source: str | None, missing_values: frozenset[Any]
) -> Any:
    if source is None:
        return None
    value = row.get(source)
    return None if _is_missing(value, missing_values) else value


def _positive_float(value: Any, name: str) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValidationError(f"{name} must be numeric") from error
    if not math.isfinite(number) or number <= 0:
        raise ValidationError(f"{name} must be positive and finite")
    return number


def _derive_bia_and_fib4(
    row: dict[str, Any], source_row: Mapping[str, Any], mapping: NHANESColumnMap
) -> None:
    """Fill only mathematically derived fields when their explicit sources exist."""

    def raw(name: str) -> Any:
        return _raw_value(source_row, mapping.columns.get(name), mapping.missing_values)

    phase_angle = raw("phase_angle")
    if phase_angle is None:
        resistance = _positive_float(raw("bia_resistance_50k"), "BIA 50-kHz resistance")
        reactance = _positive_float(raw("bia_reactance_50k"), "BIA 50-kHz reactance")
        if resistance is not None and reactance is not None:
            row["phase_angle"] = math.degrees(math.atan2(reactance, resistance))

    ecw_tbw = raw("ecw_tbw")
    if ecw_tbw is None:
        ecf = _positive_float(raw("bia_ecf"), "BIA extracellular fluid")
        tbw = _positive_float(raw("bia_tbw"), "BIA total body water")
        if ecf is not None and tbw is not None:
            if ecf > tbw:
                raise ValidationError(
                    "BIA extracellular fluid cannot exceed total body water"
                )
            row["ecw_tbw"] = ecf / tbw

    ffmi = raw("ffmi")
    if ffmi is None:
        fat_free_mass = _positive_float(raw("bia_fat_free_mass"), "BIA fat-free mass")
        height_cm = _positive_float(raw("height_cm"), "height")
        if fat_free_mass is not None and height_cm is not None:
            row["ffmi"] = fat_free_mass / (height_cm / 100.0) ** 2

    if row.get("fib_4") is None:
        age = row.get("age")
        ast = _positive_float(raw("ast"), "AST")
        alt = _positive_float(raw("alt"), "ALT")
        platelets = _positive_float(raw("platelets"), "platelets")
        if (
            age is not None
            and ast is not None
            and alt is not None
            and platelets is not None
        ):
            row["fib_4"] = calculate_fib_4(float(age), ast, alt, platelets)


def build_nhanes_rows(
    records: Iterable[Mapping[str, Any]],
    *,
    column_map: NHANESColumnMap,
    mortality_records: Iterable[Mapping[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Map raw cycle rows into canonical survival rows without imputing.

    The map controls every source-column decision.  If ``mortality_records``
    is supplied, ``duration`` and ``event`` come from the mortality index by
    ``SEQN``; otherwise those two fields must be mapped directly.  All 35
    canonical keys are emitted, with unmapped or missing values represented by
    ``None``. Mortality records must use the canonical ``duration`` in years
    emitted by ``read_public_use_mortality``; direct source-row durations may
    instead be declared in months and normalized here.
    """

    mortality_index = (
        mortality_by_seqn(mortality_records) if mortality_records is not None else None
    )
    if mortality_index is not None and column_map.duration_unit != "years":
        raise ValueError(
            "duration_unit must be 'years' when mortality_records are supplied; "
            "their duration is already normalized to years"
        )
    output: list[dict[str, Any]] = []
    for row_number, source_row in enumerate(records, start=1):
        if not isinstance(source_row, Mapping):
            raise ValidationError(f"NHANES source row {row_number} must be an object")
        source_seqn = _raw_value(
            source_row,
            column_map.columns.get("seqn", "SEQN"),
            column_map.missing_values,
        )
        try:
            seqn = int(float(source_seqn)) if source_seqn is not None else None
        except (TypeError, ValueError) as error:
            raise ValidationError(
                f"NHANES source row {row_number} has invalid SEQN"
            ) from error
        mortality = (
            mortality_index.get(seqn)
            if mortality_index is not None and seqn is not None
            else None
        )
        if mortality_index is not None and mortality is None:
            # An eligibility-filtered mortality index is authoritative for
            # training outcomes. Do not fall back to a differently sourced
            # duration/event column or accidentally train on unmatched rows.
            continue
        row: dict[str, Any] = {}
        for name in FEATURE_NAMES:
            row[name] = _raw_value(
                source_row, column_map.columns.get(name), column_map.missing_values
            )
        if "sample_weight" in column_map.columns:
            row["sample_weight"] = _raw_value(
                source_row,
                column_map.columns["sample_weight"],
                column_map.missing_values,
            )
        _derive_bia_and_fib4(row, source_row, column_map)

        if mortality is not None:
            row["patient_id"] = str(
                mortality.get("patient_id", f"nhanes-seqn-{seqn:06d}")
            )
            row["duration"] = mortality.get("duration")
            row["event"] = mortality.get("event")
        else:
            raw_id = _raw_value(
                source_row,
                column_map.columns.get("patient_id"),
                column_map.missing_values,
            )
            row["patient_id"] = (
                str(raw_id)
                if raw_id is not None
                else (
                    f"nhanes-seqn-{seqn:06d}"
                    if seqn is not None
                    else f"nhanes-row-{row_number}"
                )
            )
            row["duration"] = _raw_value(
                source_row,
                column_map.columns.get("duration"),
                column_map.missing_values,
            )
            row["event"] = _raw_value(
                source_row, column_map.columns.get("event"), column_map.missing_values
            )
            if row["duration"] is not None and column_map.duration_unit == "months":
                row["duration"] = float(row["duration"]) / 12.0

        ethnicity_source = column_map.columns.get(
            "ethnicity"
        ) or column_map.columns.get("race_ethnicity")
        ethnicity = _raw_value(source_row, ethnicity_source, column_map.missing_values)
        if ethnicity is not None:
            row["ethnicity"] = str(ethnicity).strip()
        output.append(row)
    return output


def build_nhanes_training_frame(
    records: Iterable[Mapping[str, Any]],
    *,
    column_map: NHANESColumnMap,
    mortality_records: Iterable[Mapping[str, Any]] | None = None,
    reference_panel: ReferencePanel | None = None,
    survey_design: SurveyDesign | None = None,
) -> SurvivalTrainingFrame:
    """Prepare canonical rows and apply the existing MVV/training contract."""

    rows = build_nhanes_rows(
        records, column_map=column_map, mortality_records=mortality_records
    )
    return build_survival_frame(
        rows, reference_panel=reference_panel, survey_design=survey_design
    )
