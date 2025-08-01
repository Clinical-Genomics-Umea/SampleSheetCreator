import json
import re
from datetime import datetime
from logging import Logger

import yaml
from PySide6.QtCore import QSettings, QObject, Signal, Slot
from pathlib import Path

from modules.utils.utils import read_yaml_file, uuid


class ConfigurationManager(QObject):
    """Configuration Manager"""

    run_data_changed = Signal(object)
    users_changed = Signal()
    run_data_error = Signal(list)

    def __init__(self, logger: Logger):
        """Initialize the configuration manager."""
        super().__init__()

        self.qt_settings = QSettings("Region Västerbotten", "samplecheater")
        self._run_data_is_set = False

        self._logger = logger

        self.read_cycle_pattern = re.compile(r"^\d+(-\d+)*$")

        self._index_def_root = Path("config/indexes/data")
        self._application_def_root = Path("config/applications")
        self._method_def_root = Path("config/methods")

        self._run_settings_path = Path("config/run/run_settings.yaml")
        self._instrument_data_path = Path("config/run/instrument_data.yaml")
        self._samples_settings_path = Path("config/sample_settings.yaml")
        self._validation_settings_path = Path("config/validation/validation_settings.yaml")
        self._samplesheet_v1_template_path = Path("config/samplesheet_v1.yaml")

        self._index_schema_root = Path("json_schemas/index")

        self._instruments_flowcell_obj = read_yaml_file(self._instrument_data_path)

        self._run_settings = read_yaml_file(self._run_settings_path)
        self._run_view_widgets_config = self._run_settings["RunViewFields"]
        self._run_setup_widgets_config = self._run_settings["RunSetupWidgets"]
        self._run_data = self._run_settings["RunDataDefaults"]
        self._run_data_fields = self._run_settings["RunDataFields"]
        self._read_cycles_fields = self._run_settings["ReadCyclesFields"]

        self._instrument_data = read_yaml_file(self._instrument_data_path)

        print("instrument_data", self._instrument_data)


        self._samples_settings = read_yaml_file(self._samples_settings_path)

        self._samplesheet_v1_template = read_yaml_file(
            self._samplesheet_v1_template_path
        )

        self._paths = {
            "index_def_root": self._index_def_root,
            "application_def_root": self._application_def_root,
            "methods_def_root": self._method_def_root,
            "run_settings_path": self._run_settings_path,
            "instrument_flowcells_path": self._instrument_data_path,
            "samples_settings_path": self._samples_settings_path,
            "validation_settings_path": self._validation_settings_path,
            "samplesheet_v1_template_path": self._samplesheet_v1_template_path,
            "index_schema_root": self._index_schema_root,
        }

        self._application_configs = []
        self._set_application_configs()

        self._method_configs = []
        self._set_method_configs()
        #
        # self._users = self._samples_settings["Users"]
        #

    @property
    def instrument_data(self):
        return self._instrument_data

    def _set_application_configs(self):
        paths = self._application_def_root.glob("**/*.yaml")

        for path in paths:
            with path.open() as fp:
                app_config = yaml.safe_load(fp)

            self.application_configs.append(app_config)

    def _set_method_configs(self):
        paths = self._method_def_root.glob("**/*.yaml")

        for path in paths:
            with path.open() as fp:
                method_config = yaml.safe_load(fp)

            self.method_configs.append(method_config)


    @property
    def method_configs(self):
        return self._method_configs

    @property
    def application_configs(self):
        return self._application_configs

    @property
    def fastq_extract_tool(self):
        return self._run_settings["FastqExtractTool"]

    @property
    def index_kits_root(self):
        return self._index_def_root

    @property
    def index_schema_root(self):
        return self._index_schema_root

    @property
    def instrument_flowcells(self):
        return self._instruments_flowcell_obj

    @property
    def run_data_fields(self):
        return self._run_data_fields

    @property
    def read_cycles_fields(self):
        return self._read_cycles_fields

    @property
    def samplesheet_v1_template(self):
        return self._samplesheet_v1_template

    @property
    def required_sample_fields(self):
        return self._samples_settings["required_fields"]

    @property
    def run_lanes(self):
        return self._run_settings["Lanes"]

    @property
    def samplesheet_header_data(self):
        header = {
            "FileFormatVersion": self._run_data["SampleSheetVersion"],
            "InstrumentType": self._run_data["Instrument"],
            "RunName": self._run_data["RunName"],
            "RunDescription": self._run_data["RunDescription"],
            "Custom_Flowcell": self._run_data["Flowcell"],
            "Custom_UUID7": uuid(),
        }
        return header

    @property
    def samplesheet_read_cycles(self):
        """Return a dictionary with the Read1Cycles, Index1Cycles, Index2Cycles, Read2Cycles."""

        read_cycle_headers = [
            "Read1Cycles",
            "Index1Cycles",
            "Index2Cycles",
            "Read2Cycles",
        ]

        read_cycles = self._run_data["ReadCycles"].strip()

        reads = {}

        for header, rc in zip(read_cycle_headers, read_cycles.split("-")):
            reads[header] = rc

        return reads

    @property
    def i5_samplesheet_orientation(self):
        return self._run_data["I5SampleSheetOrientation"]

    @property
    def base_colors(self):
        return {
            "A": self._run_data["A"],
            "T": self._run_data["T"],
            "G": self._run_data["G"],
            "C": self._run_data["C"],
        }

    @property
    def instruments(self):
        return self._instruments_flowcell_obj.keys()

    # @property
    # def instrument_flowcells(self):
    #     return self._instruments_flowcell_obj

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
            crc_parts = custom_read_cycles.split("-")

            if len(rc_parts) != len(crc_parts):
                run_data_error_fields.append("CustomReadCycles")

            else:
                for i in range(len(rc_parts)):
                    if not int(rc_parts[i]) >= int(crc_parts[i]):
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
    def set_run_data(self, run_data: dict):
        """
        Set the run data configuration and validate it.

        If the data is invalid, do not update the configuration and
        instead emit the run_data_error signal.

        Otherwise, update the configuration and emit the
        run_setup_changed signal.
        """

        # Validate the run data
        if not self.validate_run_data(run_data):
            return

        # Update the configuration
        self._run_data = run_data

        # Update the instrument specific settings
        instrument = run_data["Instrument"]
        flowcell = run_data["Flowcell"]

        instrument_settings = self._instruments_flowcell_obj[instrument]
        for key, value in instrument_settings.items():
            if not isinstance(value, dict):
                run_data[key] = value

        fluorophores = self._instruments_flowcell_obj[instrument]["Fluorophores"]
        for key, value in fluorophores.items():
            if not isinstance(value, dict):
                run_data[key] = value

        # Update the flowcell specific settings
        flowcell_settings = instrument_settings["Flowcell"][flowcell]
        for key, value in flowcell_settings.items():
            if not isinstance(value, dict):
                run_data[key] = value

        if run_data["CustomReadCycles"]:
            run_data["ReadCycles"] = run_data["CustomReadCycles"]

        today = datetime.today()
        self._run_data["Date"] = today.strftime("%Y-%m-%d")

        self._run_data["UUID7"] = uuid()

        self._run_data_is_set = True

        # Emit the changed signal
        self.run_data_changed.emit(self._run_data)

    @property
    def run_data_is_set(self):
        return self._run_data_is_set

    @property
    def all_config_paths(self):
        return {k: v.absolute() for k, v in self._paths.items()}

    @property
    def application_settings_basepath(self) -> Path:
        return self._application_def_root

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

        if not self.qt_settings.contains("users"):
            return []

        json_string = str(self.qt_settings.value("users"))

        if json_string:
            return json.loads(json_string)  # Convert back to list
        else:
            return []
