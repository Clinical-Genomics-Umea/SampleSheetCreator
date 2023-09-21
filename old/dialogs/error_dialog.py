#! python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog
from ui.validation_error import Ui_Dialog


class ValErrDialog(QDialog, Ui_Dialog):
    def __init__(self):
        super(ValErrDialog, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.on_click)

    def on_click(self):
        self.close()
