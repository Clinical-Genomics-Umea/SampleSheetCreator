from pathlib import Path

import numpy as np
import pandas as pd
import pandera as pa
from PySide6.QtCore import QObject, Signal
from pandas import DataFrame

from modules.logic.validation_fns import padded_index_df, substitutions_heatmap_df
from modules.logic.validation_schema import prevalidation_schema
from modules.widgets.models import SampleSheetModel
from modules.widgets.run import RunInfoWidget
from modules.widgets.validation import flowcell_validation, lane_validation, sample_count_validation, load_from_yaml, \
    create_heatmap_table


class PreValidatorWorker(QObject):
    finished = Signal(dict[str, tuple[bool, str]])

    def __init__(self, validation_settings_path: Path, model: SampleSheetModel, run_info: RunInfoWidget):
        super().__init__()

        self.model = model
        self.run_info = run_info
        self.settings = load_from_yaml(validation_settings_path)

    def run(self):
        run_data = self.run_info.get_data()
        df = self.model.to_dataframe()
        df = df.replace(r'^\s*$', np.nan, regex=True)

        flowcell_type = run_data['Run_Extra']['FlowCellType']
        instrument = run_data['Header']['Instrument']

        res = {}

        res["flowcell_validation"] = flowcell_validation(flowcell_type, instrument, self.settings)
        res["lane_validation"] = lane_validation(df, flowcell_type, instrument, self.settings)
        res["sample_count_validation"] = sample_count_validation(df)

        try:
            prevalidation_schema.validate(df)
            res["prevalidation_schema"] = (True, "")
        except pa.errors.SchemaError as exc:
            res["prevalidation schema"] = (False, str(exc))

        self.finished.emit(res)


class DataValidationWorker(QObject):
    finished_i7_i5 = Signal(DataFrame)
    finished_i7 = Signal(DataFrame)
    finished_i5 = Signal(DataFrame)

    def __init__(self, validation_settings_path: Path, model: SampleSheetModel, run_info: RunInfoWidget):
        super().__init__()

        self.df = model.to_dataframe()
        self.run_info_data = run_info.get_data()

        instrument = self.run_info_data['Header']['Instrument']
        settings = load_from_yaml(validation_settings_path)
        self.index_i5_rc = settings['flowcells'][instrument]

    def run(self):

        indexes_i7_padded = padded_index_df(self.df, 10, "IndexI7", "Sample_ID")

        if not self.index_i5_rc:
            indexes_i5_padded = padded_index_df(self.df, 10, "IndexI5", "Sample_ID")
        else:
            indexes_i5_padded = padded_index_df(self.df, 10, "IndexI5RC", "Sample_ID")

        indexes_i7_i5_padded = pd.merge(indexes_i7_padded, indexes_i5_padded, on="Sample_ID")

        i7_i5_substitution_df = substitutions_heatmap_df(indexes_i7_i5_padded)
        self.finished_i7_i5.emit(i7_i5_substitution_df)

        i7_substitution_df = substitutions_heatmap_df(indexes_i7_padded)
        self.finished_i7.emit(i7_substitution_df)

        i5_substitution_df = substitutions_heatmap_df(indexes_i5_padded)
        self.finished_i5.emit(i5_substitution_df)

