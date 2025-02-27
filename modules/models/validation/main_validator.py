from PySide6.QtCore import QObject, Signal

from modules.models.validation.color_balance_data import ColorBalanceValidator
from modules.models.validation.dataset import DataSetValidator
from modules.models.validation.index_distance_matrix_generator import (
    IndexDistanceMatrixGenerator,
)
from modules.models.validation.pre_validator import PreValidator


class MainValidator(QObject):

    clear_validator_widgets = Signal()
    prevalidator_status = Signal(bool)

    def __init__(self, samples_model, cfg_mgr, dataset_mgr, app_mgr):
        super().__init__()
        self.app_mgr = app_mgr
        self.cfg_mgr = cfg_mgr
        self.dataset_mgr = dataset_mgr

        self.pre_validator = PreValidator(samples_model, cfg_mgr, app_mgr, dataset_mgr)
        self.dataset_validator = DataSetValidator(samples_model, cfg_mgr, dataset_mgr)
        self.index_distance_validator = IndexDistanceMatrixGenerator(
            samples_model, dataset_mgr
        )
        self.color_balance_validator = ColorBalanceValidator(samples_model, dataset_mgr)

    def validate(self):

        self.clear_validator_widgets.emit()

        if not self.pre_validator.validate():
            self.prevalidator_status.emit(False)
            return

        self.prevalidator_status.emit(True)

        self.dataset_mgr.set_data_obj()

        self.dataset_validator.validate()
        self.index_distance_validator.generate()

        if self.dataset_mgr.assess_balance:
            self.color_balance_validator.validate()
