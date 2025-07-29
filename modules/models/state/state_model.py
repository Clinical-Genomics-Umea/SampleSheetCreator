from logging import Logger

from PySide6.QtCore import QObject, Signal, Slot
from modules.utils.utils import json_to_obj


class StateModel(QObject):
    freeze_state_changed = Signal(bool)

    def __init__(self, logger: Logger):

        super().__init__()

        self._logger = logger
        self._frozen = False

        self._sample_index1_maxlen = 0
        self._sample_index2_maxlen = 0
        self._sample_index1_minlen = 0
        self._sample_index2_minlen = 0

        self._runcycles_index1 = None
        self._runcycles_index2 = None

        self._dragen_app_version = None

    def set_dragen_app_version(self, dragen_app_version):
        self._dragen_app_version = dragen_app_version

    @property
    def dragen_app_version(self):
        return self._dragen_app_version

    def freeze(self):
        self._frozen = True
        self.freeze_state_changed.emit(self._frozen)

    def unfreeze(self):
        self._frozen = False
        self.freeze_state_changed.emit(self._frozen)

    @Slot(int, int)
    def set_runcycles_index_data(self, runcycles_index1, runcycles_index2):
        self._runcycles_index1 = runcycles_index1
        self._runcycles_index2 = runcycles_index2
        self.unfreeze()

    @Slot(int, int, int, int)
    def set_sample_index_len_minmax(self, sample_index1_minlen, sample_index1_maxlen,
                                    sample_index2_minlen, sample_index2_maxlen):

        self._sample_index1_minlen = sample_index1_minlen
        self._sample_index1_maxlen = sample_index1_maxlen

        self._sample_index2_minlen = sample_index2_minlen
        self._sample_index2_maxlen = sample_index2_maxlen

        self.unfreeze()

    @property
    def sample_index1_maxlen(self) -> int:
        return self._sample_index1_maxlen

    @property
    def sample_index2_maxlen(self) -> int:
        return self._sample_index2_maxlen

    @property
    def sample_index1_minlen(self) -> int:
        return self._sample_index1_minlen

    @property
    def sample_index2_minlen(self) -> int:
        return self._sample_index2_minlen

    @property
    def runcycles_index1(self) -> int:
        return self._runcycles_index1

    @property
    def runcycles_index2(self) -> int:
        return self._runcycles_index2

    @property
    def frozen(self) -> bool:
        return self._frozen
