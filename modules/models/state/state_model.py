"""
StateModel - Centralized state management for the application.

This class manages the application's state including run information, sample data,
instrument configuration, and validation states. It provides a reactive interface
using Qt signals to notify about state changes.
"""
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum, auto
from logging import Logger
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from PySide6.QtCore import QObject, Signal, Slot

from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.sample.sample_model import SampleModel
from modules.utils.utils import uuid


# from modules.models.sample.sample_model import StateModel


class RunState(Enum):
    """Enum representing the possible run states."""
    UNINITIALIZED = auto()
    CONFIGURING = auto()
    READY = auto()
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
    uuid: str = ""

    read1_cycles: int = 0
    index1_cycles: int = 0
    index2_cycles: int = 0
    read2_cycles: int = 0
    custom_cycles: bool = False

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
    sample_application_profile_names: List[str] = field(default_factory=list)

    samplesheet_v2: str = ""
    json: str = ""

    file_data_generated: bool = False

    is_validated: bool = False


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
    uuid_changed = Signal(str)


    run_cycles_changed = Signal(int, int, int, int) # read1_cycles, index1_cycles, index2_cycles, read2_cycles
    read1_cycles_changed = Signal(int)
    index1_cycles_changed = Signal(int)
    index2_cycles_changed = Signal(int)
    read2_cycles_changed = Signal(int)
    custom_cycles_changed = Signal(bool)
    i5_seq_orientation_changed = Signal(str)
    i5_samplesheet_orientation_bcl2fastq_changed = Signal(str)
    i5_samplesheet_orientation_bclconvert_changed = Signal(str)

    sample_application_profile_changed = Signal(list)
    
    # Color signals
    color_a_changed = Signal(object)
    color_t_changed = Signal(object)
    color_g_changed = Signal(object)
    color_c_changed = Signal(object)

    # Color balance signals
    assess_color_balance_changed = Signal(bool)
    
    # Index length signals
    sample_index1_minlen_changed = Signal(int)
    sample_index1_maxlen_changed = Signal(int)
    sample_index2_minlen_changed = Signal(int)
    sample_index2_maxlen_changed = Signal(int)
    
    # Application state signals
    dragen_app_version_changed = Signal(str)

    run_info_ready = Signal()
    run_info_not_ready = Signal()

    samplesheet_v2_changed = Signal(str)
    json_changed = Signal(str)

    validation_status = Signal(bool)
    file_data_status_signal = Signal(bool)


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
        self._run_info_complete = False
        
        # Initialize run info with default values
        self._run_info = RunInfo()
        

    # @property
    # def run_info(self) -> dict:
    #     """Get a copy of the current run information."""
    #     return asdict(self._run_info)
    
    def set_run_setup_data(self, run_setup_data: dict) -> None:
        """
        Update run info and emit appropriate signals.

        Args:
            run_setup_data: Dictionary containing run setup data to update

        Returns:
            None
        """

        if not run_setup_data:
            self._logger.debug("No fields to update in update_run_info")
            return

        changed = False

        # Apply updates and track changes
        for key, value in run_setup_data.items():
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
        self._validate_run_info()


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
        if all_valid != self._run_info_complete:
            self._run_info_complete = all_valid
            if self._run_info_complete:
                self.run_info_ready.emit()
            else:
                self.run_info_not_ready.emit()

    @property
    def run_description(self) -> str:
        return self._run_info.run_description

    @run_description.setter
    def run_description(self, value: str):
        if self._run_info.run_description != value:
            self.mark_as_unvalidated()
            self._run_info.run_description = value
            self.run_description_changed.emit(value)

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

        self.sample_index1_minlen = 0
        self.sample_index1_maxlen = 0
        self.sample_index2_minlen = 0
        self.sample_index2_maxlen = 0

        # self._check_run_info_complete()



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
                if self._run_info_complete:  # Only emit if state is changing
                    self.run_info_ready.emit(False)
                self._run_info_complete = False
                return
        
        # All fields are valid
        if not self._run_info_complete:  # Only emit if state is changing
            self.run_info_ready.emit(True)
        self._run_info_complete = True

    @staticmethod
    def _get_str_lengths_in_df_col(series: pd.Series) -> Tuple[int, int]:

        # Filter out empty/None values and get string lengths
        lengths = series.dropna().astype(str).str.len()

        if len(lengths) == 0:
            return 0, 0

        return lengths.min(), lengths.max()

    @staticmethod
    def _get_unique_strings_explode(series: pd.Series) -> str:
        """
        Alternative approach using pandas explode() method.

        Args:
            series: A pandas Series where each element is a list of strings

        Returns:
            A list of unique strings found across all lists in the series
        """
        series.explode().dropna().unique().tolist()

        return series.explode().dropna().unique().tolist()

    def update_aggregate_sample_data(self):
        """Update the minimum and maximum lengths of index sequences from the sample model."""
        df = self._sample_model.to_dataframe()

        # Get lengths for both index columns
        i7_min, i7_max = self._get_str_lengths_in_df_col(df["IndexI7"])
        i5_min, i5_max = self._get_str_lengths_in_df_col(df["IndexI5"])

        # Update the state model
        self.sample_index1_minlen = int(i7_min)
        self.sample_index1_maxlen = int(i7_max)
        self.sample_index2_minlen = int(i5_min)
        self.sample_index2_maxlen = int(i5_max)

        set_profile_names = self._get_unique_strings_explode(df["ApplicationProfile"])

        self.sample_application_profile_names = set_profile_names


    @property
    def run_info(self) -> RunInfo:
        return self._run_info


    @property
    def samplesheet_v2(self) -> str:
        return self._run_info.samplesheet_v2

    @samplesheet_v2.setter
    def samplesheet_v2(self, samplesheet: str):
        if self._run_info.samplesheet_v2 != samplesheet:
            self._run_info.samplesheet_v2 = samplesheet
            self.samplesheet_v2_changed.emit(samplesheet)
            self.mark_as_generated()

    @property
    def json(self) -> str:
        return self._run_info.json

    @json.setter
    def json(self, json: str):
        if self._run_info.json != json:
            self._run_info.json = json
            self.json_changed.emit(json)
            self.mark_as_generated()


    @property
    def uuid(self):
        return self._run_info.uuid

    @uuid.setter
    def uuid(self, uuid):
        if uuid != self._run_info.uuid:
            self._run_info.uuid = uuid
            self.uuid_changed.emit(uuid)

    @property
    def sample_application_profile_names(self) -> list:
        return self._run_info.sample_application_profile_names

    @sample_application_profile_names.setter
    def sample_application_profile_names(self, sample_application_profile_names: list):
        if set(sample_application_profile_names) != set(self._run_info.sample_application_profile_names):
            self._run_info.sample_application_profile_names = sample_application_profile_names
            self.sample_application_profile_changed.emit(sample_application_profile_names)
            self.mark_as_unvalidated()

    @property
    def is_validated(self):
        return self._run_info.is_validated

    @is_validated.setter
    def is_validated(self, is_validated: bool):
        if self._run_info.is_validated != is_validated:
            self._run_info.is_validated = is_validated
            
    def mark_as_validated(self) -> None:
        """Mark the current state as validated."""
        if not self._run_info.is_validated:
            self._run_info.is_validated = True
            self.uuid = uuid()
            self.validation_status.emit(True)

    def mark_as_unvalidated(self) -> None:
        """Mark the current state as validated."""
        if self._run_info.is_validated:
            self._run_info.is_validated = False
            self.uuid = "None"
            self.validation_status.emit(False)
            self._run_info.file_data_generated = False
            self.samplesheet_v2 = ""
            self.json = ""

    def mark_as_generated(self) -> None:
        if not self.samplesheet_v2 or not self.json:
            return

        self._run_info.file_data_generated = True
        self.file_data_status_signal.emit(True)


    @property
    def assess_color_balance(self):
        return self._run_info.assess_color_balance

    @assess_color_balance.setter
    def assess_color_balance(self, assess_color_balance: bool):

        if self._run_info.assess_color_balance == assess_color_balance:
            return

        self._run_info.assess_color_balance = assess_color_balance
        self.mark_as_unvalidated()
        self.assess_color_balance_changed.emit(assess_color_balance)


    @property
    def instrument(self):
        return self._run_info.instrument

    @instrument.setter
    def instrument(self, instrument: str):
        if self._run_info.instrument == instrument:
            return

        self._run_info.instrument = instrument
        self.mark_as_unvalidated()
        self.instrument_changed.emit(instrument)

    @property
    def base_colors(self):
        return {'A': self.color_a,
                'T': self.color_t,
                'G': self.color_g,
                'C': self.color_c}

    @property
    def color_a(self):
        return self._run_info.color_a

    @color_a.setter
    def color_a(self, color_a: object):

        if self._run_info.color_t == color_a:
            return

        self._run_info.color_a = color_a
        self.mark_as_unvalidated()
        self.color_a_changed.emit(color_a)

    @property
    def color_t(self):
        return self._run_info.color_t

    @color_t.setter
    def color_t(self, color_t: object):
        if self._run_info.color_t == color_t:
            return

        self._run_info.color_t = color_t
        self.mark_as_unvalidated()
        self.color_t_changed.emit(color_t)

    @property
    def color_g(self):
        return self._run_info.color_g

    @color_g.setter
    def color_g(self, color_g: object):
        if self._run_info.color_g == color_g:
            return

        self._run_info.color_g = color_g
        self.mark_as_unvalidated()
        self.color_g_changed.emit(color_g)

    @property
    def color_c(self):
        return self._run_info.color_c

    @color_c.setter
    def color_c(self, color_c: object):
        if self._run_info.color_c == color_c:
            return

        self._run_info.color_c = color_c
        self.mark_as_unvalidated()
        self.color_c_changed.emit(color_c)

    @property
    def chemistry(self) -> str:
        return self._run_info.chemistry
    
    @chemistry.setter
    def chemistry(self, value: str) -> None:
        if self._run_info.chemistry != value:
            self.mark_as_unvalidated()
            self._run_info.chemistry = value
            self.chemistry_changed.emit(value)

    @property
    def date(self) -> str:
        return self._run_info.date
        
    @date.setter
    def date(self, value: str) -> None:
        if self._run_info.date != value:
            self.mark_as_unvalidated()
            self._run_info.date = value
            self.date_changed.emit(value)

    @property
    def flowcell(self) -> str:
        return self._run_info.flowcell
    
    @flowcell.setter
    def flowcell(self, value: str) -> None:
        if self._run_info.flowcell != value:
            self.mark_as_unvalidated()
            self._run_info.flowcell = value
            self.flowcell_changed.emit(value)

    @property
    def run_name(self) -> str:
        return self._run_info.run_name
        
    @run_name.setter
    def run_name(self, value: str) -> None:
        if self._run_info.run_name != value:
            self.mark_as_unvalidated()
            self._run_info.run_name = value
            self.run_name_changed.emit(value)
    
    @property
    def reagent_kit(self) -> str:
        return self._run_info.reagent_kit
    
    @reagent_kit.setter
    def reagent_kit(self, value: str) -> None:
        if self._run_info.reagent_kit != value:
            self.mark_as_unvalidated()
            self._run_info.reagent_kit = value
            self.reagent_kit_changed.emit(value)

    @property
    def i5_samplesheet_orientation_bcl2fastq(self) -> str:
        return self._run_info.i5_samplesheet_orientation_bcl2fastq

    @i5_samplesheet_orientation_bcl2fastq.setter
    def i5_samplesheet_orientation_bcl2fastq(self, value: str) -> None:
        if self._run_info.i5_samplesheet_orientation_bcl2fastq != value:
            self.mark_as_unvalidated()
            self._run_info.i5_samplesheet_orientation_bcl2fastq = value
            self.i5_samplesheet_orientation_bcl2fastq_changed.emit(value)

    @property
    def i5_samplesheet_orientation_bclconvert(self) -> str:
        return self._run_info.i5_samplesheet_orientation_bclconvert

    @i5_samplesheet_orientation_bclconvert.setter
    def i5_samplesheet_orientation_bclconvert(self, value: str) -> None:
        if self._run_info.i5_samplesheet_orientation_bclconvert != value:
            self.mark_as_unvalidated()
            self._run_info.i5_samplesheet_orientation_bclconvert = value
            self.i5_samplesheet_orientation_bclconvert_changed.emit(value)

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

    @index1_cycles.setter
    def index1_cycles(self, value: int) -> None:
        if self._run_info.index1_cycles != value:
            self.mark_as_unvalidated()
            self._run_info.index1_cycles = value
            self.index1_cycles_changed.emit(value)

    @property
    def index2_cycles(self) -> int:
        return self._run_info.index2_cycles

    @index2_cycles.setter
    def index2_cycles(self, value: int) -> None:
        if self._run_info.index2_cycles != value:
            self.mark_as_unvalidated()
            self._run_info.index2_cycles = value
            self.index2_cycles_changed.emit(value)

    @property
    def read1_cycles(self) -> int:
        return self._run_info.read1_cycles

    @read1_cycles.setter
    def read1_cycles(self, value: int) -> None:
        if self._run_info.read1_cycles != value:
            self.mark_as_unvalidated()
            self._run_info.read1_cycles = value
            self.read1_cycles_changed.emit(value)

    @property
    def read2_cycles(self) -> int:
        return self._run_info.read2_cycles

    @read2_cycles.setter
    def read2_cycles(self, value: int) -> None:
        if self._run_info.read2_cycles != value:
            self.mark_as_unvalidated()
            self._run_info.read2_cycles = value
            self.read2_cycles_changed.emit(value)

    @property
    def custom_cycles(self) -> bool:
        return self._run_info.custom_cycles

    @custom_cycles.setter
    def custom_cycles(self, custom_cycles: bool):
        if self._run_info.custom_cycles != custom_cycles:
            self.mark_as_unvalidated()
            self._run_info.custom_cycles = custom_cycles
            self.custom_cycles_changed.emit(custom_cycles)

    @property
    def i5_seq_orientation(self) -> str:
        return self._run_info.i5_seq_orientation

    @i5_seq_orientation.setter
    def i5_seq_orientation(self, i5_seq_orientation: str):
        if self._run_info.i5_seq_orientation != i5_seq_orientation:
            self.mark_as_unvalidated()
            self._run_info.i5_seq_orientation = i5_seq_orientation
            self.i5_seq_orientation_changed.emit(i5_seq_orientation)

    @property
    def dragen_app_version(self) -> str:
        return self._run_info.dragen_app_version

    @dragen_app_version.setter
    def dragen_app_version(self, dragen_app_version):
        if self._run_info.dragen_app_version != dragen_app_version:
            self.mark_as_unvalidated()
            self._run_info.dragen_app_version = dragen_app_version
            self.dragen_app_version_changed.emit(dragen_app_version)

    @property
    def sample_index1_minlen(self) -> int:
        return self._run_info.sample_index1_minlen

    @sample_index1_minlen.setter
    def sample_index1_minlen(self, sample_index1_minlen):
        if self._run_info.sample_index1_minlen != sample_index1_minlen:
            self.mark_as_unvalidated()
            self._run_info.sample_index1_minlen = sample_index1_minlen
            self.sample_index1_minlen_changed.emit(sample_index1_minlen)

    @property
    def sample_index1_maxlen(self) -> int:
        return self._run_info.sample_index1_maxlen

    @sample_index1_maxlen.setter
    def sample_index1_maxlen(self, sample_index1_maxlen):
        if self._run_info.sample_index1_maxlen != sample_index1_maxlen:
            self.mark_as_unvalidated()
            self._run_info.sample_index1_maxlen = sample_index1_maxlen
            self.sample_index1_maxlen_changed.emit(sample_index1_maxlen)


    @property
    def sample_index2_minlen(self) -> int:
        return self._run_info.sample_index2_minlen

    @sample_index2_minlen.setter
    def sample_index2_minlen(self, sample_index2_minlen):
        if self._run_info.sample_index2_minlen != sample_index2_minlen:
            self.mark_as_unvalidated()
            self._run_info.sample_index2_minlen = sample_index2_minlen
            self.sample_index2_minlen_changed.emit(sample_index2_minlen)

    @property
    def sample_index2_maxlen(self) -> int:
        return self._run_info.sample_index2_maxlen

    @sample_index2_maxlen.setter
    def sample_index2_maxlen(self, sample_index2_maxlen):
        if self._run_info.sample_index2_maxlen != sample_index2_maxlen:
            self.mark_as_unvalidated()
            self._run_info.sample_index2_maxlen = sample_index2_maxlen
            self.sample_index2_maxlen_changed.emit(sample_index2_maxlen)

    @property
    def sample_df(self) -> pd.DataFrame:
        return self._sample_model.to_dataframe()

    @property
    def has_run_info(self) -> bool:
        return self._run_info_complete
