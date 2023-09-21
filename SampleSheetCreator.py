#! python
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
import qtawesome as qta

from modules.data_model.sample_model import SampleSheetModel
from modules.indexes import IndexesMGR
from modules.mapper import ColumnVisibilityMapper
from modules.models import read_fields_from_json
from modules.run_classes import RunSetup, RunInfo
from modules.profiles import ProfileMGR

from PySide6.QtGui import QAction, QActionGroup, QStandardItem
from PySide6.QtCore import QPropertyAnimation, Qt

from PySide6.QtCore import QSize
from PySide6 import QtGui, QtCore
from PySide6.QtWidgets import QMainWindow, QApplication, QSizePolicy, QFileDialog, \
    QWidget, QHeaderView, QToolBox

from modules.sample_view import SampleTableView, CheckableComboBox
from ui.mw import Ui_MainWindow
import qdarktheme

sys.argv += ['-platform', 'windows:darkmode=2']
__author__ = "Pär Larsson"
__version__ = "2.0.0.a"


def get_dialog_options():
    return QFileDialog.Options() | QFileDialog.DontUseNativeDialog


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        # self.main_exe = self.get_main_file()
        self.main_version = __version__
        self.setWindowTitle(f"SampleSheetCreator {self.main_version}")
        self.setWindowIcon(QtGui.QIcon('old/icons/cog.png'))
        self.toolBar.setMovable(False)
        self.toolBar.setIconSize(QSize(40, 40))
        self.menu_tabWidget.setMaximumWidth(0)

        self.file_action = QAction("file", self)
        self.run_action = QAction("run", self)
        self.profiles_action = QAction("profiles", self)
        self.indexes_action = QAction("indexes", self)
        self.generate_action = QAction("generate", self)
        self.config_action = QAction("config", self)
        self.manual_edit_action = QAction("manual_edit", self)

        self.column_visibility_mapper = ColumnVisibilityMapper()

        self.action2tab = {}
        self.setup_tool_actions()
        self.file_tab_setup()

        self.run_info_widget = RunInfo()
        self.run_setup_widget = RunSetup(Path("config/run_settings/run_settings.yaml"))

        self.indexes_toolbox = QToolBox()
        self.indexes_manager = IndexesMGR(Path("config/indexes"))
        self.indexes_widgets = {}

        self.profile_toolbox = QToolBox()
        self.profile_manager = ProfileMGR()


        self.sample_model = SampleSheetModel()
        self.samples_tableview = SampleTableView()

        self.tab_anim = {}
        self.sidemenu_setup()
        self.hide_tabwidget_headers()


        # self.run_setup()
        # self.sample_tableview_setup()
        # self.profile_widgets = {}
        # self.profiles_setup()

    def sample_tableview_setup(self):
        cb = CheckableComboBox()
        self.samples_tableview.setModel(self.sample_model)

        self.run_info_widget.add_widget(cb)
        self.verticalLayout.addWidget(self.samples_tableview)
        self.samples_tableview.setContextMenuPolicy(Qt.CustomContextMenu)
        self.samples_tableview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.column_visibility_mapper.set_map(cb, self.samples_tableview)

    def run_setup(self):
        self.run_setup_tab.layout().addWidget(self.run_setup_widget)
        self.verticalLayout.addWidget(self.run_info_widget)
        self.run_info_widget.setup(self.run_setup_widget.get_data())
        self.run_setup_widget.set_button.clicked.connect(self.on_run_set_button_click)

    def on_run_set_button_click(self):
        self.run_info_widget.set_data(self.run_setup_widget.get_data())

    def indexes_setup(self):
        layout = self.indexes_tab.layout()
        layout.addWidget(self.indexes_toolbox)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        indexes_names = self.indexes_manager.get_indexes_names()

        for name in indexes_names:
            self.indexes_widgets[name] = self.indexes_manager.get_indexes_widget(name)
            self.indexes_toolbox.addItem(self.indexes_widgets[name], name)

    def profiles_setup(self):

        layout = self.profiles_tab.layout()
        layout.addWidget(self.profile_toolbox)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        profile_names = self.profile_manager.get_profile_names()

        for profile_name in profile_names:
            self.profile_widgets[profile_name] = self.profile_manager.get_profile_widget(profile_name)
            self.profile_manager.add_buttons[profile_name].clicked.connect(self.add_button_pressed)

        for profile_name in self.profile_widgets.keys():
            self.profile_toolbox.addItem(self.profile_widgets[profile_name], profile_name)

        self.profile_toolbox.currentChanged.connect(self.on_barcodes_click)

    def add_button_pressed(self):
        send_button = self.sender()
        selected_indexes = self.samples_tableview.selectedIndexes()
        self.sample_model.set_profile_on_selected(selected_indexes, send_button.profile_name)

    def on_barcodes_click(self):
        curr_tab = self.profiles_tab.currentIndex()
        if curr_tab < len(self.profile_widgets):
            self.profile_widgets[-1].show()
        else:
            self.profile_widgets[-1].hide()

    def hide_tabwidget_headers(self):
        tabmenu = self.menu_tabWidget.tabBar()
        tabmenu.setHidden(True)
        tabmain = self.main_tabWidget.tabBar()
        tabmain.setHidden(True)

    def sidemenu_setup(self):
        self.tab_anim["open"] = self.mk_animation(0, 300)
        self.tab_anim["close"] = self.mk_animation(300, 0)

    def mk_animation(self, start_width, end_width):
        animation = QPropertyAnimation(self.menu_tabWidget, b"maximumWidth")
        animation.setStartValue(start_width)
        animation.setEndValue(end_width)
        animation.setDuration(50)

        return animation

    def setup_tool_actions(self):
        """
        Set up the tool actions for the application.

        This function initializes the action-to-tab mapping for the different tool actions
        available in the application. It also sets up the icons, checkable states, and
        connections for each tool action.
        """
        self.action2tab = {
            "file": self.file_tab,
            "run": self.run_setup_tab,
            "profiles": self.profiles_tab,
            "indexes": self.indexes_tab,
            "config": self.config_tab,
            "manual_edit": self.config_tab,
        }

        self.file_action.setIcon(qta.icon('msc.files', options=[{'draw': 'image'}]))
        self.file_action.setCheckable(True)
        self.file_action.setChecked(False)
        self.file_action.triggered.connect(self.on_toolaction_click)

        self.run_action.setIcon(qta.icon('msc.symbol-misc', options=[{'draw': 'image'}]))
        self.run_action.setCheckable(True)
        self.run_action.setChecked(False)
        self.run_action.triggered.connect(self.on_toolaction_click)

        self.profiles_action.setIcon(qta.icon('msc.type-hierarchy-sub', options=[{'draw': 'image'}]))
        self.profiles_action.setCheckable(True)
        self.profiles_action.setChecked(False)
        self.profiles_action.triggered.connect(self.on_toolaction_click)

        self.indexes_action.setIcon(qta.icon('ei.barcode', options=[{'draw': 'image'}]))
        self.indexes_action.setCheckable(True)
        self.indexes_action.setChecked(False)
        self.indexes_action.triggered.connect(self.on_toolaction_click)

        self.config_action.setIcon(qta.icon('msc.settings-gear', options=[{'draw': 'image'}]))
        self.config_action.setCheckable(True)
        self.config_action.setChecked(False)
        self.config_action.triggered.connect(self.on_config_click)

        self.generate_action.setIcon(qta.icon('msc.play-circle', options=[{'draw': 'image'}]))
        self.generate_action.setCheckable(False)
        self.generate_action.setChecked(False)
        self.generate_action.triggered.connect(self.on_generate_click)

        self.manual_edit_action.setIcon(qta.icon('msc.unlock', options=[{'draw': 'image'}]))
        self.manual_edit_action.setCheckable(True)
        self.manual_edit_action.setChecked(False)
        self.manual_edit_action.triggered.connect(self.on_manual_edit_click)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        qbgroup = QActionGroup(self)
        qbgroup.setExclusionPolicy(QActionGroup.ExclusionPolicy.ExclusiveOptional)
        qbgroup.addAction(self.file_action)
        qbgroup.addAction(self.run_action)
        qbgroup.addAction(self.profiles_action)
        qbgroup.addAction(self.indexes_action)

        self.toolBar.addAction(self.file_action)
        self.toolBar.addAction(self.run_action)
        self.toolBar.addAction(self.indexes_action)
        self.toolBar.addAction(self.profiles_action)
        self.toolBar.addAction(self.generate_action)
        self.toolBar.addWidget(spacer)
        self.toolBar.addAction(self.manual_edit_action)
        self.toolBar.addAction(self.config_action)

    def on_manual_edit_click(self):
        pass

    def on_toolaction_click(self):
        button = self.sender()
        button_text = button.text()
        is_checked = button.isChecked()
        is_menu_hidden = self.menu_tabWidget.width() == 0
        is_menu_shown = self.menu_tabWidget.width() == 300

        if is_checked and is_menu_hidden:
            self.tab_anim["open"].start()
            self.menu_tabWidget.setCurrentWidget(self.action2tab[button_text])
        elif not is_checked and is_menu_shown:
            self.tab_anim["close"].start()
        else:
            self.menu_tabWidget.setCurrentWidget(self.action2tab[button_text])

    def on_config_click(self):
        if self.config_action.isChecked():
            self.main_tabWidget.setCurrentWidget(self.profiles_tab)
        else:
            self.main_tabWidget.setCurrentWidget(self.data_tab)

    def on_generate_click(self):
        pass

    def file_tab_setup(self):
        self.new_samplesheet_pushButton.clicked.connect(self.new_samplesheet)
        self.load_worklist_toolButton.clicked.connect(self.load_worklist)

    def load_worklist(self):
        options = get_dialog_options()
        return QFileDialog.getOpenFileName(self,
                                           "Open worklist file...",
                                           "",
                                           "Worklist files (*.txt *.csv)",
                                           options=options)[0]

    def new_samplesheet(self):
        fields = read_fields_from_json("config/data_fields.json")
        self.samples_model.setColumnCount(len(fields))

        for col, field in enumerate(fields):
            header_item = QStandardItem(field)
            self.samples_model.setHorizontalHeaderItem(col, header_item)

        self.samples_tableview.setModel(self.samples_model)
        self.samples_tableview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def exit(self):
        sys.exit()


def main():
    app = QApplication(sys.argv)
    qdarktheme.setup_theme("light")
    window = MainWindow()
    window.setGeometry(QtCore.QRect(300, 300, 640, 480))  # arbitrary size/location
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
