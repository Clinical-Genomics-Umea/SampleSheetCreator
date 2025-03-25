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

from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal, Slot

from modules.views.config.configuration_widget import ConfigurationWidget
from modules.WaitingSpinner.spinner.spinner import WaitingSpinner
from modules.views.drawer_tools.file.file import FileView
from modules.views.drawer_tools.index.index_kit_toolbox import IndexKitToolbox
from modules.views.drawer_tools.lane.lane import LanesWidget
from modules.views.drawer_tools.override.override import OverrideCyclesWidget
from modules.views.drawer_tools.application.application_container import ApplicationContainerWidget
from modules.views.run.run_info_view import RunInfoView
from modules.views.drawer_tools.run_setup.run_setup import RunSetupWidget
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
        # self.left_toolBar.setMovable(False)
        # self.left_toolBar.setIconSize(QSize(40, 40))

        self.spinner = WaitingSpinner(self)

        # left toolbar actions
        # self.left_tool_action_group = QActionGroup(self)
        # self.action_group_main_view = QActionGroup(self)

        # self.file_action = QAction("File", self)
        # self.run_action = QAction("Run", self)
        # self.apps_action = QAction("Apps", self)
        # self.indexes_action = QAction("Indexes", self)
        # self.override_action = QAction("Override", self)
        # self.lane_action = QAction("Lane", self)
        # self.validate_action = QAction("Validate", self)
        # self.export_action = QAction("Export", self)
        # self.settings_action = QAction("Settings", self)
        #
        # self.export_action.setEnabled(False)
        # self.apps_action.setEnabled(False)
        # self.indexes_action.setEnabled(False)

        self.columns_settings_button = QPushButton("Columns")
        self.columns_settings_button.setObjectName("columns_settings")

        # self.override_widget = OverrideCyclesWidget()

        self.drawer_stackedWidget.setFixedWidth(300)
        self.drawer_stackedWidget.hide()
        self._setup()


    def _setup(self):
        self._setup_override()
        self._setup_lane()
        # self._setup_left_toolbar_actions()
        self._setup_drawer_file()
        self._setup_samples_widget()
        self._setup_run_view()
        self._setup_validation_widget()
        self._setup_drawer_indexes()
        self._setup_drawer_applications()
        self._setup_config()
        self._setup_export_widget()

    # def set_index_apps_actions_enabled(self):
    #     self.apps_action.setEnabled(True)
    #     self.indexes_action.setEnabled(True)
    #     self.validate_action.setEnabled(True)
    #     self.export_action.setEnabled(True)
    #
    # def set_lanes_action_enabled(self):
    #     self.lane_action.setEnabled(True)
    #
    # def set_export_action_disabled(self):
    #     self.export_action.setEnabled(False)
    #
    # def set_override_action_enabled(self):
    #     self.override_action.setEnabled(True)
    #
    # def update_export_action_state(self, is_enabled):
    #     self.export_action.setEnabled(is_enabled)
    #
    # def update_override_action_state(self, is_enabled):
    #     self.override_action.setEnabled(is_enabled)
    #
    # def update_validate_action_state(self, is_enabled):
    #     self.validate_action.setEnabled(is_enabled)

    def _setup_drawer_file(self):
        layout = self.drawer_file.layout()
        layout.addWidget(self._file_widget)

    def _setup_override(self):
        layout = self.drawer_override.layout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._override_widget)
        # self.update_override_action_state(False)

    def _setup_lane(self):
        layout = self.drawer_lane.layout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._lane_widget)
        # self.lane_action.setEnabled(False)

    def _setup_export_widget(self):
        layout = self.main_export.layout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._export_widget)

    def _setup_validation_widget(self):
        layout = self.main_validation.layout()
        layout.addWidget(self._validation_widget)
        # self.update_validate_action_state(False)

    def _setup_config(self):
        layout = self.main_settings.layout()
        layout.addWidget(self._config_widget)

    def _setup_samples_widget(self):
        layout = self.main_data.layout()
        layout.addWidget(self._samples_widget)
        self.main_stackedWidget.setCurrentWidget(self.main_data)

    def _setup_run_view(self):
        self.drawer_runsetup.layout().addWidget(self._run_setup_widget)
        main_data_layout = self.main_data.layout()
        main_data_layout.insertWidget(0, self._run_info_widget)

    def _setup_drawer_indexes(self):
        layout = self.drawer_indexes.layout()
        layout.addWidget(self._index_toolbox_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

    def _setup_drawer_applications(self):
        layout = self.drawer_apps.layout()
        layout.addWidget(self._applications_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

    @Slot(str, bool)
    def toolbar_action_handler(self, action_id: str, is_checked: bool):
        """Handle main view actions"""

        main_action_ids = {
            "config",
            "validate",
            "export",
        }

        drawer_action_ids = {
            "file",
            "run",
            "apps",
            "indexes",
            "override",
            "lane",
        }

        valid_action_ids = main_action_ids | drawer_action_ids

        if action_id not in valid_action_ids:
            return

        if is_checked:
            self.main_stackedWidget.setCurrentWidget(self._get_main_widget(action_id))

            if action_id in drawer_action_ids:
                self.drawer_stackedWidget.setCurrentWidget(self._get_drawer_widget(action_id))
                self.drawer_stackedWidget.show()
            else:
                self.drawer_stackedWidget.hide()
        else:
            self.main_stackedWidget.setCurrentWidget(self.main_data)
            self.drawer_stackedWidget.hide()

    def _get_main_widget(self, action_id: str) -> QWidget:
        """Return the main widget associated with the given action ID"""

        if action_id == "validate":
            return self.main_validation
        elif action_id == "export":
            return self.main_export
        elif action_id == "config":
            return self.main_settings
        else:
            return self.main_data

    def _get_drawer_widget(self, action_id: str) -> QWidget:
        """Return the drawer widget associated with the given action ID"""

        if action_id == "file":
            return self.drawer_file
        elif action_id == "run":
            return self.drawer_runsetup
        elif action_id == "apps":
            return self.drawer_apps
        elif action_id == "indexes":
            return self.drawer_indexes
        elif action_id == "override":
            return self.drawer_override
        elif action_id == "lane":
            return self.drawer_lane

    # def _setup_left_toolbar_actions(self):
    #     """Set up the tool actions for the application."""
    #
    #     self.left_toolBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
    #     self.left_toolBar.setFixedWidth(50)
    #
    #     actions = [
    #         (self.file_action, "msc.files", "file", "file"),
    #         (self.run_action, "msc.symbol-misc", "run", "run"),
    #         (self.indexes_action, "mdi6.barcode", "indexes", "index"),
    #         (self.apps_action, "msc.symbol-method", "apps", "apps"),
    #         (self.override_action, "msc.sync", "override", "o-ride "),
    #         (self.lane_action, "mdi6.road", "lane", "lane"),
    #         (self.validate_action, "msc.check-all", "validate", "valid"),
    #         (self.export_action, "msc.coffee", "export", "export"),
    #         (self.settings_action, "msc.settings-gear", "config", "config"),
    #     ]
    #
    #     spacer = QWidget()
    #     spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    #
    #     action_group = QActionGroup(self)
    #     action_group.setExclusionPolicy(QActionGroup.ExclusionPolicy.ExclusiveOptional)
    #
    #     for action, action_icon, action_id, action_name in actions:
    #         action.setCheckable(True)
    #         action.setChecked(False)
    #         action.setText(action_name)
    #         action.setData(action_id)
    #         action.setIcon(qta.icon(action_icon, options=[{"draw": "image"}]))
    #         action_group.addAction(action)
    #
    #     self.left_toolBar.addAction(action_group.actions()[0])
    #     self.left_toolBar.addAction(action_group.actions()[1])
    #     self.left_toolBar.addAction(action_group.actions()[2])
    #     self.left_toolBar.addAction(action_group.actions()[3])
    #     self.left_toolBar.addAction(action_group.actions()[4])
    #     self.left_toolBar.addAction(action_group.actions()[5])
    #     self.left_toolBar.addAction(action_group.actions()[6])
    #     self.left_toolBar.addAction(action_group.actions()[7])
    #     self.left_toolBar.addWidget(spacer)
    #     self.left_toolBar.addAction(action_group.actions()[8])
