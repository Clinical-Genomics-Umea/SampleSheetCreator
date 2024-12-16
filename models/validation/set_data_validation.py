from PySide6.QtCore import Signal, QObject

from models.application.application import ApplicationManager
from models.dataset.dataset import DataSetManager


class AddDataValidator(QObject):

    app_allowed = Signal(dict)
    app_not_allowed = Signal(dict)

    def __init__(self, dataset_mgr: DataSetManager, app_mgr: ApplicationManager):
        super().__init__()
        self.dataset_mgr = dataset_mgr
        self.app_mgr = app_mgr

    def add_app_validator(self, appobj: dict) -> None:
        print("add_app_validator")

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
