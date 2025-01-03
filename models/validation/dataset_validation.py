import json
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple

import numpy as np
import pandas as pd
from PySide6.QtCore import QThread, Slot, Signal, QObject, Qt
from PySide6.QtGui import QStandardItemModel

from models.application.application_manager import ApplicationManager
from models.configuration.configuration_manager import ConfigurationManager
from models.dataset.dataset_manager import DataSetManager
from models.sample.sample_model import SampleModel


class MainValidator(QObject):

    clear_validator_widgets = Signal()
    prevalidator_status = Signal(bool)

    def __init__(self, samples_model, cfg_mgr, dataset_mgr, app_mgr):
        super().__init__()
        self.app_mgr = app_mgr
        self.cfg_mgr = cfg_mgr
        self.dataset_mgr = dataset_mgr

        self.pre_validator = PreValidator(samples_model, cfg_mgr, app_mgr, dataset_mgr)
        self.dataset_validator = DataSetValidator(samples_model, cfg_mgr, dataset_mgr)
        self.index_distance_validator = IndexDistanceMatrixGenerator(
            samples_model, dataset_mgr
        )
        self.color_balance_validator = ColorBalanceValidator(samples_model, dataset_mgr)

    def validate(self):

        self.clear_validator_widgets.emit()

        if not self.pre_validator.validate():
            self.prevalidator_status.emit(False)
            return

        self.prevalidator_status.emit(True)

        self.dataset_mgr.set_samplesheet_obj()

        self.dataset_validator.validate()
        self.index_distance_validator.generate()

        if self.dataset_mgr.assess_balance:
            self.color_balance_validator.validate()


@dataclass
class PreValidationResult:
    name: str
    status: bool
    message: str = ""


