#! python
# -*- coding: utf-8 -*-
import sys

from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow,
    QSizePolicy,
    QFileDialog,
    QWidget,
    QPushButton,
    QGraphicsScene,
    QGraphicsView,
    QFrame,
)

from PySide6.QtGui import QAction, QActionGroup, QPainter, QIcon
from PySide6.QtCore import Qt, QSize, Signal

from models.configuration import ConfigurationManager
from views.configuration_view import ConfigurationWidget
from modules.WaitingSpinner.spinner.spinner import WaitingSpinner
from views.column_visibility_view import ColumnVisibilityControl
from views.index_view import IndexKitToolbox
from views.make_view import SampleSheetEdit
from views.profile_view import ApplicationProfiles
from views.run_setup_views import RunSetupWidget, RunView
from models.samplesheet_definitions import SampleSheetV2
from views.validation_view import (
    MainValidationWidget,
)

from views.samples_view import SamplesWidget
from views.ui.mw import Ui_MainWindow
import qtawesome as qta

sys.argv += ["-platform", "windows:darkmode=2"]
__author__ = "Pär Larsson"
__version__ = "2.0.0.a"

# os.environ['QT_API'] = 'pyside6'


def get_dialog_options():
    return QFileDialog.Options() | QFileDialog.DontUseNativeDialog


# def clear_layout(layout):
#     # Iterate through layout items in reverse order
#     while layout.count():
#         # Take the first item (from the top)
#         item = layout.takeAt(0)
#
#         # If the item is a layout, recursively clear it
#         if item.layout():
#             clear_layout(item.layout())
#
#         # If the item is a widget, remove it and delete it
#         elif item.widget():
#             widget = item.widget()
#             widget.setParent(None)  # Remove from parent
#             widget.deleteLater()  # Schedule for deletion


