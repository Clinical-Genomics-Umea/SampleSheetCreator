# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'run_settings_form.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QHBoxLayout, QLabel,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(400, 106)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setVerticalSpacing(1)
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label)

        self.file_format_label = QLabel(Form)
        self.file_format_label.setObjectName(u"file_format_label")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.file_format_label)

        self.label_4 = QLabel(Form)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_4)

        self.run_name_label = QLabel(Form)
        self.run_name_label.setObjectName(u"run_name_label")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.run_name_label)

        self.label_6 = QLabel(Form)
        self.label_6.setObjectName(u"label_6")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_6)

        self.run_desc_label = QLabel(Form)
        self.run_desc_label.setObjectName(u"run_desc_label")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.run_desc_label)

        self.label_9 = QLabel(Form)
        self.label_9.setObjectName(u"label_9")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_9)

        self.instrument_label = QLabel(Form)
        self.instrument_label.setObjectName(u"instrument_label")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.instrument_label)

        self.label_11 = QLabel(Form)
        self.label_11.setObjectName(u"label_11")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_11)

        self.label_12 = QLabel(Form)
        self.label_12.setObjectName(u"label_12")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.label_12)


        self.horizontalLayout.addLayout(self.formLayout)

        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setVerticalSpacing(1)
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_2)

        self.label_8 = QLabel(Form)
        self.label_8.setObjectName(u"label_8")

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.label_8)

        self.label_13 = QLabel(Form)
        self.label_13.setObjectName(u"label_13")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_13)

        self.read_profile_label = QLabel(Form)
        self.read_profile_label.setObjectName(u"read_profile_label")

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.read_profile_label)

        self.label_15 = QLabel(Form)
        self.label_15.setObjectName(u"label_15")

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.label_15)

        self.label_16 = QLabel(Form)
        self.label_16.setObjectName(u"label_16")

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.label_16)

        self.label_17 = QLabel(Form)
        self.label_17.setObjectName(u"label_17")

        self.formLayout_2.setWidget(3, QFormLayout.LabelRole, self.label_17)

        self.input_container_label = QLabel(Form)
        self.input_container_label.setObjectName(u"input_container_label")

        self.formLayout_2.setWidget(3, QFormLayout.FieldRole, self.input_container_label)

        self.label_19 = QLabel(Form)
        self.label_19.setObjectName(u"label_19")

        self.formLayout_2.setWidget(4, QFormLayout.LabelRole, self.label_19)

        self.lib_prep_kit_label = QLabel(Form)
        self.lib_prep_kit_label.setObjectName(u"lib_prep_kit_label")

        self.formLayout_2.setWidget(4, QFormLayout.FieldRole, self.lib_prep_kit_label)


        self.horizontalLayout.addLayout(self.formLayout_2)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label.setText(QCoreApplication.translate("Form", u"File Format Version", None))
        self.file_format_label.setText(QCoreApplication.translate("Form", u"ffv", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"Run Name", None))
        self.run_name_label.setText(QCoreApplication.translate("Form", u"rn", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"Run Desc", None))
        self.run_desc_label.setText(QCoreApplication.translate("Form", u"rd", None))
        self.label_9.setText(QCoreApplication.translate("Form", u"Instrument", None))
        self.instrument_label.setText(QCoreApplication.translate("Form", u"instrument", None))
        self.label_11.setText(QCoreApplication.translate("Form", u"[Header]", None))
        self.label_12.setText("")
        self.label_2.setText(QCoreApplication.translate("Form", u"[Reads]", None))
        self.label_8.setText("")
        self.label_13.setText(QCoreApplication.translate("Form", u"Read Profile", None))
        self.read_profile_label.setText(QCoreApplication.translate("Form", u"rp", None))
        self.label_15.setText(QCoreApplication.translate("Form", u"[Sequencing Settings]", None))
        self.label_16.setText("")
        self.label_17.setText(QCoreApplication.translate("Form", u"Input Container", None))
        self.input_container_label.setText(QCoreApplication.translate("Form", u"ici", None))
        self.label_19.setText(QCoreApplication.translate("Form", u"Library Prep Kits", None))
        self.lib_prep_kit_label.setText(QCoreApplication.translate("Form", u"lpk", None))
    # retranslateUi

