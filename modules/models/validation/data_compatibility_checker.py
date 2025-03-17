import re
from logging import Logger

import pandas as pd
from PySide6.QtCore import Signal, QObject, Slot

from modules.models.dataset.dataset_manager import DataSetManager
from modules.models.datastate.datastate_model import DataStateModel


class DataCompatibilityTest(QObject):
    app_ok = Signal(object)
    drop_ok = Signal(object)
    override_pat_ok = Signal(object)

    def __init__(self, datastate_model: DataStateModel, dataset_manager: DataSetManager, logger: Logger):
        super().__init__()
        self._logger = logger
        self._dataset_manager = dataset_manager
        self._datastate_model = datastate_model

        self._oc_validate_pattern = {
            "Read1Cycles": r"^(Y\d+|N\d+|U\d+)*(Y{r})(Y\d+|N\d+|U\d+)*$",
            "Index1Cycles": r"^(I\d+|N\d+|U\d+)*(I{i})(I\d+|N\d+|U\d+)*$",
            "Index2Cycles": r"^(I\d+|N\d+|U\d+)*(I{i})(I\d+|N\d+|U\d+)*$",
            "Read2Cycles": r"^(Y\d+|N\d+|U\d+)*(Y{r})(Y\d+|N\d+|U\d+)*$",
        }

        self._oc_parts_re = {
            "Read1Cycles": r"(Y\d+|N\d+|U\d+|Y{r})",
            "Index1Cycles": r"(I\d+|N\d+|U\d+|I{i})",
            "Index2Cycles": r"(I\d+|N\d+|U\d+|I{i})",
            "Read2Cycles": r"(Y\d+|N\d+|U\d+|Y{r})",
        }



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

        self._logger.warning("Dropped indexes are not compatible with run cycles.")

    def app_check(self, appobj: dict) -> None:

        app_profile = appobj.get("ApplicationProfile")
        if not self._datastate_model.application_compatibility(app_profile):
            self._logger.warning(f"incompatible app profile {app_profile}")
            return

        self.app_ok.emit(appobj)


    def override_cycles_check(self, override_cycles: dict) -> None:
        invalid_parts = []

        for oc_part_key, override_cycles_str in override_cycles.items():
            if not self._validate_override_pattern(oc_part_key, override_cycles_str):
                invalid_parts.append(oc_part_key)

        if invalid_parts:
            self._logger.warning(f"Invalid override keys: {invalid_parts}")
            return

        current_cycles = self._dataset_manager.read_cycles_dict

        for oc_part_key, override_cycles_str in override_cycles.items():
            required_length = self._nonvariable_oc_len(oc_part_key, override_cycles_str)

            if required_length > current_cycles[oc_part_key]:
                invalid_parts.append(oc_part_key)

        if invalid_parts:
            self._logger.warning(f"Tot override cycles exceeding run cycles: {invalid_parts}")
            return

        self.override_pat_ok.emit(override_cycles)

        return

    def _validate_override_pattern(self, oc_part_key, oc_part_string):
        if re.fullmatch(self._oc_validate_pattern[oc_part_key], oc_part_string):
            return True

        return False

    def _nonvariable_oc_len(self, oc_part_key, oc_part_str):
        matches = re.findall(self._oc_parts_re[oc_part_key], oc_part_str)

        print(matches)

        preset_oc_len = 0
        for m in matches[0]:
            if "{" not in m:
                preset_oc_len += int(m[1:])

        return preset_oc_len
