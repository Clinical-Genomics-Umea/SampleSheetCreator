"""
StateModel - Centralized state management for the application.

This class manages the application's state including run information, sample data,
instrument configuration, and validation states. It provides a reactive interface
using Qt signals to notify about state changes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from logging import Logger
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from PySide6.QtCore import QObject, Signal, Slot

from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.sample.sample_model import SampleModel


class RunState(Enum):
    """Enum representing the possible run states."""
    UNINITIALIZED = auto()
    CONFIGURING = auto()
    READY = auto()
    FROZEN = auto()
    ERROR = auto()


@dataclass
class RunInfo:
    """Data class holding run information with validation."""
    date: str = ""
    investigator: str = ""
    run_name: str = ""
    run_description: str = ""
    instrument: str = ""
    flowcell: str = ""
    lanes: List[int] = field(default_factory=list)
    chemistry: str = ""
    reagent_kit: str = ""

    read1_cycles: int = 0
    index1_cycles: int = 0
    index2_cycles: int = 0
    read2_cycles: int = 0

    sample_index1_maxlen: int = 0
    sample_index2_maxlen: int = 0
    sample_index1_minlen: int = 0
    sample_index2_minlen: int = 0

    i5_seq_orientation: str = ""
    i5_samplesheet_orientation_bcl2fastq: str = ""
    i5_samplesheet_orientation_bclconvert: str = ""
    color_a: Any = None
    color_t: Any = None
    color_g: Any = None
    color_c: Any = None
    assess_color_balance: bool = False
    dragen_app_version: str = ""


class StateModel(QObject):
    """
    Central state management for the application.
    
    This class manages the application's state and provides a reactive interface
    using Qt signals to notify about state changes. It maintains consistency
    between different parts of the application and validates state transitions.
    """
    
    # State change signals
    freeze_state_changed = Signal(bool)
    state_changed = Signal(dict)  # Generic signal for any state change
    
    # Run information signals
    date_changed = Signal(str)
    investigator_changed = Signal(str)
    run_name_changed = Signal(str)
    run_description_changed = Signal(str)
    instrument_changed = Signal(str)
    flowcell_changed = Signal(str)
    lanes_changed = Signal(list)  # More specific type hint
    chemistry_changed = Signal(str)
    reagent_kit_changed = Signal(str)
    run_cycles_changed = Signal(int, int, int, int) # read1_cycles, index1_cycles, index2_cycles, read2_cycles
    read1_cycles_changed = Signal(int)
    index1_cycles_changed = Signal(int)
    index2_cycles_changed = Signal(int)
    read2_cycles_changed = Signal(int)
    i5_seq_orientation_changed = Signal(str)
    i5_samplesheet_orientation_bcl2fastq_changed = Signal(str)
    i5_samplesheet_orientation_bclconvert_changed = Signal(str)
    
    # Color signals
    color_a_changed = Signal(object)
    color_t_changed = Signal(object)
    color_g_changed = Signal(object)
    color_c_changed = Signal(object)

    # Color balance signals
    assess_color_balance_changed = Signal(bool)
    
    # Index length signals
    sample_index1_maxlen_changed = Signal(int)
    sample_index2_maxlen_changed = Signal(int)
    sample_index1_minlen_changed = Signal(int)
    sample_index2_minlen_changed = Signal(int)
    
    # Application state signals
    run_info_complete = Signal(bool)
    dragen_app_version_changed = Signal(str)

    def __init__(self, sample_model: SampleModel, configuration_manager: ConfigurationManager, logger: Logger):
        """Initialize the StateModel with required dependencies.
        
        Args:
            sample_model: The sample model containing sample data
            configuration_manager: The configuration manager for application settings
            logger: Logger instance for logging messages
        """
        super().__init__()
        
        # Dependencies
        self._logger = logger
        self._sample_model = sample_model
        self._configuration_manager = configuration_manager
        self._instrument_data = self._configuration_manager.instrument_data
        
        # State tracking
        self._state = RunState.UNINITIALIZED
        self._frozen = False
        self._has_run_info = False
        
        # Initialize run info with default values
        self._run_info = RunInfo()
        
        # Initialize index length tracking

    
    # --- State Management ---
    
    @property
    def state(self) -> RunState:
        """Get the current application state."""
        return self._state
    
    @state.setter
    def state(self, new_state: RunState) -> None:
        """Update the application state and emit appropriate signals."""
        if self._state != new_state:
            old_state = self._state
            self._state = new_state
            self._logger.debug(f"State changed from {old_state} to {new_state}")
            self.state_changed.emit({"old_state": old_state, "new_state": new_state})
    
    @property
    def frozen(self) -> bool:
        """Check if the state is frozen (read-only)."""
        return self._frozen
    
    def freeze(self) -> None:
        """Freeze the state to prevent modifications."""
        if not self._frozen:
            self._frozen = True
            self.freeze_state_changed.emit(True)
            self.state = RunState.FROZEN
    
    def unfreeze(self) -> None:
        """Unfreeze the state to allow modifications."""
        if self._frozen:
            self._frozen = False
            self.freeze_state_changed.emit(False)
            self.state = RunState.READY if self._has_run_info else RunState.CONFIGURING
    
    # --- Run Info Management ---
    
    @property
    def run_info(self) -> RunInfo:
        """Get a copy of the current run information."""
        return RunInfo(**self._run_info.__dict__)
    
    def set_run_setup_data(self, run_setpup_data: dict) -> None:
        """Update run info and emit appropriate signals.
        
        Args:
            **kwargs: Key-value pairs of run info fields to update
            
        Returns:
            Tuple[bool, dict]: (success, validation_results)
                - success: True if all updates were applied successfully
                - validation_results: Results from _validate_run_info() if validation was performed
        """

        print(run_setpup_data)
        if not run_setpup_data:
            self._logger.debug("No fields to update in update_run_info")
            return

        changed = False

        
        # Apply updates and track changes
        for key, value in run_setpup_data.items():
            if not hasattr(self._run_info, key):
                self._logger.warning(f"Attempted to set unknown run info field: {key}")
                continue
                
            current_value = getattr(self._run_info, key)
            if current_value != value:
                setattr(self._run_info, key, value)
                changed = True

                # Emit specific signal for this property
                signal_name = f"{key}_changed"
                if hasattr(self, signal_name):
                    getattr(self, signal_name).emit(value)

        self._set_dependent_data_from_config()

        # If anything changed, validate the run info
        if changed:
            self._logger.debug(f"Run info changed: {run_setpup_data}")
        else:
            self._logger.debug("No changes detected in _update_run_info")

        # validation_results = self._validate_run_info()
        # return changed, validation_results


    def _validate_run_info(self) -> None:
        """Validate all run info fields and update completion status.
        
        Returns:
            bool: True if all validations pass, False otherwise
            dict: Dictionary containing validation results for each field
        """
        validations = {
            'required_fields': {
                'date': bool(self._run_info.date),
                'investigator': bool(self._run_info.investigator),
                'run_name': bool(self._run_info.run_name),
                'run_description': bool(self._run_info.run_description),
                'lanes': bool(self._run_info.lanes),
                'instrument': bool(self._run_info.instrument),
                'flowcell': bool(self._run_info.flowcell),
                'chemistry': bool(self._run_info.chemistry),
                'reagent_kit': bool(self._run_info.reagent_kit),
                'i5_seq_orientation': bool(self._run_info.i5_seq_orientation),
                'i5_samplesheet_orientation_bcl2fastq': bool(self._run_info.i5_samplesheet_orientation_bcl2fastq),
                'i5_samplesheet_orientation_bclconvert': bool(self._run_info.i5_samplesheet_orientation_bclconvert),
            },
            'numeric_fields': {
                'read1_cycles': self._run_info.read1_cycles > 0,
                'index1_cycles': self._run_info.index1_cycles >= 0,
                'index2_cycles': self._run_info.index2_cycles >= 0,
                'read2_cycles': self._run_info.read2_cycles >= 0,
            },
            'color_balance_fields': {
                'color_a': self._run_info.color_a is not None,
                'color_t': self._run_info.color_t is not None,
                'color_g': self._run_info.color_g is not None,
                'color_c': self._run_info.color_c is not None,
            }
        }
        
        # Check if all validations pass
        all_required = all(validations['required_fields'].values())
        all_numeric = all(validations['numeric_fields'].values())
        color_balance_ok = not self._run_info.assess_color_balance or all(validations['color_balance_fields'].values())
        all_valid = all_required and all_numeric and color_balance_ok
        
        # Log validation failures
        if not all_valid:
            failed = [k for k, v in validations['required_fields'].items() if not v]
            if failed:
                self._logger.warning(f"Missing required fields: {', '.join(failed)}")
                
            failed = [k for k, v in validations['numeric_fields'].items() if not v]
            if failed:
                self._logger.warning(f"Invalid numeric fields: {', '.join(failed)}")
                
            if self._run_info.assess_color_balance:
                failed = [k for k, v in validations['color_balance_fields'].items() if not v]
                if failed:
                    self._logger.warning(f"Missing color values: {', '.join(failed)}")
        
        # Update state if changed
        if all_valid != self._has_run_info:
            self._has_run_info = all_valid
            self.run_info_complete.emit(all_valid)
            
            # Update application state based on run info completion
            if all_valid and not self._frozen:
                self.state = RunState.READY
                
        return all_valid, validations
    
    # --- Index Length Management ---
    
    def _update_index_lengths(self) -> None:
        """Update index lengths from the sample model."""
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

    @staticmethod
    def _current_date_as_string():
        return datetime.now().strftime("%Y-%m-%d")

    def _set_dependent_data_from_config(self):
        instrument = self._run_info.instrument
        if not instrument in self._instrument_data:
            return

        flowcell = self._run_info.flowcell
        if not flowcell in self._instrument_data[instrument]["Flowcell"]:
            return

        lanes = (
            self._instrument_data.get(instrument, {})
            .get("Flowcell", {})
            .get(flowcell, {})
            .get("Lanes")
        )

        chemistry = (self._instrument_data.get(instrument, {})
                     .get("Chemistry", "UNKNOWN")
        )

        i5_seq_orientation = (
            self._instrument_data.get(instrument, {})
            .get("I5SampleSheetOrientation")
        )

        i5_samplesheet_orientation_bcl2fastq = (
            self._instrument_data.get(instrument, {})
            .get("I5SampleSheetOrientation", {})
            .get("BCL2Fastq")
        )

        i5_samplesheet_orientation_bclconvert = (
            self._instrument_data.get(instrument, {})
            .get("I5SampleSheetOrientation", {})
            .get("BCLConvert")
        )

        assess_color_balance = self._instrument_data.get(instrument, {}).get("AssessColorBalance")

        color_a = (
            self._instrument_data.get(instrument, {})
            .get("Fluorophores", {})
            .get("A")
        )
        color_t = (
            self._instrument_data.get(instrument, {})
            .get("Fluorophores", {})
            .get("T")
        )
        color_g = (
            self._instrument_data.get(instrument, {})
            .get("Fluorophores", {})
            .get("G")
        )
        color_c = (
            self._instrument_data.get(instrument, {})
            .get("Fluorophores", {})
            .get("C")
        )

        self.lanes = lanes
        self.chemistry = chemistry
        self.i5_seq_orientation = i5_seq_orientation
        self.i5_samplesheet_orientation_bcl2fastq = i5_samplesheet_orientation_bcl2fastq
        self.i5_samplesheet_orientation_bclconvert = i5_samplesheet_orientation_bclconvert
        self.assess_color_balance = assess_color_balance

        self.date = self._current_date_as_string()

        self.color_a = color_a
        self.color_t = color_t
        self.color_g = color_g
        self.color_c = color_c

        self._sample_index1_minlen = 0
        self._sample_index1_maxlen = 0
        self._sample_index2_minlen = 0
        self._sample_index2_maxlen = 0

        self._check_run_info_complete()


    def _check_run_info_complete(self) -> None:
        """Validate that all required run info fields are populated.
        
        This method checks that all required fields in the run info have been set to non-empty/non-None values.
        It emits the appropriate signals to indicate whether the run info is complete.
        
        The method will set `_has_run_info` to True only if all required fields are present.
        """
        # List of required fields to validate
        required_fields = [
            # Basic run information
            'date', 'investigator', 'run_name', 'run_description',
            # Instrument and flowcell details
            'instrument', 'flowcell', 'chemistry', 'reagent_kit',
            # Run cycles configuration
            'read1_cycles', 'index1_cycles', 'index2_cycles', 'read2_cycles',
            # Index orientation settings
            'i5_seq_orientation', 'i5_samplesheet_orientation_bcl2fastq',
            'i5_samplesheet_orientation_bclconvert',
            # Color balance configuration
            'color_a', 'color_t', 'color_g', 'color_c', 'assess_color_balance',
            # Sample information
            'lanes'
        ]
        
        # Check each required field
        for field_name in required_fields:
            field_value = getattr(self._run_info, field_name, None)
            if not field_value:
                if self._has_run_info:  # Only emit if state is changing
                    self.run_info_complete.emit(False)
                self._has_run_info = False
                return
        
        # All fields are valid
        if not self._has_run_info:  # Only emit if state is changing
            self.run_info_complete.emit(True)
        self._has_run_info = True

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
        self._run_info.sample_index1_minlen = int(i7_min)
        self._run_info.sample_index1_maxlen = int(i7_max)
        self._run_info.sample_index2_minlen = int(i5_min)
        self._run_info.sample_index2_maxlen = int(i5_max)

        # Emit signals for any UI updates
        self.sample_index1_minlen_changed.emit(self._run_info.sample_index1_minlen)
        self.sample_index1_maxlen_changed.emit(self._run_info.sample_index1_maxlen)
        self.sample_index2_minlen_changed.emit(self._run_info.sample_index2_minlen)
        self.sample_index2_maxlen_changed.emit(self._run_info.sample_index2_maxlen)

    @property
    def assess_color_balance(self):
        return self._run_info.assess_color_balance

    @assess_color_balance.setter
    def assess_color_balance(self, assess_color_balance: bool):

        if self._run_info.assess_color_balance == assess_color_balance:
            return

        self._run_info.assess_color_balance = assess_color_balance
        self.assess_color_balance_changed.emit(assess_color_balance)

    @property
    def color_a(self):
        return self._run_info.color_a

    @color_a.setter
    def color_a(self, color_a: object):

        if self._run_info.color_t == color_a:
            return

        self._run_info.color_a = color_a
        self.color_a_changed.emit(color_a)

    @property
    def color_t(self):
        return self._run_info.color_t

    @color_t.setter
    def color_t(self, color_t: object):
        if self._run_info.color_t == color_t:
            return

        self._run_info.color_t = color_t
        self.color_t_changed.emit(color_t)

    @property
    def color_g(self):
        return self._run_info.color_g

    @color_g.setter
    def color_g(self, color_g: object):
        if self._run_info.color_g == color_g:
            return

        self._run_info.color_g = color_g
        self.color_g_changed.emit(color_g)

    @property
    def color_c(self):
        return self._run_info.color_c

    @color_c.setter
    def color_c(self, color_c: object):
        if self._run_info.color_c == color_c:
            return

        self._run_info.color_c = color_c
        self.color_c_changed.emit(color_c)

    @property
    def chemistry(self):
        return self._run_info.chemistry

    @chemistry.setter
    def chemistry(self, chemistry: str):

        if self._run_info.chemistry == chemistry:
            return

        self._run_info.chemistry = chemistry
        self.chemistry_changed.emit(chemistry)

    @property
    def date(self) -> str:
        return self._run_info.date

    @date.setter
    def date(self, date: str) -> None:

        if self._run_info.date == date:
            return

        self._run_info.date = date
        self.date_changed.emit(date)

    @property
    def investigator(self):
        return self._run_info.investigator

    @investigator.setter
    def investigator(self, investigator: str):

        if self._run_info == investigator:
            return

        self._run_info.investigator = investigator
        self.investigator_changed.emit(investigator)

    @property
    def flowcell(self) -> str:
        return self._run_info.flowcell

    @flowcell.setter
    def flowcell(self, flowcell: str):

        if self._run_info.flowcell == flowcell:
            return

        self._run_info.flowcell = flowcell
        self.flowcell_changed.emit(flowcell)

    @property
    def run_name(self) -> str:
        return self._run_info.run_name

    @run_name.setter
    def run_name(self, run_name: str) -> None:

        if self._run_info.run_name == run_name:
            return

        self._run_info.run_name = run_name
        self.run_name_changed.emit(run_name)

    @property
    def run_description(self) -> str:
        return self._run_info.run_description

    @run_description.setter
    def run_description(self, run_desc: str):

        if self._run_info.run_description == run_desc:
            return

        self._run_info.run_description = run_desc
        self.run_description_changed.emit(run_desc)

    @property
    def instrument(self) -> str:
        return self._run_info.instrument

    @instrument.setter
    def instrument(self, instrument: str):

        if self._run_info.instrument == instrument:
            return

        self._run_info.instrument = instrument
        self.instrument_changed.emit(instrument)

    @property
    def reagent_kit(self) -> str:
        return self._run_info.reagent_kit

    @reagent_kit.setter
    def reagent_kit(self, reagent_kit: str):

        if self._run_info.reagent_kit == reagent_kit:
            return

        self._run_info.reagent_kit = reagent_kit
        self.reagent_kit_changed.emit(reagent_kit)

    @property
    def i5_samplesheet_orientation_bcl2fastq(self) -> str:
        return self._run_info.i5_samplesheet_orientation_bcl2fastq

    @i5_samplesheet_orientation_bcl2fastq.setter
    def i5_samplesheet_orientation_bcl2fastq(self, i5_samplesheet_orientation_bcl2fastq: str):

        if self._run_info.i5_samplesheet_orientation_bcl2fastq == i5_samplesheet_orientation_bcl2fastq:
            return

        self._run_info.i5_samplesheet_orientation_bcl2fastq = i5_samplesheet_orientation_bcl2fastq
        self.i5_samplesheet_orientation_bcl2fastq_changed.emit(i5_samplesheet_orientation_bcl2fastq)

    @property
    def i5_samplesheet_orientation_bclconvert(self) -> str:
        return self._run_info.i5_samplesheet_orientation_bclconvert

    @i5_samplesheet_orientation_bclconvert.setter
    def i5_samplesheet_orientation_bclconvert(self, i5_samplesheet_orientation_bclconvert: str):

        if self._run_info.i5_samplesheet_orientation_bclconvert == i5_samplesheet_orientation_bclconvert:
            return

        self._run_info.i5_samplesheet_orientation_bclconvert = i5_samplesheet_orientation_bclconvert
        self.i5_samplesheet_orientation_bclconvert_changed.emit(i5_samplesheet_orientation_bclconvert)

    @property
    def lanes(self) -> list[int]:
        return self._run_info.lanes

    @lanes.setter
    def lanes(self, lanes: list[int]):

        if self._run_info.lanes == lanes:
            return

        self._run_info.lanes = lanes
        self.lanes_changed.emit(lanes)

    @property
    def run_cycles(self) -> tuple[int, int, int, int]: # read1_cycles, index1_cycles, index2_cycles, read2_cycles
        return (self._run_info.read1_cycles,
                self._run_info.index1_cycles,
                self._run_info.index2_cycles,
                self._run_info.read1_cycles)

    @run_cycles.setter
    def run_cycles(self, run_cycle_values: tuple[int, int, int, int]): # read1_cycles, index1_cycles, index2_cycles, read2_cycles

        read1_cycles, index1_cycles, index2_cycles, read2_cycles = run_cycle_values

        if (self._run_info.read1_cycles != read1_cycles and
                   self._run_info.index1_cycles != index1_cycles and
                   self._run_info.index2_cycles != index2_cycles and
                   self._run_info.read2_cycles != read2_cycles
                   ):

            self._run_info.read1_cycles = read1_cycles
            self._run_info.index1_cycles = index1_cycles
            self._run_info.index2_cycles = index2_cycles
            self._run_info.read2_cycles = read2_cycles
            self.run_cycles_changed.emit(read1_cycles, index1_cycles, index2_cycles, read2_cycles)


    @property
    def index1_cycles(self) -> int:
        return self._run_info.index1_cycles

    @property
    def i5_seq_orientation(self) -> str:
        return self._run_info.i5_seq_orientation

    @i5_seq_orientation.setter
    def i5_seq_orientation(self, i5_seq_orientation: str):
        self._run_info.i5_seq_orientation = i5_seq_orientation
        self.i5_seq_orientation_changed.emit(i5_seq_orientation)

    @property
    def dragen_app_version(self) -> str:
        return self._run_info.dragen_app_version

    @dragen_app_version.setter
    def dragen_app_version(self, dragen_app_version):

        if self._run_info.dragen_app_version == dragen_app_version:
            return

        self._run_info.dragen_app_version = dragen_app_version
        self.dragen_app_version_changed.emit(dragen_app_version)

    @property
    def sample_index1_minlen(self) -> int:
        return self._run_info.sample_index1_minlen

    @sample_index1_minlen.setter
    def sample_index1_minlen(self, sample_index1_minlen):
        if self._run_info.sample_index1_minlen == sample_index1_minlen:
            return

        self._run_info.sample_index1_minlen = sample_index1_minlen
        self.sample_index1_minlen_changed.emit(self._sample_index1_minlen)

    @property
    def sample_index2_minlen(self) -> int:
        return self._run_info.sample_index2_minlen

    @sample_index2_minlen.setter
    def sample_index2_minlen(self, sample_index2_minlen):
        if self._run_info.sample_index1_minlen == sample_index2_minlen:
            return

        self._run_info.sample_index2_minlen = sample_index2_minlen
        self.sample_index1_minlen_changed.emit(sample_index2_minlen)

    @property
    def sample_index1_maxlen(self) -> int:
        return self._run_info.sample_index1_maxlen

    @sample_index1_maxlen.setter
    def sample_index1_maxlen(self, sample_index1_maxlen):
        if self._run_info.sample_index1_minlen == sample_index1_maxlen:
            return

        self._run_info.sample_index1_maxlen = sample_index1_maxlen
        self.sample_index1_maxlen_changed.emit(sample_index1_maxlen)

    @property
    def sample_index2_maxlen(self) -> int:
        return self._run_info.sample_index2_maxlen

    @sample_index2_maxlen.setter
    def sample_index2_maxlen(self, sample_index2_maxlen):
        if self._run_info.sample_index1_maxlen == sample_index2_maxlen:
            return

        self._run_info.sample_index2_maxlen = sample_index2_maxlen
        self.sample_index2_maxlen_changed.emit(sample_index2_maxlen)
        self.unfreeze()

    @property
    def sample_df(self) -> pd.DataFrame:
        return self._sample_model.to_dataframe()

    @property
    def has_run_info(self) -> bool:
        return self._has_run_info
