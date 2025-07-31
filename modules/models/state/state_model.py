from logging import Logger
from datetime import datetime
from typing import Tuple

import pandas as pd
from PySide6.QtCore import QObject, Signal, Slot

from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.sample.sample_model import SampleModel


class StateModel(QObject):
    freeze_state_changed = Signal(bool)

    date_changed = Signal(str)
    investigator_changed = Signal(str)
    run_name_changed = Signal(str)
    run_description_changed = Signal(str)
    instrument_changed = Signal(str)
    flowcell_changed = Signal(str)
    lanes_changed = Signal(object)
    chemistry_changed = Signal(str)
    reagent_kit_changed = Signal(str)
    run_read1_cycles_changed = Signal(int)
    run_index1_cycles_changed = Signal(int)
    run_index2_cycles_changed = Signal(int)
    run_read2_cycles_changed = Signal(int)
    i5_seq_orientation_changed = Signal(str)
    i5_samplesheet_orientation_bcl2fastq_changed = Signal(str)
    i5_samplesheet_orientation_bclconvert_changed = Signal(str)
    color_a_changed = Signal(object)
    color_t_changed = Signal(object)
    color_g_changed = Signal(object)
    color_c_changed = Signal(object)
    assess_color_balance_changed = Signal(bool)
    sample_index1_maxlen_changed = Signal(int)
    sample_index2_maxlen_changed = Signal(int)
    sample_index1_minlen_changed = Signal(int)
    sample_index2_minlen_changed = Signal(int)

    run_info_complete = Signal(bool)

    dragen_app_version_changed = Signal(str)

    def __init__(self, sample_model: SampleModel, configuration_manager: ConfigurationManager, logger: Logger):

        super().__init__()

        self._logger = logger
        self._sample_model = sample_model
        self._configuration_manager = configuration_manager

        self._instrument_data = self._configuration_manager.instrument_data

        self._frozen = False

        self._sample_index1_maxlen = 0
        self._sample_index2_maxlen = 0
        self._sample_index1_minlen = 0
        self._sample_index2_minlen = 0

        # RunInfo

        self._date = None
        self._investigator = None
        self._run_name = None
        self._run_description = None

        self._lanes = None
        self._instrument = None
        self._flowcell = None

        self._reagent_kit = None

        self._chemistry = None

        self._read1_cycles = 0
        self._index1_cycles = 0
        self._index2_cycles = 0
        self._read2_cycles = 0

        self._i5_seq_orientation = None
        self._i5_samplesheet_orientation_bcl2fastq = None
        self._i5_samplesheet_orientation_bclconvert = None

        self._color_a = None
        self._color_t = None
        self._color_g = None
        self._color_c = None

        self._assess_color_balance = False

        self._dragen_app_version = None

        self._has_run_info = False

    @staticmethod
    def _current_date_as_string():
        return datetime.now().strftime("%Y-%m-%d")

    def set_lookup_data(self):
        instrument = self._instrument
        if not instrument in self._instrument_data:
            return

        flowcell = self._flowcell
        if not flowcell in self._instrument_data[instrument]["Flowcell"]:
            return

        lanes = self._instrument_data[instrument]["Flowcell"][flowcell]["Lanes"]
        chemistry = self._instrument_data[instrument]["Chemistry"]

        i5_seq_orientation = self._instrument_data[instrument]["I5SampleSheetOrientation"]
        i5_samplesheet_orientation_bcl2fastq = self._instrument_data[instrument]["I5SampleSheetOrientation"][
            "BCL2Fastq"]
        i5_samplesheet_orientation_bclconvert = self._instrument_data[instrument]["I5SampleSheetOrientation"][
            "BCLConvert"]

        assess_color_balance = self._instrument_data[instrument]["AssessColorBalance"]

        color_a = self._instrument_data[instrument]["Fluorophores"]["A"]
        color_t = self._instrument_data[instrument]["Fluorophores"]["T"]
        color_g = self._instrument_data[instrument]["Fluorophores"]["G"]
        color_c = self._instrument_data[instrument]["Fluorophores"]["C"]


        self.set_lanes(lanes)
        self.set_chemistry(chemistry)
        self.set_i5_seq_orientation(i5_seq_orientation)
        self.set_i5_samplesheet_orientation_bcl2fastq(i5_samplesheet_orientation_bcl2fastq)
        self.set_i5_samplesheet_orientation_bclconvert(i5_samplesheet_orientation_bclconvert)
        self.set_assess_color_balance(assess_color_balance)

        self.set_date(self._current_date_as_string())

        self.set_color_a(color_a)
        self.set_color_t(color_t)
        self.set_color_g(color_g)
        self.set_color_c(color_c)

        self._test_runinfo_complete()

    def _test_runinfo_complete(self):
        if not self._date:
            self.run_info_complete.emit(False)
            self._has_run_info = False
            return

        if not self._investigator:
            self.run_info_complete.emit(False)
            self._has_run_info = False
            return

        if not self._run_name:
            self.run_info_complete.emit(False)
            self._has_run_info = False
            return

        if not self._run_description:
            self.run_info_complete.emit(False)
            self._has_run_info = False
            return

        if not self._lanes:
            self.run_info_complete.emit(False)
            self._has_run_info = False
            return

        if not self._instrument:
            self.run_info_complete.emit(False)
            self._has_run_info = False
            return

        if not self._flowcell:
            self.run_info_complete.emit(False)
            self._has_run_info = False
            return

        if not self._reagent_kit:
            self.run_info_complete.emit(False)
            self._has_run_info = False
            return

        if not self._chemistry:
            self.run_info_complete.emit(False)
            self._has_run_info = False
            return

        if not self._read1_cycles:
            self.run_info_complete.emit(False)
            self._has_run_info = False
            return

        if not self._index1_cycles:
            self.run_info_complete.emit(False)
            self._has_run_info = False
            return

        if not self._index2_cycles:
            self.run_info_complete.emit(False)
            self._has_run_info = False
            return

        if not self._read2_cycles:
            self.run_info_complete.emit(False)
            self._has_run_info = False
            return

        if not self._i5_seq_orientation:
            self.run_info_complete.emit(False)
            self._has_run_info = False
            return

        if not self._i5_samplesheet_orientation_bcl2fastq:
            self.run_info_complete.emit(False)
            self._has_run_info = False
            return

        if not self._i5_samplesheet_orientation_bclconvert:
            self.run_info_complete.emit(False)
            self._has_run_info = False
            return

        if not self._color_a:
            self.run_info_complete.emit(False)
            self._has_run_info = False
            return

        if not self._color_t:
            self.run_info_complete.emit(False)
            self._has_run_info = False
            return

        if not self._color_g:
            self.run_info_complete.emit(False)
            self._has_run_info = False
            return

        if not self._color_c:
            self.run_info_complete.emit(False)
            self._has_run_info = False
            return

        if not self._assess_color_balance:
            self.run_info_complete.emit(False)
            self._has_run_info = False
            return

        self._has_run_info = True
        self.run_info_complete.emit(True)

    @staticmethod
    def _get_str_lengths_in_df_col(pandas_col: pd.Series) -> Tuple[int, int]:

        # Filter out empty/None values and get string lengths
        lengths = pandas_col.dropna().astype(str).str.len()
        if len(lengths) == 0:
            return 0, 0
        return lengths.min(), lengths.max()

    def update_index_lengths(self):
        """Update the minimum and maximum lengths of index sequences from the sample model."""
        df = self._sample_model.to_dataframe()

        # Get lengths for both index columns
        i7_min, i7_max = self._get_str_lengths_in_df_col(df["IndexI7"])
        i5_min, i5_max = self._get_str_lengths_in_df_col(df["IndexI5"])

        # Update the state model
        self._sample_index1_minlen = int(i7_min)
        self._sample_index1_maxlen = int(i7_max)
        self._sample_index2_minlen = int(i5_min)
        self._sample_index2_maxlen = int(i5_max)

        # Emit signals for any UI updates
        self.sample_index1_minlen_changed.emit(self._sample_index1_minlen)
        self.sample_index1_maxlen_changed.emit(self._sample_index1_maxlen)
        self.sample_index2_minlen_changed.emit(self._sample_index2_minlen)
        self.sample_index2_maxlen_changed.emit(self._sample_index2_maxlen)


    def set_assess_color_balance(self, assess_color_balance: bool):

        print(assess_color_balance)

        if self._assess_color_balance == assess_color_balance:
            return

        self._assess_color_balance = assess_color_balance
        self.assess_color_balance_changed.emit(assess_color_balance)


    def set_color_a(self, color_a: object):

        if self._color_t == color_a:
            return

        self._color_a = color_a
        self.color_a_changed.emit(color_a)

    def set_color_t(self, color_t: object):
        if self._color_t == color_t:
            return

        self._color_t = color_t
        self.color_t_changed.emit(color_t)

    def set_color_g(self, color_g: object):
        if self._color_g == color_g:
            return

        self._color_g = color_g
        self.color_g_changed.emit(color_g)

    def set_color_c(self, color_c: object):
        if self._color_c == color_c:
            return

        self._color_c = color_c
        self.color_c_changed.emit(color_c)

    def set_chemistry(self, chemistry: str):

        if self._chemistry == chemistry:
            print("Same")
            return

        self._chemistry = chemistry
        self.chemistry_changed.emit(chemistry)

    def set_date(self, date: str):

        if self._date == date:
            return

        self._date = date
        self.date_changed.emit(date)

    @property
    def date(self):
        return self._date

    def set_investigator(self, investigator: str):

        if self._investigator == investigator:
            return

        self._investigator = investigator
        self.investigator_changed.emit(investigator)

    @property
    def investigator(self):
        return self._investigator


    def set_flowcell(self, flowcell: str):

        if self._flowcell == flowcell:
            return

        self._flowcell = flowcell
        self.flowcell_changed.emit(flowcell)

    @property
    def flowcell(self):
        return self._flowcell


    def set_run_name(self, run_name: str):

        if self._run_name == run_name:
            return

        self._run_name = run_name
        self.run_name_changed.emit(run_name)

    @property
    def run_name(self):
        return self._run_name

    def set_run_description(self, run_desc: str):

        if self._run_description == run_desc:
            return

        self._run_description = run_desc
        self.run_description_changed.emit(run_desc)

    @property
    def run_description(self):
        return self._run_description

    def set_instrument(self, instrument: str):

        if self._instrument == instrument:
            return

        self._instrument = instrument
        self.instrument_changed.emit(instrument)

    @property
    def instrument(self):
        return self._instrument

    def set_reagent_kit(self, reagent_kit: str):

        if self._reagent_kit == reagent_kit:
            return

        self._reagent_kit = reagent_kit
        self.reagent_kit_changed.emit(reagent_kit)

    def set_i5_samplesheet_orientation_bcl2fastq(self, i5_samplesheet_orientation_bcl2fastq: str):

        if self._i5_samplesheet_orientation_bcl2fastq == i5_samplesheet_orientation_bcl2fastq:
            return

        self._i5_samplesheet_orientation_bcl2fastq = i5_samplesheet_orientation_bcl2fastq
        self.i5_samplesheet_orientation_bcl2fastq_changed.emit(i5_samplesheet_orientation_bcl2fastq)

    def i5_samplesheet_orientation_bcl2fastq(self):
        return self._i5_samplesheet_orientation_bcl2fastq

    def set_i5_samplesheet_orientation_bclconvert(self, i5_samplesheet_orientation_bclconvert: str):

        if self._i5_samplesheet_orientation_bclconvert == i5_samplesheet_orientation_bclconvert:
            return

        self._i5_samplesheet_orientation_bclconvert = i5_samplesheet_orientation_bclconvert
        self.i5_samplesheet_orientation_bclconvert_changed.emit(i5_samplesheet_orientation_bclconvert)

    def i5_samplesheet_orientation_bclconvert(self):
        return self._i5_samplesheet_orientation_bclconvert


    @property
    def reagent_kit(self):
        return self._reagent_kit

    def set_lanes(self, lanes: list[int]):

        if self._lanes == lanes:
            return

        self._lanes = lanes
        self.lanes_changed.emit(lanes)

    @property
    def lanes(self):
        return self._lanes

    def set_read1_cycles(self, run_read1_cycles: int):

        if self._read1_cycles == run_read1_cycles:
            return

        self._read1_cycles = run_read1_cycles
        self.run_read1_cycles_changed.emit(run_read1_cycles)

    @property
    def read1_cycles(self):
        return self._read1_cycles

    def set_index1_cycles(self, run_index1_cycles: int):

        if self._index1_cycles == run_index1_cycles:
            return

        self._index1_cycles = run_index1_cycles
        self.run_index1_cycles_changed.emit(run_index1_cycles)

    @property
    def index1_cycles(self):
        return self._index1_cycles

    def set_index2_cycles(self, run_index2_cycles: int):

        if self._index2_cycles == run_index2_cycles:
            return

        self._index2_cycles = run_index2_cycles
        self.run_index2_cycles_changed.emit(run_index2_cycles)

    @property
    def index2_cycles(self):
        return self._index2_cycles

    def set_read2_cycles(self, run_read2_cycles: int):

        if self._read2_cycles == run_read2_cycles:
            return

        self._read2_cycles = run_read2_cycles
        self.run_read2_cycles_changed.emit(run_read2_cycles)

    @property
    def read2_cycles(self):
        return self._read2_cycles

    def set_i5_seq_orientation(self, i5_seq_orientation: str):
        self._i5_seq_orientation = i5_seq_orientation
        self.i5_seq_orientation_changed.emit(i5_seq_orientation)

    @property
    def i5_seq_orientation(self):
        return self._i5_seq_orientation

    def set_dragen_app_version(self, dragen_app_version):

        if self._dragen_app_version == dragen_app_version:
            return

        self._dragen_app_version = dragen_app_version
        self.dragen_app_version_changed.emit(dragen_app_version)

    @property
    def dragen_app_version(self):
        return self._dragen_app_version

    def freeze(self):
        self._frozen = True
        self.freeze_state_changed.emit(self._frozen)

    def unfreeze(self):
        self._frozen = False
        self.freeze_state_changed.emit(self._frozen)

    def set_sample_index1_minlen(self, sample_index1_minlen):
        if self._sample_index1_minlen == sample_index1_minlen:
            return

        self._sample_index1_minlen = sample_index1_minlen
        self.sample_index1_minlen_changed.emit(self._sample_index1_minlen)
        self.unfreeze()

    def set_sample_index2_minlen(self, sample_index2_minlen):
        if self._sample_index2_minlen == sample_index2_minlen:
            return

        self._sample_index2_minlen = sample_index2_minlen
        self.sample_index2_minlen_changed.emit(self._sample_index2_minlen)
        self.unfreeze()

    def set_sample_index1_maxlen(self, sample_index1_maxlen):
        if self._sample_index1_minlen == sample_index1_maxlen:
            return

        self._sample_index1_maxlen = sample_index1_maxlen
        self.sample_index1_maxlen_changed.emit(self._sample_index1_maxlen)
        self.unfreeze()

    def set_sample_index2_maxlen(self, sample_index2_maxlen):
        if self._sample_index2_maxlen == sample_index2_maxlen:
            return

        self._sample_index2_maxlen = sample_index2_maxlen
        self.sample_index2_maxlen_changed.emit(self._sample_index2_maxlen)
        self.unfreeze()

    @property
    def sample_df(self) -> pd.DataFrame:
        return self._sample_model.to_dataframe()

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

    @property
    def has_run_info(self) -> bool:
        return self._has_run_info
