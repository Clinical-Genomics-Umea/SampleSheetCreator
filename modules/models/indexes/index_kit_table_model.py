import json

import pandas as pd
from PySide6.QtCore import QAbstractTableModel, Qt, QMimeData


class IndexKitTableModel(QAbstractTableModel):
    def __init__(self, dataframe: pd.DataFrame):
        super(IndexKitTableModel, self).__init__()

        self.dataframe = dataframe

    def data(self, index, role):
        """
        Retrieves data from the model for the given index and role.
        Args:
            index (QModelIndex): The index of the data to retrieve.
            role (int): The role of the data to retrieve.
        Returns:
            str: The retrieved data as a string.
        """
        if role == Qt.DisplayRole:
            value = self.dataframe.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        """
        Returns the number of rows in the data.
        Parameters:
            index (int): The index of the data.
        Returns:
            int: The number of rows in the data.
        """
        return self.dataframe.shape[0]

    def columnCount(self, index):
        """
        Returns the number of columns in the data.
        Parameters:
            index (int): The index of the data.
        Returns:
            int: The number of columns in the data.
        """
        return self.dataframe.shape[1]

    def headerData(self, section, orientation, role):
        """
        Get the header data for the given section, orientation, and role.
        Parameters:
            section (int): The index of the column/row.
            orientation (int): The orientation of the header (Qt.Horizontal or Qt.Vertical).
            role (int): The role of the header data (Qt.DisplayRole).
        Returns:
            str: The header data for the given section, or None if the role is not Qt.DisplayRole.
        """
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.dataframe.columns[section])

            if orientation == Qt.Vertical:
                return str(self.dataframe.index[section])

    def flags(self, index):
        """
        Generate the flags for the given index.
        Args:
            index (QModelIndex): The index for which to generate the flags.
        Returns:
            int: The flags generated for the index.
        """
        flags = super().flags(index)
        if index.isValid():
            flags |= Qt.ItemIsDragEnabled
        return flags

    def indexes_to_rows(self, indexes):
        row_indexes = {index.row() for index in indexes}
        return sorted(list(row_indexes))

    def mimeData(self, indexes):
        """
        Generates a QMimeData object containing the data to be transferred to external applications.

        Parameters:
            indexes (List[QModelIndex]): A list of QModelIndex objects representing the selected indexes.

        Returns:
            QMimeData: The QMimeData object containing the transferred data.
        """

        mime_data = QMimeData()
        # row_indexes = {index.row() for index in indexes}
        rows = self.indexes_to_rows(indexes)
        df = pd.DataFrame(self.dataframe, index=rows)
        records = df.to_dict(orient="records")

        # Convert the records to JSON
        json_data = json.dumps(records)

        bytes_data = bytes(json_data, "utf-8")
        mime_data.setData("application/json", bytes_data)

        return mime_data
