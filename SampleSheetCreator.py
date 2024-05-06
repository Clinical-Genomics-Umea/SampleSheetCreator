#! python
# -*- coding: utf-8 -*-
import os
import sys

import yaml
from pathlib import Path
import qtawesome as qta

from modules.columns_visibility import ColumnsTreeWidget
from modules.data_model.sample_model import SampleSheetModel
from modules.indexes import IndexPanelWidgetMGR, IndexKitDefinitionMGR
from modules.models import read_fields_from_json
from modules.profiles import ProfileWidgetMGR
from modules.run_classes import RunSetup, RunInfo
from modules.validation.validation import DataValidationWidget

from PySide6.QtGui import QAction, QActionGroup, QStandardItem, QPainter
from PySide6.QtCore import QPropertyAnimation, Qt, Slot

from PySide6.QtCore import QSize
from PySide6 import QtGui, QtCore
from PySide6.QtWidgets import QMainWindow, QApplication, QSizePolicy, QFileDialog, \
    QWidget, QHeaderView, QToolBox, QPushButton, QGraphicsScene, QGraphicsView, QFrame

from modules.sample_view import SampleTableView, SampleWidget
from ui.mw import Ui_MainWindow
import qdarktheme

sys.argv += ['-platform', 'windows:darkmode=2']
__author__ = "Pär Larsson"
__version__ = "2.0.0.a"


def get_dialog_options():
    return QFileDialog.Options() | QFileDialog.DontUseNativeDialog


def read_yaml_file(filename):
    """
    Read a YAML file and return its data.

    Parameters:
        filename (str): The name of the YAML file to read.

    Returns:
        dict: The data loaded from the YAML file, or None if the file is not found or an error occurred.
    """
    # Get the path to the directory of the current module
    module_dir = os.path.dirname(__file__)

    # Combine the directory path with the provided filename to get the full path
    file_path = os.path.join(module_dir, filename)

    try:
        with open(file_path, 'r') as file:
            # Load YAML data from the file
            data = yaml.safe_load(file)
        return data
    except FileNotFoundError:
        print(f"File '{filename}' not found in the module directory.")
        return None
    except Exception as e:
        print(f"An error occurred while reading '{filename}': {e}")
        return None

