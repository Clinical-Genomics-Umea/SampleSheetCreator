import json

import numpy as np
import pandas as pd
from PySide6.QtCore import QThread, Slot, Signal, QObject, Qt
from PySide6.QtGui import QStandardItemModel

from controllers.validation import (
    PreValidatorWorker,
    DataValidationWorker,
)
from models.samplesheet_model import SampleSheetModel
from views.run_view import RunInfoViewWidget


class MainValidator(QObject):

    def __init__(self, samples_model, run_info_widget, validation_settings):
        super().__init__()

        self.pre_validator = PreValidator(
            samples_model, run_info_widget, validation_settings
        )

        self.index_distance_validator = IndexDistanceValidator(
            samples_model,
            run_info_widget,
            validation_settings,
        )

        self.color_balance_validator = ColorBalanceValidator(
            samples_model,
            run_info_widget,
            validation_settings,
        )

    def validate(self):

        print("validate button pressed!")

        self.pre_validator.validate()
        self.index_distance_validator.validate()
        self.color_balance_validator.validate()


class PreValidator(QObject):
    data_ready = Signal(dict)

    def __init__(
        self,
        samplesheet_model: SampleSheetModel,
        run_info: RunInfoViewWidget,
        validation_settings: dict,
    ):
        super().__init__()

        self.samplesheet_model = samplesheet_model
        self.run_info = run_info
        self.validation_settings = validation_settings

        self.flowcell = None
        self.instrument = None

        self.thread = None
        self.worker = None

    def validate(self):
        df = self.samplesheet_model.to_dataframe().replace(r"^\s*$", np.nan, regex=True)

        if df.empty:
            return

        self._run_worker()

    def _run_worker(self):

        self.thread = QThread()
        self.worker = PreValidatorWorker(
            self.validation_settings, self.samplesheet_model, self.run_info
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.data_ready.connect(self._receiver)

        self.thread.start()

    @Slot(dict)
    def _receiver(self, results):
        print("prevalidator results")

        self.thread.quit()
        self.worker.deleteLater()
        self.thread.deleteLater()

        self.data_ready.emit(results)


class ColorBalanceValidator(QObject):

    data_ready = Signal(object)

    def __init__(
        self,
        model: SampleSheetModel,
        run_info: RunInfoViewWidget,
        validation_settings: dict,
    ):
        super().__init__()

        self.model = model
        self.validation_settings = validation_settings
        self.run_info_data = run_info.get_data()

        instrument = self.run_info_data["Header"]["Instrument"]
        self.i5_rc = self.validation_settings["flowcells"][instrument]["i5_rc"]

    def validate(self):

        df = self.model.to_dataframe().replace(r"^\s*$", np.nan, regex=True).dropna()

        if df.empty:
            return

        unique_lanes = df["Lane"].unique()
        i5_col_name = "IndexI5RC" if self.i5_rc else "IndexI5"

        result = {}

        for lane in unique_lanes:
            lane_df = df[df["Lane"] == lane]

            i7_padded_indexes = self._index_df_padded(
                lane_df, 10, "IndexI7", "Sample_ID"
            )
            i5_padded_indexes = self._index_df_padded(
                lane_df, 10, i5_col_name, "Sample_ID"
            )

            merged_indexes = pd.merge(
                i7_padded_indexes, i5_padded_indexes, on="Sample_ID"
            )

            result[lane] = merged_indexes

        print(result)

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


class IndexDistanceValidator(QObject):
    data_ready = Signal(object)

    def __init__(
        self,
        model: SampleSheetModel,
        run_info: RunInfoViewWidget,
        validation_settings: dict,
    ):
        super().__init__()

        self.model = model
        self.validation_settings = validation_settings
        self.run_info_data = run_info.get_data()

        instrument = self.run_info_data["Header"]["Instrument"]
        self.i5_rc = self.validation_settings["flowcells"][instrument]["i5_rc"]

    def validate(self):
        df = self.model.to_dataframe().replace(r"^\s*$", np.nan, regex=True).dropna()
        if df.empty:
            return

        self._run_worker_thread()

    def _run_worker_thread(self):
        self.thread = QThread()
        self.worker = DataValidationWorker(self.model, self.i5_rc)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.results_ready.connect(self._receiver)

        self.thread.start()

    @Slot(object)
    def _receiver(self, results):

        # self.spinner.stop()
        self.thread.quit()
        self.worker.deleteLater()
        self.thread.deleteLater()

        self.data_ready.emit(results)


class IndexColorBalanceModel(QStandardItemModel):

    def __init__(self, parent):
        super(IndexColorBalanceModel, self).__init__(parent=parent)
        self.dataChanged.connect(self.update_summation)

    def update_summation(self):

        for col in range(2, self.columnCount()):
            bases_count = {"A": 0, "C": 0, "G": 0, "T": 0}
            merged = {}

            for row in range(self.rowCount() - 1):
                proportion = int(self.item(row, 1).text())
                base = self.item(row, col).text()
                bases_count[base] += proportion

            color_counts = self._base_to_color_count(bases_count)
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

    @staticmethod
    def _base_to_color_count(dict1):
        color_count = {
            "B": 0,
            "G": 0,
            "D": 0,
        }

        for base, count in dict1.items():
            if base == "A":
                color_count["B"] = count
            elif base == "C":
                color_count["B"] = count * 0.5
                color_count["G"] = count * 0.5
            elif base == "T":
                color_count["G"] = count
            elif base == "G":
                color_count["D"] = count

        return color_count
