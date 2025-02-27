from PySide6.QtCore import QObject, Signal, Slot

from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.sample.sample_model import SampleModel


class MakeJson(QObject):
    data_ready = Signal(object)

    def __init__(self, model: SampleModel, cfg_mgr: ConfigurationManager):
        super().__init__()

        if model is None:
            raise ValueError("model cannot be None")

        if cfg_mgr is None:
            raise ValueError("cfg_mgr cannot be None")

        self.model = model
        self.cfg_mgr = cfg_mgr

    @Slot()
    def mk_json(self):
        samples_df = self.model.to_dataframe()
        run_data = self.cfg_mgr.run_data

        samples_run_data = {
            "samples_data": samples_df.to_dict(orient="records"),
            "rundata": run_data,
        }

        self.data_ready.emit(samples_run_data)
