import numpy as np
import pandas as pd
from PySide6.QtCore import QObject, Signal

from modules.models.dataset.dataset_manager import DataSetManager
from modules.models.state.state_model import StateModel
from modules.utils.utils import explode_df_lane_column


class IndexDistanceMatricesWorker(QObject):
    results_ready = Signal(object)
    error = Signal(str)

    def __init__(self, state_model: StateModel, i5_seq_rc: bool):
        super().__init__()
        self._state_model = state_model
        self._df_lane_explode = explode_df_lane_column(self._state_model.sample_df)
        self._i5_seq_rc = i5_seq_rc

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
            for lane in self._state_model.lanes:

                index_lane_df = self._df_lane_explode[self._df_lane_explode["Lane"] == lane]

                i7_index_pos_df = self._padded_index_pos_df(
                    index_lane_df, "IndexI7", "Sample_ID"
                )
                i5_index_pos_df = self._padded_index_pos_df(
                    index_lane_df,
                    "IndexI5RC" if self._i5_seq_rc else "IndexI5",
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