def clear_layout(layout):
    # Iterate through layout items in reverse order
    while layout.count():
        # Take the first item (from the top)
        item = layout.takeAt(0)

        # If the item is a layout, recursively clear it
        if item.layout():
            clear_layout(item.layout())

        # If the item is a widget, remove it and delete it
        elif item.widget():
            widget = item.widget()
            widget.setParent(None)  # Remove from parent
            widget.deleteLater()  # Schedule for deletion


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
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
        self.validate_action = QAction("validate", self)
        self.config_action = QAction("config", self)
        self.edit_action = QAction("edit", self)

        # right sidemenu options
        self.columns_settings_button = QPushButton("Columns")
        self.columns_settings_button.setObjectName("columns_settings")

        self.left_action_tab_map = {}
        self.left_tool_actions_setup()

        self.right_action_tab_map = {}
        self.right_tool_actions_setup()

        fields_path = read_yaml_file("config/sample_fields.yaml")
        self.samples_model = SampleSheetModel(fields_path)
        self.samples_widget = SampleWidget(self.samples_model)
        self.samples_tableview = self.samples_widget.sampleview
        self.sample_tableview_setup()

        # columns settings widget
        self.columns_treeview = ColumnsTreeWidget(fields_path)
        self.columns_listview_setup()

        self.left_tab_anim = {}
        self.right_tab_anim = {}

        self.menu_animations_setup()

        self.leftmenu_stackedWidget.setMaximumWidth(0)
        self.leftmenu_stackedWidget.hide()
        self.rightmenu_stackedWidget.setMaximumWidth(0)
        self.rightmenu_stackedWidget.hide()

        # self.file_tab_setup()

        self.run_setup_widget = RunSetup(Path("config/run_settings/run_settings.yaml"))
        self.run_info_widget = RunInfo()
        self.run_setup()

        self.validate_widget = DataValidationWidget(self.samples_model, self.run_info_widget)
        self.validate_widget_setup()

        self.index_mgr = IndexKitDefinitionMGR(Path("config/indexes"))
        self.index_toolbox = QToolBox()
        self.index_panel_mgr = IndexPanelWidgetMGR(self.index_mgr)
        self.index_widgets = {}
        self.indexes_setup()

        self.profile_toolbox = QToolBox()
        self.profile_mgr = ProfileWidgetMGR(self.index_mgr, Path("config/profiles"))
        self.profile_widgets = {}
        self.profile_setup()

        self.menu_animations_setup()

        self.leftmenu_stackedWidget.setMaximumWidth(0)
        self.rightmenu_stackedWidget.setMaximumWidth(0)

    def validate_widget_setup(self):
        layout = self.main_validation.layout()
        layout.addWidget(self.validate_widget)

    def columns_listview_setup(self):
        layout = self.rightmenu_columnsettings.layout()
        layout.addWidget(self.columns_treeview)

        self.columns_treeview.field_visibility_state_changed.connect(self.samples_tableview.set_column_visibility_state)
        self.samples_tableview.field_visibility_state_changed.connect(self.columns_treeview.set_column_visibility_state)

    def on_samples_tableview_selection_changed(self):
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
        self.left_tab_anim["open"] = self.make_animation(self.leftmenu_stackedWidget, 0, 300)
        self.left_tab_anim["close"] = self.make_animation(self.leftmenu_stackedWidget, 300, 0)
        
        self.right_tab_anim["open"] = self.make_animation(self.rightmenu_stackedWidget, 0, 250)
        self.right_tab_anim["close"] = self.make_animation(self.rightmenu_stackedWidget, 250, 0)

    @staticmethod
    def make_animation(menu_widget, start_width, end_width):
        animation = QPropertyAnimation(menu_widget, b"maximumWidth")
        animation.setStartValue(start_width)
        animation.setEndValue(end_width)
        animation.setDuration(5)

        return animation

    def get_vertical_button_view(self, button: QPushButton):
        button.setFixedSize(100, 20)
        button.setContentsMargins(0, 0, 0, 0)
        button.setStyleSheet("QPushButton {border: none;}")
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

    def sample_tableview_setup(self):

        print("sample_tableview_setup")

        layout = self.main_data.layout()
        clear_layout(layout)
        layout.addWidget(self.samples_widget)
        self.main_stackedWidget.setCurrentWidget(self.main_data)

    def run_setup(self):
        self.leftmenu_runsetup.layout().addWidget(self.run_setup_widget)
        self.verticalLayout.insertWidget(0, self.run_info_widget)
        self.run_info_widget.setup(self.run_setup_widget.get_data())
        self.run_setup_widget.set_button.clicked.connect(self.handle_run_set_button_click)

    def handle_run_set_button_click(self):
        run_info = self.run_setup_widget.get_data()
        self.run_info_widget.set_data(run_info)

    def indexes_setup(self):
        layout = self.leftmenu_indexes.layout()
        layout.addWidget(self.index_toolbox)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        index_kit_names = self.index_panel_mgr.get_index_panel_widget_names()

        for name in index_kit_names:
            self.index_widgets[name] = self.index_panel_mgr.get_index_panel_widget(name)
            self.index_toolbox.addItem(self.index_widgets[name], name)

    def profile_setup(self):

        layout = self.leftmenu_profiles.layout()
        layout.addWidget(self.profile_toolbox)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        profile_names = self.profile_mgr.get_profile_names()

        for profile_name in profile_names:
            self.profile_widgets[profile_name] = self.profile_mgr.get_profile_widget(profile_name)
            self.profile_toolbox.addItem(self.profile_widgets[profile_name], profile_name)
            self.profile_widgets[profile_name].profile_data_signal.connect(self.samples_tableview.set_profiles_data)

    def add_button_pressed(self):
        send_button = self.sender()
        selected_indexes = self.samples_tableview.selectedIndexes()
        self.samples_model.set_profile_on_selected(selected_indexes, send_button.profile_name)

    def left_tool_actions_setup(self):
        """
        Set up the tool actions for the application.

        This function initializes the action-to-tab mapping for the different tool actions
        available in the application. It also sets up the icons, checkable states, and
        connections for each tool action.
        """
        self.left_action_tab_map = {
            "file": self.leftmenu_file,
            "run": self.leftmenu_runsetup,
            "profiles": self.leftmenu_profiles,
            "indexes": self.leftmenu_indexes,
            "config": self.leftmenu_config,
            # "edit": self.leftmenu_edit,
        }

        self.file_action.setIcon(qta.icon('msc.files', options=[{'draw': 'image'}]))
        self.file_action.setCheckable(True)
        self.file_action.setChecked(False)
        self.file_action.triggered.connect(self.on_tool_group_click)

        self.run_action.setIcon(qta.icon('msc.symbol-misc', options=[{'draw': 'image'}]))
        self.run_action.setCheckable(True)
        self.run_action.setChecked(False)
        self.run_action.triggered.connect(self.on_tool_group_click)

        self.profiles_action.setIcon(qta.icon('msc.type-hierarchy-sub', options=[{'draw': 'image'}]))
        self.profiles_action.setCheckable(True)
        self.profiles_action.setChecked(False)
        self.profiles_action.triggered.connect(self.on_tool_group_click)

        self.indexes_action.setIcon(qta.icon('mdi6.barcode', options=[{'draw': 'image'}]))
        self.indexes_action.setCheckable(True)
        self.indexes_action.setChecked(False)
        self.indexes_action.triggered.connect(self.on_tool_group_click)

        self.config_action.setIcon(qta.icon('msc.settings-gear', options=[{'draw': 'image'}]))
        self.config_action.setCheckable(True)
        self.config_action.setChecked(False)
        self.config_action.triggered.connect(self.on_config_click)

        self.validate_action.setIcon(qta.icon('msc.check-all', options=[{'draw': 'image'}]))
        self.validate_action.setCheckable(True)
        self.validate_action.setChecked(False)
        self.validate_action.triggered.connect(self.on_validate_click)

        self.edit_action.setIcon(qta.icon('msc.unlock', options=[{'draw': 'image'}]))
        self.edit_action.setCheckable(True)
        self.edit_action.setChecked(False)
        self.edit_action.triggered.connect(self.on_edit_click)

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
        self.left_toolBar.addAction(self.validate_action)
        self.left_toolBar.addWidget(spacer)
        self.left_toolBar.addAction(self.edit_action)
        self.left_toolBar.addAction(self.config_action)

    def right_tool_actions_setup(self):
        """
        Set up the tool actions for the application.

        This function initializes the action-to-tab mapping for the different tool actions
        available in the application. It also sets up the icons, checkable states, and
        connections for each tool action.
        """
        self.right_action_tab_map = {
            "columns_settings": self.rightmenu_columnsettings
        }

        view = self.get_vertical_button_view(self.columns_settings_button)
        layout = self.right_sidebar_widget.layout()
        layout.insertWidget(0, view)
        layout.setContentsMargins(0, 0, 0, 0)

        self.columns_settings_button.setCheckable(True)
        self.columns_settings_button.setChecked(False)

        self.columns_settings_button.clicked.connect(self.on_right_tool_click)

    def on_right_tool_click(self):
        sender = self.sender()
        obj_id = sender.objectName()

        is_checked = sender.isChecked()
        menu_width = self.rightmenu_stackedWidget.width()
        menu_shown = menu_width > 0
        if is_checked and not menu_shown:
            self.rightmenu_stackedWidget.show()
            self.right_tab_anim["open"].start()
            self.rightmenu_stackedWidget.setCurrentWidget(self.right_action_tab_map[obj_id])
        elif not is_checked and menu_shown:
            self.right_tab_anim["close"].start()
            self.rightmenu_stackedWidget.hide()
        else:
            self.rightmenu_stackedWidget.setCurrentWidget(self.right_action_tab_map[obj_id])

    def on_edit_click(self):
        pass

    def on_tool_group_click(self):
        button = self.sender()
        button_text = button.text()

        is_checked = button.isChecked()
        menu_width = self.leftmenu_stackedWidget.width()
        menu_shown = menu_width > 0
        if is_checked and not menu_shown:
            self.leftmenu_stackedWidget.show()
            self.left_tab_anim["open"].start()
            self.leftmenu_stackedWidget.setCurrentWidget(self.left_action_tab_map[button_text])
        elif not is_checked and menu_shown:
            self.left_tab_anim["close"].start()
            self.leftmenu_stackedWidget.hide()
        else:
            self.leftmenu_stackedWidget.setCurrentWidget(self.left_action_tab_map[button_text])

    def on_config_click(self):
        if self.config_action.isChecked():
            self.main_stackedWidget.setCurrentWidget(self.main_validation)
        else:
            self.main_stackedWidget.setCurrentWidget(self.main_data)

    def on_validate_click(self):

        button = self.sender()

        if button.isChecked():
            self.main_stackedWidget.setCurrentWidget(self.main_validation)
            self.validate_widget.validate()
        else:
            self.main_stackedWidget.setCurrentWidget(self.main_data)

    def file_tab_setup(self):
        print("file_tab_setup")
        fields_path = read_yaml_file("config/sample_fields.yaml")
        self.samples_model = SampleSheetModel(fields_path)
        self.samples_widget = SampleWidget(self.samples_model)
        self.samples_tableview = self.samples_widget.sampleview
        self.sample_tableview_setup()

    # def file_tab_setup(self):
    #     self.new_samplesheet_pushButton.clicked.connect(self.new_samplesheet)
    #     self.load_worklist_toolButton.clicked.connect(self.load_worklist)

    def load_worklist(self):
        options = get_dialog_options()
        return QFileDialog.getOpenFileName(self,
                                           "Open worklist file...",
                                           "",
                                           "Worklist files (*.txt *.csv)",
                                           options=options)[0]

    # def new_samplesheet(self):
    #     fields = read_fields_from_json("config/data_fields.json")
    #     self.samples_model.setColumnCount(len(fields))
    #
    #     for col, field in enumerate(fields):
    #         header_item = QStandardItem(field)
    #         self.samples_model.setHorizontalHeaderItem(col, header_item)
    #
    #     self.samples_tableview.setModel(self.samples_model)
    #     self.samples_tableview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

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
