"""Telegraph exceptions and error handling."""

from typing import Any, Optional


class TelegraphError(Exception):
    """Base exception for Telegraph package."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """Initialize Telegraph error.

        Args:
        ----
            message: Error message
            details: Additional error details

        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class TelegraphAPIError(TelegraphError):
    """Exception for Telegraph API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize Telegraph API error.

        Args:
        ----
            message: Error message
            status_code: HTTP status code
            response_data: API response data

        """
        super().__init__(message, {"status_code": status_code, "response": response_data})
        self.status_code = status_code
        self.response_data = response_data or {}


class ValidationError(TelegraphError):
    """Exception for validation errors."""

    def __init__(self, field: str, message: str, value: Any = None) -> None:
        """Initialize validation error.

        Args:
        ----
            field: Field name that failed validation
            message: Validation error message
            value: Invalid value

        """
        super().__init__(f"Validation error for {field}: {message}")
        self.field = field
        self.value = value
