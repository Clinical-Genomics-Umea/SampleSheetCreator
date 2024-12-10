import json

import numpy as np
import pandas as pd
from PySide6.QtCore import QThread, Slot, Signal, QObject, Qt
from PySide6.QtGui import QStandardItemModel
import pandera as pa

from models.application import ApplicationManager
from models.configuration import ConfigurationManager
from models.datasetmanager import DataSetManager
from models.sample_model import SampleModel
from utils.utils import explode_lane_column
from models.pa_schema import prevalidation_schema
from models.validation_fns import get_base, padded_index_df


class MainValidator(QObject):

    def __init__(self, samples_model, cfg_mgr, dataset_mgr, app_mgr):
        super().__init__()
        self.app_mgr = app_mgr
        self.cfg_mgr = cfg_mgr
        self.dataset_mgr = dataset_mgr

        self.pre_validator = PreValidator(samples_model, cfg_mgr, app_mgr, dataset_mgr)

        self.dataset_validator = DataSetValidator(samples_model, cfg_mgr, dataset_mgr)

        self.index_distance_validator = IndexDistanceValidator(
            samples_model,
            cfg_mgr,
        )

        self.color_balance_validator = ColorBalanceValidator(
            samples_model,
            cfg_mgr,
        )

    def validate(self):

        assess_color_balance = bool(self.cfg_mgr.run_data.get("AssessBalance"))

        status = self.pre_validator.validate()

        if not status:
            return

        self.dataset_validator.validate()

        self.index_distance_validator.validate()

        if assess_color_balance:
            print("validating color balance")
            self.color_balance_validator.validate()


