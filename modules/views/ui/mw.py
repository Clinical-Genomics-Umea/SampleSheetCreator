# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mw.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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
    QStackedWidget, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(1319, 849)
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
        self.drawer_stackedWidget = QStackedWidget(self.centralwidget)
        self.drawer_stackedWidget.setObjectName(u"drawer_stackedWidget")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.drawer_stackedWidget.sizePolicy().hasHeightForWidth())
        self.drawer_stackedWidget.setSizePolicy(sizePolicy2)
        self.drawer_stackedWidget.setMaximumSize(QSize(300, 16777215))
        self.drawer_config = QWidget()
        self.drawer_config.setObjectName(u"drawer_config")
        self.verticalLayout_4 = QVBoxLayout(self.drawer_config)
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.drawer_stackedWidget.addWidget(self.drawer_config)
        self.drawer_file = QWidget()
        self.drawer_file.setObjectName(u"drawer_file")
        self.verticalLayout_8 = QVBoxLayout(self.drawer_file)
        self.verticalLayout_8.setSpacing(6)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.drawer_stackedWidget.addWidget(self.drawer_file)
        self.drawer_indexes = QWidget()
        self.drawer_indexes.setObjectName(u"drawer_indexes")
        self.verticalLayout_5 = QVBoxLayout(self.drawer_indexes)
        self.verticalLayout_5.setSpacing(6)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.drawer_stackedWidget.addWidget(self.drawer_indexes)
        self.drawer_apps = QWidget()
        self.drawer_apps.setObjectName(u"drawer_apps")
        self.verticalLayout_6 = QVBoxLayout(self.drawer_apps)
        self.verticalLayout_6.setSpacing(6)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.drawer_stackedWidget.addWidget(self.drawer_apps)
        self.drawer_lane = QWidget()
        self.drawer_lane.setObjectName(u"drawer_lane")
        self.verticalLayout_7 = QVBoxLayout(self.drawer_lane)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.drawer_stackedWidget.addWidget(self.drawer_lane)
        self.drawer_runsetup = QWidget()
        self.drawer_runsetup.setObjectName(u"drawer_runsetup")
        self.verticalLayout_2 = QVBoxLayout(self.drawer_runsetup)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.drawer_stackedWidget.addWidget(self.drawer_runsetup)
        self.drawer_override = QWidget()
        self.drawer_override.setObjectName(u"drawer_override")
        self.verticalLayout_3 = QVBoxLayout(self.drawer_override)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.drawer_stackedWidget.addWidget(self.drawer_override)

        self.horizontalLayout_2.addWidget(self.drawer_stackedWidget)

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
        self.main_log = QWidget()
        self.main_log.setObjectName(u"main_log")
        self.verticalLayout_12 = QVBoxLayout(self.main_log)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.main_stackedWidget.addWidget(self.main_log)
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

        self.retranslateUi(MainWindow)

        self.drawer_stackedWidget.setCurrentIndex(6)
        self.main_stackedWidget.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
    # retranslateUi

