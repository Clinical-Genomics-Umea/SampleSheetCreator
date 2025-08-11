from logging import Logger

from PySide6.QtCore import QObject, Signal

from modules.models.state.state_model import StateModel
from modules.models.validation.color_balance.color_balance_validator import ColorBalanceValidator
from modules.models.validation.dataset.dataset_validator import DataSetValidator
from modules.models.validation.index_distance.index_distance_matrix_generator import (
    IndexDistanceValidator,
)
from modules.models.validation.prevalidation.prevalidator import PreValidator


class MainValidator(QObject):

    clear_validator_widgets = Signal()
    prevalidation_failed = Signal()
    prevalidation_success = Signal()

    def __init__(self,
                 prevalidator: PreValidator,
                 dataset_validator: DataSetValidator,
                 index_distance_validator: IndexDistanceValidator,
                 color_balance_validator: ColorBalanceValidator,
                 state_model: StateModel,
                 logger: Logger
                 ):

        super().__init__()

        self._prevalidator = prevalidator
        self._dataset_validator = dataset_validator
        self._index_distance_validator = index_distance_validator
        self._color_balance_validator = color_balance_validator
        self._state_model = state_model
        self._logger = logger


    def validate(self):
        print("validate")
        self.clear_validator_widgets.emit()

        if not self._prevalidator.validate():
            self.prevalidation_failed.emit()
            return

        # self.prevalidation_success.emit()
        # self._dataset_validator.validate()
        # self._index_distance_validator.generate()
        # #
        # if self._state_model.assess_color_balance:
        #     self._color_balance_validator.validate()

