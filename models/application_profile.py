from pathlib import Path

from models.configuration import ConfigurationManager
from utils.utils import read_yaml_file


class ApplicationProfileManager:

    def __init__(self, cfg_mgr: ConfigurationManager) -> None:
        # setup profile files

        application_files = [
            f for f in cfg_mgr.application_profile_settings_basepath.glob("**/*.yaml")
        ]
        self.application_profiles = {}

        for file in application_files:
            if not file.is_file():
                continue

            profile_data = read_yaml_file(file)
            if not profile_data:
                continue

            group = file.parent.name
            if not group:
                continue

            print(profile_data)

            profile_name = profile_data["ApplicationProfileName"]
            if not profile_name:
                continue

            if group not in self.application_profiles:
                self.application_profiles[group] = {}

            self.application_profiles[group][profile_name] = profile_data

    def send_data(self):
        button = self.sender()
        data = button.property("data")
        self.profile_data.emit(data)

    def get_application_profiles(self):
        return self.application_profiles
