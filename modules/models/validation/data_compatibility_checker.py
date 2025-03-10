import pandas as pd
from PySide6.QtCore import Signal, QObject, Slot

from modules.models.application.application_manager import ApplicationManager
from modules.models.dataset.dataset_manager import DataSetManager
from modules.utils.utils import validate_override_pattern, preset_override_cycles


class DataCompatibilityChecker(QObject):

    app_allowed = Signal(object)
    app_not_allowed = Signal(object)

    dropped_allowed = Signal(object)
    dropped_not_allowed = Signal(object)
    dropped_not_allowed_flash = Signal()

    override_pattern_invalid = Signal(list)
    override_pattern_valid = Signal(object)

    def __init__(self, dataset_mgr: DataSetManager, app_mgr: ApplicationManager):
        super().__init__()
        self.dataset_mgr = dataset_mgr
        self.app_mgr = app_mgr

    @Slot(object)
    def dropped_checker(self, dropped_data):
        df = pd.DataFrame(dropped_data["decoded_data"])

        print(df.to_string())

        index_i7_max_len = None
        index_i5_max_len = None

        if "IndexI7" in df.columns:
            index_i7_max_len = df["IndexI7"].str.len().max()

        if "IndexI5" in df.columns:
            index_i5_max_len = df["IndexI5"].str.len().max()

        read_cycles = self.dataset_mgr.read_cycles_dict()

        error_list = []

        if (
            read_cycles["Index1Cycles"]
            and not index_i7_max_len <= read_cycles["Index1Cycles"]
        ):
            error_list.append("max IndexI7 length > run setting")

        if (
            read_cycles["Index2Cycles"]
            and not index_i5_max_len <= read_cycles["Index2Cycles"]
        ):
            error_list.append("max IndexI5 length > run setting")

        if error_list:
            self.dropped_not_allowed.emit(", ".join(error_list))
            self.dropped_not_allowed_flash.emit()
        else:
            self.dropped_allowed.emit(dropped_data)

    def app_checker(self, appobj: dict) -> None:
        new_appname = appobj["ApplicationProfile"]

        df = self.dataset_mgr.sample_dataframe_appname_explode()
        if df.empty:
            self.app_allowed.emit(appobj)
            return

        unique_existing_appnames = df["ApplicationProfile"].unique()

        new_app_obj = self.app_mgr.app_profile_to_app_obj(new_appname)
        new_settings = new_app_obj["Settings"]
        new_app = new_app_obj["Application"]

        for existing_appname in unique_existing_appnames:
            if not existing_appname:
                continue

            existing_app_obj = self.app_mgr.app_profile_to_app_obj(existing_appname)
            existing_settings = existing_app_obj["Settings"]
            existing_app = existing_app_obj["Application"]
            existing_appname = existing_app_obj["ApplicationProfile"]

            if existing_app == new_app and existing_settings != new_settings:
                msg = f"{new_appname} not allowed with {existing_appname} settings"
                self.app_not_allowed.emit(msg)
                return

            if existing_appname == new_appname:
                msg = f"{new_appname} already exists for one or more selected samples"
                self.app_not_allowed.emit(msg)
                return

        self.app_allowed.emit(appobj)

    #
    # def run_checker(self, rundata_obj: dict):
    #     df = self.dataset_mgr.base_sample_dataframe()
    #
    #     r7, i7, i5, r5 = map(int, rundata_obj["ReadCycles"].split("-"))
    #
    #     index_i7_max_len = df["IndexI7"].str.len().max()
    #     index_i5_max_len = df["IndexI5"].str.len().max()
    #
    #     read_cycles = self.dataset_mgr.read_cycles_dict()

    def override_cycles_checker(self, override_pattern: dict):

        invalid_override_names = []

        for cycles_name, pattern in override_pattern.items():
            if not validate_override_pattern(cycles_name, pattern):
                invalid_override_names.append(cycles_name)

        if invalid_override_names:
            self.override_pattern_invalid.emit(invalid_override_names)
            return

        run_read_cycles = self.dataset_mgr.read_cycles_dict

        for cycles_name, pattern in override_pattern.items():
            preset_len = preset_override_cycles(cycles_name, pattern)

            if preset_len > run_read_cycles[cycles_name]:
                invalid_override_names.append(cycles_name)

        if invalid_override_names:
            self.override_pattern_invalid.emit(invalid_override_names)
            return

        self.override_pattern_valid.emit(override_pattern)

        return
