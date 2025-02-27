from typing import Optional


class ApplicationError(Exception):
    """Base exception class for all application-specific exceptions"""

    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class ConfigurationError(ApplicationError):
    """Raised when there's an error in application configuration"""

    def __init__(self, message: str, config_key: Optional[str] = None):
        details = f"Configuration key: {config_key}" if config_key else None
        super().__init__(message, details)


class ResourceError(ApplicationError):
    """Raised when a required resource (file, image, etc.) is missing or invalid"""

    def __init__(self, message: str, resource_path: Optional[str] = None):
        details = f"Resource path: {resource_path}" if resource_path else None
        super().__init__(message, details)


class DataError(ApplicationError):
    """Base class for data-related exceptions"""

    pass


class DataValidationError(DataError):
    """Raised when data validation fails"""

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        value: Optional[str] = None,
    ):
        details = f"Field: {field_name}, Value: {value}" if field_name else None
        super().__init__(message, details)


class DataAccessError(DataError):
    """Raised when there's an error accessing data (file, database, etc.)"""

    def __init__(self, message: str, operation: Optional[str] = None):
        details = f"Operation: {operation}" if operation else None
        super().__init__(message, details)


class UIError(ApplicationError):
    """Base class for UI-related exceptions"""

    pass


class WidgetError(UIError):
    """Raised when there's an error with a specific widget"""

    def __init__(self, message: str, widget_name: Optional[str] = None):
        details = f"Widget: {widget_name}" if widget_name else None
        super().__init__(message, details)


class ActionError(UIError):
    """Raised when there's an error executing a UI action"""

    def __init__(self, message: str, action_id: Optional[str] = None):
        details = f"Action ID: {action_id}" if action_id else None
        super().__init__(message, details)


class StateError(ApplicationError):
    """Raised when the application enters an invalid state"""

    def __init__(
        self,
        message: str,
        current_state: Optional[str] = None,
        expected_state: Optional[str] = None,
    ):
        details = (
            f"Current state: {current_state}, Expected: {expected_state}"
            if current_state
            else None
        )
        super().__init__(message, details)


class NetworkError(ApplicationError):
    """Raised when network operations fail"""

    def __init__(
        self,
        message: str,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
    ):
        details = f"Endpoint: {endpoint}, Status: {status_code}" if endpoint else None
        super().__init__(message, details)


class PermissionError(ApplicationError):
    """Raised when there's a permission-related error"""

    def __init__(self, message: str, required_permission: Optional[str] = None):
        details = (
            f"Required permission: {required_permission}"
            if required_permission
            else None
        )
        super().__init__(message, details)