class PreValidator(QObject):
    data_ready = Signal(list)

    def __init__(
        self,
        samplesheet_model: SampleModel,
        cfg_mgr: ConfigurationManager,
        app_mgr: ApplicationManager,
        dataset_mgr: DataSetManager,
    ):
        super().__init__()

        self.dataset = None
        self.application_profile_names = None
        self.used_lanes = None

        self.samplesheet_model = samplesheet_model
        self.cfg_mgr = cfg_mgr
        self.app_mgr = app_mgr
        self.dataset_mgr = dataset_mgr

    @staticmethod
    def create_int_list(max_value_str):
        max_value = int(max_value_str)
        return list(range(1, max_value + 1))

    def validate(self):
        """Run a series of validations on the SampleSheetModel and RunSetup config"""
        results = []
        dataframe = self.dataset_mgr.base_sample_dataframe()
        dataframe = explode_lane_column(dataframe)

        # self.dataset = DataSetManager(dataframe)

        # self.application_profile_names = self.dataset.application_profile_names
        # self.used_lanes = self.dataset.used_lanes

        run_data = self.cfg_mgr.run_data

        results.append(self.run_lanes_int_validation(run_data["Lanes"]))
        if not results[-1][1]:
            self.data_ready.emit(results)
            return

        results.append(self.empty_sample_id_validation(dataframe))
        if not results[-1][1]:
            self.data_ready.emit(results)
            return

        results.append(self.dataframe_type_validation(dataframe))
        if not results[-1][1]:
            self.data_ready.emit(results)
            return

        results.append(self.application_validation(dataframe))
        if not results[-1][1]:
            self.data_ready.emit(results)
            return

        # results.extend(self.schema_validation(dataframe))
        #
        status = all(item[1] for item in results)

        # if status:
        #     results.append(("schema validation", True, ""))

        self.data_ready.emit(results)
        return status

    def application_validation(self, dataframe):

        name = "application settings validation"

        app_exploded_df = dataframe.explode("ApplicationName", ignore_index=True)

        print(app_exploded_df.to_string())

        unique_app_names = app_exploded_df["ApplicationName"].unique()

        app_settings = {}
        app_settings_results = {}

        for app_name in unique_app_names:
            print("name", app_name)
            app = self.app_mgr.appobj_by_appname(app_name)
            print("app", app)
            application = app["Application"]

            if application not in app_settings:
                app_settings[application] = []

            app_settings[application].append(app["Settings"])

        for application in app_settings:
            list_of_settings = app_settings[application]

            app_settings_results[application] = all(
                d == list_of_settings[0] for d in list_of_settings
            )

        for application in app_settings_results:
            if not app_settings_results[application]:
                return (
                    name,
                    False,
                    f"Non-identical settings exist for: {application}",
                )

        return name, True, ""

    @staticmethod
    def schema_validation(df):

        results = []

        try:
            prevalidation_schema.validate(df, lazy=True)
        except pa.errors.SchemaErrors as e:
            for index, row in e.failure_cases.iterrows():
                results.append(("schema validation", False, row["check"]))
        return results

    @staticmethod
    def empty_sample_id_validation(df):
        name = "empty sample id validation"

        empty_items = df["Sample_ID"].isna()

        if empty_items.any():
            empty_row_indices_list = (df.index[empty_items] + 1).tolist()
            empty_row_indices_list_str = map(str, empty_row_indices_list)
            emtpy_row_indices_str = ",".join(empty_row_indices_list_str)
            return (
                name,
                False,
                f"Empty items found in the Sample_ID column at row numbers: {emtpy_row_indices_str}",
            )

        return name, True, ""

    @staticmethod
    def run_lanes_int_validation(set_lanes):
        name = "set number of lanes validation"

        set_lanes_set = set(set_lanes)

        if not isinstance(set_lanes, list):
            return name, False, "Lanes must a list of integers."

        if not all(isinstance(item, int) for item in set_lanes):
            return name, False, "Lanes must be an list of integers."

        return name, True, ""

    @staticmethod
    def dataframe_type_validation(df):
        name = "dataframe basic validation"

        if not isinstance(df, pd.DataFrame):
            return name, False, "Data is not in a pandas dataframe format."

        if df.empty:
            return name, False, "No data to validate (empty dataframe)."

        return name, True, ""

    @staticmethod
    def validate_unique_sample_lane_combinations(df):
        """
        Validate that the combination of sample_id and individual lane values in a DataFrame is unique.

        Parameters:
        df (pandas.DataFrame): The DataFrame to be validated, with columns 'sample_id' and 'lane'.

        Returns:
        Tuple[bool, Optional[str]]: A tuple containing a boolean success flag and an optional error message.
        """

        name = "unique sample lane validation"

        # Create a new DataFrame with exploded lane values

        df_tmp = df.copy(deep=True)
        df_tmp["sample_lane"] = df_tmp["Sample_ID"] + "_" + df_tmp["Lane"].astype(str)

        # Check if the 'sample_lane' column has any duplicates
        if df_tmp["sample_lane"].duplicated().any():
            # Get the duplicate values
            duplicates = df_tmp.loc[
                df_tmp["sample_lane"].duplicated(), "sample_lane"
            ].tolist()

            # Construct the error message
            error_msg = (
                f"Duplicates of Sample_ID and Lane exists: {', '.join(duplicates)}"
            )
            return name, False, error_msg

        # If no duplicates are found
        return name, True, None

    def allowed_lanes_validation(self, df, lanes):
        name = "allowed lanes validation"

        allowed_lanes = self.create_int_list(lanes)
        used_lanes = set(df["Lane"])
        disallowed_lanes = used_lanes.difference(allowed_lanes)

        if disallowed_lanes:
            return (
                name,
                False,
                f"Lane(s) {disallowed_lanes} are not allowed.",
            )

        return name, True, ""

    @staticmethod
    def sample_id_validation(df):
        name = "sample id validation"
        if not isinstance(df, pd.DataFrame):
            return False, "Data could not be converted to a pandas dataframe."

        if df.empty:
            return False, "No data to validate (empty dataframe)."

        return True, ""


class DataSetValidator(QObject):
    data_ready = Signal(object)

    def __init__(
        self,
        model: SampleModel,
        cfg_mgr: ConfigurationManager,
        dataset_mgr: DataSetManager,
    ):
        super().__init__()

        if model is None:
            raise ValueError("model cannot be None")

        if cfg_mgr is None:
            raise ValueError("cfg_mgr cannot be None")

        if dataset_mgr is None:
            raise ValueError("dataset_mgr cannot be None")

        self.model = model
        self.cfg_mgr = cfg_mgr
        self.dataset_mgr = dataset_mgr
        self.dataset = None

    def validate(self):
        sample_dfs = self.dataset_mgr.validation_view_obj()

        self.data_ready.emit(sample_dfs)


