from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from packaging.version import Version, parse


@dataclass
class ApplicationProfile:
    _v: str
    name: str
    application_name: str
    application_type: str
    settings: Dict[str, Any]
    data: Dict[str, Any]
    data_fields: List[str]
    id: str = ""
    translate: Optional[Dict[str, Any]] = field(default_factory=dict)
    version: Version = field(init=False)

    def __post_init__(self):
        self.id = f"{self.name}_{self._v}"
        self.version = parse(str(self._v))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ApplicationProfile':
        mapping = {
            '_v': 'ApplicationProfileVersion',
            'name': 'ApplicationProfileName',
            'application_name': 'ApplicationName',
            'application_type': 'ApplicationType',
            'settings': 'Settings',
            'data': 'Data',
            'data_fields': 'DataFields',
            'translate': 'Translate'
        }

        mapped_data = {k: data.get(v) for k, v in mapping.items()}
        return cls(**mapped_data)