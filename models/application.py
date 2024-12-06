from pathlib import Path

from models.configuration import ConfigurationManager
from utils.utils import read_yaml_file


class ApplicationManager:

    def __init__(self, cfg_mgr: ConfigurationManager) -> None:
        # setup profile files

        application_files = [
            f for f in cfg_mgr.application_settings_basepath.glob("**/*.yaml")
        ]

        self._application_group_name = {}
        self._application_name = {}

        for file in application_files:
            if not file.is_file():
                continue

            profile_data = read_yaml_file(file)
            if not profile_data:
                continue

            profile_name = profile_data["ApplicationName"]

            if not profile_name:
                continue

            group_name = profile_data["ApplicationGroupName"]

            if not group_name:
                continue

            if profile_name not in self._application_name:
                self._application_name[profile_name] = profile_data

            if group_name not in self._application_group_name:
                self._application_group_name[group_name] = {}
                self._application_group_name[group_name][profile_name] = profile_data
            else:
                self._application_group_name[group_name][profile_name] = profile_data

    @property
    def application_by_group_by_name(self):
        return self._application_group_name

    def application_by_name(self, name):
        return self._application_name[name]
