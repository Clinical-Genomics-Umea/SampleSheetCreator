import re

from utils.utils import int_str_to_int_list, json_to_obj

import json

import pandas as pd
from pprint import pprint


# def to_json(sample_obj):
#     return json.dumps(sample_obj)


class DataSetManager:
    def __init__(self, sample_model, cfg_mgr, app_mgr):

        self.sample_model = sample_model
        self.cfg_mgr = cfg_mgr
        self.app_mgr = app_mgr
        self.read_cycles_header = ("r1", "i1", "i2", "r2")
        self.read_cycles = []
        self._samplesheet_obj = None

    def set_read_cycles(self):
        self.read_cycles = []
        _read_cycles = self.cfg_mgr.read_cycles

        if _read_cycles:
            _read_cycles.strip()
            for item in _read_cycles.split("-"):
                self.read_cycles.append(int(item.strip()))

    @staticmethod
    def _convert_override_pattern(input_str, target_sum):
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
            output_items.append(
                self._convert_override_pattern(item, self.read_cycles[i])
            )

        return ";".join(output_items)

    def index_maxlens(self):
        dataframe = self.sample_model.to_dataframe()

        if dataframe.empty:
            return None

        indexi7_maxlen = int(dataframe["IndexI7"].str.len().max())
        indexi5_maxlen = int(dataframe["IndexI5"].str.len().max())

        return {"IndexI7_maxlen": indexi7_maxlen, "IndexI5_maxlen": indexi5_maxlen}

    def validation_view_obj(self):

        sample_dfs_obj = {
            "no_explode": self.base_sample_dataframe(),
            "apn_explode": self._appname_explode(),
            "lane_explode": self.sample_dataframe_lane_explode(),
        }

        return sample_dfs_obj

    def json_data(self):
        s_obj = self.samplesheet_obj_data()
        return json.dumps(s_obj)

    def samplesheet_obj_data(self):
        """Return the samplesheet object with the data dict converted to records."""
        samplesheet_obj = self._samplesheet_obj

        for appobj in samplesheet_obj["Applications"]:
            appobj["Data"] = appobj["Data"].to_dict(orient="records")

        samplesheet_obj["I5SampleSheetOrientation"] = self.cfg_mgr.run_data[
            "I5SampleSheetOrientation"
        ]

        return samplesheet_obj

    def samplesheet_v1(self):
        data_df = self.base_sample_dataframe().copy()
        run_data = self.cfg_mgr.run_data
        read_cycles = self.cfg_mgr.samplesheet_read_cycles()
        template = self.cfg_mgr.samplesheet_v1_template

        header = {}
        for k, v in template["Header"].items():

            if v in run_data:
                rd_val = run_data[v]
                header[k] = rd_val
            else:
                header[k] = v

        reads = []
        for tv in template["Reads"]:
            v = read_cycles[tv]
            reads.append(v)

        if self.cfg_mgr.run_data["I5SampleSheetOrientation"] == "rc":
            data_df["IndexI5"] = data_df["IndexI5RC"]

        data_df = data_df[template["Data"]]
        settings = self._bclconvert_adapters(data_df)
        data = data_df.to_csv(index=False).splitlines()

        output = ["[Header]"]
        output.extend([f"{k},{v}" for k, v in header.items()])

        output.append("")
        output.append("[Settings]")
        output.extend([f"{k},{v}" for k, v in settings.items()])

        output.append("")
        output.append("[Reads]")
        output.extend(reads)

        output.append("")
        output.append("[Data]")
        output.extend(data)

        return "\n".join(output)

    def _bclconvert_adapters(self, data_df):
        application_names = data_df["ApplicationName"].explode().tolist()

        adapters_read1 = set()
        adapters_read2 = set()

        for name in application_names:
            app_object = self.app_mgr.appobj_by_appname(name)
            if app_object.get("Application") == "BCLConvert":
                adapters_read1.update(
                    app_object.get("Settings", {})
                    .get("AdapterRead1", "")
                    .strip()
                    .split("+")
                )
                adapters_read2.update(
                    app_object.get("Settings", {})
                    .get("AdapterRead2", "")
                    .strip()
                    .split("+")
                )

        adapters = {
            "Adapter": "+".join(adapters_read1),
            "AdapterRead2": "+".join(adapters_read2),
        }

        return adapters

    def samplesheet_v2(self):
        sample_obj = self._samplesheet_obj

        header = ["[Header]"]
        for k, v in sample_obj["Header"].items():
            header.append(f"{k},{v}")

        reads = ["[Reads]"]
        for k, v in sample_obj["Reads"].items():
            reads.append(f"{k},{v}")

        applications = []
        for app_obj in sample_obj["Applications"]:

            app = app_obj["Application"]

            if app_obj["ApplicationGroupName"] == "Dragen":
                applications.append(f"[{app}_Settings]")

                for k, v in app_obj["Settings"].items():
                    applications.append(f"{k},{v}")

                applications.append("")

                applications.append(f"[{app}_Data]")

                data_df = pd.DataFrame.from_dict(app_obj["Data"])

                if "IndexI5" in data_df.columns:
                    if self.cfg_mgr.run_data["I5SampleSheetOrientation"] == "rc":
                        data_df["IndexI5"] = data_df["IndexI5RC"]

                    del data_df["IndexI5RC"]

                csv_obj = data_df.to_csv(index=False).splitlines()
                applications.extend(csv_obj)
                applications.append("")

        output = header
        output.append("")
        output.extend(reads)
        output.append("")
        output.extend(applications)

        return "\n".join(output)

    def set_samplesheet_obj(self):

        obj = {
            "Header": self.cfg_mgr.samplesheet_header_data,
            "Reads": self.cfg_mgr.samplesheet_read_cycles,
            "Applications": self.app_settings_data(),
        }

        self._samplesheet_obj = obj

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
                        "ApplicationGroupName": self.app_mgr.app_to_appgroup(app),
                        "Application": app,
                        "Data": merged_df,
                        "Settings": settings[0],
                    }
                )

        return _app_settings_data

    def base_sample_dataframe(self):
        self.set_read_cycles()
        dataframe = self.sample_model.to_dataframe()
        dataframe["OverrideCycles"] = dataframe["OverrideCyclesPattern"].apply(
            self._override_cycles
        )
        dataframe_corr = self._dataframe_strs_to_obj(dataframe)
        return dataframe_corr

    def sample_dataframe_lane_explode(self):
        base_df = self.base_sample_dataframe()
        return base_df.explode("Lane", ignore_index=True)

    def _appname_explode(self):
        base_df = self.base_sample_dataframe()
        return base_df.explode("ApplicationName", ignore_index=True)

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
