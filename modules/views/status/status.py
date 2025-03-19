from PySide6.QtCore import Qt, QTimer, QObject, Slot
from PySide6.QtGui import QPainter, QBrush, QColor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QStatusBar,
)


class SelectionInfo(QLabel):
    def __init__(self):
        super().__init__()
        self.set_selection_data()

    def set_selection_data(self, rows: int = 0, cols: int = 0 ):

        rows_str = str(rows)
        cols_str = str(cols)

        msg = f"selected rows: {rows_str:<3} cols: {cols_str: <3}"
        self.setText(msg)


class StatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.selection_label = SelectionInfo()
        self.selection_label.setStyleSheet("color: black")
        self.addPermanentWidget(self.selection_label)


        self.error_timer = QTimer()
        self.error_timer.setSingleShot(True)
        self.error_timer.timeout.connect(self.clear_error_message)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;;font-weight: bold;")
        self.addPermanentWidget(self.error_label)

    @Slot(object)
    def display_selection_data(self, selection_data):
        rows = selection_data.get("rows", 0)
        cols = selection_data.get("cols", 0)
        self.selection_label.set_selection_data(rows, cols)

    @Slot(str)
    def display_error_msg(self, msg):
        self.error_label.setText(f"Error: {msg}")
        self.error_timer.start(5000)

    def clear_error_message(self):
        self.error_label.setText("")

