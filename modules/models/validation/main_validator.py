from logging import Logger

from PySide6.QtCore import QObject, Signal

from modules.models.application.application_manager import ApplicationManager
from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.dataset.dataset_manager import DataSetManager
from modules.models.sample.sample_model import SampleModel
from modules.models.validation.color_balance_validator import ColorBalanceValidator
from modules.models.validation.dataset_validator import DataSetValidator
from modules.models.validation.index_distance_matrix_generator import (
    IndexDistanceValidator,
)
from modules.models.validation.prevalidator import PreValidator


class MainValidator(QObject):

    clear_validator_widgets = Signal()
    pre_validator_status = Signal(bool)

    def __init__(self,
                 prevalidator: PreValidator,
                 dataset_validator: DataSetValidator,
                 index_distance_validator: IndexDistanceValidator,
                 color_balance_validator: ColorBalanceValidator,
                 dataset_manager: DataSetManager,
                 logger: Logger
                 ):

        super().__init__()

        self._prevalidator = prevalidator
        self._dataset_validator = dataset_validator
        self._index_distance_validator = index_distance_validator
        self._color_balance_validator = color_balance_validator
        self._dataset_manager = dataset_manager
        self._logger = logger


    def validate(self):

        self.clear_validator_widgets.emit()

        if not self._prevalidator.validate():
            self.pre_validator_status.emit(False)
            return

        self.pre_validator_status.emit(True)

        self._dataset_manager.set_data_obj()

        self._dataset_validator.validate()

        self._index_distance_validator.generate()
        #
        if self._dataset_manager.assess_balance:
            self._color_balance_validator.validate()

