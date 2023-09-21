# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'generate.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Generate(object):
    def setupUi(self, Generate):
        Generate.setObjectName("Generate")
        Generate.resize(912, 755)
        self.verticalLayout = QtWidgets.QVBoxLayout(Generate)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter = QtWidgets.QSplitter(Generate)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.groupBox = QtWidgets.QGroupBox(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.treeWidget = QtWidgets.QTreeWidget(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.treeWidget.sizePolicy().hasHeightForWidth())
        self.treeWidget.setSizePolicy(sizePolicy)
        self.treeWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.verticalLayout_2.addWidget(self.treeWidget)
        self.groupBox_2 = QtWidgets.QGroupBox(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(3)
        sizePolicy.setHeightForWidth(self.plainTextEdit.sizePolicy().hasHeightForWidth())
        self.plainTextEdit.setSizePolicy(sizePolicy)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.horizontalLayout_2.addWidget(self.plainTextEdit)
        self.verticalLayout.addWidget(self.splitter)
        self.frame = QtWidgets.QFrame(Generate)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton_ok = QtWidgets.QPushButton(self.frame)
        self.pushButton_ok.setObjectName("pushButton_ok")
        self.horizontalLayout.addWidget(self.pushButton_ok)
        self.pushButton_cancel = QtWidgets.QPushButton(self.frame)
        self.pushButton_cancel.setObjectName("pushButton_cancel")
        self.horizontalLayout.addWidget(self.pushButton_cancel)
        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi(Generate)
        QtCore.QMetaObject.connectSlotsByName(Generate)

    def retranslateUi(self, Generate):
        _translate = QtCore.QCoreApplication.translate
        Generate.setWindowTitle(_translate("Generate", "Dialog"))
        self.groupBox.setTitle(_translate("Generate", "Review data"))
        self.groupBox_2.setTitle(_translate("Generate", "Preview SampleSheet.csv"))
        self.pushButton_ok.setText(_translate("Generate", "Save SampleSheet"))
        self.pushButton_cancel.setText(_translate("Generate", "Cancel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Generate = QtWidgets.QDialog()
    ui = Ui_Generate()
    ui.setupUi(Generate)
    Generate.show()
    sys.exit(app.exec_())

