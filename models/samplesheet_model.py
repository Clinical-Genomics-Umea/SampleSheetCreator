import re

import numpy as np
import pandas as pd
from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtGui import QStandardItemModel, QStandardItem

from utils.utils import decode_bytes_json


def get_column_headers(fields):
    headers = []
    for section in fields:
        headers.extend(iter(fields[section]))
    return headers


def field_count(fields):
    return sum(len(fields[section]) for section in fields)


class SampleSheetModel(QStandardItemModel):
    def __init__(self, sample_settings):
        super(SampleSheetModel, self).__init__()

        self.sections_fields = sample_settings["fields"]
        self.fields = get_column_headers(self.sections_fields)

        self.setColumnCount(len(self.fields))
        self.setHorizontalHeaderLabels(self.fields)
        self.setRowCount(sample_settings["row_count"])
        self.set_empty_strings()

        self.select_samples = False

        self.refresh_view()

    def refresh_view(self):
        # Emit dataChanged signal to notify the view to update
        top_left = self.index(0, 0)
        bottom_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bottom_right)

    def set_empty_strings(self):
        """
        Set empty strings for each cell in the table.

        This function iterates over each cell in the table and sets an empty string value.

        Parameters:
        - self: The reference to the instance of the class.

        Returns:
        - None
        """
        for row in range(self.rowCount()):
            for column in range(self.columnCount()):
                self.setData(self.index(row, column), "")

    def canDropMimeData(self, data, action, row, column, parent):
        """
        Check if the given mime data can be dropped into the specified row and column.

        Parameters:
            data (MimeData): The mime data object being dropped.
            action (str): The action being performed on the mime data.
            row (int): The row in which the data is to be dropped.
            column (int): The column in which the data is to be dropped.
            parent (QObject): The parent object of the data.

        Returns:
            bool: True if the mime data has the format "application/json", False otherwise.
        """
        return bool(data.hasFormat("application/json"))

    def dropMimeData(self, data, action, row, column, parent) -> bool:
        """
        Drop the mime data into the specified location in the model.
        Args:
            data (QMimeData): The mime data to be dropped.
            action (Qt.DropAction): The action to be performed on the data.
            row (int): The row index of the drop location.
            column (int): The column index of the drop location.
            parent (QModelIndex): The parent index of the drop location.
        Returns:
            bool: True if the drop was successful, False otherwise.
        """
        json_data_qba = data.data("application/json")
        decoded_data = decode_bytes_json(json_data_qba)

        print(decoded_data)

        start_row = parent.row()

        self.blockSignals(True)

        for i, row_data in enumerate(decoded_data):
            for key, value in row_data.items():
                row = start_row + i
                if key in self.fields:
                    column = self.fields.index(key)
                    self.setData(self.index(row, column), value)

        self.blockSignals(False)
        self.dataChanged.emit(
            self.index(0, 0),
            self.index(self.rowCount() - 1, self.columnCount() - 1),
            Qt.DisplayRole,
        )

        return True

    def flags(self, index):
        """
        Return the item flags for the given index.

        Parameters:
            index (QModelIndex): The index of the item.

        Returns:
            int: The item flags.

        Description:
            This function returns the item flags for the given index. It calls the base class implementation
            of the flags() function and then checks if the index is valid. If the index is valid, the
            Qt.ItemFlags.ItemIsDropEnabled flag is added to the flags. Finally, the resulting flags are returned.
        """
        flags = super().flags(index)
        if index.isValid():
            flags |= Qt.ItemIsDropEnabled
        return flags

    def to_dataframe(self):
        # Get the number of rows and columns in the model
        rows = self.rowCount()
        columns = self.columnCount()

        # Initialize a list to hold the data
        data = []

        # Loop through the rows and columns to extract the data
        for row in range(rows):
            row_data = []
            for column in range(columns):
                item = self.item(row, column)
                row_data.append(item.text() if item is not None else None)
            data.append(row_data)

        # Create a DataFrame from the extracted data
        df = pd.DataFrame(data)

        # Optionally, set the column headers
        headers = [self.headerData(i, Qt.Horizontal) for i in range(columns)]
        df.columns = headers

        df["IndexI5RC"] = df["IndexI5"].apply(self.reverse_complement)

        df.replace("", pd.NA, inplace=True)
        df.dropna(how="all", inplace=True)
        df = self.explode_lane_df(df)

        # print("to dataframe", df.to_string())

        return df

    def to_dataframe_cleaned(self):
        df = self.to_dataframe()
        return df.replace(r"^\s*$", np.nan, regex=True)

    @staticmethod
    def reverse_complement(sequence):
        complement = {"A": "T", "T": "A", "C": "G", "G": "C"}
        return "".join(complement[base] for base in reversed(sequence))

    @staticmethod
    def split_lanes(lane_string: str):
        return re.split(r"\D+", lane_string.strip())

    def explode_lane_df(self, df: pd.DataFrame):
        df["Lane"] = df["Lane"].apply(self.split_lanes)
        df = df.explode("Lane")
        df["Lane"] = df["Lane"].astype(int)
        return df


class CustomProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_text = ""

    def filterAcceptsRow(self, source_row, source_parent):
        if not self.filter_text:
            return True
        for column in range(self.sourceModel().columnCount()):
            index = self.sourceModel().index(source_row, column, source_parent)
            data = self.sourceModel().data(index, Qt.DisplayRole)
            if self.filter_text.lower() in str(data).lower():
                return True
        return False

    def set_filter_text(self, text):
        self.filter_text = text
        self.invalidateFilter()
