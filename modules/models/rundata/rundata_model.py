from logging import Logger

from PySide6.QtCore import QObject, Slot, Signal
from modules.models.configuration.configuration_manager import ConfigurationManager


class RunDataModel(QObject):

    # run_data_changed = Signal()
    run_data_ready = Signal(dict)
    index_lens_ready = Signal(int, int)

    def __init__(self, configuration_manager: ConfigurationManager, logger: Logger):
        super().__init__()
        self._configuration_manager = configuration_manager
        self._logger = logger

        self._rundata = {}
        self._read_cycles_dict = {}
        self._read_cycles_fields = []
        self._read_cycles_list = []
        self._instr_flowcell_obj = self._configuration_manager.instrument_flowcells
        self._has_rundata = False

        self._setup()

    def _setup(self):
        for field in self._configuration_manager.run_data_fields:
            self._rundata[field] = None

        self._read_cycles_fields = self._configuration_manager.read_cycles_fields

        for field in self._configuration_manager.read_cycles_fields:
            self._read_cycles_dict[field] = None

    def _set_i5_seq_orientation(self):
        self._rundata["I5SeqOrientation"] = self._instr_flowcell_obj[
            self._rundata["Instrument"]
        ]["I5SeqOrientation"]

    def _set_lanes(self):
        self._rundata["Lanes"] = self._instr_flowcell_obj[self._rundata["Instrument"]][
            "Flowcell"
        ][self._rundata["Flowcell"]]["Lanes"]

    def _set_fluorophores(self):
        self._rundata["Fluorophores"] = self._instr_flowcell_obj[
            self._rundata["Instrument"]
        ]["Fluorophores"]

    def _base_to_fluorophore_list(self, base: str):
        return self._rundata["Fluorophores"][base]

    def _set_chemistry(self):
        self._rundata["Chemistry"] = self._instr_flowcell_obj[
            self._rundata["Instrument"]
        ]["Chemistry"]

    def _set_assess_balance(self):
        self._rundata["AssessColorBalance"] = bool(
            self._instr_flowcell_obj[self._rundata["Instrument"]]["AssessColorBalance"]
        )

    def _set_samplesheet_version(self):
        self._rundata["SampleSheetVersion"] = self._instr_flowcell_obj[
            self._rundata["Instrument"]
        ]["SampleSheetVersion"]

    def _set_read_cycles_from_custom(self):

        crc_str = self._rundata["CustomReadCycles"]
        rc_str = self._rundata["ReadCycles"]

        custom_read_cycles = crc_str.split()
        read_cycles = rc_str.split("-")

        if len(custom_read_cycles) != len(read_cycles):
            self._rundata["ReadCycles"] = rc_str
            return

        for crc, rc in zip(custom_read_cycles, read_cycles):
            if int(crc) > int(rc):
                self._rundata["ReadCycles"] = rc_str
                return

        self._rundata["ReadCycles"] = crc_str

    def _set_read_cycles_dict(self):
        read_cycles = self._rundata["ReadCycles"].split("-")

        self._read_cycles_dict = {
            "Read1Cycles": int(read_cycles[0]),
            "Index1Cycles": int(read_cycles[1]),
            "Index2Cycles": int(read_cycles[2]),
            "Read2Cycles": int(read_cycles[3]),
        }

        self._read_cycles_list = [
            int(read_cycles[0]),
            int(read_cycles[1]),
            int(read_cycles[2]),
            int(read_cycles[3]),
        ]

    def _set_read_cycle_items(self):
        self._rundata["Read1Cycles"] = self._read_cycles_dict["Read1Cycles"]
        self._rundata["Index1Cycles"] = self._read_cycles_dict["Index1Cycles"]
        self._rundata["Index2Cycles"] = self._read_cycles_dict["Index2Cycles"]
        self._rundata["Read2Cycles"] = self._read_cycles_dict["Read2Cycles"]

    @property
    def read_cycles_dict(self):

        read_cycles_dict = {
            "Read1Cycles": self._rundata["Read1Cycles"],
            "Index1Cycles": self._rundata["Index1Cycles"],
            "Index2Cycles": self._rundata["Index2Cycles"],
            "Read2Cycles": self._rundata["Read2Cycles"],
        }

        return read_cycles_dict

    @property
    def index_1_cycles(self):
        return self._rundata["Index1Cycles"]

    @property
    def index_2_cycles(self):
        return self._rundata["Index2Cycles"]

    @property
    def read_1_cycles(self):
        return self._rundata["Read1Cycles"]

    @property
    def read_2_cycles(self):
        return self._rundata["Read2Cycles"]


    def _set_extract_tool_samplesheet_orientation(self):
        for tool, orientation in self._instr_flowcell_obj[self._rundata["Instrument"]][
            "I5SampleSheetOrientation"
        ].items():
            self._rundata[tool] = orientation

    @Slot(dict)
    def set_run_data(self, run_data: dict):

        """
        Set the run data configuration and validate it.

        If the data is invalid, do not update the configuration and
        instead emit the run_data_error signal.

        Otherwise, update the configuration and emit the
        run_setup_changed signal.
        """

        # Initialize the run data with default values
        for key in self._configuration_manager.run_data_fields:
            self._rundata[key] = None

        # Update the run data with user input values
        for key, value in run_data.items():
            if key not in self._rundata:
                continue
            self._rundata[key] = value

        # Set instrument specific settings
        # self._set_i5_smplsht_orientation()
        self._set_i5_seq_orientation()
        self._set_lanes()
        self._set_fluorophores()
        self._set_chemistry()
        self._set_assess_balance()
        self._set_samplesheet_version()
        self._set_read_cycles_from_custom()
        self._set_read_cycles_dict()
        self._set_read_cycle_items()
        self._set_extract_tool_samplesheet_orientation()

        # Set base fluorphores
        self._rundata["A"] = self._base_to_fluorophore_list("A")
        self._rundata["C"] = self._base_to_fluorophore_list("C")
        self._rundata["G"] = self._base_to_fluorophore_list("G")
        self._rundata["T"] = self._base_to_fluorophore_list("T")

        # Emit the run data changed signal
        self._has_rundata = True

        # self.run_data_changed.emit()
        self.run_data_ready.emit(self._rundata)
        self.index_lens_ready.emit(
            self._read_cycles_dict["Index1Cycles"],
            self._read_cycles_dict["Index2Cycles"],
        )

    @property
    def i5_samplesheet_orientation(self) -> dict:
        return {
            "BCL2Fastq": self._rundata["BCL2Fastq"],
            "BCLConvert": self._rundata["BCL2Fastq"],
        }

    @property
    def i5_seq_orientation(self) -> str:
        return self._rundata["I5SeqOrientation"]

    # @property
    # def read_cycles_dict(self) -> dict:
    #     return self._read_cycles_dict

    @property
    def read_cycles_list(self) -> list:
        return self._read_cycles_list

    @property
    def assess_balance(self) -> bool:
        return self._rundata["AssessColorBalance"]

    @property
    def has_rundata(self) -> bool:
        return self._has_rundata

    @property
    def rundata(self) -> dict:
        return self._rundata

    @property
    def base_colors(self) -> dict:
        return self._rundata["Fluorophores"]

    @property
    def lanes(self) -> list:
        return self._rundata["Lanes"]
