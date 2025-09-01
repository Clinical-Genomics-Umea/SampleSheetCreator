from dataclasses import dataclass
from typing import List

from modules.models.test.test_application_profile import TestApplicationProfile


@dataclass
class TestProfile:
    TestType: str
    TestName: str
    Description: str
    Version: str
    TestApplicationProfiles: List[TestApplicationProfile]

    def has_application_profile(self, application_profile_name: str, application_profile_version: str) -> bool:
        """Check if this test profile has an application profile with the specified name and version.

        Args:
            application_profile_name: Name of the application profile to check for
            application_profile_version: Version of the application profile to check for

        Returns:
            bool: True if a matching application profile is found, False otherwise
        """
        for test_app_profile in self.TestApplicationProfiles:
            if (test_app_profile.ApplicationProfileName == application_profile_name and
                    test_app_profile.ApplicationProfileVersion == application_profile_version):
                return True
        return False