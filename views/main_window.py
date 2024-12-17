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
)

from PySide6.QtGui import QAction, QActionGroup, QIcon
from PySide6.QtCore import Qt, QSize, Signal

from models.application.application import ApplicationManager
from models.configuration.configuration import ConfigurationManager
from models.dataset.dataset import DataSetManager
from views.config.configuration_view import ConfigurationWidget
from modules.WaitingSpinner.spinner.spinner import WaitingSpinner
from views.leftmenu.file import FileView
from views.leftmenu.index import IndexKitToolbox
from views.notify.notify import StatusBar
from views.leftmenu.override import OverrideCyclesWidget
from views.leftmenu.application import Applications
from views.runview.runview import RunView, RunInfoView
from views.leftmenu.runsetup import RunSetupWidget
from views.export.export_view import ExportWidget
from views.validation.validation_view import (
    MainValidationWidget,
)

from views.sample.sample_view import SamplesWidget
from views.ui.mw import Ui_MainWindow
import qtawesome as qta

sys.argv += ["-platform", "windows:darkmode=2"]
__author__ = "Pär Larsson"
__version__ = "2.0.0.a"

# os.environ['QT_API'] = 'pyside6'


def get_dialog_options():
    return QFileDialog.Options() | QFileDialog.DontUseNativeDialog


