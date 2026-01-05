import logging

import pandas as pd
from PySide6.QtCore import QSortFilterProxyModel, Qt, Signal, QModelIndex
from PySide6.QtGui import QStandardItem, QStandardItemModel


class WorksheetPandasModel(QStandardItemModel):
    """QStandardItemModel that can be populated from a pandas DataFrame"""

    model_changed = Signal()

    def __init__(self, logger: logging.Logger, parent=None):
        super().__init__(parent)
        self._df = pd.DataFrame()
        self._logger = logger

    def get_column_index(self, name: str) -> int:
        """
        Get the index of a column by name.

        Args:
            name (str): Name of the column to find

        Returns:
            int: Column index if found, -1 if not found
        """
        try:
            return int(self._df.columns.get_loc(name))
        except (KeyError, ValueError):
            return -1

    def set_dataframe(self, df):
        """Replace the model's data with a new DataFrame"""
        # Store the new data
        self._df = df.copy()  # Make a copy to avoid external modifications

        # Reset proxy models
        for proxy in self.findChildren(QSortFilterProxyModel):
            if hasattr(proxy, 'reset_filter'):
                proxy.reset_filter()

        # Repopulate the model
        self._populate_from_dataframe()
        self.model_changed.emit()

    def _populate_from_dataframe(self):
        """Clear and repopulate the model from the DataFrame"""
        # Clear existing data
        self.removeRows(0, self.rowCount())
        self.setColumnCount(0)

        if self._df.empty:
            return

        # Set headers
        self.setColumnCount(len(self._df.columns))
        self.setHorizontalHeaderLabels(self._df.columns.tolist())

        # Populate data
        for row_idx in range(len(self._df)):
            items = []
            for col_idx in range(len(self._df.columns)):
                value = self._df.iloc[row_idx, col_idx]
                if isinstance(value, list):
                    value = str(value)
                # Convert to string, handling NaN and None
                if pd.isna(value):
                    item = QStandardItem("")
                else:
                    item = QStandardItem(str(value))
                items.append(item)
            self.appendRow(items)

    @property
    def df(self):
        """Return a copy of the current DataFrame"""
        return self._df


class WorksheetIDModel(QStandardItemModel):
    """QStandardItemModel that can be populated from a pandas DataFrame"""

    model_changed = Signal()

    def __init__(self, logger: logging.Logger, target_colname: str = "WorksheetID", parent=None):
        super().__init__(parent)
        self._df = pd.DataFrame()
        self._logger = logger
        self._target_colname = target_colname

    def get_column_index(self, name: str) -> int:
        """
        Get the index of a column by name.

        Args:
            name (str): Name of the column to find

        Returns:
            int: Column index if found, -1 if not found
        """
        try:
            return int(self._df.columns.get_loc(name))
        except (KeyError, ValueError):
            return -1

    def set_dataframe(self, df):
        """Replace the model's data with a new DataFrame"""
        # Store the new data
        self._df = df[[self._target_colname]].drop_duplicates()  # Make a copy to avoid external modifications

        # Reset proxy models
        # Repopulate the model
        self._populate_from_dataframe()

    def _populate_from_dataframe(self):
        """Clear and repopulate the model from the DataFrame"""
        # Clear existing data
        self.removeRows(0, self.rowCount())
        self.setColumnCount(0)

        if self._df.empty:
            return

        # Set headers
        self.setColumnCount(len(self._df.columns))
        self.setHorizontalHeaderLabels(self._df.columns.tolist())

        # Populate data
        for row_idx in range(len(self._df)):
            items = []
            for col_idx in range(len(self._df.columns)):
                value = self._df.iloc[row_idx, col_idx]
                if isinstance(value, list):
                    value = str(value)
                # Convert to string, handling NaN and None
                if pd.isna(value):
                    item = QStandardItem("")
                else:
                    item = QStandardItem(str(value))
                items.append(item)
            self.appendRow(items)

    @property
    def df(self):
        """Return a copy of the current DataFrame"""
        return self._df




