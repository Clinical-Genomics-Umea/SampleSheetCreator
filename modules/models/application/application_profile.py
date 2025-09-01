from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ApplicationProfile:
    ApplicationProfileVersion: str
    ApplicationProfileName: str
    ApplicationName: str
    ApplicationType: str
    Settings: Dict[str, Any]
    Data: Dict[str, Any]
    DataFields: List[str]
    Translate: Optional[Dict[str, Any]] = field(default_factory=dict)
