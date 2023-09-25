#! python
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
import qtawesome as qta

from modules.columns_visibility import ColumnsWidget
from modules.data_model.sample_model import SampleSheetModel
from modules.indexes import IndexesMGR
from modules.mapper import ColumnVisibilityMapper
from modules.models import read_fields_from_json
from modules.run_classes import RunSetup, RunInfo
from modules.profiles import ProfileMGR

from PySide6.QtGui import QAction, QActionGroup, QStandardItem, QPainter, QFont
from PySide6.QtCore import QPropertyAnimation, Qt, Slot

from PySide6.QtCore import QSize
from PySide6 import QtGui, QtCore
from PySide6.QtWidgets import QMainWindow, QApplication, QSizePolicy, QFileDialog, \
    QWidget, QHeaderView, QToolBox, QPushButton, QGraphicsScene, QGraphicsView, QFrame, QToolButton, QSpacerItem, \
    QLineEdit

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
        self.setMinimumWidth(1000)
        self.left_toolBar.setMovable(False)
        self.left_toolBar.setIconSize(QSize(40, 40))

        # left sidemenu options
        self.file_action = QAction("file", self)
        self.run_action = QAction("run", self)
        self.profiles_action = QAction("profiles", self)
        self.indexes_action = QAction("indexes", self)
        self.generate_action = QAction("generate", self)
        self.config_action = QAction("config", self)
        self.manual_edit_action = QAction("manual_edit", self)

        # right sidemenu options
        self.columns_settings_button = QPushButton("Columns")
        self.columns_settings_button.setObjectName("columns_settings")

        # columns settings widget
        self.columns_listview = ColumnsWidget()
        self.columns_listview_setup()

        self.column_visibility_mapper = ColumnVisibilityMapper()

        self.left_action2tab = {}
        self.setup_lefttool_actions()

        self.right_action2tab = {}
        self.setup_righttool_actions()

        self.sample_model = SampleSheetModel()
        self.samples_tableview = SampleTableView()
        self.sample_tableview_setup()

        self.file_tab_setup()

        self.run_setup_widget = RunSetup(Path("config/run_settings/run_settings.yaml"))
        self.run_info_widget = RunInfo()
        self.run_setup()

        self.field_view = QLineEdit()
        self.field_view_setup()

        self.indexes_toolbox = QToolBox()
        self.indexes_manager = IndexesMGR(Path("config/indexes"))
        self.indexes_widgets = {}
        self.indexes_setup()
        #
        # self.profile_toolbox = QToolBox()
        # self.profile_manager = ProfileMGR()
        #

        self.left_tab_anim = {}
        self.right_tab_anim = {}

        # self.sidemenu_right_animation_setup()
        self.menu_animations_setup()
        self.hide_tabwidget_headers()
        # self.column_visibility_combobox_setup()

        # self.run_setup()
        #
        # self.profile_widgets = {}
        # self.profiles_setup()

        self.leftmenu_tabWidget.setMaximumWidth(0)
        self.rightmenu_tabWidget.setMaximumWidth(0)

    def columns_listview_setup(self):
        layout = self.columns_settings_tab.layout()
        layout.addWidget(self.columns_listview)
        self.columns_listview.set_items({'test': True, 'test2': False})
        self.columns_listview.itemChecked.connect(self.handle_item_checked)

    @Slot()
    def handle_item_checked(self, item, checked):
        print(f"Item '{item}' checked: {checked}")

    def field_view_setup(self):
        self.verticalLayout.insertWidget(1, self.field_view)
        self.field_view.setFont(QFont("Arial", 8))
        self.field_view.setReadOnly(True)
        self.samples_tableview.selectionModel().selectionChanged.connect(self.on_tv_selection_changed)
        self.samples_tableview.model().dataChanged.connect(self.on_tv_selection_changed)

    def on_tv_selection_changed(self):
        selection_model = self.samples_tableview.selectionModel()
        selected_indexes = selection_model.selectedIndexes()
        if len(selected_indexes) == 1 and selected_indexes:
            model = self.samples_tableview.model()
            data = model.data(selected_indexes[0], Qt.DisplayRole)
            column = selected_indexes[0].column()
            row = selected_indexes[0].row()
            column_name = self.samples_tableview.horizontalHeader().model().headerData(column, Qt.Horizontal)
            self.field_view.setText(f"{row}, {column_name}: {data}")

    @Slot(str)
    def set_field_view_text(self, text):
        self.field_view.setText(text)

    def menu_animations_setup(self):
        self.left_tab_anim["open"] = self.mk_animation(self.leftmenu_tabWidget, 0, 300)
        self.left_tab_anim["close"] = self.mk_animation(self.leftmenu_tabWidget, 300, 0)
        
        self.right_tab_anim["open"] = self.mk_animation(self.rightmenu_tabWidget, 0, 200)
        self.right_tab_anim["close"] = self.mk_animation(self.rightmenu_tabWidget, 200, 0)

    def mk_animation(self, menu_widget, start_width, end_width):
        animation = QPropertyAnimation(menu_widget, b"maximumWidth")
        animation.setStartValue(start_width)
        animation.setEndValue(end_width)
        animation.setDuration(50)

        return animation

    def get_vertical_button_view(self, button: QPushButton):
        button.setFixedHeight(20)
        button.setFixedWidth(100)
        button.setContentsMargins(0, 0, 0, 0)
        button.setStyleSheet("QPushButton {border-width: 0px;}")
        button.setIcon(qta.icon('ph.rows-light'))

        button_size = button.size()

        scene = QGraphicsScene(self)
        proxy_widget = scene.addWidget(button)
        proxy_widget.setRotation(90)
        view = QGraphicsView(self.right_sidebar_widget)
        view.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        view.setFrameStyle(QFrame.NoFrame)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setFixedHeight(button_size.width() + 2)
        view.setFixedWidth(button_size.height() + 2)
        view.setScene(scene)
        view.setContentsMargins(0, 0, 0, 0)

        return view


    def column_visibility_combobox_setup(self):
        cb = CheckableComboBox()
        self.column_visibility_mapper.set_map(cb, self.samples_tableview)
        self.run_info_widget.add_widget(cb)

    def sample_tableview_setup(self):
        self.samples_tableview.setModel(self.sample_model)
        self.verticalLayout.addWidget(self.samples_tableview)
        self.samples_tableview.setContextMenuPolicy(Qt.CustomContextMenu)
        self.samples_tableview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def run_setup(self):
        self.run_setup_tab.layout().addWidget(self.run_setup_widget)
        self.verticalLayout.insertWidget(0, self.run_info_widget)
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
            name2 = self.indexes_widgets[name].get_name()

            readable_name = self.indexes_widgets[name].get_name_readable()
            self.indexes_toolbox.addItem(self.indexes_widgets[name], readable_name)

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
        self.leftmenu_tabWidget.tabBar().setHidden(True)
        self.main_tabWidget.tabBar().setHidden(True)
        self.rightmenu_tabWidget.tabBar().setHidden(True)

    # def sidemenu_animation_setup(self):
    #     self.left_tab_anim["open"] = self.mk_animation(0, 300)
    #     self.left_tab_anim["close"] = self.mk_animation(300, 0)

    # def mk_animation_right(self, start_width, end_width):
    #     animation = QPropertyAnimation(self.rightmenu_tabWidget, b"maximumWidth")
    #     animation.setStartValue(start_width)
    #     animation.setEndValue(end_width)
    #     animation.setDuration(50)
    #
    #     return animation

    def setup_lefttool_actions(self):
        """
        Set up the tool actions for the application.

        This function initializes the action-to-tab mapping for the different tool actions
        available in the application. It also sets up the icons, checkable states, and
        connections for each tool action.
        """
        self.left_action2tab = {
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
        self.file_action.triggered.connect(self.on_toolgroup_click)

        self.run_action.setIcon(qta.icon('msc.symbol-misc', options=[{'draw': 'image'}]))
        self.run_action.setCheckable(True)
        self.run_action.setChecked(False)
        self.run_action.triggered.connect(self.on_toolgroup_click)

        self.profiles_action.setIcon(qta.icon('msc.type-hierarchy-sub', options=[{'draw': 'image'}]))
        self.profiles_action.setCheckable(True)
        self.profiles_action.setChecked(False)
        self.profiles_action.triggered.connect(self.on_toolgroup_click)

        self.indexes_action.setIcon(qta.icon('mdi6.barcode', options=[{'draw': 'image'}]))
        self.indexes_action.setCheckable(True)
        self.indexes_action.setChecked(False)
        self.indexes_action.triggered.connect(self.on_toolgroup_click)

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

        self.left_toolBar.addAction(self.file_action)
        self.left_toolBar.addAction(self.run_action)
        self.left_toolBar.addAction(self.indexes_action)
        self.left_toolBar.addAction(self.profiles_action)
        self.left_toolBar.addAction(self.generate_action)
        self.left_toolBar.addWidget(spacer)
        self.left_toolBar.addAction(self.manual_edit_action)
        self.left_toolBar.addAction(self.config_action)

    def setup_righttool_actions(self):
        """
        Set up the tool actions for the application.

        This function initializes the action-to-tab mapping for the different tool actions
        available in the application. It also sets up the icons, checkable states, and
        connections for each tool action.
        """
        self.right_action2tab = {
            "columns_settings": self.columns_settings_tab
        }

        view = self.get_vertical_button_view(self.columns_settings_button)
        layout = self.right_sidebar_widget.layout()
        layout.insertWidget(0, view)
        layout.setContentsMargins(0, 0, 0, 0)

        self.columns_settings_button.setCheckable(True)
        self.columns_settings_button.setChecked(False)

        self.columns_settings_button.clicked.connect(self.on_righttool_click)

    def on_righttool_click(self):
        sender = self.sender()
        obj_id = sender.objectName()

        is_checked = sender.isChecked()
        menu_width = self.rightmenu_tabWidget.width()
        menu_shown = menu_width > 0
        if is_checked and not menu_shown:
            self.right_tab_anim["open"].start()
            # self.rightmenu_tabWidget.setMinimumWidth(200)
            # self.rightmenu_tabWidget.setMaximumWidth(200)
            self.rightmenu_tabWidget.setCurrentWidget(self.right_action2tab[obj_id])
        elif not is_checked and menu_shown:
            self.right_tab_anim["close"].start()
        else:
            self.rightmenu_tabWidget.setCurrentWidget(self.right_action2tab[obj_id])

    def on_manual_edit_click(self):
        pass

    def on_toolgroup_click(self):
        button = self.sender()
        button_text = button.text()

        is_checked = button.isChecked()
        menu_width = self.leftmenu_tabWidget.width()
        menu_shown = menu_width > 0
        if is_checked and not menu_shown:
            self.left_tab_anim["open"].start()
            self.leftmenu_tabWidget.setCurrentWidget(self.left_action2tab[button_text])
        elif not is_checked and menu_shown:
            self.left_tab_anim["close"].start()
        else:
            self.leftmenu_tabWidget.setCurrentWidget(self.left_action2tab[button_text])

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
