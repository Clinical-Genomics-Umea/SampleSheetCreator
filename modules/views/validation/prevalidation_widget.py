from PySide6.QtCore import Slot
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import QTableWidget, QVBoxLayout, QSizePolicy, QTableWidgetItem


class PreValidationWidget(QTableWidget):
    def __init__(self):
        super().__init__()

        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["Validator", "Status", "Message"])
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)

        self.setColumnWidth(0, 200)
        self.setColumnWidth(1, 200)
        self.horizontalHeader().setStretchLastSection(True)

    def _add_row(self, validator_text, is_valid, message):
        self.insertRow(self.rowCount())
        last_row = self.rowCount() - 1

        validator_item = QTableWidgetItem(validator_text)
        status_item = QTableWidgetItem("OK" if is_valid else "FAIL")
        status_item.setForeground(
            QBrush(QColor(0, 200, 0)) if is_valid else QBrush(QColor(200, 0, 0))
        )

        message_item = QTableWidgetItem(message)

        self.setItem(last_row, 0, validator_item)
        self.setItem(last_row, 1, status_item)
        self.setItem(last_row, 2, message_item)

    def clear(self):
        self.setRowCount(0)

    @Slot(dict)
    def populate(self, validation_results):

        self.setRowCount(0)

        for validation_name, is_valid, message in validation_results:
            self._add_row(validation_name, is_valid, message)
