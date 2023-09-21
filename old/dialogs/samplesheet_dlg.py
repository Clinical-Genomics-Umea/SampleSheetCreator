from PyQt5.QtWidgets import QDialog
from PyQt5 import QtGui
from ui.samplesheet_dlg import Ui_Dialog


class SampleSheetDialog(QDialog, Ui_Dialog):
    def __init__(self):
        super(SampleSheetDialog, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('SampleSheet Import')
        self.setWindowIcon(QtGui.QIcon('icons/rv_icon.png'))