class IndexDistanceValidator(QObject):
    data_ready = Signal(object)

    def __init__(
        self,
        model: SampleModel,
        cfg_mgr: ConfigurationManager,
    ):
        super().__init__()

        if model is None:
            raise ValueError("model cannot be None")

        if cfg_mgr is None:
            raise ValueError("cfg_mgr cannot be None")

        self.model = model
        self.cfg_mgr = cfg_mgr

        self.thread = None
        self.worker = None

    def validate(self):

        i5_orientation = self.cfg_mgr.run_data.get("I5SeqOrientation")
        i5_rc = i5_orientation == "rc"

        self.thread = QThread()
        self.worker = IndexDistanceValidationWorker(self.model, i5_rc)

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.results_ready.connect(self._receiver)
        self.worker.error.connect(self._receiver)

        print("starting worker")

        self.thread.start()

    @Slot(object)
    def _receiver(self, results):

        self.thread.quit()
        self.worker.deleteLater()
        self.thread.deleteLater()

        self.data_ready.emit(results)


class IndexDistanceValidationWorker(QObject):
    results_ready = Signal(object)
    error = Signal(str)

    def __init__(self, model: SampleModel, i5_rc: bool):
        super().__init__()

        self.df = model.to_dataframe()
        self.i5_rc = i5_rc

    def run(self):
        df_split = explode_lane_column(self.df)

        try:
            result = {}
            unique_lanes = df_split["Lane"].unique()

            for lane in unique_lanes:
                lane_result = {}
                lane_df = df_split[df_split["Lane"] == lane]

                i7_padded_indexes = padded_index_df(lane_df, 10, "IndexI7", "Sample_ID")
                i5_padded_indexes = padded_index_df(
                    lane_df, 10, "IndexI5RC" if self.i5_rc else "IndexI5", "Sample_ID"
                )

                merged_indexes = pd.merge(
                    i7_padded_indexes, i5_padded_indexes, on="Sample_ID"
                )

                lane_result["i7_i5_substitutions"] = self.substitutions_heatmap_df(
                    merged_indexes
                )
                lane_result["i7_substitutions"] = self.substitutions_heatmap_df(
                    i7_padded_indexes
                )
                lane_result["i5_substitutions"] = self.substitutions_heatmap_df(
                    i5_padded_indexes
                )

                result[int(lane)] = lane_result

            self.results_ready.emit(result)

        except Exception as e:
            self.error.emit(str(e))

    def substitutions_heatmap_df(
        self, indexes_df: pd.DataFrame, id_colname="Sample_ID"
    ):
        a = indexes_df.drop(id_colname, axis=1).to_numpy()

        header = list(indexes_df[id_colname])
        return pd.pandas.DataFrame(
            self.get_row_mismatch_matrix(a), index=header, columns=header
        )

    def get_row_mismatch_matrix(self, array: np.ndarray) -> np.ndarray:
        # Reshape A and B to 3D arrays with dimensions (N, 1, K) and (1, M, K), respectively
        array1 = array[:, np.newaxis, :]
        array2 = array[np.newaxis, :, :]

        # Apply the custom function using vectorized operations
        return np.sum(np.vectorize(self.cmp_bases)(array1, array2), axis=2)

    @staticmethod
    def cmp_bases(v1, v2):
        if isinstance(v1, str) and isinstance(v2, str):
            return np.sum(v1 != v2)

        return 0


