from PyQt5.QtWidgets import QDialog, QLabel
from PyQt5 import QtGui, QtCore
import sys
from ui.notify_gui import Ui_Dialog


class Notify(QDialog, Ui_Dialog):
    def __init__(self, messages):
        super(Notify, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Notofication')
        self.setWindowIcon(QtGui.QIcon('icons/rv_icon.png'))
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        for m in messages:
            label = QLabel(m)
            label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            self.vbox.addWidget(label)

        self.vbox.addWidget(QLabel(" "))
        self.vbox.addStretch(1)

        self.pushButton_ok.clicked.connect(self.set_accept)
        self.pushButton_exit.clicked.connect(self.exit_program)

    def set_accept(self):
        self.accept()

    def exit_program(self):
        sys.exit()

