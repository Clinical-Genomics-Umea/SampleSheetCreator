from logging import Logger

import pandas as pd
from PySide6.QtCore import Signal, QObject, Slot

from modules.models.application.application_manager import ApplicationManager
from modules.models.dataset.dataset_manager import DataSetManager
from modules.models.datastate.datastate_model import DataStateModel
from modules.utils.utils import validate_override_pattern, preset_override_cycles


class DataCompatibilityChecker(QObject):
    app_ok = Signal(object)
    drop_ok = Signal(object)
    override_pattern_ok = Signal(object)

    def __init__(self, datastate_model: DataStateModel, dataset_manager: DataSetManager, logger: Logger):
        super().__init__()
        self._logger = logger
        self._dataset_manager = dataset_manager
        self._datastate_model = datastate_model

    @Slot(object)
    def drop_check(self, dropped_data: dict) -> None:
        """Check if the dropped data is compatible with the current run settings."""

        df = pd.DataFrame(dropped_data["decoded_data"])

        max_index_i7_len = df["IndexI7"].str.len().max() if "IndexI7" in df.columns else None
        max_index_i5_len = df["IndexI5"].str.len().max() if "IndexI5" in df.columns else None

        if max_index_i7_len and max_index_i5_len:
            if (max_index_i7_len <= self._datastate_model.rundata_model.index_1_cycles and
                    max_index_i5_len <= self._datastate_model.rundata_model.index_1_cycles):
                self.drop_ok.emit(dropped_data)
                return

        elif max_index_i7_len:
            if max_index_i7_len <= self._datastate_model.rundata_model.index_1_cycles:
                self.drop_ok.emit(dropped_data)
                return

        self._logger.warning("Dropped indexes are not compatible with set run cycles.")

    def app_check(self, appobj: dict) -> None:

        app_profile = appobj.get("ApplicationProfile")
        if not self._datastate_model.application_compatibility(app_profile):
            self._logger.warning(f"incompatible app profile {app_profile}")
            return

        self.app_ok.emit(appobj)


    def override_cycles_check(self, override_cycles: dict) -> None:
        invalid_keys = []

        for key, pattern in override_cycles.items():
            if not validate_override_pattern(key, pattern):
                invalid_keys.append(key)

        if invalid_keys:
            print(invalid_keys)
            self._logger.warning(f"Invalid override keys: {invalid_keys}")
            return

        current_cycles = self._dataset_manager.read_cycles_dict

        for key, pattern in override_cycles.items():
            required_length = preset_override_cycles(key, pattern)

            if required_length > current_cycles[key]:
                invalid_keys.append(key)

        if invalid_keys:
            self._logger.warning(f"Override keys exceeding limits: {invalid_keys}")
            return

        self.override_pattern_ok.emit(override_cycles)

        return
