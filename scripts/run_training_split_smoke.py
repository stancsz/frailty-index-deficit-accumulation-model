"""Exercise the deterministic patient-level training split on the fixture."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from frailty_engine.training import split_survival_rows


def run(path: Path) -> dict[str, Any]:
    envelope = json.loads(path.read_text(encoding="utf-8"))
    rows = envelope.get("rows")
    if not isinstance(rows, list) or len(rows) < 2:
        raise ValueError("fixture must contain at least two rows")
    first = split_survival_rows(rows, holdout_fraction=0.2, seed=42)
    second = split_survival_rows(rows, holdout_fraction=0.2, seed=42)
    first_train_ids = {row["patient_id"] for row in first.train_rows}
    first_holdout_ids = {row["patient_id"] for row in first.holdout_rows}
    second_train_ids = {row["patient_id"] for row in second.train_rows}
    second_holdout_ids = {row["patient_id"] for row in second.holdout_rows}
    if first_train_ids & first_holdout_ids:
        raise RuntimeError("patient-level split leaked an identifier across partitions")
    if (first_train_ids, first_holdout_ids) != (second_train_ids, second_holdout_ids):
        raise RuntimeError("patient-level split is not deterministic")
    summary = first.to_mapping()
    for partition in (summary["train"], summary["holdout"]):
        if partition["event_count"] == 0 or partition["censored_count"] == 0:
            raise RuntimeError("fixture split did not preserve event/censor support")

    stratified = split_survival_rows(
        rows,
        holdout_fraction=0.2,
        seed=42,
        strata=("sex", "age_band"),
    )
    stratified_repeat = split_survival_rows(
        rows,
        holdout_fraction=0.2,
        seed=42,
        strata=("sex", "age_band"),
    )
    stratified_holdout_ids = {row["patient_id"] for row in stratified.holdout_rows}
    repeat_holdout_ids = {row["patient_id"] for row in stratified_repeat.holdout_rows}
    if stratified_holdout_ids != repeat_holdout_ids:
        raise RuntimeError("stratified patient-level split is not deterministic")
    for partition in (stratified.train_rows, stratified.holdout_rows):
        if {row.get("sex") for row in partition} != {"female", "male"}:
            raise RuntimeError("stratified split did not preserve sex support")
        age_bands = {
            "18-39"
            if row["age"] < 40
            else "40-59"
            if row["age"] < 60
            else "60-79"
            if row["age"] < 80
            else "80+"
            for row in partition
        }
        if age_bands != {"18-39", "40-59", "60-79", "80+"}:
            raise RuntimeError("stratified split did not preserve age-band support")
    return {
        "fixture": path.as_posix(),
        "strategy": summary["strategy"],
        "seed": summary["seed"],
        "train": summary["train"],
        "holdout": summary["holdout"],
        "patient_overlap": summary["patient_overlap"],
        "stratified": stratified.to_mapping(),
        "clinical_use": "forbidden",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path("examples/external_validation_synthetic.json"),
    )
    args = parser.parse_args()
    print(json.dumps(run(args.path), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
