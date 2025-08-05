from PySide6.QtCore import QSortFilterProxyModel, Qt


class AllColumnFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, filter_columns=None):
        """
        Initialize the proxy model with optional filter columns.
        
        Args:
            filter_columns (list, optional): List of column names to filter on. 
                                          If None, all columns will be filtered.
        """
        super().__init__()
        self.filter_text = ""
        self.filter_columns = filter_columns or []

    def set_filter_text(self, text):
        """Set the filter text and trigger a filter update."""
        self.filter_text = text.strip().lower()
        self.invalidateFilter()

    def set_filter_columns(self, columns):
        """
        Set which columns should be included in the filter.
        
        Args:
            columns (list): List of column names to filter on.
        """
        self.filter_columns = columns
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        """
        Determine if the row should be included based on the filter.
        Only checks columns that are in filter_columns (if any specified).
        """
        if not self.filter_text:
            return True
            
        model = self.sourceModel()
        
        for column in range(model.columnCount()):
            # Skip columns not in filter_columns if filter_columns is specified
            if self.filter_columns:
                header = model.headerData(column, Qt.Horizontal, Qt.DisplayRole)
                if header not in self.filter_columns:
                    continue
                    
            index = model.index(source_row, column, source_parent)
            data = model.data(index, Qt.DisplayRole)
            if self.filter_text in str(data).lower():
                return True
                
        return False
