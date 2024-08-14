from pathlib import Path

import numpy as np
import pandera as pa
from PySide6.QtCore import QObject, Signal

from modules.logic.validation_schema import prevalidation_schema
from modules.widgets.models import SampleSheetModel
from modules.widgets.run import RunInfoWidget
from modules.widgets.validation import flowcell_validation, lane_validation, sample_count_validation, load_from_yaml


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
