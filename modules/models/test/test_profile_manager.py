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

    def _setup(self):
        test_profile_dict_list = self._configuration_manager.test_profiles_dict_list

        for test_profile_dict in test_profile_dict_list:

            app_profiles = [TestApplicationProfile(**ap) for ap in test_profile_dict.get("ApplicationProfiles")]

            test_profile = TestProfile(
                TestType=test_profile_dict.get("TestType"),
                TestName=test_profile_dict.get("TestName"),
                Description=test_profile_dict.get("Description"),
                Version=str(test_profile_dict.get("Version")),  # cast to str if needed
                TestApplicationProfiles=app_profiles,
            )

            self._test_profiles.append(test_profile)

    def has_test_profile(self, test_name, test_version) -> bool:
        for test_profile in self._test_profiles:
            if test_profile.test_name == test_name and test_profile.test_version == test_version:
                return True

        return False

    def get_test_application_profile_names(self, test_name, test_version) -> list[str]:
        application_profile_names = []

        for test_profile in self._test_profiles:
            if test_profile.test_name == test_name and test_profile.test_version == test_version:
                for test_application_profile in test_profile.application_profiles:
                    application_profile_names.append(test_application_profile.application_profile_name)

        return application_profile_names

    def _validate_test_profiles(self):
        for test_profile in self._test_profiles:
            for test_application_profile in test_profile.application_profiles:
                if not self._application_manager.has_application_profile(test_application_profile.application_profile_name):
                    pass