from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def _load_script() -> Any:
    path = Path(__file__).parents[1] / "scripts" / "review_nhanes_intake.py"
    spec = importlib.util.spec_from_file_location("review_nhanes_intake", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _FakeFrame:
    columns = ["SEQN", "AGE", "SEX", "BMI", "RESISTANCE", "REACTANCE"]

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows

    def to_dict(self, *, orient: str) -> list[dict[str, Any]]:
        assert orient == "records"
        return self._rows


def _inputs(tmp_path: Path) -> tuple[Path, Path, Path]:
    xpt = tmp_path / "component.xpt"
    mortality = tmp_path / "mortality.dat"
    column_map = tmp_path / "column-map.json"
    xpt.write_bytes(b"local xpt placeholder")
    mortality.write_bytes(b"local mortality placeholder")
    column_map.write_text(
        json.dumps(
            {
                "columns": {
                    "seqn": "SEQN",
                    "age": "AGE",
                    "sex": "SEX",
                    "bmi": "BMI",
                    "bia_resistance_50k": "RESISTANCE",
                    "bia_reactance_50k": "REACTANCE",
                },
                "duration_unit": "years",
                "missing_values": [".", 9999],
            }
        ),
        encoding="utf-8",
    )
    return xpt, mortality, column_map


def _args(
    xpt: Path,
    mortality: Path,
    column_map: Path,
    *,
    output: Path | None = None,
    check: bool = False,
) -> SimpleNamespace:
    return SimpleNamespace(
        cycle="2003-2004",
        xpt=[xpt],
        mortality=mortality,
        column_map=column_map,
        output=output,
        check=check,
    )


def _patch_sources(module: Any, monkeypatch: Any, rows: list[dict[str, Any]]) -> None:
    monkeypatch.setattr(module, "merge_xpt_files", lambda paths: _FakeFrame(rows))
    monkeypatch.setattr(
        module,
        "read_public_use_mortality",
        lambda path, require_eligible=False: [
            {
                "seqn": 1001,
                "patient_id": "nhanes-seqn-001001",
                "eligstat": 1,
                "event": False,
                "duration": 4.0,
            },
            {
                "seqn": 1002,
                "patient_id": "nhanes-seqn-001002",
                "eligstat": 1,
                "event": True,
                "duration": 3.0,
            },
            {
                "seqn": 9000,
                "patient_id": "nhanes-seqn-009000",
                "eligstat": 0,
                "event": None,
                "duration": None,
            },
        ],
    )


def test_review_is_deterministic_and_never_serializes_rows(
    tmp_path: Path, monkeypatch: Any
) -> None:
    module = _load_script()
    xpt, mortality, column_map = _inputs(tmp_path)
    _patch_sources(
        module,
        monkeypatch,
        [
            {
                "SEQN": 1001,
                "AGE": 50,
                "SEX": 1,
                "BMI": 25,
                "RESISTANCE": 500,
                "REACTANCE": 50,
            },
            {
                "SEQN": 1002,
                "AGE": 60,
                "SEX": 2,
                "BMI": 27,
                "RESISTANCE": 600,
                "REACTANCE": 60,
            },
        ],
    )

    first = module.run_review(_args(xpt, mortality, column_map))
    second = module.run_review(_args(xpt, mortality, column_map))

    assert first == second
    assert first["outcome"] == {"status": "passed", "blockers": []}
    assert first["xpt_summary"]["row_count"] == 2
    assert first["mortality_summary"]["eligible_rows"] == 2
    assert first["canonical_row_summary"]["rows_after_map"] == 2
    assert first["canonical_row_summary"]["derived_signal_presence"]["phase_angle"] == 2
    assert first["checks"]["no_imputation"] is True
    serialized = json.dumps(first, sort_keys=True)
    assert "1001" not in serialized
    assert "nhanes-seqn" not in serialized
    assert "500" not in serialized


def test_review_blocks_duplicate_seqn_without_exposing_the_duplicate(
    tmp_path: Path, monkeypatch: Any
) -> None:
    module = _load_script()
    xpt, mortality, column_map = _inputs(tmp_path)
    _patch_sources(
        module,
        monkeypatch,
        [
            {"SEQN": 1001, "AGE": 50, "SEX": 1, "BMI": 25},
            {"SEQN": 1001, "AGE": 51, "SEX": 1, "BMI": 26},
        ],
    )

    receipt = module.run_review(_args(xpt, mortality, column_map))

    assert receipt["outcome"]["status"] == "failed"
    assert receipt["outcome"]["blockers"] == [
        "XPT components contain duplicate SEQN rows"
    ]
    assert "1001" not in json.dumps(receipt, sort_keys=True)


def test_review_requires_explicit_anchor_map_and_year_duration(
    tmp_path: Path, monkeypatch: Any
) -> None:
    module = _load_script()
    xpt, mortality, column_map = _inputs(tmp_path)
    column_map.write_text(
        json.dumps(
            {
                "columns": {"seqn": "SEQN", "age": "AGE", "sex": "SEX"},
                "duration_unit": "years",
                "missing_values": [],
            }
        ),
        encoding="utf-8",
    )
    _patch_sources(module, monkeypatch, [{"SEQN": 1001, "AGE": 50, "SEX": 1}])

    missing_anchor = module.run_review(_args(xpt, mortality, column_map))
    assert missing_anchor["outcome"]["status"] == "failed"
    assert (
        "explicitly map seqn, age, sex, and bmi"
        in missing_anchor["outcome"]["blockers"][0]
    )

    column_map.write_text(
        json.dumps(
            {
                "columns": {"seqn": "SEQN", "age": "AGE", "sex": "SEX", "bmi": "BMI"},
                "duration_unit": "months",
                "missing_values": [],
            }
        ),
        encoding="utf-8",
    )
    duration_conflict = module.run_review(_args(xpt, mortality, column_map))
    assert duration_conflict["outcome"]["status"] == "failed"
    assert "duration_unit must be years" in duration_conflict["outcome"]["blockers"][0]

    column_map.write_text(
        json.dumps(
            {
                "columns": {
                    "seqn": "SEQN",
                    "age": "AGE",
                    "sex": "SEX",
                    "bmi": "NOT_IN_XPT",
                },
                "duration_unit": "years",
                "missing_values": [],
            }
        ),
        encoding="utf-8",
    )
    missing_source = module.run_review(_args(xpt, mortality, column_map))
    assert missing_source["outcome"]["status"] == "failed"
    assert "source column missing" in missing_source["outcome"]["blockers"][0]

    valid_map = {
        "columns": {"seqn": "SEQN", "age": "AGE", "sex": "SEX", "bmi": "BMI"},
        "duration_unit": "years",
        "missing_values": [],
    }
    column_map.write_text(json.dumps(valid_map), encoding="utf-8")
    monkeypatch.setattr(
        module,
        "read_public_use_mortality",
        lambda path, require_eligible=False: [
            {"seqn": 7777, "eligstat": 1, "event": False, "duration": 4.0}
        ],
    )
    no_join = module.run_review(_args(xpt, mortality, column_map))
    assert no_join["outcome"]["status"] == "failed"
    assert "no eligible mortality rows matched" in no_join["outcome"]["blockers"][0]

    monkeypatch.setattr(
        module,
        "read_public_use_mortality",
        lambda path, require_eligible=False: [
            {"seqn": 1001, "eligstat": 1, "event": False, "duration": None}
        ],
    )
    missing_duration = module.run_review(_args(xpt, mortality, column_map))
    assert missing_duration["outcome"]["status"] == "failed"
    assert "missing follow-up duration" in missing_duration["outcome"]["blockers"][0]


def test_cli_writes_and_checks_a_deterministic_receipt(
    tmp_path: Path, monkeypatch: Any
) -> None:
    module = _load_script()
    xpt, mortality, column_map = _inputs(tmp_path)
    _patch_sources(
        module,
        monkeypatch,
        [{"SEQN": 1001, "AGE": 50, "SEX": 1, "BMI": 25}],
    )
    output = tmp_path / "receipt.json"
    command = [
        "--cycle",
        "2003-2004",
        "--xpt",
        str(xpt),
        "--mortality",
        str(mortality),
        "--column-map",
        str(column_map),
        "--output",
        str(output),
    ]

    assert module.main(command) == 0
    assert module.main(command + ["--check"]) == 0
    output.write_text("{}\n", encoding="utf-8")
    assert module.main(command + ["--check"]) == 3


def test_cli_help_exposes_local_only_review_contract() -> None:
    module = _load_script()
    try:
        module.main(["--help"])
    except SystemExit as error:
        assert error.code == 0
    else:
        raise AssertionError("--help should exit")
