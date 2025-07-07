"""Custom exceptions for the Homey API client."""

from typing import Any, Dict, Optional


class HomeyError(Exception):
    """Base exception for all Homey API errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class HomeyConnectionError(HomeyError):
    """Raised when there's a connection error to Homey."""

    pass


class HomeyAuthenticationError(HomeyError):
    """Raised when authentication fails."""

    pass


class HomeyNotFoundError(HomeyError):
    """Raised when a requested resource is not found."""

    pass


class HomeyPermissionError(HomeyError):
    """Raised when the user doesn't have permission to perform an action."""

    pass


class HomeyAPIError(HomeyError):
    """Raised when the Homey API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.status_code = status_code
        self.error_code = error_code


class HomeyTimeoutError(HomeyError):
    """Raised when a request times out."""

    pass


class HomeyValidationError(HomeyError):
    """Raised when input validation fails."""

    pass


class HomeyDeviceError(HomeyError):
    """Raised when there's an error with a specific device."""

    def __init__(
        self,
        message: str,
        device_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.device_id = device_id


class HomeyFlowError(HomeyError):
    """Raised when there's an error with a flow."""

    def __init__(
        self,
        message: str,
        flow_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.flow_id = flow_id


class HomeyWebSocketError(HomeyError):
    """Raised when there's an error with the WebSocket connection."""

    pass


class HomeyZoneError(HomeyError):
    """Raised when there's an error with a zone."""

    def __init__(
        self,
        message: str,
        zone_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.zone_id = zone_id


class HomeyAppError(HomeyError):
    """Raised when there's an error with an app."""

    def __init__(
        self,
        message: str,
        app_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.app_id = app_id
