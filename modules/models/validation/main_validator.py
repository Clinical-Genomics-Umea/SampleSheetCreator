from logging import Logger

from PySide6.QtCore import QObject, Signal

from modules.models.state.state_model import StateModel
from modules.models.validation.color_balance.color_balance_data_generator import ColorBalanceDataGenerator
from modules.models.validation.sample_data_overview_prepare.sample_data_overview_prepare import SampleDataOverviewGenerator
from modules.models.validation.index_distance.index_distance_data_generator import (
    IndexDistanceDataGenerator,
)
from modules.models.validation.prevalidation.prevalidator import PreValidator


class MainValidator(QObject):

    clear_validator_widgets = Signal()
    prevalidation_failed = Signal()
    prevalidation_success = Signal()

    def __init__(self,
                 prevalidator: PreValidator,
                 sample_data_overview_generator: SampleDataOverviewGenerator,
                 index_distance_data_generator: IndexDistanceDataGenerator,
                 color_balance_data_generator: ColorBalanceDataGenerator,
                 state_model: StateModel,
                 logger: Logger
                 ):

        super().__init__()

        self._prevalidator = prevalidator
        self._sample_data_overview_generator = sample_data_overview_generator
        self._index_distance_data_generator = index_distance_data_generator
        self._color_balance_data_generator = color_balance_data_generator
        self._state_model = state_model
        self._logger = logger

    def pre_validate(self):
        self.clear_validator_widgets.emit()
        self._prevalidator.validate()

    def populate_manual_overview_widgets(self):

        self._sample_data_overview_generator.data_to_data_widget()
        self._index_distance_data_generator.generate()
        self._color_balance_data_generator.generate()


