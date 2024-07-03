# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'widget.ui'
##
## Created by: Qt User Interface Compiler version 6.7.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGroupBox, QHBoxLayout, QLabel,
    QPlainTextEdit, QPushButton, QRadioButton, QSizePolicy,
    QSpacerItem, QStackedWidget, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(892, 591)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.widget = QWidget(Form)
        self.widget.setObjectName(u"widget")
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox = QGroupBox(self.widget)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_5 = QVBoxLayout(self.groupBox)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.csv_radioButton = QRadioButton(self.groupBox)
        self.csv_radioButton.setObjectName(u"csv_radioButton")

        self.verticalLayout_5.addWidget(self.csv_radioButton)

        self.ilmn_radioButton = QRadioButton(self.groupBox)
        self.ilmn_radioButton.setObjectName(u"ilmn_radioButton")

        self.verticalLayout_5.addWidget(self.ilmn_radioButton)


        self.verticalLayout_2.addWidget(self.groupBox)

        self.load_pushButton = QPushButton(self.widget)
        self.load_pushButton.setObjectName(u"load_pushButton")

        self.verticalLayout_2.addWidget(self.load_pushButton)

        self.export_pushButton = QPushButton(self.widget)
        self.export_pushButton.setObjectName(u"export_pushButton")

        self.verticalLayout_2.addWidget(self.export_pushButton)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.help_pushButton = QPushButton(self.widget)
        self.help_pushButton.setObjectName(u"help_pushButton")

        self.verticalLayout_2.addWidget(self.help_pushButton)


        self.horizontalLayout.addWidget(self.widget)

        self.stackedWidget = QStackedWidget(Form)
        self.stackedWidget.setObjectName(u"stackedWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
        self.stackedWidget.setSizePolicy(sizePolicy)
        self.csv_page_widget = QWidget()
        self.csv_page_widget.setObjectName(u"csv_page_widget")
        sizePolicy.setHeightForWidth(self.csv_page_widget.sizePolicy().hasHeightForWidth())
        self.csv_page_widget.setSizePolicy(sizePolicy)
        self.verticalLayout_3 = QVBoxLayout(self.csv_page_widget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.stackedWidget.addWidget(self.csv_page_widget)
        self.help_page_widget = QWidget()
        self.help_page_widget.setObjectName(u"help_page_widget")
        sizePolicy.setHeightForWidth(self.help_page_widget.sizePolicy().hasHeightForWidth())
        self.help_page_widget.setSizePolicy(sizePolicy)
        self.verticalLayout_4 = QVBoxLayout(self.help_page_widget)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_2 = QLabel(self.help_page_widget)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_4.addWidget(self.label_2, 0, Qt.AlignmentFlag.AlignHCenter)

        self.stackedWidget.addWidget(self.help_page_widget)
        self.ilmn_page_widget = QWidget()
        self.ilmn_page_widget.setObjectName(u"ilmn_page_widget")
        sizePolicy.setHeightForWidth(self.ilmn_page_widget.sizePolicy().hasHeightForWidth())
        self.ilmn_page_widget.setSizePolicy(sizePolicy)
        self.verticalLayout_6 = QVBoxLayout(self.ilmn_page_widget)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.plainTextEdit = QPlainTextEdit(self.ilmn_page_widget)
        self.plainTextEdit.setObjectName(u"plainTextEdit")

        self.verticalLayout_6.addWidget(self.plainTextEdit)

        self.stackedWidget.addWidget(self.ilmn_page_widget)

        self.horizontalLayout.addWidget(self.stackedWidget)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(Form)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", u"Data source", None))
        self.csv_radioButton.setText(QCoreApplication.translate("Form", u"csv", None))
        self.ilmn_radioButton.setText(QCoreApplication.translate("Form", u"ilmn index kit", None))
        self.load_pushButton.setText(QCoreApplication.translate("Form", u"Load source", None))
        self.export_pushButton.setText(QCoreApplication.translate("Form", u"Export json", None))
        self.help_pushButton.setText(QCoreApplication.translate("Form", u"Help", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"1. select data source", None))
    # retranslateUi

