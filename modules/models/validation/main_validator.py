from logging import Logger

from PySide6.QtCore import QObject, Signal

from modules.models.application.application_manager import ApplicationManager
from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.dataset.dataset_manager import DataSetManager
from modules.models.sample.sample_model import SampleModel
from modules.models.validation.color_balance_data import ColorBalanceValidator
from modules.models.validation.dataset import DataSetValidator
from modules.models.validation.index_distance_matrix_generator import (
    IndexDistanceMatrixGenerator,
)
from modules.models.validation.pre_validator import PreValidator


class MainValidator(QObject):

    clear_validator_widgets = Signal()
    pre_validator_status = Signal(bool)

    def __init__(self,
                 sample_model: SampleModel,
                 configuration_manager: ConfigurationManager,
                 dataset_manager: DataSetManager,
                 application_manager: ApplicationManager,
                 logger: Logger):
        super().__init__()
        self._application_manager = application_manager
        self._configuration_manager = configuration_manager
        self._dataset_manager = dataset_manager
        self._logger = logger

        self.pre_validator = PreValidator(sample_model, configuration_manager,
                                          application_manager, dataset_manager, logger)
        self.dataset_validator = DataSetValidator(sample_model, configuration_manager, dataset_manager, logger)
        self.index_distance_validator = IndexDistanceMatrixGenerator(
            sample_model, dataset_manager, logger
        )
        self.color_balance_validator = ColorBalanceValidator(sample_model, dataset_manager, logger)

    def validate(self):

        self.clear_validator_widgets.emit()

        if not self.pre_validator.validate():
            self.pre_validator_status.emit(False)
            return

        self.pre_validator_status.emit(True)

        self._dataset_manager.set_data_obj()

        self.dataset_validator.validate()
        self.index_distance_validator.generate()

        if self._dataset_manager.assess_balance:
            self.color_balance_validator.validate()
