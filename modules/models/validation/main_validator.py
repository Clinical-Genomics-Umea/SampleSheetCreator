from logging import Logger

from PySide6.QtCore import QObject, Signal
from pydantic_core.core_schema import general_wrap_validator_function

from modules.models.state.state_model import StateModel
from modules.models.validation.color_balance.color_balance_data_generator import ColorBalanceDataGenerator
from modules.models.validation.sample_data_overview.sample_data_overview import SampleDataOverviewGenerator
from modules.models.validation.index_distance.index_distance_data_generator import (
    IndexDistanceDataGenerator,
)
from modules.models.validation.general_validation.general_validator import GeneralValidator


class MainValidator(QObject):

    clear_validator_widgets = Signal()
    prevalidation_failed = Signal()
    prevalidation_success = Signal()

    def __init__(self,
                 general_validator: GeneralValidator,
                 sample_data_overview_generator: SampleDataOverviewGenerator,
                 index_distance_data_generator: IndexDistanceDataGenerator,
                 color_balance_data_generator: ColorBalanceDataGenerator,
                 state_model: StateModel,
                 logger: Logger
                 ):

        super().__init__()

        self._general_validator = general_validator
        self._sample_data_overview_generator = sample_data_overview_generator
        self._index_distance_data_generator = index_distance_data_generator
        self._color_balance_data_generator = color_balance_data_generator
        self._state_model = state_model
        self._logger = logger

    def general_validate(self):
        self.clear_validator_widgets.emit()
        self._general_validator.validate()

    def populate_manual_overview_widgets(self):

        self._sample_data_overview_generator.data_to_data_widget()
        self._index_distance_data_generator.generate()
        self._color_balance_data_generator.generate()


