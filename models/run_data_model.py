from PySide6.QtCore import QObject, Slot, Signal
from models.configuration import ConfigurationManager


class RunDataModel(QObject):

    run_data_changed = Signal()
    run_data_ready = Signal(dict)

    def __init__(self, cfg_mgr: ConfigurationManager):
        super().__init__()
        self._cfg_mgr = cfg_mgr
        self._run_data = {}
        self._read_cycles_dict = {}
        self._read_cycles_fields = []
        self._instr_fcells_obj = self._cfg_mgr.instrument_flowcells

        self._setup()

    def _setup(self):
        print("run data fields", self._cfg_mgr.run_data_fields)
        for field in self._cfg_mgr.run_data_fields:
            self._run_data[field] = None

        self._read_cycles_fields = self._cfg_mgr.read_cycles_fields

        for field in self._cfg_mgr.read_cycles_fields:
            self._read_cycles_dict[field] = None

    def _i5_seq_orientation(self):
        return self._instr_fcells_obj[self._run_data["Instrument"]]["I5SeqOrientation"]

    def _i5_smplsht_orientation(self):
        return self._instr_fcells_obj[self._run_data["Instrument"]][
            "I5SampleSheetOrientation"
        ][self._run_data["FastqExtractTool"]]

    def _lanes(self):
        return self._instr_fcells_obj[self._run_data["Instrument"]]["Flowcell"][
            self._run_data["Flowcell"]
        ]["Lanes"]

    def _fluorophores(self):
        return self._instr_fcells_obj[self._run_data["Instrument"]]["Fluorophores"]

    def _chemistry(self):
        return self._instr_fcells_obj[self._run_data["Instrument"]]["Chemistry"]

    def _assess_balance(self):
        return self._instr_fcells_obj[self._run_data["Instrument"]]["AssessBalance"]

    def _samplesheet_version(self):
        return self._instr_fcells_obj[self._run_data["Instrument"]][
            "SampleSheetVersion"
        ]

    def _get_read_cycles(self):

        crc_str = self._run_data["CustomReadCycles"]
        rc_str = self._run_data["ReadCycles"]

        custom_read_cycles = crc_str.split()
        read_cycles = rc_str.split("-")

        if len(custom_read_cycles) != len(read_cycles):
            return rc_str

        for crc, rc in zip(custom_read_cycles, read_cycles):
            if int(crc) > int(rc):
                return rc_str

        return crc_str

    def _get_read_cycles_dict(self):
        read_cycles = self._run_data["ReadCycles"].split("-")

        return {
            "Read1Cycles": int(read_cycles[0]),
            "Index1Cycles": int(read_cycles[1]),
            "Index2Cycles": int(read_cycles[2]),
            "Read2Cycles": int(read_cycles[3]),
        }

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
        for key in self._cfg_mgr.run_data_fields:
            self._run_data[key] = None

        # Update the run data with user input values
        for key, value in run_data.items():
            if key not in self._run_data:
                continue
            self._run_data[key] = value

        # Set instrument specific settings
        self._run_data["I5SampleSheetOrientation"] = self._i5_smplsht_orientation()
        self._run_data["I5SeqOrientation"] = self._i5_seq_orientation()
        self._run_data["Lanes"] = self._lanes()
        self._run_data["Fluorophores"] = self._fluorophores()
        self._run_data["Chemistry"] = self._chemistry()
        self._run_data["AssessBalance"] = self._assess_balance()
        self._run_data["SampleSheetVersion"] = self._assess_balance()
        self._run_data["ReadCycles"] = self._get_read_cycles()
        self._read_cycles_dict = self._get_read_cycles_dict()

        # Set base fluorphores
        self._run_data["A"] = self._fluorophores()["A"]
        self._run_data["C"] = self._fluorophores()["C"]
        self._run_data["G"] = self._fluorophores()["G"]
        self._run_data["T"] = self._fluorophores()["T"]

        # Emit the run data changed signal
        self.run_data_changed.emit()
        self.run_data_ready.emit(self._run_data)

    @property
    def read_cycles(self) -> dict:
        return self._read_cycles

    @property
    def run_data(self) -> dict:
        return self._run_data
