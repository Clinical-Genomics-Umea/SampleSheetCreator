from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from packaging.version import Version, parse

@dataclass
class TestApplicationProfile:
    name: str
    _v: str
    version: Version = field(default=Version)
    id: str = field(default=None)

    def __post_init__(self):
        self.version : Version = parse(str(self._v))
        self.id = f"{self.name}_{self._v}"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestApplicationProfile':
        mapping = {
            '_v': 'ApplicationProfileVersion',
            'name': 'ApplicationProfileName',
        }

        mapped_data = {k: data.get(v) for k, v in mapping.items()}
        return cls(**mapped_data)

