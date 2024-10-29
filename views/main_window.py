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

from views.settings_view import SettingsWidget
from modules.WaitingSpinner.spinner.spinner import WaitingSpinner
from views.visibility_view import ColumnsTreeWidget
from views.index_view import IndexKitToolbox
from views.make_view import SampleSheetEdit
from views.profile_view import ApplicationProfiles
from views.run_view import RunSetupWidget, RunInfoViewWidget
from models.samplesheet import SampleSheetV2
from views.validation_view import (
    ValidationWidget,
)

from views.samples_view import SampleWidget
from views.ui.mw import Ui_MainWindow
import qtawesome as qta

sys.argv += ["-platform", "windows:darkmode=2"]
__author__ = "Pär Larsson"
__version__ = "2.0.0.a"

# os.environ['QT_API'] = 'pyside6'


def get_dialog_options():
    return QFileDialog.Options() | QFileDialog.DontUseNativeDialog


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

    run_validate = Signal()

    def __init__(self, sample_settings_path):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.main_version = __version__
        self.setWindowTitle(f"SampleCheater {self.main_version}")
        self.setWindowIcon(
            QIcon(qta.icon("ri.settings-line", options=[{"draw": "image"}]))
        )

        self.application_profiles_basepath = Path("config/applications")

        self.setMinimumWidth(1000)
        self.left_toolBar.setMovable(False)
        self.left_toolBar.setIconSize(QSize(40, 40))

        self.spinner = WaitingSpinner(self)

        # left sidemenu options
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

        # right sidemenu options
        self.columns_settings_button = QPushButton("Columns")
        self.columns_settings_button.setObjectName("columns_settings")

        self.left_tool_action_map = {}
        self.left_tool_actions_setup()

        self.right_action_tab_map = {}
        self.right_tool_actions_setup()

        self.sample_widget = SampleWidget()

        # columns settings widget
        self.columns_treeview = ColumnsTreeWidget(sample_settings_path)
        self.columns_listview_setup()

        self.leftmenu_stackedWidget.setFixedWidth(300)
        self.leftmenu_stackedWidget.hide()
        self.rightmenu_stackedWidget.setFixedWidth(250)
        self.rightmenu_stackedWidget.hide()

        self.run_setup_widget = RunSetupWidget(Path("config/run/run_settings.yaml"))
        self.run_infoview_widget = RunInfoViewWidget()
        self.run_info_setup()

        self.validation_widget = ValidationWidget()
        self.validation_widget_setup()

        self.indexes_widget = IndexKitToolbox(Path("config/indexes/indexes_json"))
        self.indexes_setup()
        #
        self.application_profiles_widget = ApplicationProfiles(
            self.application_profiles_basepath
        )
        self.profile_setup()

        self.settings = SettingsWidget()
        self.settings_setup()

    def validation_widget_setup(self):
        layout = self.main_validation.layout()
        layout.addWidget(self.validation_widget)

    def settings_setup(self):
        layout = self.main_settings.layout()
        layout.addWidget(self.settings)

    def samplesheetedit_setup(self):
        layout = self.main_make.layout()
        layout.addWidget(self.samplesheetedit)

    def columns_listview_setup(self):
        layout = self.rightmenu_columnsettings.layout()
        layout.addWidget(self.columns_treeview)

        self.columns_treeview.field_visibility_state_changed.connect(
            self.sample_widget.sample_view.set_column_visibility_state
        )
        self.sample_widget.sample_view.field_visibility_state_changed.connect(
            self.columns_treeview.set_column_visibility_state
        )

    def get_vertical_button_view(self, button: QPushButton):
        button.setFixedSize(100, 20)
        button.setContentsMargins(0, 0, 0, 0)
        button.setStyleSheet("QPushButton {border: none;}")
        button.setIcon(qta.icon("ph.rows-light"))

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

    def sample_widget_setup(self):

        layout = self.main_data.layout()
        clear_layout(layout)
        layout.addWidget(self.sample_widget)
        self.main_stackedWidget.setCurrentWidget(self.main_data)

    def run_info_setup(self):
        self.leftmenu_runsetup.layout().addWidget(self.run_setup_widget)
        self.main_verticalLayout.insertWidget(0, self.run_infoview_widget)
        self.run_infoview_widget.setup(self.run_setup_widget.get_data())
        self.run_setup_widget.set_button.clicked.connect(
            self.handle_run_set_button_click
        )

    def handle_run_set_button_click(self):
        run_info = self.run_setup_widget.get_data()
        self.run_infoview_widget.set_data(run_info)

    def indexes_setup(self):
        layout = self.leftmenu_indexes.layout()
        layout.addWidget(self.indexes_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

    def profile_setup(self):
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

    def left_tool_actions_setup(self):
        """
        Set up the tool actions for the application.

        This function initializes the action-to-tab mapping for the different tool actions
        available in the application. It also sets up the icons, checkable states, and
        connections for each tool action.
        """
        self.left_tool_action_map = {
            "file": self.leftmenu_file,
            "run": self.leftmenu_runsetup,
            "profiles": self.leftmenu_profiles,
            "indexes": self.leftmenu_indexes,
            "config": self.leftmenu_config,
        }

        self.file_action.setIcon(qta.icon("msc.files", options=[{"draw": "image"}]))
        self.file_action.setCheckable(True)
        self.file_action.setChecked(False)
        self.file_action.setData("file")
        # self.file_action.triggered.connect(self.click_action_leftmenu)

        self.run_action.setIcon(
            qta.icon("msc.symbol-misc", options=[{"draw": "image"}])
        )
        self.run_action.setCheckable(True)
        self.run_action.setChecked(False)
        self.run_action.setData("run")
        # self.run_action.triggered.connect(self.click_action_leftmenu)

        self.profiles_action.setIcon(
            qta.icon("msc.symbol-method", options=[{"draw": "image"}])
        )
        self.profiles_action.setCheckable(True)
        self.profiles_action.setChecked(False)
        self.profiles_action.setData("profiles")
        # self.profiles_action.triggered.connect(self.click_action_leftmenu)

        self.indexes_action.setIcon(
            qta.icon("mdi6.barcode", options=[{"draw": "image"}])
        )
        self.indexes_action.setCheckable(True)
        self.indexes_action.setChecked(False)
        self.indexes_action.setData("indexes")
        # self.indexes_action.triggered.connect(self.click_action_leftmenu)

        self.settings_action.setIcon(
            qta.icon("msc.settings-gear", options=[{"draw": "image"}])
        )
        self.settings_action.setCheckable(True)
        self.settings_action.setChecked(False)
        self.settings_action.setData("config")
        # self.settings_action.triggered.connect(self.click_action_mainview)

        self.validate_action.setIcon(
            qta.icon("msc.check-all", options=[{"draw": "image"}])
        )
        self.validate_action.setCheckable(True)
        self.validate_action.setChecked(False)
        self.validate_action.setData("validate")
        # self.validate_action.triggered.connect(self.click_action_mainview)

        self.make_action.setIcon(qta.icon("msc.coffee", options=[{"draw": "image"}]))
        self.make_action.setCheckable(True)
        self.make_action.setChecked(False)
        self.make_action.setData("make")
        # self.make_action.triggered.connect(self.click_action_mainview)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.left_tool_action_group.setExclusionPolicy(
            QActionGroup.ExclusionPolicy.ExclusiveOptional
        )
        self.left_tool_action_group.addAction(self.file_action)
        self.left_tool_action_group.addAction(self.run_action)
        self.left_tool_action_group.addAction(self.profiles_action)
        self.left_tool_action_group.addAction(self.indexes_action)
        self.left_tool_action_group.addAction(self.settings_action)
        self.left_tool_action_group.addAction(self.validate_action)
        self.left_tool_action_group.addAction(self.make_action)

        self.left_toolBar.addAction(self.file_action)
        self.left_toolBar.addAction(self.run_action)
        self.left_toolBar.addAction(self.indexes_action)
        self.left_toolBar.addAction(self.profiles_action)
        self.left_toolBar.addAction(self.validate_action)
        self.left_toolBar.addAction(self.make_action)
        self.left_toolBar.addWidget(spacer)
        self.left_toolBar.addAction(self.settings_action)

    def right_tool_actions_setup(self):
        """
        Set up the tool actions for the application.

        This function initializes the action-to-tab mapping for the different tool actions
        available in the application. It also sets up the icons, checkable states, and
        connections for each tool action.
        """
        self.right_action_tab_map = {"columns_settings": self.rightmenu_columnsettings}

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

        print(obj_id)

        is_checked = sender.isChecked()
        # menu_width = self.rightmenu_stackedWidget.width()
        # menu_shown = menu_width > 0
        if is_checked:
            self.rightmenu_stackedWidget.show()
            self.rightmenu_stackedWidget.setCurrentWidget(
                self.right_action_tab_map[obj_id]
            )
        else:
            # self.right_tab_anim["close"].start()
            self.rightmenu_stackedWidget.hide()

        self.rightmenu_stackedWidget.setCurrentWidget(self.right_action_tab_map[obj_id])

    def load_worklist(self):
        options = get_dialog_options()
        return QFileDialog.getOpenFileName(
            self,
            "Open worklist file...",
            "",
            "Worklist files (*.txt *.csv)",
            options=options,
        )[0]

    def exit(self):
        sys.exit()
