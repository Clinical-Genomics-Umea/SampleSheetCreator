from dataclasses import dataclass
from logging import Logger
from typing import List

from PySide6.QtCore import QObject

from modules.models.application.application_manager import ApplicationManager
from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.test.test_application_profile import TestApplicationProfile
from modules.models.test.test_profile import TestProfile


class TestProfileManager(QObject):
    def __init__(self, configuration_manager: ConfigurationManager, application_manager: ApplicationManager, logger: Logger):
        super().__init__()

        self._application_manager = application_manager
        self._configuration_manager = configuration_manager
        self._logger = logger

        self._test_profiles = []

        self._setup()

    def latest_test_profile_id_by_worksheet_test(self, worksheet_test: str) -> str | None:

        # If no exact match, find the highest version with same test name and major version
        try:
            # Extract test name and version from test_profile_id (format: "test_name_version")
            ws_test_name, ws_version_str = worksheet_test.rsplit('_', 1)
            target_major = int(ws_version_str.split('.')[0]) if '.' in ws_version_str else int(ws_version_str)

            matching_profiles = []
            for test_profile in self._test_profiles:
                if test_profile.test_name == ws_test_name:
                    profile_major = test_profile.version.major
                    if profile_major == target_major:
                        matching_profiles.append(test_profile)

            if matching_profiles:
                # Return the test_profile with the highest version
                test_profile = max(matching_profiles, key=lambda p: p.version)
                return test_profile.id

        except (ValueError, AttributeError):
            pass

        return None

    def application_profile_ids_by_test_profile_id(self, test_profile_id: str) -> list[str] | None:
        """
        Get the list of application profile IDs associated with a test profile ID.

        Args:
            test_profile_id: The ID of the test profile in format "test_name_version"

        Returns:
            List of application profile IDs if found, None otherwise
        """
        try:
            # First try exact match
            for test_profile in self._test_profiles:
                if test_profile.id == test_profile_id:
                    return test_profile.application_profile_ids

        except (ValueError, AttributeError):
            self._logger.warning(f"Invalid test profile ID format: {test_profile_id}")

        return None



    def _setup(self):
        test_profile_dict_list = self._configuration_manager.test_profiles_dict_list

        for test_profile_dict in test_profile_dict_list:

            test_application_profiles = [TestApplicationProfile(**ap_profile_dict)
                                         for ap_profile_dict in test_profile_dict.get("TestApplicationProfiles")]

            app_profile_ids = [ap_profile.id for ap_profile in test_profile_dict.get("TestApplicationProfiles")]

            test_profile = TestProfile(
                test_type=test_profile_dict.get("TestType"),
                test_name=test_profile_dict.get("TestName"),
                description=test_profile_dict.get("Description"),
                _v=str(test_profile_dict.get("Version")),  # cast to str if needed
                test_application_profiles=test_application_profiles,
                application_profile_ids=app_profile_ids,
            )

            self._test_profiles.append(test_profile)

    def has_test_profile(self, test_name, test_main_version) -> bool:
        for test_profile in self._test_profiles:
            test_profile_main_version = test_profile.version.split('.')[0]
            if test_profile.test_name == test_name and test_profile_main_version == test_main_version:
                return True

        return False

    def get_test_application_profiles(self, test_name, test_version) -> list[TestApplicationProfile] | None:
        for test_profile in self._test_profiles:
            if test_profile.test_name == test_name and test_profile.test_version == test_version:
                return test_profile.application_profiles

        return None

    # def _validate_test_profiles(self):
    #     for test_profile in self._test_profiles:
    #         for test_application_profile in test_profile.application_profiles:
    #             if not self._application_manager.has_application_profile(test_application_profile.application_profile_name):
    #                 pass