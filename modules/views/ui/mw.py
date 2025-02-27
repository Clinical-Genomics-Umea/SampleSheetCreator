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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QMainWindow, QSizePolicy,
    QStackedWidget, QToolBar, QVBoxLayout, QWidget)

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
        self.leftmenu_stackedWidget.addWidget(self.leftmenu_config)
        self.leftmenu_file = QWidget()
        self.leftmenu_file.setObjectName(u"leftmenu_file")
        self.verticalLayout_8 = QVBoxLayout(self.leftmenu_file)
        self.verticalLayout_8.setSpacing(6)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.leftmenu_stackedWidget.addWidget(self.leftmenu_file)
        self.leftmenu_indexes = QWidget()
        self.leftmenu_indexes.setObjectName(u"leftmenu_indexes")
        self.verticalLayout_5 = QVBoxLayout(self.leftmenu_indexes)
        self.verticalLayout_5.setSpacing(6)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.leftmenu_stackedWidget.addWidget(self.leftmenu_indexes)
        self.leftmenu_apps = QWidget()
        self.leftmenu_apps.setObjectName(u"leftmenu_apps")
        self.verticalLayout_6 = QVBoxLayout(self.leftmenu_apps)
        self.verticalLayout_6.setSpacing(6)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.leftmenu_stackedWidget.addWidget(self.leftmenu_apps)
        self.leftmenu_lane = QWidget()
        self.leftmenu_lane.setObjectName(u"leftmenu_lane")
        self.verticalLayout_7 = QVBoxLayout(self.leftmenu_lane)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.leftmenu_stackedWidget.addWidget(self.leftmenu_lane)
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
        self.main_export = QWidget()
        self.main_export.setObjectName(u"main_export")
        self.verticalLayout_13 = QVBoxLayout(self.main_export)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.main_stackedWidget.addWidget(self.main_export)

        self.main_verticalLayout.addWidget(self.main_stackedWidget)


        self.horizontalLayout_2.addLayout(self.main_verticalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.left_toolBar = QToolBar(MainWindow)
        self.left_toolBar.setObjectName(u"left_toolBar")
        MainWindow.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.left_toolBar)

        self.retranslateUi(MainWindow)

        self.leftmenu_stackedWidget.setCurrentIndex(4)
        self.main_stackedWidget.setCurrentIndex(3)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.left_toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

