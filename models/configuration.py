import json

from PySide6.QtCore import QSettings, QObject, Signal, Slot
from pathlib import Path

from utils.utils import read_yaml_file


class ConfigurationManager(QObject):
    """Configuration Manager"""

    run_setup_changed = Signal(object)
    users_changed = Signal()
    run_data_error = Signal(list)

    def __init__(self):
        """Initialize the configuration manager."""

        super().__init__()

        self.qt_settings = QSettings("Region Västerbotten", "samplecheater")

        # paths
        self._config_paths = {
            "indexes_settings_basepath": Path("config/indexes/indexes_json"),
            "application_profile_settings_basepath": Path(
                "config/application_profiles"
            ),
            "run_settings_path": Path("config/run/run_settings.yaml"),
            "instrument_flowcells_path": Path("config/run/instrument_flowcells.yaml"),
            "samples_settings_path": Path("config/sample_settings.yaml"),
            "validation_settings_path": Path(
                "config/validation/validation_settings.yaml"
            ),
        }

        self._instruments_flowcell_obj = read_yaml_file(
            self._config_paths["instrument_flowcells_path"]
        )
        self._run_settings = read_yaml_file(self._config_paths["run_settings_path"])
        self._run_view_widgets_config = self._run_settings["RunViewWidgets"]
        self._run_setup_widgets_config = self._run_settings["RunSetupWidgets"]
        self._run_data = self._run_settings["RunDataDefaults"]

        self._samples_settings = read_yaml_file(
            self._config_paths["samples_settings_path"]
        )

        # self._setup_run()

    @property
    def instruments(self):
        return self._instruments_flowcell_obj.keys()

    @property
    def instrument_flowcells(self):
        return self._instruments_flowcell_obj

    @property
    def run_setup_widgets_config(self):
        return self._run_setup_widgets_config

    @property
    def run_view_widgets_config(self):
        return self._run_view_widgets_config

    @property
    def run_data(self):
        return self._run_data

    def validate_run_data(self, data):
        run_data_error_fields = []

        custom_read_cycles = data["CustomReadCycles"].strip()
        if custom_read_cycles:
            read_cycles = data["ReadCycles"].strip()

            rc_parts = read_cycles.split("-")
            crc_parts = custom_read_cycles.split("_")

            if len(rc_parts) != len(crc_parts):
                run_data_error_fields.append("CustomReadCycles")

            else:
                for i in range(len(rc_parts)):
                    if int(rc_parts[i]) < int(crc_parts[i]):
                        run_data_error_fields.append("CustomReadCycles")

        if not data["RunName"].strip():
            run_data_error_fields.append("RunName")

        if not data["RunDescription"]:
            run_data_error_fields.append("RunDescription")

        if run_data_error_fields:
            self.run_data_error.emit(run_data_error_fields)
            return False

        return True

    @Slot(dict)
    def set_run_data(self, data: dict):

        self._run_data = data

        if not self.validate_run_data(data):
            return

        instrument = data["Instrument"]
        flowcell = data["Flowcell"]

        for key, value in self._instruments_flowcell_obj[instrument].items():
            if isinstance(value, str):
                self._run_data[key] = value

            elif isinstance(value, bool):
                self._run_data[key] = str(value)

            if key == "Fluorophores":
                for base, color in self._instruments_flowcell_obj[instrument][
                    "Fluorophores"
                ].items():
                    self._run_data[base] = str(color)

        for key, value in self._instruments_flowcell_obj[instrument]["Flowcell"][
            flowcell
        ].items():
            if isinstance(value, list):
                list_str = ", ".join(value)
                self._run_data[key] = f"[{list_str}]"

            elif not isinstance(value, dict):
                self._run_data[key] = value

        print(self._run_data)

        self.run_setup_changed.emit(self._run_data)

    @property
    def all_config_paths(self):
        return {k: v.absolute() for k, v in self._config_paths.items()}

    @property
    def application_profile_settings_basepath(self) -> Path:
        return self._config_paths["application_profile_settings_basepath"]

    @property
    def samples_settings(self) -> dict:
        return self._samples_settings

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
        self.users_changed.emit()

    # Retrieve a list from QSettings
    def _load_users(self):
        json_string = str(self.qt_settings.value("users"))

        if json_string:
            return json.loads(json_string)  # Convert back to list
        else:
            return []