class UniqueWorksheetProxyModel(QSortFilterProxyModel):
    """Proxy model that shows only unique WorksheetIDs (first column)"""

    def __init__(self, parent=None, id_column_name="WorksheetID"):
        super().__init__(parent)
        self.setDynamicSortFilter(True)
        self.seen_ids = set()
        self.id_column_name = id_column_name
        self.id_column_index = 0

    def filterAcceptsRow(self, source_row, source_parent):
        source_model = self.sourceModel()
        if not source_model:
            return False

        # Reset column index if needed
        if hasattr(source_model, 'get_column_index'):
            self.id_column_index = source_model.get_column_index(self.id_column_name)

            print(self.id_column_index, self.id_column_name)

            if self.id_column_index == -1:
                return False

        # Get the worksheet ID
        index = source_model.index(source_row, self.id_column_index, source_parent)
        worksheet_id = source_model.data(index, Qt.DisplayRole)

        # Only show if we haven't seen this ID yet
        if worksheet_id not in self.seen_ids:
            self.seen_ids.add(worksheet_id)  # Add to seen_ids
            return True
        return False

    def reset_filter(self):
        """Reset the seen IDs and refilter"""

        print()

        self.seen_ids.clear()
        self.invalidate()


# class UniqueWorksheetProxyModel(QSortFilterProxyModel):
#     """Proxy model that shows only unique WorksheetIDs (first column)"""
#
#     def __init__(self, parent=None, id_column_name="WorksheetID"):
#         super().__init__(parent)
#
#         self.setDynamicSortFilter(True)
#
#         self.seen_ids = set()
#         self.id_column_name = id_column_name
#         self.id_column_index = 0  # Default to 0 if column not found
#
#     # def filterAcceptsRow(self, source_row, source_parent):
#     #     # Get the WorksheetID from the source model using column name
#     #     source_model = self.sourceModel()
#     #     if source_model is None:
#     #         return False
#     #
#     #     if self.id_column_index is not None:
#     #         colnames = list(source_model.df.columns)
#     #         self.id_column_index = colnames.index(self.id_column_name)
#     #
#     #     index = source_model.index(source_row, self.id_column_index, source_parent)
#     #     worksheet_id = source_model.data(index, Qt.DisplayRole)
#     #
#     #     # Only accept if we haven't seen this ID yet
#     #     if worksheet_id not in self.seen_ids:
#     #         self.seen_ids.add(worksheet_id)
#     #         return True
#     #     return False
#
#     def filterAcceptsRow(self, source_row, source_parent):
#         # Get the source model
#         source_model = self.sourceModel()
#         if source_model is None:
#             return False
#
#         # Get the column index of the ID column
#         if hasattr(source_model, 'get_column_index'):
#             self.id_column_index = source_model.get_column_index(self.id_column_name)
#             if self.id_column_index == -1:  # Column not found
#                 return False
#
#         # Get the worksheet ID
#         index = source_model.index(source_row, self.id_column_index, source_parent)
#         worksheet_id = source_model.data(index, Qt.DisplayRole)
#
#         # Only accept if we haven't seen this ID yet
#         if worksheet_id not in self.seen_ids:
#             self.seen_ids.add(worksheet_id)
#             return True
#         return False
#
#     def reset_filter(self):
#         """Reset the seen IDs and refilter"""
#         self.seen_ids.clear()
#         self.invalidate()

class WorksheetDetailProxyModel(QSortFilterProxyModel):
    """Proxy model that filters rows based on selected WorksheetID"""

    def __init__(self, id_column_name="WorksheetID", parent=None):
        super().__init__(parent)
        self.selected_worksheet = None
        self.setDynamicSortFilter(True)
        self.id_column_name = id_column_name
        self.id_column_index = 0  # Default to 0 if column not found

    def set_worksheet_filter(self, worksheet_id):
        """Set which worksheet to filter by"""
        self.selected_worksheet = worksheet_id
        self.invalidate()

    def filterAcceptsRow(self, source_row, source_parent):
        if self.selected_worksheet is None:
            return False

        source_model = self.sourceModel()
        if source_model is None:
            return False

        if self.id_column_index is not None:
            colnames = list(source_model.df.columns)
            self.id_column_index = colnames.index(self.id_column_name)

        # Get the WorksheetID from the source model (column 0)
        source_model = self.sourceModel()
        if source_model is None:
            return False

        index = source_model.index(source_row, 0, source_parent)
        worksheet_id = source_model.data(index, Qt.DisplayRole)

        return worksheet_id == self.selected_worksheet

    def reset_filter(self):
        """Reset the seen IDs and refilter"""
        self.selected_worksheet = None
        self.invalidate()