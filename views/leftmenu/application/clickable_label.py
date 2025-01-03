import qtawesome as qta
import yaml
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QDialog, QVBoxLayout, QTextEdit


class ClickableLabel(QLabel):
    def __init__(self, text: str, data: dict, parent=None):
        super().__init__(text, parent)
        self.data = data
        self.name = data["ApplicationName"]
        self.setCursor(Qt.PointingHandCursor)  # Change the cursor to a hand pointer

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._show_popup()

    def _show_popup(self):
        # Create a popup dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(self.name)
        dialog.setWindowIcon(qta.icon("msc.symbol-method", options=[{"draw": "image"}]))

        # Add content to the popup dialog
        layout = QVBoxLayout(dialog)
        textedit = QTextEdit(self)
        textedit.setReadOnly(True)
        textedit.setPlainText(yaml.dump(self.data))
        layout.addWidget(textedit)

        dialog.show()
