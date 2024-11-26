# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mw.ui'
##
## Created by: Qt User Interface Compiler version 6.7.1
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QPushButton,
    QSizePolicy, QStackedWidget, QToolBar, QToolButton,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(1319, 610)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMaximumSize(QSize(16777215, 16777215))
        MainWindow.setDockNestingEnabled(False)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy1)
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.leftmenu_stackedWidget = QStackedWidget(self.centralwidget)
        self.leftmenu_stackedWidget.setObjectName(u"leftmenu_stackedWidget")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.leftmenu_stackedWidget.sizePolicy().hasHeightForWidth())
        self.leftmenu_stackedWidget.setSizePolicy(sizePolicy2)
        self.leftmenu_stackedWidget.setMaximumSize(QSize(300, 16777215))
        self.leftmenu_config = QWidget()
        self.leftmenu_config.setObjectName(u"leftmenu_config")
        self.verticalLayout_4 = QVBoxLayout(self.leftmenu_config)
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.frame_6 = QFrame(self.leftmenu_config)
        self.frame_6.setObjectName(u"frame_6")
        self.formLayout_3 = QFormLayout(self.frame_6)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.formLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_6 = QLabel(self.frame_6)
        self.label_6.setObjectName(u"label_6")

        self.formLayout_3.setWidget(0, QFormLayout.LabelRole, self.label_6)

        self.lineEdit_config_file = QLineEdit(self.frame_6)
        self.lineEdit_config_file.setObjectName(u"lineEdit_config_file")
        self.lineEdit_config_file.setReadOnly(True)

        self.formLayout_3.setWidget(0, QFormLayout.FieldRole, self.lineEdit_config_file)

        self.label_4 = QLabel(self.frame_6)
        self.label_4.setObjectName(u"label_4")

        self.formLayout_3.setWidget(1, QFormLayout.LabelRole, self.label_4)

        self.lineEdit_index_file = QLineEdit(self.frame_6)
        self.lineEdit_index_file.setObjectName(u"lineEdit_index_file")
        self.lineEdit_index_file.setReadOnly(True)

        self.formLayout_3.setWidget(1, QFormLayout.FieldRole, self.lineEdit_index_file)

        self.label_7 = QLabel(self.frame_6)
        self.label_7.setObjectName(u"label_7")

        self.formLayout_3.setWidget(2, QFormLayout.LabelRole, self.label_7)

        self.lineEdit_analysis_file = QLineEdit(self.frame_6)
        self.lineEdit_analysis_file.setObjectName(u"lineEdit_analysis_file")
        self.lineEdit_analysis_file.setReadOnly(True)

        self.formLayout_3.setWidget(2, QFormLayout.FieldRole, self.lineEdit_analysis_file)


        self.verticalLayout_4.addWidget(self.frame_6)

        self.leftmenu_stackedWidget.addWidget(self.leftmenu_config)
        self.leftmenu_file = QWidget()
        self.leftmenu_file.setObjectName(u"leftmenu_file")
        self.verticalLayout_8 = QVBoxLayout(self.leftmenu_file)
        self.verticalLayout_8.setSpacing(6)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.new_samplesheet_pushButton = QPushButton(self.leftmenu_file)
        self.new_samplesheet_pushButton.setObjectName(u"new_samplesheet_pushButton")

        self.verticalLayout_7.addWidget(self.new_samplesheet_pushButton)

        self.formLayout_6 = QFormLayout()
        self.formLayout_6.setObjectName(u"formLayout_6")
        self.label_8 = QLabel(self.leftmenu_file)
        self.label_8.setObjectName(u"label_8")

        self.formLayout_6.setWidget(0, QFormLayout.LabelRole, self.label_8)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.load_worklist_lineEdit = QLineEdit(self.leftmenu_file)
        self.load_worklist_lineEdit.setObjectName(u"load_worklist_lineEdit")

        self.horizontalLayout_3.addWidget(self.load_worklist_lineEdit)

        self.load_worklist_toolButton = QToolButton(self.leftmenu_file)
        self.load_worklist_toolButton.setObjectName(u"load_worklist_toolButton")

        self.horizontalLayout_3.addWidget(self.load_worklist_toolButton)


        self.formLayout_6.setLayout(0, QFormLayout.FieldRole, self.horizontalLayout_3)


        self.verticalLayout_7.addLayout(self.formLayout_6)


        self.verticalLayout_8.addLayout(self.verticalLayout_7)

        self.leftmenu_stackedWidget.addWidget(self.leftmenu_file)
        self.leftmenu_indexes = QWidget()
        self.leftmenu_indexes.setObjectName(u"leftmenu_indexes")
        self.verticalLayout_5 = QVBoxLayout(self.leftmenu_indexes)
        self.verticalLayout_5.setSpacing(6)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.leftmenu_stackedWidget.addWidget(self.leftmenu_indexes)
        self.leftmenu_profiles = QWidget()
        self.leftmenu_profiles.setObjectName(u"leftmenu_profiles")
        self.verticalLayout_6 = QVBoxLayout(self.leftmenu_profiles)
        self.verticalLayout_6.setSpacing(6)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.leftmenu_stackedWidget.addWidget(self.leftmenu_profiles)
        self.leftmenu_runsetup = QWidget()
        self.leftmenu_runsetup.setObjectName(u"leftmenu_runsetup")
        self.verticalLayout_2 = QVBoxLayout(self.leftmenu_runsetup)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.leftmenu_stackedWidget.addWidget(self.leftmenu_runsetup)
        self.leftmenu_override = QWidget()
        self.leftmenu_override.setObjectName(u"leftmenu_override")
        self.verticalLayout_3 = QVBoxLayout(self.leftmenu_override)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.leftmenu_stackedWidget.addWidget(self.leftmenu_override)

        self.horizontalLayout_2.addWidget(self.leftmenu_stackedWidget)

        self.main_verticalLayout = QVBoxLayout()
        self.main_verticalLayout.setObjectName(u"main_verticalLayout")
        self.main_stackedWidget = QStackedWidget(self.centralwidget)
        self.main_stackedWidget.setObjectName(u"main_stackedWidget")
        sizePolicy2.setHeightForWidth(self.main_stackedWidget.sizePolicy().hasHeightForWidth())
        self.main_stackedWidget.setSizePolicy(sizePolicy2)
        self.main_data = QWidget()
        self.main_data.setObjectName(u"main_data")
        self.verticalLayout = QVBoxLayout(self.main_data)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.main_stackedWidget.addWidget(self.main_data)
        self.main_validation = QWidget()
        self.main_validation.setObjectName(u"main_validation")
        self.verticalLayout_10 = QVBoxLayout(self.main_validation)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")

        self.verticalLayout_10.addLayout(self.horizontalLayout)

        self.main_stackedWidget.addWidget(self.main_validation)
        self.main_settings = QWidget()
        self.main_settings.setObjectName(u"main_settings")
        self.verticalLayout_11 = QVBoxLayout(self.main_settings)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.main_stackedWidget.addWidget(self.main_settings)
        self.main_make = QWidget()
        self.main_make.setObjectName(u"main_make")
        self.verticalLayout_13 = QVBoxLayout(self.main_make)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.main_stackedWidget.addWidget(self.main_make)

        self.main_verticalLayout.addWidget(self.main_stackedWidget)


        self.horizontalLayout_2.addLayout(self.main_verticalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.left_toolBar = QToolBar(MainWindow)
        self.left_toolBar.setObjectName(u"left_toolBar")
        self.left_toolBar.setMinimumSize(QSize(70, 0))
        MainWindow.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.left_toolBar)

        self.retranslateUi(MainWindow)

        self.leftmenu_stackedWidget.setCurrentIndex(5)
        self.main_stackedWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Config file", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Index file", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Analysis file", None))
        self.new_samplesheet_pushButton.setText(QCoreApplication.translate("MainWindow", u"New Samplesheet", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Load Worklist", None))
        self.load_worklist_toolButton.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.left_toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