class MainWindow(QMainWindow, Ui_MainWindow):

    run_validate = Signal()

    def __init__(self, cfg_mgr: ConfigurationManager):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.main_version = __version__
        self.setWindowTitle(f"SampleCheater {self.main_version}")
        self.setWindowIcon(
            QIcon(qta.icon("ri.settings-line", options=[{"draw": "image"}]))
        )

        self.cfg_mgr = cfg_mgr

        self.setMinimumWidth(1000)
        self.left_toolBar.setMovable(False)
        self.left_toolBar.setIconSize(QSize(40, 40))

        self.spinner = WaitingSpinner(self)

        # left toolbar actions
        self.file_action = QAction("file", self)
        self.run_action = QAction("run", self)
        self.profiles_action = QAction("profiles", self)
        self.indexes_action = QAction("indexes", self)
        self.validate_action = QAction("validate", self)
        self.make_action = QAction("make", self)
        self.settings_action = QAction("settings", self)
        # self.edit_action = QAction("edit", self)

        self.left_tool_action_group = QActionGroup(self)
        self.actiongroup_mainview = QActionGroup(self)

        # right sidemenu button
        self.columns_settings_button = QPushButton("Columns")
        self.columns_settings_button.setObjectName("columns_settings")

        # self.left_tool_action_map = {}
        self.setup_left_toolbar_actions()

        # self.right_action_tab_map = {}
        self.setup_right_menu_actions()

        self.samples_widget = SamplesWidget()
        self.setup_samples_widget()

        # columns settings widget
        self.columns_treeview = ColumnVisibilityControl(
            self.cfg_mgr.samples_settings_dict
        )
        self.setup_columns_treeview()

        self.run_setup_widget = RunSetupWidget(self.cfg_mgr)
        self.run_view_widget = RunView()
        self.setup_run_view()

        self.validation_widget = MainValidationWidget()
        self.setup_validation_widget()

        self.indexes_widget = IndexKitToolbox(Path("config/indexes/indexes_json"))
        self.setup_indexes()
        #
        self.application_profiles_widget = ApplicationProfiles(
            self.cfg_mgr.application_profile_settings_basepath
        )
        self.setup_profile()

        self.cfg_widget = ConfigurationWidget(self.cfg_mgr)
        self.setup_cfg()

        self.leftmenu_stackedWidget.setFixedWidth(300)
        self.leftmenu_stackedWidget.hide()
        self.rightmenu_stackedWidget.setFixedWidth(250)
        self.rightmenu_stackedWidget.hide()

    def setup_validation_widget(self):
        layout = self.main_validation.layout()
        layout.addWidget(self.validation_widget)

    def setup_cfg(self):
        layout = self.main_settings.layout()
        layout.addWidget(self.cfg_widget)

    def setup_samplesheetedit(self):
        layout = self.main_make.layout()
        layout.addWidget(self.samplesheetedit)

    def setup_columns_treeview(self):
        layout = self.rightmenu_columnsettings.layout()
        layout.addWidget(self.columns_treeview)

        self.columns_treeview.field_visibility_state_changed.connect(
            self.samples_widget.sample_view.set_column_visibility_state
        )
        self.samples_widget.sample_view.field_visibility_state_changed.connect(
            self.columns_treeview.set_column_visibility_state
        )

    def _vertical_button_view(self, button: QPushButton):
        button.setFixedSize(100, 20)
        button.setContentsMargins(0, 0, 0, 0)
        button.setStyleSheet("QPushButton {border: none;}")
        button.setIcon(qta.icon("ph.rows-light"))

        scene = QGraphicsScene(self)
        button_proxy = scene.addWidget(button)
        button_proxy.setRotation(90)

        view = QGraphicsView(self.right_sidebar_widget)
        view.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        view.setFrameStyle(QFrame.NoFrame)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        button_size = button.size()
        view.setFixedSize(button_size.height() + 2, button_size.width() + 2)
        view.setScene(scene)
        view.setContentsMargins(0, 0, 0, 0)

        return view

    def setup_samples_widget(self):
        layout = self.main_data.layout()
        layout.addWidget(self.samples_widget)
        self.main_stackedWidget.setCurrentWidget(self.main_data)

    def setup_run_view(self):
        self.leftmenu_runsetup.layout().addWidget(self.run_setup_widget)
        main_data_layout = self.main_data.layout()
        main_data_layout.insertWidget(0, self.run_view_widget)

    def handle_run_set_button_click(self):
        run_info = self.run_setup_widget.get_data()
        self.run_view_widget.set_data(run_info)

    def setup_indexes(self):
        layout = self.leftmenu_indexes.layout()
        layout.addWidget(self.indexes_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

    def setup_profile(self):
        layout = self.leftmenu_profiles.layout()
        layout.addWidget(self.application_profiles_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

    def handle_left_toolbar_action(self):
        """Handle main view actions"""

        known_actions = {
            "file",
            "run",
            "profiles",
            "indexes",
            "config",
            "validate",
            "make",
        }

        main_data_actions = {"file", "run", "profiles", "indexes"}

        action = self.sender()
        action_id = action.data()
        is_checked = action.isChecked()

        if action_id not in known_actions:
            return

        if is_checked:
            self.leftmenu_stackedWidget.hide()
            if action_id in main_data_actions:
                self.main_stackedWidget.setCurrentWidget(self.main_data)
            elif action_id == "validate":
                self.main_stackedWidget.setCurrentWidget(self.main_validation)
                self.run_validate.emit()
            elif action_id == "make":
                self.main_stackedWidget.setCurrentWidget(self.main_make)
            elif action_id == "config":
                self.main_stackedWidget.setCurrentWidget(self.main_settings)

        if is_checked:
            if action_id == "file":
                self.leftmenu_stackedWidget.show()
                self.leftmenu_stackedWidget.setCurrentWidget(self.leftmenu_file)
            elif action_id == "run":
                self.leftmenu_stackedWidget.show()
                self.leftmenu_stackedWidget.setCurrentWidget(self.leftmenu_runsetup)
            elif action_id == "profiles":
                self.leftmenu_stackedWidget.show()
                self.leftmenu_stackedWidget.setCurrentWidget(self.leftmenu_profiles)
            elif action_id == "indexes":
                self.leftmenu_stackedWidget.show()
                self.leftmenu_stackedWidget.setCurrentWidget(self.leftmenu_indexes)
            else:
                return

        if not is_checked:
            self.leftmenu_stackedWidget.hide()
            self.main_stackedWidget.setCurrentWidget(self.main_data)

    def setup_left_toolbar_actions(self):
        """Set up the tool actions for the application."""

        actions = [
            (self.file_action, "msc.files", "file"),
            (self.run_action, "msc.symbol-misc", "run"),
            (self.indexes_action, "mdi6.barcode", "indexes"),
            (self.profiles_action, "msc.symbol-method", "profiles"),
            (self.validate_action, "msc.check-all", "validate"),
            (self.make_action, "msc.coffee", "make"),
            (self.settings_action, "msc.settings-gear", "config"),
        ]

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        action_group = QActionGroup(self)
        action_group.setExclusionPolicy(QActionGroup.ExclusionPolicy.ExclusiveOptional)

        for action, action_icon, action_id in actions:
            action.setCheckable(True)
            action.setChecked(False)
            action.setData(action_id)
            action.setIcon(qta.icon(action_icon, options=[{"draw": "image"}]))
            action_group.addAction(action)

        self.left_toolBar.addAction(action_group.actions()[0])
        self.left_toolBar.addAction(action_group.actions()[1])
        self.left_toolBar.addAction(action_group.actions()[2])
        self.left_toolBar.addAction(action_group.actions()[3])
        self.left_toolBar.addAction(action_group.actions()[4])
        self.left_toolBar.addAction(action_group.actions()[5])
        self.left_toolBar.addWidget(spacer)
        self.left_toolBar.addAction(action_group.actions()[6])

    def setup_right_menu_actions(self):
        """
        Set up the tool actions for the application.

        This function initializes the action-to-tab mapping for the different tool actions
        available in the application. It also sets up the icons, checkable states, and
        connections for each tool action.
        """
        self.right_action_tab_map = {"columns_settings": self.rightmenu_columnsettings}

        view = self._vertical_button_view(self.columns_settings_button)
        layout = self.right_sidebar_widget.layout()
        layout.insertWidget(0, view)
        layout.setContentsMargins(0, 0, 0, 0)

        self.columns_settings_button.setCheckable(True)
        self.columns_settings_button.setChecked(False)

        self.columns_settings_button.clicked.connect(self.on_right_menu_click)

    def on_right_menu_click(self):
        button = self.sender()
        button_id = button.objectName()

        is_button_checked = button.isChecked()

        if is_button_checked:
            self.rightmenu_stackedWidget.show()
            self.rightmenu_stackedWidget.setCurrentWidget(
                self.right_action_tab_map[button_id]
            )
        else:
            self.rightmenu_stackedWidget.hide()

    # def load_worklist(self):
    #     options = get_dialog_options()
    #     return QFileDialog.getOpenFileName(
    #         self,
    #         "Open worklist file...",
    #         "",
    #         "Worklist files (*.txt *.csv)",
    #         options=options,
    #     )[0]
    #
    # def exit(self):
    #     sys.exit()
