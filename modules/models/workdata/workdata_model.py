import logging

import pandas as pd
from PySide6.QtCore import QModelIndex, QSortFilterProxyModel
from PySide6.QtGui import QStandardItemModel, Qt
from typing import Any


class WorkDataModel(QStandardItemModel):
    def __init__(self, logger: logging.Logger, parent=None):
        super().__init__(parent)
        self._work_data = None
        self._logger = logger

    def set_work_data(self, work_data: pd.DataFrame):
        self._work_data = work_data
        self._logger.info("Work data set")
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount() - 1, self.columnCount() - 1))

    def rowCount(self, parent=QModelIndex()) -> int:
        if self._work_data is None:
            return 0
        return len(self._work_data)

    def columnCount(self, parent=QModelIndex()) -> int:
        if self._work_data is None:
            return 0
        return len(self._work_data.columns)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return str(self._work_data.iloc[index.row(), index.column()])
        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole):
        if not index.isValid():
            return False
        if role == Qt.EditRole:
            self._work_data.iloc[index.row(), index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._work_data.columns[section])
            elif orientation == Qt.Vertical:
                return str(self._work_data.index[section])
        return None


class UniqueWorksheetCreatedProxyModel(QSortFilterProxyModel):
    """
    Keeps only one row for each unique (worksheet, created) combination.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._seen = set()

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()

        worksheet_index = model.index(source_row, 0, source_parent)
        created_index = model.index(source_row, 1, source_parent)

        worksheet = model.data(worksheet_index, Qt.DisplayRole)
        created = model.data(created_index, Qt.DisplayRole)

        key = (worksheet, created)

        # Only allow the first occurrence of each key
        if key in self._seen:
            return False

        self._seen.add(key)
        return True

    def invalidateFilter(self):
        """Reset cache each time filter is re-applied."""
        self._seen.clear()
        super().invalidateFilter()



class WorksheetFilterProxyModel(QSortFilterProxyModel):
    """Filters rows by selected worksheet."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_worksheet = None

    def set_worksheet(self, worksheet):
        self.selected_worksheet = worksheet
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if not self.selected_worksheet:
            return False
        model = self.sourceModel()
        worksheet = model.index(source_row, 0, source_parent).data()
        return worksheet == self.selected_worksheet


