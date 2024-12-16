from pathlib import Path

from models.configuration.configuration import ConfigurationManager
from utils.utils import read_yaml_file


class ApplicationManager:

    def __init__(self, cfg_mgr: ConfigurationManager) -> None:

        app_files = [f for f in cfg_mgr.application_settings_basepath.glob("**/*.yaml")]

        self._appgroup_to_appnames = {}
        self._appname_to_appobj = {}
        self._app_to_appnames = {}
        self._appname_to_app = {}
        self._app_to_appgroup = {}

        for file in app_files:
            if not file.is_file():
                continue

            appobj = read_yaml_file(file)
            if not appobj:
                continue

            appname = appobj.get("ApplicationName")
            appgroup = appobj.get("ApplicationGroupName")
            app = appobj.get("Application")

            if not all([appname, appgroup, app]):
                continue

            if appname not in self._appname_to_appobj:
                self._appname_to_appobj[appname] = appobj

            if app not in self._app_to_appgroup:
                self._app_to_appgroup[app] = appgroup

            if appgroup not in self._appgroup_to_appnames:
                self._appgroup_to_appnames[appgroup] = []

            if appname not in self._appgroup_to_appnames[appgroup]:
                self._appgroup_to_appnames[appgroup].append(appname)

            if appname not in self._appname_to_app:
                self._appname_to_app[appname] = app

    def appname_to_app(self, appname):
        return self._appname_to_app[appname]

    def app_to_appgroup(self, app):
        return self._app_to_appgroup[app]

    @property
    def app_hierarchy(self):
        _appgroup_to_appname_to_appobj = {}
        for appgroup in self._appgroup_to_appnames:
            if appgroup not in _appgroup_to_appname_to_appobj:
                _appgroup_to_appname_to_appobj[appgroup] = {}

            for appname in self._appgroup_to_appnames[appgroup]:
                _appgroup_to_appname_to_appobj[appgroup][appname] = (
                    self._appname_to_appobj[appname]
                )

        print(_appgroup_to_appname_to_appobj)

        return _appgroup_to_appname_to_appobj

    def appobj_by_appname(self, appname):
        return self._appname_to_appobj[appname]

    def app_data_populate(self, df, appname):
        appobj = self._appname_to_appobj[appname]

        for key, value in appobj["Data"].items():
            df[key] = value

        df = self._subset_rename_cols(df, appname)

        if appobj["Application"] == "BCLConvert":
            df = df.explode("Lane", ignore_index=True)

        return df

    def _subset_rename_cols(self, df, appname):
        appobj = self.appobj_by_appname(appname)

        df = df[appobj["DataFields"]]
        if "Translate" in appobj:
            df = df.rename(columns=appobj["Translate"])

        return df
