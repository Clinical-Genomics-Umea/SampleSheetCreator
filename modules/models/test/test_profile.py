from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from packaging.version import Version, parse

from modules.models.test.test_application_profile import TestApplicationProfile


@dataclass
class TestProfile:
    test_type: str
    test_name: str
    description: str
    _v: str = ""
    test_application_profiles: List[TestApplicationProfile] = field(default_factory=list)
    application_profile_ids: List[str] = field(default_factory=list)
    version: Version = field(init=False)
    id: str = field(init=False)

    def __post_init__(self):
        # No need to recreate TestApplicationProfile objects if they're already instantiated
        if self.test_application_profiles and isinstance(self.test_application_profiles[0], TestApplicationProfile):
            self.application_profile_ids = [ap_profile.id for ap_profile in self.test_application_profiles]
        else:
            self.test_application_profiles = [TestApplicationProfile(**ap_profile)
                                            for ap_profile in self.test_application_profiles]
            self.application_profile_ids = [ap_profile.id for ap_profile in self.test_application_profiles]
            
        self.id = f"{self.test_name}_{self._v}"
        self.version = parse(str(self._v))

    def has_application_profile_id(self, application_profile_id: str) -> bool:
        if application_profile_id in self.application_profile_ids:
            return True
        return False