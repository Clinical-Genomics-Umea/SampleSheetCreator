import numpy as np
import pandas as pd
from PySide6.QtCore import QObject, Signal

from modules.models.dataset.dataset_manager import DataSetManager
from modules.models.sample.sample_model import SampleModel


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
