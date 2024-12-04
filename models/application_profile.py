from pathlib import Path

from models.configuration import ConfigurationManager
from utils.utils import read_yaml_file


class ApplicationProfileManager:

    def __init__(self, cfg_mgr: ConfigurationManager) -> None:
        # setup profile files

        application_files = [
            f for f in cfg_mgr.application_profile_settings_basepath.glob("**/*.yaml")
        ]

        self._application_group_name_profile = {}
        self._application_name_profile = {}

        for file in application_files:
            if not file.is_file():
                continue

            profile_data = read_yaml_file(file)
            if not profile_data:
                continue

            profile_name = profile_data["ApplicationProfileName"]

            if not profile_name:
                continue

            group_name = profile_data["ApplicationGroupName"]

            if not group_name:
                continue

            if profile_name not in self._application_name_profile:
                self._application_name_profile[profile_name] = profile_data

            if group_name not in self._application_group_name_profile:
                self._application_group_name_profile[group_name] = {}
                self._application_group_name_profile[group_name][
                    profile_name
                ] = profile_data
            else:
                self._application_group_name_profile[group_name][
                    profile_name
                ] = profile_data

    @property
    def application_group_name_profiles(self):
        return self._application_group_name_profile

    def application_profile_by_name(self, name):
        return self._application_name_profile[name]
