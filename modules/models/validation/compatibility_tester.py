import re
from logging import Logger
from pprint import pprint

import pandas as pd
from PySide6.QtCore import Signal, QObject, Slot

from modules.models.state.state_model import StateModel


class CompatibilityTester(QObject):
    application_profile_ok = Signal(object)
    index_drop_ok = Signal(object)
    override_pat_ok = Signal(object)

    def __init__(self, state_model: StateModel, logger: Logger):
        super().__init__()
        self._logger = logger
        self._state_model = state_model

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
    def index_drop_check(self, dropped_data: dict) -> None:
        """Check if the dropped data is compatible with the current run settings."""

        df = pd.DataFrame(dropped_data["decoded_data"])

        max_index_i7_len = df["IndexI7"].str.len().max() if "IndexI7" in df.columns else None
        max_index_i5_len = df["IndexI5"].str.len().max() if "IndexI5" in df.columns else None

        if max_index_i7_len and max_index_i5_len:
            if (max_index_i7_len <= self._state_model.index1_cycles and
                    max_index_i5_len <= self._state_model.index2_cycles):
                self.index_drop_ok.emit(dropped_data)
                return

        elif max_index_i7_len:
            if max_index_i7_len <= self._state_model.index1_cycles:
                self.index_drop_ok.emit(dropped_data)
                return

        elif max_index_i5_len:
            if max_index_i5_len <= self._state_model.index2_cycles:
                self.index_drop_ok.emit(dropped_data)
                return

        self._logger.warning("Dropped indexes not compatible with run cycles.")

    @staticmethod
    def _get_profile_dragen_version(application_profile: dict):
        if not application_profile:
            return None

        if application_profile.get("ApplicationType") != "Dragen":
            return None

        return application_profile.get("Settings", {}).get("DragenVersion")

    @Slot(object)
    def verify_dragen_ver_compatibility(self, data):

        new_application_dragen_version = self._get_profile_dragen_version(data)
        prev_set_application_dragen_version = self._state_model.dragen_app_version

        if not prev_set_application_dragen_version:
            self.application_profile_ok.emit(data)
            return

        if not new_application_dragen_version:
            self.application_profile_ok.emit(data)
            return

        if prev_set_application_dragen_version == new_application_dragen_version:
            self.application_profile_ok.emit(data)
            return

        self._logger.warning("Dropped application profile not compatible with previous profiles.")

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


    def _validate_override_pattern(self, oc_part_key, oc_part_string):
        if re.fullmatch(self._oc_validate_pattern[oc_part_key], oc_part_string):
            return True

        return False

    def _nonvariable_oc_len(self, oc_part_key, oc_part_str):
        matches = re.findall(self._oc_parts_re[oc_part_key], oc_part_str)

        preset_oc_len = 0
        for m in matches[0]:
            if "{" not in m:
                preset_oc_len += int(m[1:])

        return preset_oc_len
