import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QSizePolicy, QAbstractScrollArea, QTableWidget, QWidget, QVBoxLayout, QLabel, \
    QItemDelegate


def set_heatmap_table_properties(table):

    table.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
    table.setContentsMargins(0, 0, 0, 0)
    table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    h_header_height = table.horizontalHeader().height()
    row_height = table.rowHeight(0)
    no_items = table.columnCount()
    table.setMaximumHeight(h_header_height + row_height * no_items + 5)

    table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)

    table.setItemDelegate(NonEditableDelegate())

    return table


def create_heatmap_table(data: pd.DataFrame) -> QTableWidget:
    table_widget = QTableWidget(data.shape[0], data.shape[1])
    table_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
    table_widget.setHorizontalHeaderLabels(data.columns)
    table_widget.setVerticalHeaderLabels(data.index)

    for row in range(data.shape[0]):
        for col in range(data.shape[1]):
            cell_value = int(data.iat[row, col])

            if row == col:
                continue

            if cell_value < 5:
                red_intensity = int(192 + (255 - 192) * (cell_value / 4))
                color = QColor(red_intensity, 0, 0)
            else:
                green_intensity = int(192 + (255 - 192) * (1 - ((cell_value - 4) / (data.max().max() - 4))))
                color = QColor(0, green_intensity, 0)

            widget = QWidget()
            widget.setAutoFillBackground(True)
            widget.setStyleSheet(f"background-color: {color.name()};")

            layout = QVBoxLayout()
            label = QLabel(str(cell_value))
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
            widget.setLayout(layout)

            table_widget.setCellWidget(row, col, widget)

    return table_widget


class NonEditableDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        # Return None to make the item non-editable
        return None
