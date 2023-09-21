#! python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from ui.import_issues import Ui_Dialog


class ImportIssuesDialog(QDialog, Ui_Dialog):
    def __init__(self):
        super(ImportIssuesDialog, self).__init__()
        self.setupUi(self)

        self.buttonBox.button(QDialogButtonBox.Cancel).setText("Reject import")
        self.buttonBox.button(QDialogButtonBox.Ok).setText("Accept import")
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)


