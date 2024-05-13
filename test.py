from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QApplication, QTableView, QHeaderView,  QStyledItemDelegate


class ColoredVerticalHeaderDelegate(QStyledItemDelegate):
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = color

    def paint(self, painter, option, index):
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        else:
            painter.fillRect(option.rect, self.color)


class TableView(QTableView):
    def __init__(self):
        super().__init__()

        self.setHorizontalScrollMode(QTableView.ScrollPerPixel)
        self.setVerticalScrollMode(QTableView.ScrollPerPixel)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setEditTriggers(QTableView.NoEditTriggers)

        # Set initial color for the delegate
        self.setcolor()

    def setcolor(self):
        self.verticalHeader().setStyleSheet("QHeaderView::section { background-color: lightgreen; }")



if __name__ == "__main__":
    app = QApplication([])

    # Create a standard item model
    model = QStandardItemModel(4, 3)
    for row in range(4):
        for column in range(3):
            item = QStandardItem("Row %d, Column %d" % (row, column))
            model.setItem(row, column, item)

    # Create a custom table view
    tableView = TableView()
    tableView.setModel(model)

    tableView.show()

    # Change the color dynamically

    app.exec()