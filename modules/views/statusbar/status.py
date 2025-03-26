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

        self.color_map = {
            "DEBUG": "#808080",  # Gray
            "INFO": "#008000",  # Black
            "WARNING": "#CC0000",  # Red
            "ERROR": "#8B0000",  # Dark Red
            "CRITICAL": "#8B0000"  # Dark Red
        }

        self.spacer = QWidget()
        self.spacer.setFixedWidth(15)


        self.label = QLabel()
        self.label.setTextFormat(Qt.TextFormat.RichText)  # Enable HTML formatting
        self.addWidget(self.spacer)
        self.addWidget(self.label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.clear_message)

    def display_message(self, level: str, message: str, timeout: int = 5000):
        """Show a colored message for a given time (in milliseconds)."""
        color = self.color_map.get(level, "#000000")  # Default to black
        self.label.setText(f'<span style="color:{color};">{message}</span>')

        # Restart the timer with the new timeout
        self.timer.stop()
        self.timer.start(timeout)

    def clear_message(self):
        """Clears the message when the timer expires."""
        self.label.clear()

    @Slot(object)
    def display_selection_data(self, selection_data):
        rows = selection_data.get("rows", 0)
        cols = selection_data.get("cols", 0)
        self.selection_label.set_selection_data(rows, cols)
