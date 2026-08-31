"""Typed errors exposed by the API and command-line interface."""


class FrailtyEngineError(Exception):
    """Base class for expected domain errors."""


class ValidationError(FrailtyEngineError):
    """Raised when an assessment contains invalid or unknown input."""

    def __init__(self, message: str, *, field_errors: dict[str, str] | None = None):
        super().__init__(message)
        self.field_errors = field_errors or {}


class InsufficientDataError(FrailtyEngineError):
    """Raised when the API-enforced minimum viable vector is not satisfied."""

    def __init__(self, message: str, *, missing_requirements: list[str] | None = None):
        super().__init__(message)
        self.missing_requirements = missing_requirements or []


class ModelUnavailableError(FrailtyEngineError):
    """Raised when an optional production ML dependency or artifact is absent."""


class PredictionFailure(FrailtyEngineError):
    """Internal signal that a predictor or runtime dependency failed mid-request.

    The HTTP layer maps this to a generic 500 envelope without echoing the
    underlying exception text or any caller-supplied data.
    """

    def __init__(self, message: str = "prediction failed"):
        super().__init__(message)
