from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from ui.review import Ui_Review
from pathlib import Path
import os


class Review(QDialog, Ui_Review):
    def __init__(self, root_samplesheet_path, folder_name):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('icons/cog.png'))
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        self.lineEdit.setText(str(Path(root_samplesheet_path, folder_name)))
        self.treeView.setUniformRowHeights(True)
        self.pushButton_ok.clicked.connect(self.save)
        self.pushButton_cancel.clicked.connect(self.close_window)
        self.pushButton_ok.setDisabled(True)
        self.pushButton.setDisabled(True)

        self.groupBox.setStyleSheet("QGroupBox"
                                    "{"
                                    "border: 2px solid red;"
                                    "}")

        self.checkBox.clicked.connect(self.toggle_save_button)
        self.pushButton.clicked.connect(self.open_folder)

    def save(self):
        if self.checkBox.isChecked():
            folder = Path(self.lineEdit.text())
            if not folder.is_dir():
                folder.mkdir()
                samplesheet_data = self.plainTextEdit.toPlainText()
                sheetfile = Path(folder, "SampleSheet.csv")
                sheetfile.write_text(samplesheet_data)
                self.pushButton.setDisabled(False)
            else:
                self.msg("Outfolder already exists")

    def msg(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Error")
        msg.setInformativeText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

    def open_folder(self):
        os.startfile(Path(self.lineEdit.text()))

    def close_window(self):
        self.close()

    def toggle_save_button(self):
        if self.checkBox.isChecked():
            self.pushButton_ok.setDisabled(False)
            self.groupBox.setStyleSheet("QGroupBox"
                                        "{"
                                        "border: 2px solid green;"
                                        "}")
        else:
            self.pushButton_ok.setDisabled(True)
            self.groupBox.setStyleSheet("QGroupBox"
                                        "{"
                                        "border: 2px solid red;"
                                        "}")


