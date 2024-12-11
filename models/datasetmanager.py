import json
import re
from pprint import pprint

import pandas as pd

from utils.utils import int_str_to_int_list, json_to_obj


class DataSetManager:
    def __init__(self, sample_model, cfg_mgr, app_mgr):

        self.sample_model = sample_model
        self.cfg_mgr = cfg_mgr
        self.app_mgr = app_mgr
        self.read_cycles_header = ("r1", "i1", "i2", "r2")
        self.read_cycles = []

    def set_read_cycles(self):
        self.read_cycles = []
        _read_cycles = self.cfg_mgr.read_cycles

        if _read_cycles:
            _read_cycles.strip()
            for item in _read_cycles.split("-"):
                self.read_cycles.append(int(item.strip()))

    def validate(self):
        pass
        # print(self.cfg_mgr)
        # print(self.cfg_mgr.read_cycles)
        # self.set_read_cycles()
        # self.applications()

    def _fill_placeholder(self, input_str, target_sum):
        parts = re.findall(r"([A-Z])(\d+|\{(?:r1|i1|i2|r2)\})", input_str)

        non_placeholders = [
            (key, int(num)) for key, num in parts if not num.startswith("{")
        ]
        placeholders = [
            (key, placeholder)
            for key, placeholder in parts
            if placeholder.startswith("{")
        ]

        if not len(placeholders) == 1:
            return "error"

        placeholder = placeholders[0][1]

        current_sum = sum(non_placeholders)
        remaining_value = target_sum - current_sum

        return input_str.replace(placeholder, str(remaining_value))

    def _override_cycles(self, item):
        item_list = item.strip().split("-")
        output_items = []

        if not self.read_cycles:
            return item

        for i, item in enumerate(item_list):
            output_items.append(self._fill_placeholder(item, self.read_cycles[i]))

        return ";".join(output_items)

    def index_maxlens(self):
        dataframe = self.sample_model.to_dataframe()

        if dataframe.empty:
            return None

        indexi7_maxlen = int(dataframe["IndexI7"].str.len().max())
        indexi5_maxlen = int(dataframe["IndexI5"].str.len().max())

        return {"IndexI7_maxlen": indexi7_maxlen, "IndexI5_maxlen": indexi5_maxlen}

    def base_sample_dataframe(self):
        self.set_read_cycles()
        dataframe = self.sample_model.to_dataframe()
        dataframe["OverrideCycles"] = dataframe["OverrideCyclesPattern"].apply(
            self._override_cycles
        )
        dataframe_corr = self._dataframe_strs_to_obj(dataframe)
        return dataframe_corr

    def validation_view_obj(self):

        sample_dfs_obj = {
            "no_explode": self.base_sample_dataframe(),
            "apn_explode": self._appname_explode(),
            "lane_explode": self.base_sample_dataframe_lane_explode(),
        }

        return sample_dfs_obj

    def app_settings_data(self):

        _app_settings_data = []

        data_df = self._appname_explode()
        data_df["OverrideCycles"] = data_df["OverrideCyclesPattern"].apply(
            self._override_cycles
        )

        unique_appnames = data_df["ApplicationName"].unique()

        used_app_to_appnames = {}
        for appname in unique_appnames:
            app = self.app_mgr.appname_to_app(appname)
            if app not in used_app_to_appnames:
                used_app_to_appnames[app] = []
            used_app_to_appnames[app].append(appname)

        for app in used_app_to_appnames:
            dfs = []
            settings = []
            for appname in used_app_to_appnames[app]:
                appname_df = data_df[data_df["ApplicationName"] == appname].copy()
                dfs.append(self.app_mgr.app_data_populate(appname_df, appname))

                appobj = self.app_mgr.appobj_by_appname(appname)
                settings.append(appobj["Settings"])

            merged_df = pd.concat(dfs)
            are_identical = all(d == settings[0] for d in settings)

            if are_identical:
                _app_settings_data.append(
                    {
                        "Application": app,
                        "Data": merged_df.to_dict(orient="records"),
                        "Settings": settings[0],
                    }
                )

        return _app_settings_data

    def samplesheet_obj(self):

        obj = {
            "Header": self.cfg_mgr.samplesheet_header_data,
            "Reads": self.cfg_mgr.samplesheet_read_cycles,
            "Applications": self.app_settings_data(),
        }

        return obj

    def json_data(self):
        app_obj = {
            "Header": self.cfg_mgr.samplesheet_header_data,
            "Reads": self.cfg_mgr.samplesheet_read_cycles,
        }

        data_df = self._appname_explode()
        data_df["OverrideCycles"] = data_df["OverrideCyclesPattern"].apply(
            self._override_cycles
        )

        unique_app_names = data_df["ApplicationName"].unique()

        for app in unique_app_names:
            app_df = data_df[data_df["ApplicationName"] == app].copy()
            app_profile = self.app_mgr.appobj_by_appname(app)

            for field, value in app_profile["Data"].items():
                if field not in app_df.columns:
                    app_df[field] = value

            if app_profile["Application"] == "BCLConvert":
                app_df = app_df.explode("Lane", ignore_index=True)

            app_df = app_df[app_profile["DataFields"]]

            if "Translate" in app_profile:
                app_df = app_df.rename(columns=app_profile["Translate"])

            if "applications" not in app_obj:
                app_obj["applications"] = {}

            app_obj["Applications"][app] = {
                "Application": app_profile["Application"],
                "Settings": app_profile["Settings"],
                "Data": app_df.to_dict(orient="records"),
            }

        return app_obj

    def samplesheet_data(self):
        pass

    def base_sample_dataframe_lane_explode(self):
        base_df = self.base_sample_dataframe()
        return base_df.explode("Lane", ignore_index=True)

    def _appname_explode(self):
        base_df = self.base_sample_dataframe()
        return base_df.explode("ApplicationName", ignore_index=True)

    # def sample_data_exploded(self):
    #     dataframe = self.base_sample_dataframe()
    #     return dataframe

    @staticmethod
    def _dataframe_strs_to_obj(dataframe):
        dataframe["Lane"] = dataframe["Lane"].apply(int_str_to_int_list)
        dataframe["ApplicationName"] = dataframe["ApplicationName"].apply(json_to_obj)

        return dataframe

    @staticmethod
    def _explode_apn_lane(dataframe):

        _exploded_name_df = dataframe.explode("ApplicationName", ignore_index=True)

        _exploded_name_lane_df = _exploded_name_df.explode("Lane", ignore_index=True)

        return _exploded_name_lane_df
