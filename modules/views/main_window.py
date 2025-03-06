#! python
# -*- coding: utf-8 -*-
import sys

from PySide6.QtWidgets import (
    QMainWindow,
    QSizePolicy,
    QFileDialog,
    QWidget,
    QPushButton,
)

from PySide6.QtGui import QAction, QActionGroup, QIcon
from PySide6.QtCore import Qt, QSize, Signal

from modules.models.application.application_manager import ApplicationManager
from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.dataset.dataset_manager import DataSetManager
from modules.models.indexes.index_kit_manager import IndexKitManager
from modules.views.config.configuration_widget import ConfigurationWidget
from modules.WaitingSpinner.spinner.spinner import WaitingSpinner
from modules.views.leftmenu.file.file import FileView
from modules.views.leftmenu.index.index_kit_toolbox import IndexKitToolbox
from modules.views.leftmenu.lane.lane import LanesWidget
from modules.views.leftmenu.override.override import OverrideCyclesWidget
from modules.views.leftmenu.application.application_container import ApplicationContainerWidget
from modules.views.run.run_info_view import RunInfoView
from modules.views.leftmenu.run_setup.run_setup import RunSetupWidget
from modules.views.export.export import ExportWidget
from modules.views.validation.main_validation_widget import (
    MainValidationWidget,
)

from modules.views.sample.sample_view import SamplesWidget
from modules.views.ui.mw import Ui_MainWindow
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
        # config_manager: ConfigurationManager,
        # application_manager: ApplicationManager,
        # dataset_manager: DataSetManager,
        # index_kit_manager: IndexKitManager
        override_widget: OverrideCyclesWidget,
        lane_widget: LanesWidget,
        file_widget: FileView,
        samples_widget: SamplesWidget,
        run_setup_widget: RunSetupWidget,
        run_info_widget: RunInfoView,
        validation_widget: MainValidationWidget,
        index_toolbox_widget: IndexKitToolbox,
        applications_widget: ApplicationContainerWidget,
        config_widget: ConfigurationWidget,
        export_widget: ExportWidget,
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

        self._override_widget = override_widget
        self._lane_widget = lane_widget
        self._file_widget = file_widget
        self._samples_widget = samples_widget
        self._run_setup_widget = run_setup_widget
        self._run_info_widget = run_info_widget
        self._validation_widget = validation_widget
        self._index_toolbox_widget = index_toolbox_widget
        self._applications_widget = applications_widget
        self._config_widget = config_widget
        self._export_widget = export_widget

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
        self.lane_action = QAction("Lane", self)
        self.validate_action = QAction("Validate", self)
        self.export_action = QAction("Export", self)
        self.settings_action = QAction("Settings", self)

        self.export_action.setEnabled(False)
        self.apps_action.setEnabled(False)
        self.indexes_action.setEnabled(False)

        self.columns_settings_button = QPushButton("Columns")
        self.columns_settings_button.setObjectName("columns_settings")

        # self.override_widget = OverrideCyclesWidget()

        self.leftmenu_stackedWidget.setFixedWidth(300)
        self.leftmenu_stackedWidget.hide()
        self._setup()

    def _setup(self):
        self._setup_override()
        self._setup_lane()
        self._setup_left_toolbar_actions()
        self._setup_leftmenu_file()
        self._setup_samples_widget()
        self._setup_run_view()
        self._setup_validation_widget()
        self._setup_left_menu_indexes()
        self._setup_left_menu_applications()
        self._setup_config()
        self._setup_export_widget()

    def set_index_apps_actions_enabled(self):
        self.apps_action.setEnabled(True)
        self.indexes_action.setEnabled(True)
        self.validate_action.setEnabled(True)
        self.export_action.setEnabled(True)

    def set_lanes_action_enabled(self):
        self.lane_action.setEnabled(True)

    def set_export_action_disabled(self):
        self.export_action.setEnabled(False)

    def set_override_action_enabled(self):
        self.override_action.setEnabled(True)

    def update_export_action_state(self, is_enabled):
        self.export_action.setEnabled(is_enabled)

    def update_override_action_state(self, is_enabled):
        self.override_action.setEnabled(is_enabled)

    def update_validate_action_state(self, is_enabled):
        self.validate_action.setEnabled(is_enabled)

    def _setup_leftmenu_file(self):
        layout = self.leftmenu_file.layout()
        layout.addWidget(self._file_widget)

    def _setup_override(self):
        layout = self.leftmenu_override.layout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._override_widget)
        self.update_override_action_state(False)

    def _setup_lane(self):
        layout = self.leftmenu_lane.layout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._lane_widget)
        self.lane_action.setEnabled(False)

    def _setup_export_widget(self):
        layout = self.main_export.layout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._export_widget)

    def _setup_validation_widget(self):
        layout = self.main_validation.layout()
        layout.addWidget(self._validation_widget)
        self.update_validate_action_state(False)

    def _setup_config(self):
        layout = self.main_settings.layout()
        layout.addWidget(self._config_widget)

    def _setup_samples_widget(self):
        layout = self.main_data.layout()
        layout.addWidget(self._samples_widget)
        self.main_stackedWidget.setCurrentWidget(self.main_data)

    def _setup_run_view(self):
        self.leftmenu_runsetup.layout().addWidget(self._run_setup_widget)
        main_data_layout = self.main_data.layout()
        main_data_layout.insertWidget(0, self._run_info_widget)

    def _setup_left_menu_indexes(self):
        layout = self.leftmenu_indexes.layout()
        layout.addWidget(self._index_toolbox_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

    def _setup_left_menu_applications(self):
        layout = self.leftmenu_apps.layout()
        layout.addWidget(self._applications_widget)
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
            "lane",
            "config",
            "validate",
            "export",
        }

        main_data_actions = {"file", "run", "apps", "indexes", "override", "lane"}

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
            elif action_id == "lane":
                self.leftmenu_stackedWidget.show()
                self.leftmenu_stackedWidget.setCurrentWidget(self.leftmenu_lane)
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
            (self.lane_action, "mdi6.road", "lane", "lane"),
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
        self.left_toolBar.addAction(action_group.actions()[7])
        self.left_toolBar.addWidget(spacer)
        self.left_toolBar.addAction(action_group.actions()[8])
