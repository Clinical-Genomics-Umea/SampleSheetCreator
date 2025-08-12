from dataclasses import dataclass
from enum import Enum, auto


class StatusLevel(Enum):
    """Enumeration of validation status levels."""
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


@dataclass
class ValidationResult:
    """Represents the result of a validation check.
    
    Attributes:
        name: The name of the validation check
        message: A message describing the validation result
        severity: The severity level of the validation result
    """
    name: str
    message: str = ""
    severity: StatusLevel = StatusLevel.INFO

    def __post_init__(self):
        if not self.message:
            if self.severity == StatusLevel.INFO:
                self.message = f"{self.name} validation passed"
            elif self.severity == StatusLevel.WARNING:
                self.message = f"{self.name} validation warning"
            elif self.severity == StatusLevel.ERROR:
                self.message = f"{self.name} validation failed"
