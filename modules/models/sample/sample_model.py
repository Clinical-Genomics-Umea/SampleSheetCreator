
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
            action (str): The action being performed on the mime data.
            row (int): The row in which the data is to be dropped.
            column (int): The column in which the data is to be dropped.
            parent (QObject): The parent object of the data.

        Returns:
            bool: True if the mime data has the format "application/json", False otherwise.
        """

        return bool(data.hasFormat("application/json"))

    def set_dropped_index_data(self, data):
        start_row = data["start_row"]

        print(data)

        print(f"set_dropped_index_data: start_row={start_row}")
        print(f"set_dropped_index_data: decoded_data={data['decoded_data']}")

        self.blockSignals(True)

        for i, row_data in enumerate(data["decoded_data"]):
            for key, value in row_data.items():
                if key in self.fields:
                    column = self.fields.index(key)
                    print(f"set_dropped_index_data: setting {key} to {value} at row {i+start_row}, column {column}")
                    self.setData(self.index(start_row + i, column), value)

        self.blockSignals(False)

        topLeft = self.index(0, 0)
        bottomRight = self.index(self.rowCount() - 1, self.columnCount() - 1)

        print(f"before data changed")

        self.dataChanged.emit(
            topLeft,
            bottomRight,
            Qt.DisplayRole,
        )

        print(f"after data changed")

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

        json_data_qba = data.data("application/json")
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

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert the data in the model to a DataFrame.

        Returns:
            DataFrame: A DataFrame containing the data from the model.
        """
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
                # If the item is None, use None as the value
                # Otherwise, use the text of the item
                row_data.append(item.text() if item is not None else None)
            data.append(row_data)

        # Create a DataFrame from the extracted data
        df = pd.DataFrame(data)

        # Optionally, set the column headers
        headers = [self.headerData(i, Qt.Horizontal) for i in range(columns)]
        df.columns = headers

        # Calculate the reverse complement of the IndexI5 column
        df["IndexI5RC"] = df["IndexI5"].apply(self.reverse_complement)

        # Replace empty strings and whitespace-only strings with NaN
        # and drop any rows that contain only NaN values
        df.replace("", pd.NA, inplace=True)
        df.replace(r"^\s*$", pd.NA, regex=True)
        df.dropna(how="all", inplace=True)
        return df

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
