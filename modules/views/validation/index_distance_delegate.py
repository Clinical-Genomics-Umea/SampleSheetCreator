from PySide6.QtGui import QColor
from PySide6.QtWidgets import QStyledItemDelegate


class IndexDistanceColorDelegate(QStyledItemDelegate):

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)

        # Get the cell value and check if it's numeric
        try:
            value = int(index.data())
        except (TypeError, ValueError):
            value = None

        # Set background color based on the value
        if value is not None:
            if value < 5:
                color = QColor(139, 0, 1)
            else:
                color = QColor(0, 100, 1)

            option.backgroundBrush = color
