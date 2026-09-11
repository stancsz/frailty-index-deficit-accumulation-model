from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_gde_authority_chain_is_current() -> None:
    receipt = json.loads((ROOT / "docs/test-receipt.json").read_text())
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/verify_docs.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    assert f"{receipt['python_tests_collected']} Python" in result.stdout
