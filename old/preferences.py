from PyQt5.QtWidgets import QFileDialog, QDialog, QListWidgetItem
from PyQt5.QtCore import QSettings, QDir, Qt

from ui.preferences_dlg import Ui_Dialog
from PyQt5 import QtGui
from pathlib import Path


class Preferences(QDialog, Ui_Dialog):
    def __init__(self):
        super(Preferences, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Preferences')
        self.setWindowIcon(QtGui.QIcon('icons/cog.png'))

        self.toolButton_indices_file.clicked.connect(self.open_indices_file_dialog)
        self.toolButton_samplesheets_folder.clicked.connect(self.open_samplesheet_folder_dialog)
        self.toolButton_worklist_folder.clicked.connect(self.open_worklist_folder_dialog)
        self.toolButton_config_file.clicked.connect(self.open_config_file_dialog)
        self.toolButton_analysis_file.clicked.connect(self.open_analysis_file_dialog)
        self.pushButton_add_investigator.clicked.connect(self.add_investigator)
        self.pushButton_remove_investigators.clicked.connect(self.remove_investigator)

        self.settings = QSettings('vll', 'SampleSheetCreator')

        institute               = self.settings.value('institute', type=str) or ""
        path_indices_file       = self.settings.value('path_indices_file', type=str) or ""
        path_config_file        = self.settings.value('path_config_file', type=str) or ""
        path_analysis_file      = self.settings.value('path_analysis_file', type=str) or ""
        path_samplesheet_folder = self.settings.value('path_samplesheet_folder', type=str) or ""
        path_worklist_folder = self.settings.value('path_worklist_folder', type=str) or ""
        investigators_list      = self.settings.value('investigators', type=list) or []

        self.lineEdit_institute.setText(institute)
        self.lineEdit_indices_file.setText(path_indices_file)
        self.lineEdit_config_file.setText(path_config_file)
        self.lineEdit_analysis_file.setText(path_analysis_file)
        self.lineEdit_samplesheets_folder.setText(path_samplesheet_folder)
        self.lineEdit_worklist_folder.setText(path_worklist_folder)

        for i in investigators_list:
            item = QListWidgetItem(i)
            self.listWidget_investigators.addItem(item)

        self.buttonBox.accepted.connect(self.accept)

    def accept(self):

        institute           = self.lineEdit_institute.text()
        indices_file        = self.lineEdit_indices_file.text()
        config_file         = self.lineEdit_config_file.text()
        analysis_file       = self.lineEdit_analysis_file.text()
        samplesheets_folder = self.lineEdit_samplesheets_folder.text()
        worklist_folder     = self.lineEdit_worklist_folder.text()

        self.settings.setValue('last_indices_folder',     str(Path(indices_file).parent))
        self.settings.setValue('last_config_folder',      str(Path(config_file).parent))
        self.settings.setValue('last_analysis_folder',    str(Path(analysis_file).parent))
        self.settings.setValue('last_samplesheet_folder', samplesheets_folder)
        self.settings.setValue('last_worklist_folder',    worklist_folder)

        self.settings.setValue('institute',               institute)
        self.settings.setValue('path_indices_file',       indices_file)
        self.settings.setValue('path_config_file',        config_file)
        self.settings.setValue('path_analysis_file',      analysis_file)
        self.settings.setValue('path_samplesheet_folder', samplesheets_folder)
        self.settings.setValue('path_worklist_folder',    worklist_folder)

        investigator_list = []
        for row in range(self.listWidget_investigators.count()):
            investigator_list.append(self.listWidget_investigators.item(row).text())

        self.settings.setValue('investigators', investigator_list)
        self.done(QDialog.Accepted)

    def open_indices_file_dialog(self):
        last = self.settings.value('last_indices_folder', type=str) or ""
        options = QFileDialog.Options()
        path_tmp, _ = QFileDialog.getOpenFileName(self,
                                                  "QFileDialog.getOpenFileName()",
                                                  last, "Indices yaml files (*indices*.yaml);;All filetypes (*)",
                                                  options=options)
        path = str(QDir.toNativeSeparators(path_tmp))
        if len(path) > 0:
            self.lineEdit_indices_file.setText(path)

    def open_config_file_dialog(self):
        options = QFileDialog.Options()
        last = self.settings.value('last_config_folder', type=str) or ""
        path_tmp, _ = QFileDialog.getOpenFileName(self,
                                                  "QFileDialog.getOpenFileName()",
                                                  last, "Config yaml files (*config*.yaml);;All filetypes (*)",
                                                  options=options)
        path = str(QDir.toNativeSeparators(path_tmp))
        if len(path) > 0:
            self.lineEdit_config_file.setText(path)

    def open_analysis_file_dialog(self):
        options = QFileDialog.Options()
        last = self.settings.value('last_analysis_folder', type=str) or ""
        path_tmp, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()",
                                                  last, "Analysis yaml files (*analysis*.yaml);;All filetypes (*)",
                                                  options=options)
        path = str(QDir.toNativeSeparators(path_tmp))
        if len(path) > 0:
            self.lineEdit_analysis_file.setText(path)

    def open_samplesheet_folder_dialog(self):
        last = self.settings.value('last_samplesheet_folder', type=str) or ""
        path_tmp = str(QFileDialog.getExistingDirectory(self, "Select Directory", last, QFileDialog.ShowDirsOnly))
        path = str(QDir.toNativeSeparators(path_tmp))
        if len(path) > 0:
            self.lineEdit_samplesheets_folder.setText(path)

    def open_worklist_folder_dialog(self):
        last = self.settings.value('last_worklist_folder', type=str) or ""
        path_tmp = str(QFileDialog.getExistingDirectory(self, "Select Directory", last, QFileDialog.ShowDirsOnly))
        path = str(QDir.toNativeSeparators(path_tmp))
        if len(path) > 0:
            self.lineEdit_worklist_folder.setText(path)

    def add_investigator(self):
        investigator = self.lineEdit_add_investigator.text()
        existing_items = self.listWidget_investigators.findItems(investigator, Qt.MatchExactly)
        if len(existing_items) == 0:
            item = QListWidgetItem(investigator)
            self.listWidget_investigators.addItem(item)

        self.lineEdit_add_investigator.setText("")

    def remove_investigator(self):
        item = self.listWidget_investigators.currentItem()
        if item:
            r = self.listWidget_investigators.row(item)
            self.listWidget_investigators.takeItem(r)
