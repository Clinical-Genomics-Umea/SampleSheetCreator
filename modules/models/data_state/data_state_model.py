from PySide6.QtCore import QObject

from modules.models.rundata.rundata_model import RunDataModel
from modules.models.sample.sample_model import SampleModel


class DataStateModel(QObject):
    def __init__(self, sample_model: SampleModel, rundata_model: RunDataModel):
        super().__init__()

        self._read_cycles_dict = {}
        self._read_cycles_fields = []
        self._read_cycles_list = []
        self._has_rundata = False

        self._max_index_i5_len = 0
        self._max_index_i7_len = 0
        self._min_index_i7_len = 0
        self._min_index_i5_len = 0





