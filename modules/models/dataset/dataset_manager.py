import re
from logging import Logger

from modules.models.application.application_manager import ApplicationManager
from modules.models.rundata.rundata_model import RunDataModel
from modules.models.sample.sample_model import SampleModel
from modules.utils.utils import int_str_to_int_list, json_to_obj, uuid
import json
import pandas as pd


class DataSetManager:
    def __init__(self, sample_model: SampleModel,
                 application_manager: ApplicationManager,
                 rundata_model: RunDataModel,
                 logger: Logger):

        self._logger = logger

        self._rundata_model = rundata_model
        self._sample_model = sample_model
        self._application_manager = application_manager
        self._read_cycles_header = ("r1", "i1", "i2", "r2")
        self._data_obj = None

    @staticmethod
    def _convert_override_pattern(input_str, target_sum):

        parts = re.findall(r"([A-Z])(\d+|\{(?:r|i)\})", input_str)

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

        for i, item in enumerate(item_list):
            output_items.append(
                self._convert_override_pattern(
                    item, self._rundata_model.read_cycles_list[i]
                )
            )

        return ";".join(output_items)

    def index_maxlens(self):
        """Return a dictionary of the maximum lengths of IndexI5 and IndexI7 columns in the sample model dataframe."""
        dataframe = self._sample_model.to_dataframe()

        if dataframe.empty:
            return {"IndexI7_maxlen": 0, "IndexI5_maxlen": 0}

        index_i7_maxlen = dataframe["IndexI7"].str.len().max()
        index_i5_maxlen = dataframe["IndexI5"].str.len().max()

        try:
            index_i7_maxlen = int(index_i7_maxlen)
            index_i5_maxlen = int(index_i5_maxlen)

        except ValueError:
            index_i7_maxlen = 0
            index_i5_maxlen = 0

        return {"IndexI7_maxlen": index_i7_maxlen, "IndexI5_maxlen": index_i5_maxlen}

    def validation_view_obj(self):

        sample_dfs_obj = {
            "no_explode": self.base_sample_dataframe(),
            "apn_explode": self.sample_dataframe_appname_explode(),
            "lane_explode": self.sample_dataframe_lane_explode(),
        }

        return sample_dfs_obj

    def json_data(self):
        s_obj = self.data_obj()
        return json.dumps(s_obj)

    def data_obj(self):

        app_settings_data = self.app_settings_data()

        obj = {
            "Header": self._header_data(),
            "Reads": self.read_cycles_dict,
            "Applications": [],
            "SampleSheetConfig": {},
        }

        for item in app_settings_data:
            item_obj = {
                "ApplicationType": item["ApplicationType"],
                "Application": item["Application"],
                "Data": item["Data"].to_dict(orient="records"),
                "Settings": item["Settings"],
            }

            obj["Applications"].append(item_obj)

        sample_sheet_config = {
            "InstrumentType": obj["Header"]["InstrumentType"],
            "I5SeqOrientation": self._rundata_model.i5_seq_orientation,
            "I5SampleSheetOrientation": self._rundata_model.i5_samplesheet_orientation,
        }

        obj["SampleSheetConfig"] = sample_sheet_config

        return obj

        # return self._data_obj

    def _bclconvert_adapters(self, data_df):
        application_names = data_df["ApplicationProfile"].explode().tolist()

        adapters_read1 = set()
        adapters_read2 = set()

        for name in application_names:
            app_object = self._application_manager.profile_name_to_profile(name)
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
            "AdapterRead1": "+".join(adapters_read1),
            "AdapterRead2": "+".join(adapters_read2),
        }

        return adapters

    def _header_data(self):
        return {
            "FileFormatVersion": self._rundata_model.rundata["SampleSheetVersion"],
            "InstrumentType": self._rundata_model.rundata["Instrument"],
            "RunName": self._rundata_model.rundata["RunName"],
            "RunDescription": self._rundata_model.rundata["RunDescription"],
            "Custom_Flowcell": self._rundata_model.rundata["Flowcell"],
            "Custom_UUID7": uuid(),
        }

    @property
    def read_cycles_dict(self) -> dict:

        return self._rundata_model.read_cycles_dict

    def set_data_obj(self):

        app_settings_data = self.app_settings_data()

        obj = {
            "Header": self._header_data(),
            "Reads": self.read_cycles_dict,
            "Applications": [],
            "SampleSheetConfig": {},
        }

        for item in app_settings_data:
            item_obj = {
                "ApplicationType": item["ApplicationType"],
                "Application": item["Application"],
                "Data": item["Data"].to_dict(orient="records"),
                "Settings": item["Settings"],
            }

            obj["Applications"].append(item_obj)

        sample_sheet_config = {
            "InstrumentType": obj["Header"]["InstrumentType"],
            "I5SeqOrientation": self._rundata_model.i5_seq_orientation,
            "I5SampleSheetOrientation": self._rundata_model.i5_samplesheet_orientation,
        }

        obj["SampleSheetConfig"] = sample_sheet_config

        self._data_obj = obj

    def app_settings_data(self) -> list:
        """Returns a list of dictionaries containing application settings and data."""
        _app_settings_data = []

        all_sample_data_df = self.sample_dataframe_appname_explode()
        all_sample_data_df["OverrideCycles"] = all_sample_data_df[
            "OverrideCyclesPattern"
        ].apply(self._override_cycles)

        unique_app_profiles = all_sample_data_df["ApplicationProfile"].unique()

        _tmp = {}
        for app_profile in unique_app_profiles:
            app = self._application_manager.application_profile_to_app(app_profile)
            if app not in _tmp:
                _tmp[app] = {"Data": [], "Settings": {}, "DataFields": []}

            data_df = all_sample_data_df[
                all_sample_data_df["ApplicationProfile"] == app_profile
            ].copy(deep=True)

            app_profile_data = self._application_manager.profile_name_to_data(app_profile)

            for k, v in app_profile_data.items():
                if k not in data_df.columns:
                    data_df[k] = v

            data_df = data_df[self._application_manager.profile_name_to_data_fields(app_profile)]

            _tmp[app]["Data"].append(data_df)
            _tmp[app]["Settings"] = self._application_manager.profile_name_to_settings(app_profile)

        for app in _tmp:
            concat_data = pd.concat(_tmp[app]["Data"])

            if "Lane" in concat_data.columns:
                concat_data = concat_data.explode("Lane", ignore_index=True)

            _app_settings_data.append(
                {
                    "ApplicationType": self._application_manager.application_name_to_application_type(app),
                    "Application": app,
                    "Data": concat_data,
                    "Settings": _tmp[app]["Settings"],
                }
            )

        return _app_settings_data

    @property
    def used_lanes(self):
        df = self.sample_dataframe_lane_explode()
        used_lanes = set(df["Lane"])
        return sorted(list(used_lanes))

    @property
    def run_lanes(self):
        return self._rundata_model.lanes

    def base_sample_dataframe(self):
        dataframe = self._sample_model.to_dataframe()
        dataframe_corr = self._dataframe_strs_to_obj(dataframe)
        return dataframe_corr

    def sample_dataframe_lane_explode(self):
        base_df = self.base_sample_dataframe().copy(deep=True)
        return base_df.explode("Lane", ignore_index=True)

    def sample_dataframe_appname_explode(self):
        _df = self.base_sample_dataframe().copy(deep=True)
        df = _df[_df["ApplicationProfile"].apply(lambda x: x != [])]
        if not df.empty:
            return df.explode("ApplicationProfile", ignore_index=True)

        return df

    @staticmethod
    def _dataframe_strs_to_obj(dataframe):
        dataframe["Lane"] = dataframe["Lane"].apply(int_str_to_int_list)
        dataframe["ApplicationProfile"] = dataframe["ApplicationProfile"].apply(json_to_obj)

        return dataframe

    @staticmethod
    def _explode_apn_lane(dataframe):
        _exploded_name_df = dataframe.explode("ApplicationProfile", ignore_index=True)
        _exploded_name_lane_df = _exploded_name_df.explode("Lane", ignore_index=True)

        return _exploded_name_lane_df

    @property
    def assess_balance(self) -> bool:
        return self._rundata_model.assess_balance

    @property
    def has_rundata(self) -> bool:
        return self._rundata_model.has_rundata

    @property
    def rundata(self) -> dict:
        return self._rundata_model.rundata

    @property
    def i5_samplesheet_orientation(self) -> dict:
        return self._rundata_model.i5_samplesheet_orientation

    @property
    def i5_seq_orientation(self) -> str:
        return self._rundata_model.i5_seq_orientation

    @property
    def base_colors(self) -> dict:
        return self._rundata_model.base_colors
