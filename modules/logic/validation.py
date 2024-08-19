from pathlib import Path

import numpy as np
import pandas as pd
import pandera as pa
from PySide6.QtCore import QObject, Signal

from modules.logic.validation_fns import padded_index_df
from modules.logic.validation_schema import prevalidation_schema
from modules.widgets.models import SampleSheetModel
from modules.widgets.run import RunInfoWidget
import yaml


def load_from_yaml(config_file):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)


def flowcell_validation(flowcell, instrument, settings):
    if instrument not in settings['flowcells']:
        return False, f"Instrument '{instrument}' not present in validation_settings.yaml ."
    if flowcell not in settings['flowcells'][instrument]['type']:
        return False, f"flowcell '{flowcell}' not present in validation_settings.yaml ."

    return True, ""


def lane_validation(df, flowcell, instrument, settings):
    allowed_lanes = set(map(int, settings['flowcells'][instrument]['type'][flowcell]))
    used_lanes = set(df['Lane'])

    disallowed_lanes = used_lanes.difference(allowed_lanes)

    if disallowed_lanes:
        return False, f"Lane(s) {disallowed_lanes} incompatible with selected flowcell {flowcell}."

    return True, ""


def sample_count_validation(df):
    if not isinstance(df, pd.DataFrame):
        return False, "Data could not be converted to a pandas dataframe."

    if df.empty:
        return False, "No data to validate (empty dataframe)."

    return True, ""


class PreValidatorWorker(QObject):
    data_ready = Signal(dict)

    def __init__(self, validation_settings_path: Path, model: SampleSheetModel, run_info: RunInfoWidget):
        super().__init__()

        self.model = model
        self.run_info = run_info
        self.settings = load_from_yaml(validation_settings_path)

    def run(self):
        """Execute validation tasks and emit results."""
        results = {}
        rundata = self.run_info.get_data()
        dataframe = self.model.to_dataframe().replace(r'^\s*$', np.nan, regex=True)

        flowcell_type = rundata['Run_Extra']['FlowCellType']
        instrument = rundata['Header']['Instrument']

        results['flowcell'] = flowcell_validation(flowcell_type, instrument, self.settings)
        results['lane'] = lane_validation(dataframe, flowcell_type, instrument, self.settings)
        results['sample_count'] = sample_count_validation(dataframe)

        try:
            prevalidation_schema.validate(dataframe)
            results['prevalidation_schema'] = (True, "")
        except pa.errors.SchemaError as error:
            results['prevalidation_schema'] = (False, str(error))

        self.data_ready.emit(results)


class DataValidationWorker(QObject):
    results_ready = Signal(object)

    def __init__(self, model: SampleSheetModel, i5_rc: bool):
        super().__init__()

        self.df = model.to_dataframe()
        self.i5_rc = i5_rc

    def run(self):
        result = {}
        unique_lanes = self.df['Lane'].unique()

        for lane in unique_lanes:
            lane_result = {}
            lane_df = self.df[self.df['Lane'] == lane]

            i7_padded_indexes = padded_index_df(lane_df, 10, "IndexI7", "Sample_ID")
            i5_padded_indexes = padded_index_df(lane_df, 10, "IndexI5RC" if self.i5_rc else "IndexI5",
                                                "Sample_ID")

            merged_indexes = pd.merge(i7_padded_indexes, i5_padded_indexes, on="Sample_ID")

            lane_result["i7_i5_substitutions"] = self.substitutions_heatmap_df(merged_indexes)
            lane_result["i7_substitutions"] = self.substitutions_heatmap_df(i7_padded_indexes)
            lane_result["i5_substitutions"] = self.substitutions_heatmap_df(i5_padded_indexes)

            result[int(lane)] = lane_result

        print("worker datavalidation ")
        self.results_ready.emit(result)

    def substitutions_heatmap_df(self, indexes_df: pd.DataFrame, id_colname="Sample_ID"):
        a = indexes_df.drop(id_colname, axis=1).to_numpy()

        header = list(indexes_df[id_colname])
        return pd.pandas.DataFrame(self.get_row_mismatch_matrix(a), index=header, columns=header)

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