class MainWindow(QMainWindow, Ui_MainWindow):

    run_validate = Signal()

    def __init__(
        self,
        config_manager: ConfigurationManager,
        application_manager: ApplicationManager,
        dataset_manager: DataSetManager,
        status_bar: StatusBar,
    ):
        """
        Initialize the main window
        """
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(f"SampleCheater {__version__}")
        self.setWindowIcon(
            QIcon(qta.icon("ri.settings-line", options=[{"draw": "image"}]))
        )
        self.status_bar = status_bar
        self.setStatusBar(self.status_bar)

        self.config_manager = config_manager
        self.application_manager = application_manager
        self.dataset_manager = dataset_manager

        self.setMinimumWidth(1000)
        self.left_toolBar.setMovable(False)
        self.left_toolBar.setIconSize(QSize(40, 40))

        self.spinner = WaitingSpinner(self)

        # left toolbar actions
        self.left_tool_action_group = QActionGroup(self)
        self.action_group_main_view = QActionGroup(self)

        self.file_action = QAction("File", self)
        self.run_action = QAction("Run", self)
        self.apps_action = QAction("Apps", self)
        self.indexes_action = QAction("Indexes", self)
        self.override_action = QAction("Override", self)
        self.validate_action = QAction("Validate", self)
        self.export_action = QAction("Export", self)
        self.settings_action = QAction("Settings", self)

        self.export_action.setEnabled(False)

        self.columns_settings_button = QPushButton("Columns")
        self.columns_settings_button.setObjectName("columns_settings")

        self.override_widget = OverrideCyclesWidget()
        self._setup_override()

        self._setup_left_toolbar_actions()

        self.file_widget = FileView()
        self._setup_leftmenu_file()

        self.samples_widget = SamplesWidget(self.config_manager.samples_settings)
        self._setup_samples_widget()

        self.run_setup_widget = RunSetupWidget(self.config_manager, dataset_manager)
        # self.run_view_widget = RunView(self.config_manager)
        self.run_info_view = RunInfoView("Run Setup", self.config_manager)
        self._setup_run_view()

        self.validation_widget = MainValidationWidget(self.dataset_manager)
        self._setup_validation_widget()

        self.indexes_widget = IndexKitToolbox(Path("config/indexes/indexes_json"))
        self._setup_left_menu_indexes()

        self.applications_widget = Applications(
            self.application_manager, self.dataset_manager
        )
        self._setup_left_menu_applications()

        self.config_widget = ConfigurationWidget(self.config_manager)
        self._setup_config()

        self.export_widget = ExportWidget(self.dataset_manager)
        self._setup_export_widget()

        self.leftmenu_stackedWidget.setFixedWidth(300)
        self.leftmenu_stackedWidget.hide()

    def disable_export_action(self):
        self.export_action.setEnabled(False)
        self.validation_widget.clear_validation_widgets()

    def set_export_action_status(self, is_enabled):
        self.export_action.setEnabled(is_enabled)

    def _setup_leftmenu_file(self):
        layout = self.leftmenu_file.layout()
        layout.addWidget(self.file_widget)

    def _setup_override(self):
        layout = self.leftmenu_override.layout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.override_widget)

    def _setup_export_widget(self):
        layout = self.main_export.layout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.export_widget)

    def _setup_validation_widget(self):
        layout = self.main_validation.layout()
        layout.addWidget(self.validation_widget)

    def _setup_config(self):
        layout = self.main_settings.layout()
        layout.addWidget(self.config_widget)

    def _setup_samples_widget(self):
        layout = self.main_data.layout()
        layout.addWidget(self.samples_widget)
        self.main_stackedWidget.setCurrentWidget(self.main_data)

    def _setup_run_view(self):
        self.leftmenu_runsetup.layout().addWidget(self.run_setup_widget)
        main_data_layout = self.main_data.layout()
        # main_data_layout.insertWidget(0, self.run_view_widget)
        main_data_layout.insertWidget(0, self.run_info_view)

    def _setup_left_menu_indexes(self):
        layout = self.leftmenu_indexes.layout()
        layout.addWidget(self.indexes_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

    def _setup_left_menu_applications(self):
        layout = self.leftmenu_apps.layout()
        layout.addWidget(self.applications_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

    def handle_left_toolbar_action(self):
        """Handle main view actions"""

        known_actions = {
            "file",
            "run",
            "apps",
            "indexes",
            "override",
            "config",
            "validate",
            "export",
        }

        main_data_actions = {"file", "run", "apps", "indexes", "override"}

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
            elif action_id == "export":
                self.main_stackedWidget.setCurrentWidget(self.main_export)
                self.export_widget.del_data_tree()
            elif action_id == "config":
                self.main_stackedWidget.setCurrentWidget(self.main_settings)

        if is_checked:
            if action_id == "file":
                self.leftmenu_stackedWidget.show()
                self.leftmenu_stackedWidget.setCurrentWidget(self.leftmenu_file)
            elif action_id == "run":
                self.leftmenu_stackedWidget.show()
                self.leftmenu_stackedWidget.setCurrentWidget(self.leftmenu_runsetup)
            elif action_id == "apps":
                self.leftmenu_stackedWidget.show()
                self.leftmenu_stackedWidget.setCurrentWidget(self.leftmenu_apps)
            elif action_id == "indexes":
                self.leftmenu_stackedWidget.show()
                self.leftmenu_stackedWidget.setCurrentWidget(self.leftmenu_indexes)
            elif action_id == "override":
                self.leftmenu_stackedWidget.show()
                self.leftmenu_stackedWidget.setCurrentWidget(self.leftmenu_override)
            else:
                return

        if not is_checked:
            self.leftmenu_stackedWidget.hide()
            self.main_stackedWidget.setCurrentWidget(self.main_data)

    def _setup_left_toolbar_actions(self):
        """Set up the tool actions for the application."""

        self.left_toolBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.left_toolBar.setFixedWidth(50)

        actions = [
            (self.file_action, "msc.files", "file", "file"),
            (self.run_action, "msc.symbol-misc", "run", "run"),
            (self.indexes_action, "mdi6.barcode", "indexes", "index"),
            (self.apps_action, "msc.symbol-method", "apps", "apps"),
            (self.override_action, "msc.sync", "override", "o-ride "),
            (self.validate_action, "msc.check-all", "validate", "valid"),
            (self.export_action, "msc.coffee", "export", "export"),
            (self.settings_action, "msc.settings-gear", "config", "config"),
        ]

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        action_group = QActionGroup(self)
        action_group.setExclusionPolicy(QActionGroup.ExclusionPolicy.ExclusiveOptional)

        for action, action_icon, action_id, action_name in actions:
            action.setCheckable(True)
            action.setChecked(False)
            action.setText(action_name)
            action.setData(action_id)
            action.setIcon(qta.icon(action_icon, options=[{"draw": "image"}]))
            action_group.addAction(action)

        self.left_toolBar.addAction(action_group.actions()[0])
        self.left_toolBar.addAction(action_group.actions()[1])
        self.left_toolBar.addAction(action_group.actions()[2])
        self.left_toolBar.addAction(action_group.actions()[3])
        self.left_toolBar.addAction(action_group.actions()[4])
        self.left_toolBar.addAction(action_group.actions()[5])
        self.left_toolBar.addAction(action_group.actions()[6])
        self.left_toolBar.addWidget(spacer)
        self.left_toolBar.addAction(action_group.actions()[7])
