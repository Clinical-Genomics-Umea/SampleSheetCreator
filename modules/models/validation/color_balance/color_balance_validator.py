from logging import Logger

import numpy as np
import pandas as pd
from PySide6.QtCore import QObject, Signal

from modules.models.dataset.dataset_manager import DataSetManager
from modules.models.sample.sample_model import SampleModel
from modules.views.validation.color_balance_widget import ColorBalanceValidationWidget


class ColorBalanceValidator(QObject):

    def __init__(
        self,
        sample_model: SampleModel,
        dataset_manager: DataSetManager,
        color_balance_widget: ColorBalanceValidationWidget,
        logger: Logger
    ):
        super().__init__()

        self._sample_model = sample_model
        self._dataset_manager = dataset_manager
        self._color_balance_widget = color_balance_widget
        self._logger = logger


    def validate(self):
        i5_orientation = self._dataset_manager.i5_seq_orientation
        i5_seq_rc = i5_orientation == "rc"

        df = self._dataset_manager.sample_dataframe_lane_explode()

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

        self._color_balance_widget.populate(result)

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