class ColorBalanceValidator(QObject):

    data_ready = Signal(object)

    def __init__(
        self,
        model: SampleModel,
        cfg_mgr: ConfigurationManager,
    ):
        super().__init__()

        self.model = model
        self.cfg_mgr = cfg_mgr

        i5_orientation = cfg_mgr.run_data.get("I5SeqOrientation")
        # print("i5 orientation", i5_orientation)

        self.i5_rc = i5_orientation == "rc"

    def validate(self):
        i5_orientation = self.cfg_mgr.run_data.get("I5SeqOrientation")
        i5_rc = i5_orientation == "rc"

        df = explode_lane_column(self.model.to_dataframe())

        if df.empty:
            return

        unique_lanes = df["Lane"].unique()
        i5_col_name = "IndexI5RC" if i5_rc else "IndexI5"
        # print(i5_col_name)

        result = {}

        for lane in unique_lanes:
            lane_df = df[df["Lane"] == lane]

            i7_padded_indexes = self._index_df_padded(
                lane_df, 10, "IndexI7", "Sample_ID"
            )
            i5_padded_indexes = self._index_df_padded(
                lane_df, 10, i5_col_name, "Sample_ID"
            )

            concat_indexes = pd.merge(
                i7_padded_indexes, i5_padded_indexes, on="Sample_ID"
            )

            result[lane] = concat_indexes

        self.data_ready.emit(result)

    def _index_df_padded(
        self, df: pd.DataFrame, tot_len: int, col_name: str, id_name: str
    ) -> pd.DataFrame:

        index_type = col_name.replace("Index_", "")
        pos_names = [f"{index_type}_{i + 1}" for i in range(tot_len)]

        # Extract i7 indexes
        i7_df = (
            df[col_name]
            .apply(lambda x: pd.Series(self._get_base(x, i) for i in range(tot_len)))
            .fillna(np.nan)
        )
        i7_df.columns = pos_names

        # Concatenate indexes and return the resulting DataFrame
        return pd.concat([df[id_name], i7_df], axis=1)

    @staticmethod
    def _get_base(index_seq, base_pos):

        if base_pos >= len(index_seq):
            return np.nan
        else:
            return index_seq[base_pos]


class IndexColorBalanceModel(QStandardItemModel):

    def __init__(self, base_colors, parent):
        super(IndexColorBalanceModel, self).__init__(parent=parent)
        self.dataChanged.connect(self.update_summation)
        self.transformed_base_colors = {
            key: [color[0].upper() for color in colors]
            for key, colors in base_colors.items()
        }

    def data(self, index, role=Qt.DisplayRole):
        # Only modify data for display purposes
        if role == Qt.DisplayRole:
            original_value = super().data(index, role)
            # Replace "na" with "-"
            if original_value == "nan":
                return "-"
        return super().data(index, role)

    def update_summation(self):

        for col in range(2, self.columnCount()):
            bases_count = {"A": 0, "C": 0, "G": 0, "T": 0}
            merged = {}

            for row in range(self.rowCount() - 1):
                proportion = int(self.item(row, 1).text())
                base = self.item(row, col).text()

                if base in ["A", "C", "G", "T"]:
                    bases_count[base] += proportion

            color_counts = self._generic_base_to_color_count(bases_count)
            normalized_color_counts = self._normalize(color_counts)
            normalized_base_counts = self._normalize(bases_count)

            merged["colors"] = normalized_color_counts
            merged["bases"] = normalized_base_counts
            norm_json = json.dumps(merged)

            last_row = self.rowCount() - 1
            self.setData(self.index(last_row, col), norm_json, Qt.EditRole)

    @staticmethod
    def merge(dict1, dict2):
        res = dict1 | {"--": "---"} | dict2
        return res

    @staticmethod
    def _normalize(input_dict):
        # Calculate the sum of values in the input dictionary
        total = sum(input_dict.values())

        if total == 0:
            total = 0.00001

        # Normalize the values and create a new dictionary
        normalized_dict = {
            key: round(value / total, 2) for key, value in input_dict.items()
        }

        return normalized_dict

    def _generic_base_to_color_count(self, dict1):
        color_count = {
            "B": 0,
            "G": 0,
            "D": 0,
        }

        for base, count in dict1.items():

            base_colors = self.transformed_base_colors[base]
            no_colors = len(base_colors)

            for color in base_colors:
                color_count[color] += count / no_colors

        return color_count
