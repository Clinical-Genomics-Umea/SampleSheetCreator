from PySide6.QtWidgets import (
    QTableWidget,
    QSizePolicy,
    QTableWidgetItem,
    QAbstractScrollArea,
)

from views.validation.index_distance_delegate import IndexDistanceColorDelegate


class IndexDistanceWidget(QTableWidget):
    def __init__(self, substitutions):
        super().__init__()

        h_labels = list(substitutions.columns)
        v_labels = list(substitutions.index)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setContentsMargins(0, 0, 0, 0)

        self._setup(substitutions)

        self.setHorizontalHeaderLabels(h_labels)
        self.setVerticalHeaderLabels(v_labels)

        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setItemDelegate(IndexDistanceColorDelegate())

    def _setup(self, substitutions):
        self.setRowCount(substitutions.shape[0])
        self.setColumnCount(substitutions.shape[1])

        for row in range(substitutions.shape[0]):
            for col in range(substitutions.shape[1]):
                cell_value = int(substitutions.iat[row, col])

                if row == col:
                    continue

                self.setItem(row, col, QTableWidgetItem(str(cell_value)))

        h_header_height = self.horizontalHeader().height()
        row_height = self.rowHeight(0)
        no_items = self.columnCount()
        self.setFixedHeight(h_header_height + row_height * no_items + 5)

        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)
