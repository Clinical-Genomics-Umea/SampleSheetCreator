from logging import Logger

from PySide6.QtCore import Signal, QObject

from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.dataset.dataset_manager import DataSetManager
from modules.models.sample.sample_model import SampleModel


class DataSetValidator(QObject):
    data_ready = Signal(object)

    def __init__(
        self,
        sample_model: SampleModel,
        configuration_manager: ConfigurationManager,
        dataset_manager: DataSetManager,
        logger: Logger
    ):
        super().__init__()
        self._logger = logger

        if sample_model is None:
            self._logger.error("sample_model cannot be None")
            return

        if configuration_manager is None:
            self._logger.error("configuration manager cannot be None")
            return

        if dataset_manager is None:
            self._logger.error("dataset manager cannot be None")
            return

        self._sample_model = sample_model
        self._configuration_manager = configuration_manager
        self._dataset_manager = dataset_manager
        self._dataset = None
        self._logger = logger

    def validate(self):
        sample_dfs = self._dataset_manager.validation_view_obj()

        self.data_ready.emit(sample_dfs)
