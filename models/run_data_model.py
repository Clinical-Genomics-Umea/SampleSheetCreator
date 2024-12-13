from PySide6.QtCore import QObject, Slot, Signal

from models.configuration import ConfigurationManager


class RunDataModel(QObject):

    run_data_changed = Signal()

    def __init__(self, cfg_mgr: ConfigurationManager):
        super().__init__()
        self._cfg_mgr = cfg_mgr
        self._run_data = {}
        self._read_cycles = {}
        self._read_cycles_fields = []

    def setup(self):
        for field in self._cfg_mgr.run_data_fields:
            self._run_data[field] = None

        self._read_cycles_fields = self._cfg_mgr.read_cycles_fields

        for field in self._cfg_mgr.read_cycles_fields:
            self._read_cycles[field] = None

    @Slot(dict)
    def set_run_data(self, run_data: dict):
        """
        Set the run data configuration and validate it.

        If the data is invalid, do not update the configuration and
        instead emit the run_data_error signal.

        Otherwise, update the configuration and emit the
        run_setup_changed signal.
        """

        for k, v in run_data.items():
            if k not in self._run_data:
                continue
            self._run_data[k] = v

            if k == "ReadCycles":
                read_cycles_items = v.strip().split("-")
                self._read_cycles = dict(
                    zip(self._read_cycles_fields, read_cycles_items)
                )

        self.run_data_changed.emit()

    @property
    def read_cycles(self) -> dict:
        return self._read_cycles

    @property
    def run_data(self) -> dict:
        return self._run_data
