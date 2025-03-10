from logging import Logger

from PySide6.QtCore import QObject

from modules.models.application.application_manager import ApplicationManager
from modules.models.rundata.rundata_model import RunDataModel
from modules.models.sample.sample_model import SampleModel
from modules.utils.utils import json_to_obj


class DataStateModel(QObject):
    def __init__(self,
                 sample_model: SampleModel,
                 rundata_model: RunDataModel,
                 application_manager: ApplicationManager,
                 logger: Logger):

        super().__init__()

        self.logger = logger
        self.sample_model = sample_model
        self.rundata_model = rundata_model
        self.application_manager = application_manager

    def minlen_index_i7(self):
        return self._min_strlen_in_column("IndexI7")

    def maxlen_index_i7(self):
        return self._max_strlen_in_column("IndexI7")

    def minlen_index_i5(self):
        return self._min_strlen_in_column("IndexI5")

    def maxlen_index_i5(self):
        return self._max_strlen_in_column("IndexI5")

    def application_compatibility(self, application_profile: str):

        application_obj = self.application_manager.app_profile_to_app_obj(application_profile)

        application_type = application_obj['ApplicationType']
        software_version = application_obj['Settings']['ApplicationType']
        fastq_compression_format = application_obj['Settings']['FastqCompressionFormat']

        column_index = -1
        for col in range(self.sample_model.columnCount()):
            header_item = self.sample_model.horizontalHeaderItem(col)
            if header_item and header_item.text() == "ApplicationProfile":
                column_index = col
                break

        set_application_profiles = []
        for row in range(self.sample_model.rowCount()):
            item = self.sample_model.item(row, column_index)
            if item:
                text = item.text().strip()
                if text:  # Ensure it's non-empty
                    json_obj = json_to_obj(text)
                    set_application_profiles.extend(json_obj)

        set_application_profiles = set(set_application_profiles)

        for set_application_profile in set_application_profiles:

            set_application_obj = self.application_manager.app_profile_to_app_obj(set_application_profile)

            set_application_type = set_application_obj['ApplicationType']
            set_software_version = set_application_obj['Settings']['ApplicationType']
            set_fastq_compression_format = set_application_obj['Settings']['FastqCompressionFormat']


            if set_application_type == application_type:
                if not set_software_version == software_version:
                    self.logger.error("incompatible software version")
                    return False
                if not set_fastq_compression_format == fastq_compression_format:
                    self.logger.error("incompatible compression format")
                    return False

            return True

    def index_i7_compatibility(self) -> bool:
        """Check if the sample index i7 lengths are compatible with the run data."""
        max_samples_index_i7_len = self._max_strlen_in_column("IndexI7")
        if self.rundata_model.index_1_cycles and max_samples_index_i7_len:
            return max_samples_index_i7_len <= self.rundata_model.index_1_cycles
        return False

    def index_i5_compatibility(self) -> bool:
        """Check if the sample index i5 lengths are compatible with the run data."""
        max_samples_index_i7_len = self._max_strlen_in_column("IndexI5")
        if self.rundata_model.index_1_cycles and max_samples_index_i7_len:
            return max_samples_index_i7_len <= self.rundata_model.index_1_cycles
        return False


    def _max_strlen_in_column(self, column_name: str) -> int:
        """Returns the maximum string length for non-empty values in the specified column."""
        # Find the column index by matching the header text
        column_index = -1
        for col in range(self.sample_model.columnCount()):
            header_item = self.sample_model.horizontalHeaderItem(col)
            if header_item and header_item.text() == column_name:
                column_index = col
                break

        if column_index == -1:
            raise ValueError(f"Column '{column_name}' not found in the model.")

        max_length = 0
        for row in range(self.sample_model.rowCount()):
            item = self.sample_model.item(row, column_index)
            if item:
                text = item.text().strip()
                if text:  # Ensure it's non-empty
                    max_length = max(max_length, len(text))

        return max_length

    def _min_strlen_in_column(self, column_name: str) -> int:
        """Returns the minimum string length for non-empty values in the specified column."""
        # Find the column index by matching the header text
        column_index = -1
        for col in range(self.sample_model.columnCount()):
            header_item = self.sample_model.horizontalHeaderItem(col)
            if header_item and header_item.text() == column_name:
                column_index = col
                break

        if column_index == -1:
            raise ValueError(f"Column '{column_name}' not found in the model.")

        min_length = 0
        for row in range(self.sample_model.rowCount()):
            item = self.sample_model.item(row, column_index)
            if item:
                text = item.text().strip()
                if text:  # Ensure it's non-empty
                    min_length = min(min_length, len(text))

        return min_length
