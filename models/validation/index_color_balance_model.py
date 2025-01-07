import json

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel


class IndexColorBalanceModel(QStandardItemModel):

    def __init__(self, base_colors, parent):
        super(IndexColorBalanceModel, self).__init__(parent=parent)
        self.dataChanged.connect(self.update_summation)

        self._transformed_base_colors = {
            key: [color[0].upper() for color in colors]
            for key, colors in base_colors.items()
        }

    def data(self, index, role=Qt.DisplayRole):
        # Only modify data for display purposes
        if role == Qt.DisplayRole:
            original_value = super().data(index, role)
            if original_value == "nan":
                return "-"
        return super().data(index, role)

    def update_summation(self):

        for col in range(2, self.columnCount()):
            bases_count = {"A": 0, "C": 0, "G": 0, "T": 0}
            merged = {}

            for row in range(self.rowCount() - 1):
                proportion = int(self.item(row, 1).text())
                base = self.item(row, col).text()

                if base in ["A", "C", "G", "T"]:
                    bases_count[base] += proportion

            color_counts = self._generic_base_to_color_count(bases_count)
            normalized_color_counts = self._normalize(color_counts)
            normalized_base_counts = self._normalize(bases_count)

            merged["colors"] = normalized_color_counts
            merged["bases"] = normalized_base_counts
            norm_json = json.dumps(merged)

            last_row = self.rowCount() - 1
            self.setData(self.index(last_row, col), norm_json, Qt.EditRole)

    @staticmethod
    def merge(dict1, dict2):
        res = dict1 | {"--": "---"} | dict2
        return res

    @staticmethod
    def _normalize(input_dict):
        # Calculate the sum of values in the input dictionary
        total = sum(input_dict.values())

        if total == 0:
            total = 0.00001

        # Normalize the values and create a new dictionary
        normalized_dict = {
            key: round(value / total, 2) for key, value in input_dict.items()
        }

        return normalized_dict

    def _generic_base_to_color_count(self, dict1):
        color_count = {
            "B": 0,
            "G": 0,
            "D": 0,
        }

        for base, count in dict1.items():

            base_colors = self._transformed_base_colors[base]
            no_colors = len(base_colors)

            for color in base_colors:
                color_count[color] += count / no_colors

        return color_count