class PreValidator(QObject):
    data_ready = Signal(list)

    def __init__(
        self,
        sample_model: SampleModel,
        cfg_mgr: ConfigurationManager,
        app_mgr: ApplicationManager,
        dataset_mgr: DataSetManager,
    ):
        super().__init__()
        self.sample_model = sample_model
        self.cfg_mgr = cfg_mgr
        self.app_mgr = app_mgr
        self.dataset_mgr = dataset_mgr

        self.dataframe: Optional[pd.DataFrame] = None
        self.rundata: Optional[Dict] = None

    @staticmethod
    def _run_validators(validators: List[callable]) -> List[PreValidationResult]:
        """
        Run a series of validation methods and collect results.

        :param validators: List of validation methods to run
        :return: List of validation results
        """
        results = [validator() for validator in validators]
        return results

    def validate(self) -> bool:
        """Run comprehensive validations on the dataset"""
        self.dataframe = self.dataset_mgr.sample_dataframe_lane_explode()
        self.rundata = self.dataset_mgr.rundata

        validators = [
            self.rundata_is_set,
            self.required_cols_populated,
            self.run_lanes_int_validation,
            self.empty_sample_id_validation,
            self.dataframe_type_validation,
            self.application_validation,
            self.allowed_lanes_validation,
            self.validate_unique_sample_lane_combinations,
        ]

        results = self._run_validators(validators)
        status = all(result.status for result in results)

        self.data_ready.emit([(r.name, r.status, r.message) for r in results])
        return status

    def rundata_is_set(self) -> PreValidationResult:
        """Validate if run data is set"""
        if not self.dataset_mgr.has_rundata:
            return PreValidationResult(
                name="Run data set validator",
                status=False,
                message="Run data has not been set",
            )
        return PreValidationResult(name="Run data set validator", status=True)

    def required_cols_populated(self) -> PreValidationResult:
        """Validate that required columns are populated"""
        required_columns = self.cfg_mgr.required_sample_fields
        dataframe = self.dataset_mgr.sample_dataframe_lane_explode()

        missing_columns = [
            column for column in required_columns if dataframe[column].isnull().any()
        ]

        if missing_columns:
            return PreValidationResult(
                name="required fields populated",
                status=False,
                message=f"Required fields are not populated: {', '.join(missing_columns)}",
            )
        return PreValidationResult(name="required fields populated", status=True)

    def application_validation(self) -> PreValidationResult:
        """Validate application settings consistency"""
        app_exploded_df = self.dataframe.explode("ApplicationName", ignore_index=True)
        unique_appnames = app_exploded_df["ApplicationName"].unique()

        # Group settings by application
        app_settings = {}
        for appname in unique_appnames:
            app = self.app_mgr.appobj_by_appname(appname)
            app_type = app["Application"]

            if app_type not in app_settings:
                app_settings[app_type] = []
            app_settings[app_type].append(app["Settings"])

        # Check if all settings are identical within each application type
        for app_type, settings_list in app_settings.items():
            if not all(settings == settings_list[0] for settings in settings_list):
                return PreValidationResult(
                    name="application settings validation",
                    status=False,
                    message=f"Non-identical settings exist for: {app_type}",
                )

        return PreValidationResult(name="application settings validation", status=True)

    def empty_sample_id_validation(self) -> PreValidationResult:
        """Validate that no Sample_ID entries are empty"""
        empty_items = self.dataframe["Sample_ID"].isna()

        if empty_items.any():
            empty_row_indices = (self.dataframe.index[empty_items] + 1).tolist()
            return PreValidationResult(
                name="empty sample id validation",
                status=False,
                message=f"Empty items found in Sample_ID column at row numbers: {','.join(map(str, empty_row_indices))}",
            )
        return PreValidationResult(name="empty sample id validation", status=True)

    def run_lanes_int_validation(self) -> PreValidationResult:
        """Validate run lanes are a list of integers"""
        run_lanes = self.rundata["Lanes"]

        if not isinstance(run_lanes, list) or not all(
            isinstance(item, int) for item in run_lanes
        ):
            return PreValidationResult(
                name="set number of lanes validation",
                status=False,
                message="Lanes must be a list of integers",
            )
        return PreValidationResult(name="set number of lanes validation", status=True)

    def dataframe_type_validation(self) -> PreValidationResult:
        """Validate dataframe type and content"""
        if not isinstance(self.dataframe, pd.DataFrame):
            return PreValidationResult(
                name="dataframe basic validation",
                status=False,
                message="Data is not in a pandas dataframe format",
            )
        if self.dataframe.empty:
            return PreValidationResult(
                name="dataframe basic validation",
                status=False,
                message="No data to validate (empty dataframe)",
            )
        return PreValidationResult(name="dataframe basic validation", status=True)

    def validate_unique_sample_lane_combinations(self) -> PreValidationResult:
        """Validate unique sample-lane combinations"""
        df_tmp = self.dataframe.copy(deep=True)
        df_tmp["sample_lane"] = df_tmp["Sample_ID"] + "_" + df_tmp["Lane"].astype(str)

        if df_tmp["sample_lane"].duplicated().any():
            duplicates = df_tmp.loc[
                df_tmp["sample_lane"].duplicated(), "sample_lane"
            ].tolist()
            return PreValidationResult(
                name="unique sample lane validation",
                status=False,
                message=f"Duplicates of Sample_ID and Lane exists: {', '.join(duplicates)}",
            )
        return PreValidationResult(name="unique sample lane validation", status=True)

    def allowed_lanes_validation(self) -> PreValidationResult:
        """Validate used lanes are within allowed lanes"""
        allowed_lanes = set(self.rundata["Lanes"])
        used_lanes = set(self.dataframe["Lane"])

        disallowed_lanes = used_lanes.difference(allowed_lanes)

        if disallowed_lanes:
            return PreValidationResult(
                name="allowed lanes validation",
                status=False,
                message=f"Lane(s) {disallowed_lanes} not allowed, does not exist in flowcell",
            )
        return PreValidationResult(name="allowed lanes validation", status=True)

    @staticmethod
    def sample_id_validation(df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
        """Static method for standalone sample ID validation"""
        if not isinstance(df, pd.DataFrame):
            return False, "Data could not be converted to a pandas dataframe."
        if df.empty:
            return False, "No data to validate (empty dataframe)."
        return True, None


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


class IndexDistanceMatrixGenerator(QObject):
    data_ready = Signal(object)

    def __init__(
        self,
        model: SampleModel,
        dataset_mgr: DataSetManager,
    ):
        super().__init__()

        if model is None:
            raise ValueError("model cannot be None")

        self.model = model
        self.dataset_mgr = dataset_mgr

        self.thread = None
        self.worker = None

    def generate(self):

        i5_seq_orientation = self.dataset_mgr.i5_seq_orientation
        i5_seq_rc = i5_seq_orientation == "rc"

        self.thread = QThread()
        self.worker = IndexDistanceMatricesWorker(self.dataset_mgr, i5_seq_rc)

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.results_ready.connect(self._receiver)
        self.worker.error.connect(self._receiver)

        self.thread.start()

    @Slot(object)
    def _receiver(self, results):

        self.thread.quit()
        self.worker.deleteLater()
        self.thread.deleteLater()

        self.data_ready.emit(results)


class IndexDistanceMatricesWorker(QObject):
    results_ready = Signal(object)
    error = Signal(str)

    def __init__(self, dataset_mgr: DataSetManager, i5_seq_rc: bool):
        super().__init__()
        self.dataset_mgr = dataset_mgr
        self.df = self.dataset_mgr.sample_dataframe_lane_explode()
        self.i5_seq_rc = i5_seq_rc

    def run(self):
        """
        Run the index distance validation and emit the result when finished.

        Emits a dictionary with the lane number as the key and a distance matrices dictionary with the
        following structure as the value:
        {
            "i7_i5": pd.DataFrame,
            "i7": pd.DataFrame,
            "i5": pd.DataFrame
        }
        """
        try:
            validation_data = {}
            for lane in self.dataset_mgr.used_lanes:

                index_lane_df = self.df[self.df["Lane"] == lane]

                i7_index_pos_df = self._padded_index_pos_df(
                    index_lane_df, "IndexI7", "Sample_ID"
                )
                i5_index_pos_df = self._padded_index_pos_df(
                    index_lane_df,
                    "IndexI5RC" if self.i5_seq_rc else "IndexI5",
                    "Sample_ID",
                )

                i7_i5_indexes_pos_df = pd.merge(
                    i7_index_pos_df, i5_index_pos_df, on="Sample_ID"
                )

                validation_data[int(lane)] = {
                    "i7_i5": self._index_distance_matrix_df(i7_i5_indexes_pos_df),
                    "i7": self._index_distance_matrix_df(i7_index_pos_df),
                    "i5": self._index_distance_matrix_df(i5_index_pos_df),
                }

            self.results_ready.emit(validation_data)

        except Exception as error:
            self.error.emit(str(error))

    @staticmethod
    def _base_by_index_pos(index_seq, index_pos):
        """
        Retrieve the DNA base from a given DNA sequence at a specified position.

        Parameters
        ----------
        index_seq : str
            The DNA sequence from which to retrieve the base.
        index_pos : int
            The zero-based position of the base to retrieve.

        Returns
        -------
        str or float
            The DNA base at the specified position, or np.nan if the index is out of bounds.
        """
        if index_pos >= len(index_seq):
            return np.nan
        else:
            return index_seq[index_pos]

    def _padded_index_pos_df(
        self, data_df: pd.DataFrame, index_col_name: str, sample_id_col_name: str
    ) -> pd.DataFrame:
        """
        Extract the DNA bases at each position for the given index type and dataframe.

        Parameters
        ----------
        data_df : pd.DataFrame
            DataFrame with the index to be extracted
        index_col_name : str
            Name of the column in `df` containing the index
        sample_id_col_name : str
            Name of the column in `df` containing the sample ID

        Returns
        -------
        pd.DataFrame
            DataFrame with the extracted DNA bases, concatenated with the sample ID column
        """

        max_index_length = data_df[index_col_name].apply(len).max()
        index_base_name = index_col_name.replace("Index", "")

        # Generate column names
        index_pos_names = [
            f"{index_base_name}_{i + 1}" for i in range(max_index_length)
        ]

        padded_index_pos_df = (
            data_df[index_col_name]
            .apply(
                lambda x: pd.Series(
                    self._base_by_index_pos(x, i) for i in range(max_index_length)
                )
            )
            .fillna(np.nan)
        )
        padded_index_pos_df.columns = index_pos_names

        # Concatenate indexes and return the resulting DataFrame
        return pd.concat([data_df[sample_id_col_name], padded_index_pos_df], axis=1)

    def _index_distance_matrix_df(
        self, indexes_df: pd.DataFrame, sample_id_colname: str = "Sample_ID"
    ) -> pd.DataFrame:
        """
        Generate a index distance matrix for the given DataFrame containing indexes.

        Parameters
        ----------
        indexes_df : pd.DataFrame
            DataFrame of indexes with Sample_ID column
        sample_id_colname : str, optional
            Name of the column containing Sample_IDs, by default "Sample_ID"

        Returns
        -------
        pd.DataFrame
            Heatmap of substitutions for the given indexes
        """
        a = indexes_df.drop(sample_id_colname, axis=1).to_numpy()

        header = list(indexes_df[sample_id_colname])
        return pd.pandas.DataFrame(
            self._get_row_mismatch_matrix(a), index=header, columns=header
        )

    def _get_row_mismatch_matrix(self, array: np.ndarray) -> np.ndarray:
        # Reshape A and B to 3D arrays with dimensions (N, 1, K) and (1, M, K), respectively
        array1 = array[:, np.newaxis, :]
        array2 = array[np.newaxis, :, :]

        # Apply the custom function using vectorized operations
        return np.sum(np.vectorize(self._cmp_bases)(array1, array2), axis=2)

    @staticmethod
    def _cmp_bases(v1, v2):
        if isinstance(v1, str) and isinstance(v2, str):
            return np.sum(v1 != v2)

        return 0


class ColorBalanceValidator(QObject):

    data_ready = Signal(object)

    def __init__(
        self,
        model: SampleModel,
        dataset_mgr: DataSetManager,
    ):
        super().__init__()

        self.model = model
        self.dataset_mgr = dataset_mgr

        i5_seq_orientation = dataset_mgr.i5_seq_orientation

        self.i5_rc = i5_seq_orientation == "rc"

    def validate(self):
        i5_orientation = self.dataset_mgr.i5_seq_orientation
        i5_seq_rc = i5_orientation == "rc"

        df = self.dataset_mgr.sample_dataframe_lane_explode()

        if df.empty:
            return

        unique_lanes = df["Lane"].unique()
        i5_col_name = "IndexI5RC" if i5_seq_rc else "IndexI5"

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

        self._transformed_base_colors = {
            key: [color[0].upper() for color in colors]
            for key, colors in base_colors.items()
        }

    def data(self, index, role=Qt.DisplayRole):
        # Only modify data for display purposes
        if role == Qt.DisplayRole:
            original_value = super().data(index, role)
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

            base_colors = self._transformed_base_colors[base]
            no_colors = len(base_colors)

            for color in base_colors:
                color_count[color] += count / no_colors

        return color_count
