from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QLabel,
    QVBoxLayout, QFileDialog,
)
from modules.views.ui_components import HorizontalLine


class FileView(QWidget):
    def __init__(self):
        super().__init__()

        profiles_label = QLabel("File")
        profiles_label.setStyleSheet("font-weight: bold")

        self.new_samplesheet_btn = QPushButton("New Samplesheet")
        self.import_worksheet_btn = QPushButton("Import Worksheet")

        layout = QVBoxLayout()

        layout.addWidget(profiles_label)
        layout.addWidget(HorizontalLine())
        layout.addWidget(self.new_samplesheet_btn)
        layout.addWidget(self.import_worksheet_btn)
        layout.addStretch()

        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def import_worksheet(self):
        # TODO: open a dialog to import a worksheet file.
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Import Worksheet",
            "",
            "CSV Files (*.csv);;All Files (*)",
        )

        if file_path:
            self.parent().parent().parent().import_worksheet(file_path)
        # TODO: open a dialog to import a worksheet file.
