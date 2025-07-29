from logging import Logger

from PySide6.QtCore import QObject, Signal, Slot
from modules.utils.utils import json_to_obj


class StateModel(QObject):
    freeze_state_changed = Signal(bool)

    date_changed = Signal(str)
    investigator_changed = Signal(str)
    run_name_changed = Signal(str)
    run_desc_changed = Signal(str)
    lanes_changed = Signal(int)
    run_read1_cycles_changed = Signal(int)
    run_index1_cycles_changed = Signal(int)
    run_index2_cycles_changed = Signal(int)
    run_read2_cycles_changed = Signal(int)
    i5_seq_orientation_changed = Signal(str)
    color_A_changed = Signal(str)
    color_T_changed = Signal(str)
    color_G_changed = Signal(str)
    color_C_changed = Signal(str)
    asses_color_balance_changed = Signal(bool)
    sample_index1_maxlen_changed = Signal(int)
    sample_index2_maxlen_changed = Signal(int)
    sample_index1_minlen_changed = Signal(int)
    sample_index2_minlen_changed = Signal(int)
    runcycles_index1_changed = Signal(int)

    def __init__(self, logger: Logger):

        super().__init__()

        self._logger = logger
        self._frozen = False

        self._sample_index1_maxlen = 0
        self._sample_index2_maxlen = 0
        self._sample_index1_minlen = 0
        self._sample_index2_minlen = 0

        # RunInfo

        self._date = None
        self._investigator = None
        self._run_name = None
        self._run_desc = None

        self._lanes = None

        self._run_read1_cycles = 0
        self._run_index1_cycles = 0
        self._run_index2_cycles = 0
        self._run_read2_cycles = 0

        self._i5_seq_orientation = None

        self._color_A = None
        self._color_T = None
        self._color_G = None
        self._color_C = None

        self._asses_color_balance = False

        self._runcycles_index1 = None
        self._runcycles_index2 = None

        self._dragen_app_version = None

        self._has_rundata = False

    def set_date(self, date: str):
        self._date = date
        self.date_changed.emit(date)

    @property
    def date(self):
        return self._date

    def set_investigator(self, investigator: str):
        self._investigator = investigator
        self.investigator_changed.emit(investigator)

    @property
    def investigator(self):
        return self._investigator

    def set_run_name(self, run_name: str):
        self._run_name = run_name
        self.run_name_changed.emit(run_name)

    @property
    def run_name(self):
        return self._run_name


    def set_run_desc(self, run_desc: str):
        self._run_desc = run_desc
        self.run_desc_changed.emit(run_desc)

    @property
    def run_desc(self):
        return self._run_desc

    def set_lanes(self, lanes: list[int]):
        self._lanes = lanes
        self.lanes_changed.emit(lanes)

    @property
    def lanes(self):
        return self._lanes

    def set_run_read1_cycles(self, run_read1_cycles: int):
        self._run_read1_cycles = run_read1_cycles
        self.run_read1_cycles_changed.emit(run_read1_cycles)

    @property
    def run_read1_cycles(self):
        return self._run_read1_cycles

    def set_run_index1_cycles(self, run_index1_cycles: int):
        self._run_index1_cycles = run_index1_cycles
        self.run_index1_cycles_changed.emit(run_index1_cycles)

    @property
    def run_index1_cycles(self):
        return self._run_index1_cycles

    def set_run_index2_cycles(self, run_index2_cycles: int):
        self._run_index2_cycles = run_index2_cycles
        self.run_index2_cycles_changed.emit(run_index2_cycles)

    @property
    def run_index2_cycles(self):
        return self._run_index2_cycles

    def set_run_read2_cycles(self, run_read2_cycles: int):
        self._run_read2_cycles = run_read2_cycles
        self.run_read2_cycles_changed.emit(run_read2_cycles)

    @property
    def run_read2_cycles(self):
        return self._run_read2_cycles

    def set_i5_seq_orientation(self, i5_seq_orientation: str):
        self._i5_seq_orientation = i5_seq_orientation
        self.i5_seq_orientation_changed.emit(i5_seq_orientation)

    @property
    def i5_seq_orientation(self):
        return self._i5_seq_orientation


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
