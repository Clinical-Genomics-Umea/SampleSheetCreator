import json
import os
from pathlib import Path

import yaml
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel


def read_yaml_file(filename):
    """
    Read a YAML file and return its data.

    Parameters:
        filename (str): The name of the YAML file to read.

    Returns:
        dict: The data loaded from the YAML file, or None if the file is not found or an error occurred.
    """
    # Get the path to the directory of the current module
    module_dir = os.path.dirname(__file__)

    # Combine the directory path with the provided filename to get the full path
    file_path = os.path.join(module_dir, filename)

    try:
        with open(file_path, 'r') as file:
            # Load YAML data from the file
            data = yaml.safe_load(file)
        return data
    except FileNotFoundError:
        print(f"File '{filename}' not found in the module directory.")
        return None
    except Exception as e:
        print(f"An error occurred while reading '{filename}': {e}")
        return None


def decode_bytes_json(data):
    """
    Decode bytes to JSON.

    Args:
        data (bytes): The bytes data to decode.

    Returns:
        dict: The decoded JSON data.

    Raises:
        ValueError: If there is an error decoding the JSON data.

    """
    try:
        decoded_data = bytes(data).decode()
        return json.loads(decoded_data)
    except json.JSONDecodeError as e:
        raise ValueError("Error decoding JSON data") from e


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

        self.sections_fields = sample_settings['fields']
        self.fields = get_column_headers(self.sections_fields)

        self.setColumnCount(len(self.fields))
        self.setHorizontalHeaderLabels(self.fields)
        self.setRowCount(sample_settings['row_count'])
        self.set_empty_strings()

        self.select_samples = False


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

        start_row = parent.row()

        self.blockSignals(True)

        for i, row_data in enumerate(decoded_data):
            for key, value in row_data.items():
                row = start_row + i

                if key in self.fields:
                    column = self.fields.index(key)

                    print(column, row, key, value)

                    self.setData(self.index(row, column), value)

        self.blockSignals(False)
        self.dataChanged.emit(
            self.index(0, 0),
            self.index(self.rowCount() - 1, self.columnCount() - 1),
            Qt.DisplayRole
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

    def set_profile_on_selected(self, selected_indexes, profile_name):
        """
        Sets the profile name on selected rows in the table.

        Args:
            selected_indexes (list): A list of QModelIndex objects representing the selected rows.
            profile_name (str): The name of the profile to set.

        Returns:
            None
        """
        print("set_profile")
        profile_name_column = self.fields.index("ProfileName")
        print("got col")
        self.blockSignals(True)
        print("blocked")
        for index in selected_indexes:
            new_index = self.index(index.row(), profile_name_column)
            self.setData(new_index, profile_name)

        self.blockSignals(False)
        print("unblocked")
        self.dataChanged.emit(
            self.index(0, 0),
            self.index(self.rowCount() - 1, self.columnCount() - 1),
            Qt.DisplayRole
        )

