# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'run_settings_form_grid.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QFrame, QGroupBox,
    QHBoxLayout, QLabel, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1165, 76)
        self.horizontalLayout = QHBoxLayout(Form)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupBox = QGroupBox(Form)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QSize(451, 0))
        self.groupBox.setMaximumSize(QSize(451, 16777215))
        self.groupBox.setLayoutDirection(Qt.LeftToRight)
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(9, 9, 9, 9)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")
        font = QFont()
        font.setPointSize(8)
        self.label_2.setFont(font)

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_2)

        self.FileFormatVersion = QLabel(self.groupBox)
        self.FileFormatVersion.setObjectName(u"FileFormatVersion")
        self.FileFormatVersion.setFont(font)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.FileFormatVersion)

        self.label_10 = QLabel(self.groupBox)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setFont(font)

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_10)

        self.RunName = QLabel(self.groupBox)
        self.RunName.setObjectName(u"RunName")
        self.RunName.setFont(font)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.RunName)


        self.horizontalLayout_2.addLayout(self.formLayout)

        self.line = QFrame(self.groupBox)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout_2.addWidget(self.line)

        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_12 = QLabel(self.groupBox)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setFont(font)

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_12)

        self.RunDescription = QLabel(self.groupBox)
        self.RunDescription.setObjectName(u"RunDescription")
        self.RunDescription.setFont(font)

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.RunDescription)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font)

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_3)

        self.Instrument = QLabel(self.groupBox)
        self.Instrument.setObjectName(u"Instrument")
        self.Instrument.setFont(font)

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.Instrument)


        self.horizontalLayout_2.addLayout(self.formLayout_2)


        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.horizontalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(Form)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy1)
        self.groupBox_2.setMinimumSize(QSize(225, 0))
        self.groupBox_2.setMaximumSize(QSize(225, 16777215))
        self.groupBox_2.setLayoutDirection(Qt.LeftToRight)
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(9, 9, 9, 9)
        self.formLayout_3 = QFormLayout()
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.label_13 = QLabel(self.groupBox_2)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setFont(font)

        self.formLayout_3.setWidget(0, QFormLayout.LabelRole, self.label_13)

        self.ReadProfile = QLabel(self.groupBox_2)
        self.ReadProfile.setObjectName(u"ReadProfile")
        self.ReadProfile.setFont(font)

        self.formLayout_3.setWidget(0, QFormLayout.FieldRole, self.ReadProfile)


        self.verticalLayout_2.addLayout(self.formLayout_3)


        self.horizontalLayout.addWidget(self.groupBox_2)

        self.groupBox_4 = QGroupBox(Form)
        self.groupBox_4.setObjectName(u"groupBox_4")
        sizePolicy1.setHeightForWidth(self.groupBox_4.sizePolicy().hasHeightForWidth())
        self.groupBox_4.setSizePolicy(sizePolicy1)
        self.groupBox_4.setMinimumSize(QSize(225, 0))
        self.groupBox_4.setMaximumSize(QSize(225, 16777215))
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_4)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.formLayout_5 = QFormLayout()
        self.formLayout_5.setObjectName(u"formLayout_5")
        self.label = QLabel(self.groupBox_4)
        self.label.setObjectName(u"label")
        self.label.setFont(font)

        self.formLayout_5.setWidget(0, QFormLayout.LabelRole, self.label)

        self.Investigator = QLabel(self.groupBox_4)
        self.Investigator.setObjectName(u"Investigator")
        self.Investigator.setFont(font)

        self.formLayout_5.setWidget(0, QFormLayout.FieldRole, self.Investigator)

        self.label_7 = QLabel(self.groupBox_4)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setFont(font)

        self.formLayout_5.setWidget(1, QFormLayout.LabelRole, self.label_7)

        self.FlowCellType = QLabel(self.groupBox_4)
        self.FlowCellType.setObjectName(u"FlowCellType")
        self.FlowCellType.setFont(font)

        self.formLayout_5.setWidget(1, QFormLayout.FieldRole, self.FlowCellType)


        self.verticalLayout_4.addLayout(self.formLayout_5)


        self.horizontalLayout.addWidget(self.groupBox_4)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.columns_widget = QWidget(Form)
        self.columns_widget.setObjectName(u"columns_widget")
        self.columns_widget.setMinimumSize(QSize(250, 0))
        self.columns_widget.setMaximumSize(QSize(250, 16777215))

        self.horizontalLayout.addWidget(self.columns_widget)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", u"[Header]", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"File Format v:", None))
        self.FileFormatVersion.setText(QCoreApplication.translate("Form", u"Unknown", None))
        self.label_10.setText(QCoreApplication.translate("Form", u"Run Name:", None))
        self.RunName.setText(QCoreApplication.translate("Form", u"Unknown", None))
        self.label_12.setText(QCoreApplication.translate("Form", u"Run Descr:", None))
        self.RunDescription.setText(QCoreApplication.translate("Form", u"Unknown", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"Instrument:", None))
        self.Instrument.setText(QCoreApplication.translate("Form", u"Unknown", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Form", u"[Reads]", None))
        self.label_13.setText(QCoreApplication.translate("Form", u"Read Profile:", None))
        self.ReadProfile.setText(QCoreApplication.translate("Form", u"Unknown", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("Form", u"[Run Extra]", None))
        self.label.setText(QCoreApplication.translate("Form", u"Investigator:", None))
        self.Investigator.setText(QCoreApplication.translate("Form", u"Unknown", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"FlowCellType:", None))
        self.FlowCellType.setText(QCoreApplication.translate("Form", u"Unknown", None))
    # retranslateUi

