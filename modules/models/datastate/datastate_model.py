from PySide6.QtCore import QObject

from modules.models.rundata.rundata_model import RunDataModel
from modules.models.sample.sample_model import SampleModel


class DataStateModel(QObject):
    def __init__(self, sample_model: SampleModel, rundata_model: RunDataModel):
        super().__init__()
        self._state = {}
        self._constraints = []

    def set(self, key, value):
        if self._validate(key, value):
            self._state[key] = value
            self._apply_dependencies(key, value)
            return True
        return False

    def get(self, key):
        return self._state.get(key)

    def _validate(self, key, value):
        """Check if the new value conflicts with existing settings"""
        for constraint in self._constraints:
            if not constraint(self._state, key, value):
                return False
        return True

    def _apply_dependencies(self, key, value):
        """Update dependent settings"""
        # Example: Disable feature B if feature A is enabled
        if key == "feature_A" and value:
            self._state["feature_B"] = False

    def add_constraint(self, constraint_func):
        """Register constraint functions"""
        self._constraints.append(constraint_func)



    #     self.sample_model = sample_model
    #     self.rundata_model = rundata_model
    #
    #     self._read_cycles_dict = {}
    #     self._read_cycles_fields = []
    #     self._read_cycles_list = []
    #     self._has_rundata = False
    #
    #     self._max_index_i5_len = 0
    #     self._max_index_i7_len = 0
    #     self._min_index_i7_len = 0
    #     self._min_index_i5_len = 0
    #
    #
    # def sample_index_i7_compatible(self) -> bool:
    #     """Check if the sample index i7 lengths are compatible with the run data."""
    #     max_samples_index_i7_len = self.max_strlen_in_column("IndexI7")
    #     if self.rundata_model.index_1_cycles and max_samples_index_i7_len:
    #         return max_samples_index_i7_len <= self.rundata_model.index_1_cycles
    #     return False
    #
    # def sample_index_i5_compatible(self) -> bool:
    #     """Check if the sample index i5 lengths are compatible with the run data."""
    #     max_samples_index_i7_len = self.max_strlen_in_column("IndexI5")
    #     if self.rundata_model.index_1_cycles and max_samples_index_i7_len:
    #         return max_samples_index_i7_len <= self.rundata_model.index_1_cycles
    #     return False
    #
    #
    # def max_strlen_in_column(self, column_name: str) -> int:
    #     """Returns the maximum string length for non-empty values in the specified column."""
    #     # Find the column index by matching the header text
    #     column_index = -1
    #     for col in range(self.sample_model.columnCount()):
    #         header_item = self.sample_model.horizontalHeaderItem(col)
    #         if header_item and header_item.text() == column_name:
    #             column_index = col
    #             break
    #
    #     if column_index == -1:
    #         raise ValueError(f"Column '{column_name}' not found in the model.")
    #
    #     max_length = 0
    #     for row in range(self.sample_model.rowCount()):
    #         item = self.sample_model.item(row, column_index)
    #         if item:
    #             text = item.text().strip()
    #             if text:  # Ensure it's non-empty
    #                 max_length = max(max_length, len(text))
    #
    #     return max_length
    #
    # def min_strlen_in_column(self, column_name: str) -> int:
    #     """Returns the minimum string length for non-empty values in the specified column."""
    #     # Find the column index by matching the header text
    #     column_index = -1
    #     for col in range(self.sample_model.columnCount()):
    #         header_item = self.sample_model.horizontalHeaderItem(col)
    #         if header_item and header_item.text() == column_name:
    #             column_index = col
    #             break
    #
    #     if column_index == -1:
    #         raise ValueError(f"Column '{column_name}' not found in the model.")
    #
    #     min_length = 0
    #     for row in range(self.sample_model.rowCount()):
    #         item = self.sample_model.item(row, column_index)
    #         if item:
    #             text = item.text().strip()
    #             if text:  # Ensure it's non-empty
    #                 min_length = min(min_length, len(text))
    #
    #     return min_length
