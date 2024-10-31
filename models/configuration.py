import json

from PySide6.QtCore import QSettings, QObject
from pathlib import Path
from utils.utils import read_yaml_file


class ConfigurationManager(QObject):
    """Configuration Manager"""

    def __init__(self):
        super().__init__()

        self.qt_settings = QSettings("Region Västerbotten", "samplecheater")

        # paths
        self._indexes_settings_basepath = Path("config/indexes/indexes_json")
        self._application_profile_settings_basepath = Path(
            "config/application_profiles"
        )
        self._run_settings_path = Path("config/run/run_settings.yaml")
        self._samples_settings_path = Path("config/sample_settings.yaml")
        self._validation_settings_path = Path(
            "config/validation/validation_settings.yaml"
        )

        self._all_config_paths = {
            "indexes_settings_basepath": self._indexes_settings_basepath,
            "application_profile_settings_basepath": self._application_profile_settings_basepath,
            "run_settings_path": self._run_settings_path,
            "samples_settings_path": self._samples_settings_path,
            "validation_settings_path": self._validation_settings_path,
        }

    @property
    def all_config_paths(self):
        return {k: v.absolute() for k, v in self._all_config_paths.items()}

    @property
    def indexes_settings_basepath(self) -> Path:
        return self._indexes_settings_basepath

    @property
    def application_profile_settings_basepath(self) -> Path:
        return self._application_profile_settings_basepath

    @property
    def run_settings_path(self) -> Path:
        return self._run_settings_path

    @property
    def run_settings_dict(self) -> dict:
        return read_yaml_file(self._run_settings_path)

    @property
    def samples_settings_path(self) -> Path:
        return self._samples_settings_path

    @property
    def samples_settings_dict(self) -> dict:
        print(read_yaml_file(self._samples_settings_path))
        return read_yaml_file(self._samples_settings_path)

    @property
    def validation_settings_path(self) -> Path:
        return self._validation_settings_path

    @property
    def validation_settings_dict(self) -> dict:
        return read_yaml_file(self._validation_settings_path)

    @property
    def users(self):
        return self._load_users()

    def add_user(self, user):

        current_users = self._load_users()
        if user not in current_users:
            current_users.append(user)
            self._save_users(current_users)

    def remove_user(self, user):

        current_users = self._load_users()
        current_users.remove(user)
        self._save_users(current_users)

    def _save_users(self, users: list):
        json_string = json.dumps(users)  # Convert list to JSON string
        self.qt_settings.setValue("users", json_string)

    # Retrieve a list from QSettings
    def _load_users(self):
        json_string = self.qt_settings.value("users")

        if json_string:
            return json.loads(json_string)  # Convert back to list
        else:
            return []
