from PySide6.QtCore import Signal, QObject

from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.dataset.dataset_manager import DataSetManager
from modules.models.sample.sample_model import SampleModel


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
