#! python
# -*- coding: utf-8 -*-
import sys

from PySide6.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QWidget,
    QPushButton,
)

from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal, Slot

from modules.views.config.configuration_widget import ConfigurationWidget
from modules.views.file.file import FileView
from modules.views.index.index_kit_toolbox import IndexKitToolbox
from modules.views.lane.lane import LanesWidget
from modules.views.override.override import OverrideCyclesWidget
from modules.views.application.application_container import ApplicationContainerWidget
from modules.views.log.log_widget import LogWidget
from modules.views.run_info.run_info_view import RunInfoView
from modules.views.run_setup.run_setup import RunSetupWidget
from modules.views.export.export import ExportWidget
from modules.views.validation.main_validation_widget import (
    MainValidationWidget,
)

from modules.views.sample.sample_view import SamplesWidget
from modules.views.ui.mw import Ui_MainWindow
import qtawesome as qta

sys.argv += ["-platform", "windows:darkmode=2"]
__author__ = "Pär Larsson"
__version__ = "2.0.0.a3"

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
        log_widget: LogWidget
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
        self._log_widget = log_widget

        self.setMinimumWidth(1000)

        self.columns_settings_button = QPushButton("Columns")
        self.columns_settings_button.setObjectName("columns_settings")

        self.drawer_stackedWidget.setFixedWidth(300)
        self.drawer_stackedWidget.hide()
        self._setup()


    def _setup(self):
        self._setup_override()
        self._setup_lane()
        self._setup_drawer_file()
        self._setup_samples_widget()
        self._setup_run_view()
        self._setup_validation_widget()
        self._setup_drawer_indexes()
        self._setup_drawer_applications()
        self._setup_config()
        self._setup_export_widget()
        self._setup_log_widget()

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

    def _setup_log_widget(self):
        layout = self.main_log.layout()
        layout.addWidget(self._log_widget)

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
            "log",
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
        elif action_id == "log":
            return self.main_log
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
