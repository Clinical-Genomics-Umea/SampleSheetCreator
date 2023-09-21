# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'incomplete_info_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(405, 190)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(310, 150, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 10, 371, 81))
        self.label.setObjectName("label")
        self.label_incomplete_rows = QtWidgets.QLabel(Dialog)
        self.label_incomplete_rows.setGeometry(QtCore.QRect(20, 110, 351, 16))
        self.label_incomplete_rows.setObjectName("label_incomplete_rows")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Error - Incomplete information"))
        self.pushButton.setText(_translate("Dialog", "OK"))
        self.label.setText(_translate("Dialog", "Required fields are:\n"
"\n"
"Batch, Sample_ID, Prep_ID, I7_Indes_ID, Analysis_Def, Panel, Analysis.\n"
"\n"
"Insufficient information is provided in the following rows:"))
        self.label_incomplete_rows.setText(_translate("Dialog", "TextLabel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

