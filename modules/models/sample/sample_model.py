import ast
import re

import pandas as pd
from PySide6.QtCore import Qt, QSortFilterProxyModel, Signal
from PySide6.QtGui import QStandardItemModel, QStandardItem

from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.sample.samplesheet_fns import to_json
from modules.utils.utils import decode_bytes_json


def get_column_headers(fields):
    headers = []
    for section in fields:
        headers.extend(iter(fields[section]))
    return headers


def field_count(fields):
    return sum(len(fields[section]) for section in fields)


class SampleModel(QStandardItemModel):

    dropped_data = Signal(object)
    index_minmax_ready = Signal(int, int, int, int)

    def __init__(self, configuration_manager: ConfigurationManager):
        super(SampleModel, self).__init__()
        self._configuration_manager = configuration_manager

        self.sections_fields = self._configuration_manager.samples_settings["fields"]
        self.row_count = self._configuration_manager.samples_settings["row_count"]
        self.fields = get_column_headers(self.sections_fields)

        self.setColumnCount(len(self.fields))
        self.setHorizontalHeaderLabels(self.fields)
        self.setRowCount(self.row_count)
        self.set_empty_strings()

        self.select_samples = False

        self.refresh_view()

        self.dataChanged.connect(self._index_minmax_sender)

    def _index_minmax_sender(self):

        index_i7_col = self.fields.index("IndexI7")
        index_i5_col = self.fields.index("IndexI5")

        index_i7_lengths = [len(self.item(row, index_i7_col).text())
                            for row in range(self.rowCount()) if self.item(row, index_i7_col)]
        index_i5_lengths = [len(self.item(row, index_i5_col).text())
                            for row in range(self.rowCount()) if self.item(row, index_i5_col)]

        if index_i7_lengths:
            index_i7_minlen, index_i7_maxlen = min(index_i7_lengths), max(index_i7_lengths)
        else:
            index_i7_minlen, index_i7_maxlen = 0, 0  # or some other default values

        if index_i5_lengths:
            index_i5_minlen, index_i5_maxlen = min(index_i5_lengths), max(index_i5_lengths)
        else:
            index_i5_minlen, index_i5_maxlen = 0, 0  # or some other default values

        self.index_minmax_ready.emit(index_i7_minlen, index_i7_maxlen, index_i5_minlen, index_i5_maxlen)



    def refresh_view(self):

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
            action (str): The action being performed on the data.
            row (int): The row in which the data is to be dropped.
            column (int): The column in which the data is to be dropped.
            parent (QObject): The parent object of the data.

        Returns:
            bool: True if the mime data has the format "application/json", False otherwise.
        """

        return bool(data.hasFormat("application/json"))

    def set_dropped_index_data(self, data):
        start_row = data["start_row"]

        self.blockSignals(True)

        for i, row_data in enumerate(data["decoded_data"]):
            for key, value in row_data.items():
                if key in self.fields:
                    column = self.fields.index(key)
                    self.setData(self.index(start_row + i, column), value)

        self.blockSignals(False)

        topLeft = self.index(0, 0)
        bottomRight = self.index(self.rowCount() - 1, self.columnCount() - 1)

        self.dataChanged.emit(
            topLeft,
            bottomRight,
            Qt.DisplayRole,
        )

        return True

    def _find_first_empty_row(self):
        """
        Find the first empty row in the QStandardItemModel.
        An empty row is where all columns are empty (optional: customize this logic).
        """
        row_count = self.rowCount()
        column_count = self.columnCount()

        for row in range(row_count):
            is_empty = True
            for col in range(column_count):
                item = self.item(row, col)
                if item is not None and item.text().strip() != "":
                    is_empty = False
                    break
            if is_empty:
                return row
        return row_count

    def set_worksheet_data(self, df):
        model_columns = [self.headerData(col, Qt.Horizontal) for col in range(self.columnCount())]

        for df_index, df_row in df.iterrows():
            # Find the first empty row in the model
            first_empty_row = self._find_first_empty_row()
            # Add items to the row by matching column names
            for col_index, column_name in enumerate(model_columns):
                if column_name in df.columns:
                    value = df_row[column_name]

                    if isinstance(value, list):
                        value = to_json(value)

                    if isinstance(value, dict):
                        value = to_json(value)

                    item = QStandardItem(str(value))
                    self.setItem(first_empty_row, col_index, item)

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

        json_data_qba = data._profile("application/json")
        decoded_data = decode_bytes_json(json_data_qba)


        data = {"start_row": parent.row(), "decoded_data": decoded_data}
        self.dropped_data.emit(data)

        # self.blockSignals(True)
        #
        # for i, row_data in enumerate(decoded_data):
        #     for key, value in row_data.items():
        #         row = parent.row() + i
        #         if key in self.fields:
        #             column = self.fields.index(key)
        #             self.setData(self.index(row, column), value)
        #
        # self.blockSignals(False)
        #
        # self.dataChanged.emit(
        #     self.index(0, 0),
        #     self.index(self.rowCount() - 1, self.columnCount() - 1),
        #     Qt.DisplayRole,
        # )
        #
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

    def _convert_string_to_list(self, value):
        """Convert string representation of a list to a Python list.
        
        Args:
            value: The value to convert (string, list, or other)
            
        Returns:
            The converted value or original value if not a string list representation
        """
        if not isinstance(value, str) or not value.startswith('[') or not value.endswith(']'):
            return value
            
        try:
            # Try to evaluate as a Python literal (safe for strings, numbers, tuples, lists, dicts, booleans, and None)
            import ast
            result = ast.literal_eval(value)
            return result if isinstance(result, list) else value
        except (ValueError, SyntaxError):
            # If evaluation fails, try to parse as a list of strings
            try:
                # Remove brackets and split by comma, then strip whitespace
                items = [item.strip().strip("'\"") for item in value[1:-1].split(',')]
                # Remove empty strings that might result from splitting
                return [item for item in items if item]
            except Exception:
                return value

    def get_index_length_stats(self) -> dict:
        """
        Optimized version to calculate min/max lengths of IndexI5 and IndexI7 columns.

        Returns:
            dict: {
                'IndexI5': {'min_len': int, 'max_len': int},
                'IndexI7': {'min_len': int, 'max_len': int}
            }
        """
        stats = {
            'IndexI5': {'min_len': float('inf'), 'max_len': 0},
            'IndexI7': {'min_len': float('inf'), 'max_len': 0}
        }

        try:
            i5_col = self.fields.index("IndexI5")
            i7_col = self.fields.index("IndexI7")
        except ValueError:
            return {
                'IndexI5': {'min_len': 0, 'max_len': 0},
                'IndexI7': {'min_len': 0, 'max_len': 0}
            }

        # Pre-fetch all items to reduce method calls
        row_count = self.rowCount()
        i5_items = [self.item(row, i5_col) for row in range(row_count)]
        i7_items = [self.item(row, i7_col) for row in range(row_count)]

        # Process IndexI5
        i5_min = float('inf')
        i5_max = 0

        for item in i5_items:
            if item and (text := item.text().strip()):
                length = len(text)
                if length < i5_min:
                    i5_min = length
                if length > i5_max:
                    i5_max = length

        # Process IndexI7
        i7_min = float('inf')
        i7_max = 0

        for item in i7_items:
            if item and (text := item.text().strip()):
                length = len(text)
                if length < i7_min:
                    i7_min = length
                if length > i7_max:
                    i7_max = length

        # Update stats with found values or 0 if none found
        if i5_min != float('inf'):
            stats['IndexI5'] = {'min_len': i5_min, 'max_len': i5_max}
        if i7_min != float('inf'):
            stats['IndexI7'] = {'min_len': i7_min, 'max_len': i7_max}

        return stats

    def to_dataframe(self) -> pd.DataFrame:
        # Get all data at once using list comprehension
        data = [
            [self.item(row, col).text() if self.item(row, col) is not None else None
             for col in range(self.columnCount())]
            for row in range(self.rowCount())
        ]

        # Create DataFrame in one go
        headers = [self.headerData(i, Qt.Horizontal) for i in range(self.columnCount())]
        df = pd.DataFrame(data, columns=headers)

        # Early return for empty DataFrames
        if df.empty:
            return df

        # Calculate reverse complement if needed
        if "IndexI5" in df.columns:
            df["IndexI5RC"] = df["IndexI5"].apply(self.reverse_complement)

        # Clean data
        df = df.replace("", pd.NA).replace(r"^\s*$", pd.NA, regex=True)
        df = df.dropna(how="all")

        # Apply conversions only to non-NA values
        if not df.empty:
            if "BarcodeMismatchesIndex1" in df.columns:
                df["BarcodeMismatchesIndex1"] = df["BarcodeMismatchesIndex1"].apply(self.safe_convert_numeric)
            if "BarcodeMismatchesIndex2" in df.columns:
                df["BarcodeMismatchesIndex2"] = df["BarcodeMismatchesIndex2"].apply(self.safe_convert_numeric)
            if "Lane" in df.columns:
                df["Lane"] = df["Lane"].apply(self.safe_literal_eval)
            if "ApplicationProfile" in df.columns:
                df["ApplicationProfile"] = df["ApplicationProfile"].apply(self.safe_literal_eval)

        return df

    @staticmethod
    def safe_convert_numeric(x):

        if not isinstance(x, str):
            return pd.NA

        try:
            return int(x)

        except Exception as e:
            return pd.NA


    @staticmethod
    def safe_literal_eval(x):
        if pd.isna(x):  # This catches <NA>, NaN, None
            return None  # or return [] for empty list, or whatever default you want
        try:
            return ast.literal_eval(x)
        except (ValueError, SyntaxError):
            return None  # Handle other malformed strings


    @staticmethod
    def reverse_complement(sequence):
        complement = {"A": "T", "T": "A", "C": "G", "G": "C"}
        return "".join(complement[base] for base in reversed(sequence))


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
