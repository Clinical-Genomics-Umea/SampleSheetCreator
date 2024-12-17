import pandas as pd
from PySide6.QtCore import Signal, QObject, Slot

from models.application.application import ApplicationManager
from models.dataset.dataset import DataSetManager


class DataCompatibilityChecker(QObject):

    app_allowed = Signal(object)
    app_not_allowed = Signal(object)

    dropped_allowed = Signal(object)
    dropped_not_allowed = Signal(object)

    def __init__(self, dataset_mgr: DataSetManager, app_mgr: ApplicationManager):
        super().__init__()
        self.dataset_mgr = dataset_mgr
        self.app_mgr = app_mgr

    @Slot(object)
    def dropped_checker(self, dropped_data):
        df = pd.DataFrame(dropped_data["decoded_data"])
        index_i7_max_len = df["IndexI7"].str.len().max()
        index_i5_max_len = df["IndexI5"].str.len().max()

        read_cycles = self.dataset_mgr.read_cycle_data()

        print(read_cycles)

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
        else:
            self.dropped_allowed.emit(dropped_data)

    def app_checker(self, appobj: dict) -> None:
        appname = appobj["ApplicationName"]

        df = self.dataset_mgr.sample_dataframe_appname_explode()
        unique_existing_appnames = df["ApplicationName"].unique()

        new_app_obj = self.app_mgr.appobj_by_appname(appname)
        new_settings = new_app_obj["Settings"]
        new_group = new_app_obj["ApplicationGroupName"]

        for existing_appname in unique_existing_appnames:
            existing_app_obj = self.app_mgr.appobj_by_appname(existing_appname)
            existing_settings = existing_app_obj["Settings"]
            existing_group = existing_app_obj["ApplicationGroupName"]

            print(existing_settings)
            print(new_settings)

            if existing_group == new_group and existing_settings != new_settings:
                print("app not allowed")
                self.app_not_allowed.emit(appobj)
                return

        print("app allowed")
        self.app_allowed.emit(appobj)
