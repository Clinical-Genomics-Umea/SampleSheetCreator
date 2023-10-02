# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mw.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QPushButton,
    QSizePolicy, QSpacerItem, QTabWidget, QToolBar,
    QToolButton, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(1319, 610)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMaximumSize(QSize(16777215, 16777215))
        MainWindow.setDockNestingEnabled(False)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy1)
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.leftmenu_tabWidget = QTabWidget(self.centralwidget)
        self.leftmenu_tabWidget.setObjectName(u"leftmenu_tabWidget")
        sizePolicy2 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.leftmenu_tabWidget.sizePolicy().hasHeightForWidth())
        self.leftmenu_tabWidget.setSizePolicy(sizePolicy2)
        self.leftmenu_tabWidget.setMaximumSize(QSize(300, 16777215))
        self.config_tab = QWidget()
        self.config_tab.setObjectName(u"config_tab")
        self.verticalLayout_4 = QVBoxLayout(self.config_tab)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.frame_6 = QFrame(self.config_tab)
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

        self.leftmenu_tabWidget.addTab(self.config_tab, "")
        self.file_tab = QWidget()
        self.file_tab.setObjectName(u"file_tab")
        self.verticalLayout_8 = QVBoxLayout(self.file_tab)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.new_samplesheet_pushButton = QPushButton(self.file_tab)
        self.new_samplesheet_pushButton.setObjectName(u"new_samplesheet_pushButton")

        self.verticalLayout_7.addWidget(self.new_samplesheet_pushButton)

        self.open_samplesheet_pushButton = QPushButton(self.file_tab)
        self.open_samplesheet_pushButton.setObjectName(u"open_samplesheet_pushButton")

        self.verticalLayout_7.addWidget(self.open_samplesheet_pushButton)

        self.formLayout_6 = QFormLayout()
        self.formLayout_6.setObjectName(u"formLayout_6")
        self.label_8 = QLabel(self.file_tab)
        self.label_8.setObjectName(u"label_8")

        self.formLayout_6.setWidget(0, QFormLayout.LabelRole, self.label_8)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.lineEdit_7 = QLineEdit(self.file_tab)
        self.lineEdit_7.setObjectName(u"lineEdit_7")

        self.horizontalLayout_3.addWidget(self.lineEdit_7)

        self.load_worklist_toolButton = QToolButton(self.file_tab)
        self.load_worklist_toolButton.setObjectName(u"load_worklist_toolButton")

        self.horizontalLayout_3.addWidget(self.load_worklist_toolButton)


        self.formLayout_6.setLayout(0, QFormLayout.FieldRole, self.horizontalLayout_3)


        self.verticalLayout_7.addLayout(self.formLayout_6)


        self.verticalLayout_8.addLayout(self.verticalLayout_7)

        self.leftmenu_tabWidget.addTab(self.file_tab, "")
        self.run_setup_tab = QWidget()
        self.run_setup_tab.setObjectName(u"run_setup_tab")
        self.verticalLayout_5 = QVBoxLayout(self.run_setup_tab)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.leftmenu_tabWidget.addTab(self.run_setup_tab, "")
        self.indexes_tab = QWidget()
        self.indexes_tab.setObjectName(u"indexes_tab")
        self.verticalLayout_6 = QVBoxLayout(self.indexes_tab)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.leftmenu_tabWidget.addTab(self.indexes_tab, "")
        self.profiles_tab = QWidget()
        self.profiles_tab.setObjectName(u"profiles_tab")
        self.verticalLayout_2 = QVBoxLayout(self.profiles_tab)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.leftmenu_tabWidget.addTab(self.profiles_tab, "")

        self.horizontalLayout_2.addWidget(self.leftmenu_tabWidget)

        self.verticalLayout_12 = QVBoxLayout()
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.main_tabWidget = QTabWidget(self.centralwidget)
        self.main_tabWidget.setObjectName(u"main_tabWidget")
        sizePolicy2.setHeightForWidth(self.main_tabWidget.sizePolicy().hasHeightForWidth())
        self.main_tabWidget.setSizePolicy(sizePolicy2)
        self.data_tab = QWidget()
        self.data_tab.setObjectName(u"data_tab")
        self.verticalLayout = QVBoxLayout(self.data_tab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.main_tabWidget.addTab(self.data_tab, "")
        self.validation_tab = QWidget()
        self.validation_tab.setObjectName(u"validation_tab")
        self.verticalLayout_10 = QVBoxLayout(self.validation_tab)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.main_tabWidget.addTab(self.validation_tab, "")

        self.verticalLayout_12.addWidget(self.main_tabWidget)


        self.horizontalLayout_2.addLayout(self.verticalLayout_12)

        self.rightmenu_tabWidget = QTabWidget(self.centralwidget)
        self.rightmenu_tabWidget.setObjectName(u"rightmenu_tabWidget")
        sizePolicy2.setHeightForWidth(self.rightmenu_tabWidget.sizePolicy().hasHeightForWidth())
        self.rightmenu_tabWidget.setSizePolicy(sizePolicy2)
        self.columns_settings_tab = QWidget()
        self.columns_settings_tab.setObjectName(u"columns_settings_tab")
        self.verticalLayout_9 = QVBoxLayout(self.columns_settings_tab)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.rightmenu_tabWidget.addTab(self.columns_settings_tab, "")

        self.horizontalLayout_2.addWidget(self.rightmenu_tabWidget)

        self.right_sidebar_widget = QWidget(self.centralwidget)
        self.right_sidebar_widget.setObjectName(u"right_sidebar_widget")
        sizePolicy3 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.right_sidebar_widget.sizePolicy().hasHeightForWidth())
        self.right_sidebar_widget.setSizePolicy(sizePolicy3)
        self.right_sidebar_widget.setMinimumSize(QSize(32, 0))
        self.right_sidebar_widget.setMaximumSize(QSize(32, 16777215))
        self.verticalLayout_3 = QVBoxLayout(self.right_sidebar_widget)
        self.verticalLayout_3.setSpacing(4)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalSpacer = QSpacerItem(3, 404, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)


        self.horizontalLayout_2.addWidget(self.right_sidebar_widget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.left_toolBar = QToolBar(MainWindow)
        self.left_toolBar.setObjectName(u"left_toolBar")
        self.left_toolBar.setMinimumSize(QSize(70, 0))
        MainWindow.addToolBar(Qt.LeftToolBarArea, self.left_toolBar)

        self.retranslateUi(MainWindow)

        self.leftmenu_tabWidget.setCurrentIndex(2)
        self.main_tabWidget.setCurrentIndex(1)
        self.rightmenu_tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Config file", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Index file", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Analysis file", None))
        self.leftmenu_tabWidget.setTabText(self.leftmenu_tabWidget.indexOf(self.config_tab), QCoreApplication.translate("MainWindow", u"config_tab_h", None))
        self.new_samplesheet_pushButton.setText(QCoreApplication.translate("MainWindow", u"New Samplesheet", None))
        self.open_samplesheet_pushButton.setText(QCoreApplication.translate("MainWindow", u"Open Samplesheet", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Load Worklist", None))
        self.load_worklist_toolButton.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.leftmenu_tabWidget.setTabText(self.leftmenu_tabWidget.indexOf(self.file_tab), QCoreApplication.translate("MainWindow", u"file_tab_h", None))
        self.leftmenu_tabWidget.setTabText(self.leftmenu_tabWidget.indexOf(self.run_setup_tab), QCoreApplication.translate("MainWindow", u"run_setup_tab_h", None))
        self.leftmenu_tabWidget.setTabText(self.leftmenu_tabWidget.indexOf(self.indexes_tab), QCoreApplication.translate("MainWindow", u"indexes_tab_h", None))
        self.leftmenu_tabWidget.setTabText(self.leftmenu_tabWidget.indexOf(self.profiles_tab), QCoreApplication.translate("MainWindow", u"profiles_tab_h", None))
        self.main_tabWidget.setTabText(self.main_tabWidget.indexOf(self.data_tab), QCoreApplication.translate("MainWindow", u"samplesheet data", None))
        self.main_tabWidget.setTabText(self.main_tabWidget.indexOf(self.validation_tab), QCoreApplication.translate("MainWindow", u"validation", None))
        self.rightmenu_tabWidget.setTabText(self.rightmenu_tabWidget.indexOf(self.columns_settings_tab), QCoreApplication.translate("MainWindow", u"columns_settings_tab_h", None))
        self.left_toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

