import json
from typing import Any, List, Set, Optional, Dict, Union

import pandas as pd
from PySide6.QtCore import QAbstractTableModel, Qt, QMimeData, QModelIndex, QObject
from PySide6.QtCore import QPersistentModelIndex


class IndexTableModel(QAbstractTableModel):
    """A table model for displaying and interacting with index kit data.
    
    This model provides a Qt-compatible interface for displaying pandas DataFrames
    in Qt views, with support for drag and drop operations.
    
    Args:
        dataframe: The pandas DataFrame containing the index kit data.
        parent: Optional parent QObject.
    """
    
    def __init__(self, dataframe: pd.DataFrame, parent: Optional[QObject] = None):
        super().__init__(parent)
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("dataframe must be a pandas DataFrame")
        self._dataframe = dataframe.copy()
    
    @property
    def dataframe(self) -> pd.DataFrame:
        """Get the underlying DataFrame."""
        return self._dataframe
    
    @dataframe.setter
    def dataframe(self, value: pd.DataFrame) -> None:
        """Set a new DataFrame and update the model."""
        if not isinstance(value, pd.DataFrame):
            raise TypeError("dataframe must be a pandas DataFrame")
        self.beginResetModel()
        self._dataframe = value.copy()
        self.endResetModel()

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """Retrieve data from the model for the given index and role.
        
        Args:
            index: The index of the data to retrieve.
            role: The role of the data to retrieve.
                
        Returns:
            The data for the given role at the given index, or None if no data available.
        """
        if not index.isValid() or not (0 <= index.row() < self.rowCount() and 
                                     0 <= index.column() < self.columnCount()):
            return None
            
        if role == Qt.DisplayRole or role == Qt.EditRole:
            try:
                value = self._dataframe.iat[index.row(), index.column()]
                return str(value) if pd.notna(value) else ""
            except (IndexError, KeyError):
                return None
                
        return None

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return the number of rows in the model.
        
        Args:
            parent: The parent index (unused for table models).
            
        Returns:
            The number of rows in the DataFrame.
        """
        return 0 if self._dataframe.empty else len(self._dataframe)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return the number of columns in the model.
        
        Args:
            parent: The parent index (unused for table models).
            
        Returns:
            The number of columns in the DataFrame.
        """
        return len(self._dataframe.columns) if not self._dataframe.empty else 0

    def headerData(self, section: int, orientation: Qt.Orientation, 
                  role: int = Qt.DisplayRole) -> Optional[str]:
        """Get the header data for the given section, orientation, and role.
        
        Args:
            section: The index of the column/row.
            orientation: The orientation of the header (Qt.Horizontal or Qt.Vertical).
            role: The role of the header data.
            
        Returns:
            The header data for the given section, or None if not applicable.
        """
        if role != Qt.DisplayRole or self._dataframe.empty:
            return None
            
        if orientation == Qt.Horizontal and 0 <= section < len(self._dataframe.columns):
            return str(self._dataframe.columns[section])
            
        if orientation == Qt.Vertical and 0 <= section < len(self._dataframe):
            return str(self._dataframe.index[section] + 1)
            
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Get the item flags for the given index.
        
        Args:
            index: The index to get flags for.
            
        Returns:
            The flags for the item at the given index.
        """
        if not index.isValid():
            return Qt.NoItemFlags
            
        flags = super().flags(index)
        return flags | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def indexes_to_rows(self, indexes: List[QModelIndex]) -> List[int]:
        """Convert a list of model indexes to a sorted list of unique row numbers.
        
        Args:
            indexes: List of QModelIndex objects.
            
        Returns:
            Sorted list of unique row numbers.
        """
        if not indexes:
            return []
            
        row_indexes: Set[int] = {index.row() for index in indexes if index.isValid()}
        return sorted(row_indexes)

    def mimeData(self, indexes: List[QModelIndex]) -> Optional[QMimeData]:
        """Generate a QMimeData object containing the selected data in JSON format.
        
        Args:
            indexes: List of QModelIndex objects representing the selected items.
            
        Returns:
            A QMimeData object containing the selected data as JSON, or None if no valid indexes.
        """
        if not indexes:
            return None
            
        try:
            rows = self.indexes_to_rows(indexes)
            if not rows:
                return None
                
            # Create a DataFrame with only the selected rows
            df = self._dataframe.iloc[rows].copy()
            
            # Convert to list of dicts and handle non-serializable types
            records = []
            for _, row in df.iterrows():
                record = {}
                for col in df.columns:
                    val = row[col]
                    # Convert non-serializable types to strings
                    if pd.isna(val):
                        record[col] = None
                    elif isinstance(val, (pd.Timestamp, pd.Timedelta)):
                        record[col] = str(val)
                    else:
                        record[col] = val
                records.append(record)
            
            # Convert to JSON
            json_data = json.dumps(records, default=str)
            
            # Create and return MIME data
            mime_data = QMimeData()
            mime_data.setData("application/json", json_data.encode('utf-8'))
            return mime_data
            
        except Exception as e:
            return None
