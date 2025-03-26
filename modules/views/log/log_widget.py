from PySide6.QtWidgets import QListWidget


class LogWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def append_log(self, text):
        self.addItem(text)