"""Derived clinical markers accepted by the feature contract."""

from __future__ import annotations

import math

from .exceptions import ValidationError


def calculate_fib_4(age: float, ast: float, alt: float, platelets: float) -> float:
    """Calculate FIB-4 from age, AST, ALT, and platelet count.

    Expected units are years, U/L, U/L, and 10^9/L respectively. The public
    35-feature vector stores the resulting `fib_4`; raw AST/ALT/platelets are
    intentionally not additional model features.
    """

    values = {"age": age, "ast": ast, "alt": alt, "platelets": platelets}
    for name, value in values.items():
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
            or float(value) <= 0
        ):
            raise ValidationError(
                f"{name} must be a positive finite number",
                field_errors={name: "expected > 0"},
            )
    return float(age) * float(ast) / (float(platelets) * math.sqrt(float(alt)))
