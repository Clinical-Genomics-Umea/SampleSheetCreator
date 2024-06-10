from dataclasses import dataclass

import pandas as pd
from PySide6.QtWidgets import (QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy,
                               QSpacerItem, QLabel, QFormLayout, QFrame, QTextEdit, QFileDialog, QMessageBox)

from modules.widgets.run import RunInfo
from modules.widgets.sample_view import SampleTableView


class SampleSheetEdit(QWidget):
    def __init__(self):
        super().__init__()

        self.setContentsMargins(0, 0, 0, 0)
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save SampleSheet")

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addSpacerItem(spacer)

        self.main_layout.addLayout(self.button_layout)
        self.setLayout(self.main_layout)

        self.textedit = QTextEdit()
        self.textedit.setLineWrapMode(QTextEdit.NoWrap)
        self.main_layout.addWidget(self.textedit)
        self.save_button.clicked.connect(self.export_samplesheet)

    def set_samplesheetdata(self, samplesheet: list[str]):
        self.textedit.clear()
        self.textedit.setText("\n".join(samplesheet))

    def export_samplesheet(self):

        # Open a file dialog to choose the save location and file name
        file_path, _ = QFileDialog.getSaveFileName(self, "Save SampleSheet", "", "CSV Files (*.csv);;All Files (*)")

        if file_path:
            try:
                # Get the text from the QTextEdit widget
                text = self.textedit.toPlainText()

                # Write the text to the file
                with open(file_path, 'w') as file:
                    file.write(text)

                # Inform the user that the file was saved successfully
                QMessageBox.information(self, "Success", "File saved successfully!")
            except Exception as e:
                # Inform the user in case of an error
                QMessageBox.critical(self, "Error", f"An error occurred while saving the file: {e}")


