import logging
from typing import Any

import pandas as pd
from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QStandardItemModel


class WorkSheetIDModel(QStandardItemModel):
    """A model that provides a pandas DataFrame to QTableView."""

    def __init__(self, logger: logging.Logger, parent=None):
        super().__init__(parent)
        self._worksheets_df = pd.DataFrame()
        self._worksheet_id_df = pd.DataFrame()

        self._logger = logger
        self._worksheet_col = -1

        # Set initial row and column count to 0
        self.setRowCount(0)
        self.setColumnCount(0)

    def set_work_data(self, worksheets_df: pd.DataFrame) -> None:
        """Set the worksheet data and update the model."""
        try:
            self._logger.info("Setting work data...")

            if worksheets_df is None or worksheets_df.empty:
                self._logger.warning("Received empty or None DataFrame")
                self.clear()
                return

            self._worksheets_df = worksheets_df.copy()
            # Get unique WorksheetIDs
            if "WorksheetID" in self._worksheets_df.columns:
                self._worksheet_id_df = pd.DataFrame({
                    'WorksheetID': self._worksheets_df['WorksheetID'].unique()
                })
            else:
                self._worksheet_id_df = pd.DataFrame(columns=['WorksheetID'])

            self.beginResetModel()

            # Set model dimensions
            rows = len(self._worksheet_id_df)
            cols = len(self._worksheet_id_df.columns)
            self.setRowCount(rows)
            self.setColumnCount(cols)

            # Set headers
            if not self._worksheet_id_df.columns.empty:
                self.setHorizontalHeaderLabels([str(col) for col in self._worksheet_id_df.columns])

            self._logger.info(f"Work data set: {rows} rows, {cols} columns")
            self._logger.debug(f"Columns: {self._worksheet_df.columns.tolist()}")

            self.endResetModel()

            # Emit data changed signal for the entire model
            top_left = self.index(0, 0)
            bottom_right = self.index(rows - 1, cols - 1)
            self.dataChanged.emit(top_left, bottom_right)

            self._logger.info("Model update complete")

        except Exception as e:
            self._logger.error(f"Error setting work data: {str(e)}", exc_info=True)
            raise

    def rowCount(self, parent: QModelIndex = None) -> int:
        """Return the number of rows in the model."""
        if parent is not None and parent.isValid():
            return 0
        return len(self._worksheet_id_df ) if self._worksheet_id_df  is not None else 0

    def columnCount(self, parent: QModelIndex = None) -> int:
        """Return the number of columns in the model."""
        if parent is not None and parent.isValid():
            return 0
        return len(self._worksheet_id_df .columns) if self._worksheet_id_df is not None else 0

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """Return data for the given role and index."""
        if not index.isValid() or not (0 <= index.row() < self.rowCount() and 0 <= index.column() < self.columnCount()):
            return None

        if role in (Qt.DisplayRole, Qt.EditRole):
            try:
                value = self._worksheet_id_df.iat[index.row(), index.column()]

                # Handle different types of values safely
                if pd.isna(value) or value is None:
                    return ""
                try:
                    return str(value)
                except Exception:
                    try:
                        return value  # Return the raw value if str() fails
                    except:
                        return ""

            except (IndexError, KeyError) as e:
                self._logger.warning(f"Error getting data at {index.row()}, {index.column()}: {e}")
                return ""

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        """Return header data for the given role, section and orientation."""
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal and 0 <= section < self.columnCount():
            return str(self._worksheet_df.columns[section])
        elif orientation == Qt.Vertical and 0 <= section < self.rowCount():
            return str(section + 1)  # 1-based row numbers

        return None

    def clear(self) -> None:
        """Clear the model data."""
        self.beginResetModel()
        self._worksheet_df = pd.DataFrame()
        self._worksheet_id_df = pd.DataFrame()
        self._worksheet_col = -1
        self.setRowCount(0)
        self.setColumnCount(0)
        self.endResetModel()