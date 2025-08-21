from logging import Logger
from PySide6.QtCore import QObject, Signal

from modules.models.application.application_manager import ApplicationManager
from modules.models.rundata.rundata_model import RunDataModel
from modules.models.sample.sample_model import StateModel
from modules.utils.utils import json_to_obj


class DataStateModel(QObject):

    freeze_state_changed = Signal(bool)

    def __init__(self,
                 sample_model: StateModel,
                 rundata_model: RunDataModel,
                 application_manager: ApplicationManager,
                 logger: Logger):

        super().__init__()

        self._logger = logger
        self._sample_model = sample_model
        self._rundata_model = rundata_model
        self._application_manager = application_manager

        self._frozen = False

        self._sample_model.itemChanged.connect(self._unfreeze)
        self._rundata_model.run_data_ready.connect(self._unfreeze)

    def set_freeze_state(self, freeze_state: bool):
        if self._frozen != freeze_state:
            self._frozen = freeze_state
            self.freeze_state_changed.emit(self._frozen)

    def _unfreeze(self):
        self._frozen = False
        self.freeze_state_changed.emit(self._frozen)

    # def _freeze(self):
    #     self._frozen = True
    #     self.freeze_state_changed.emit(self._frozen)

    @property
    def freeze_state(self) -> bool:
        return self._frozen

    def run_read1_cycles(self):
        return self._rundata_model.read_1_cycles

    def run_read2_cycles(self):
        return self._rundata_model.read_2_cycles

    def run_index1_cycles(self):
        return self._rundata_model.index_1_cycles

    def run_index2_cycles(self):
        return self._rundata_model.index_2_cycles

    def sample_minlen_index_i7(self):
        return self._sample_min_strlen_in_column("IndexI7")

    def sample_maxlen_index_i7(self):
        return self._sample__max_strlen_in_column("IndexI7")

    def sample_minlen_index_i5(self):
        return self._sample_min_strlen_in_column("IndexI5")

    def sample_maxlen_index_i5(self):
        return self._sample__max_strlen_in_column("IndexI5")

    def application_compatibility(self, application_profile: str):

        application_obj = self._application_manager.profile_name_to_profile(application_profile)

        application_type = application_obj['ApplicationType']
        software_version = application_obj['Settings']['SoftwareVersion']

        column_index = -1
        for col in range(self._sample_model.columnCount()):
            header_item = self._sample_model.horizontalHeaderItem(col)
            if header_item and header_item.text() == "ApplicationProfile":
                column_index = col
                break

        set_application_profiles = []
        for row in range(self._sample_model.rowCount()):
            item = self._sample_model.item(row, column_index)
            if item:
                text = item.text().strip()
                if text:  # Ensure it's non-empty
                    json_obj = json_to_obj(text)
                    set_application_profiles.extend(json_obj)

        set_application_profiles = set(set_application_profiles)

        for set_application_profile in set_application_profiles:

            set_application_obj = self._application_manager.profile_name_to_profile(set_application_profile)

            set_application_type = set_application_obj['ApplicationType']
            set_software_version = set_application_obj['Settings']['SoftwareVersion']

            if set_application_type == application_type:
                if not set_software_version == software_version:
                    self._logger.error("Incompatible software version")
                    return False

            return True

        return True

    def index_i7_compatibility(self) -> bool:
        """Check if the sample index i7 lengths are compatible with the run data."""
        max_samples_index_i7_len = self._sample__max_strlen_in_column("IndexI7")
        if self._rundata_model.index_1_cycles and max_samples_index_i7_len:
            return max_samples_index_i7_len <= self._rundata_model.index_1_cycles
        return False

    def index_i5_compatibility(self) -> bool:
        """Check if the sample index i5 lengths are compatible with the run data."""
        max_samples_index_i7_len = self._sample__max_strlen_in_column("IndexI5")
        if self._rundata_model.index_1_cycles and max_samples_index_i7_len:
            return max_samples_index_i7_len <= self._rundata_model.index_1_cycles
        return False


    def _sample__max_strlen_in_column(self, column_name: str) -> int:
        """Returns the maximum string length for non-empty values in the specified column."""
        # Find the column index by matching the header text
        column_index = -1
        for col in range(self._sample_model.columnCount()):
            header_item = self._sample_model.horizontalHeaderItem(col)
            if header_item and header_item.text() == column_name:
                column_index = col
                break

        if column_index == -1:
            raise ValueError(f"Column '{column_name}' not found in the model.")

        max_length = 0
        for row in range(self._sample_model.rowCount()):
            item = self._sample_model.item(row, column_index)
            if item:
                text = item.text().strip()
                if text:  # Ensure it's non-empty
                    max_length = max(max_length, len(text))

        return max_length

    def _sample_min_strlen_in_column(self, column_name: str) -> int:
        """Returns the minimum string length for non-empty values in the specified column."""
        # Find the column index by matching the header text
        column_index = -1
        for col in range(self._sample_model.columnCount()):
            header_item = self._sample_model.horizontalHeaderItem(col)
            if header_item and header_item.text() == column_name:
                column_index = col
                break

        if column_index == -1:
            raise ValueError(f"Column '{column_name}' not found in the model.")

        min_length = 0
        for row in range(self._sample_model.rowCount()):
            item = self._sample_model.item(row, column_index)
            if item:
                text = item.text().strip()
                if text:  # Ensure it's non-empty
                    min_length = min(min_length, len(text))

        return min_length
