from PySide6.QtCore import QObject

from models.application.application import ApplicationManager
from models.configuration.configuration import ConfigurationManager
from models.dataset.dataset import DataSetManager
from models.rundata.rundata_model import RunDataModel
from models.sample.sample_model import SampleModel, CustomProxyModel
from models.validation.compatibility import DataCompatibilityChecker
from models.validation.dataset_validation import MainValidator
from views.notify.notify import StatusBar
from views.main_window import MainWindow


class MainController(QObject):
    def __init__(self):
        """
        Initialize main controller, setting up models, views, and connections.
        """
        super().__init__()

        self._config_manager = ConfigurationManager()
        self._application_manager = ApplicationManager(self._config_manager)
        self._status_bar = StatusBar()

        self._sample_model = SampleModel(self._config_manager.samples_settings)
        self._sample_proxy_model = CustomProxyModel()
        self._sample_proxy_model.setSourceModel(self._sample_model)

        self._run_data_model = RunDataModel(self._config_manager)

        self._dataset_manager = DataSetManager(
            self._sample_model,
            self._application_manager,
            self._run_data_model,
        )

        self._main_window = MainWindow(
            self._config_manager,
            self._application_manager,
            self._dataset_manager,
            self._status_bar,
        )
        self._main_window.samples_widget.set_model(self._sample_proxy_model)

        self._main_validator = MainValidator(
            self._sample_model,
            self._config_manager,
            self._dataset_manager,
            self._application_manager,
        )
        self._compatibility_checker = DataCompatibilityChecker(
            self._dataset_manager, self._application_manager
        )

        self._connect_signals()

    def _connect_signals(self):
        """
        Connect UI signals to controller slots.
        """
        self._connect_notifications()
        self._connect_validation_signals()
        self._connect_left_tool_action_signals()
        self._connect_run_signals()
        self._connect_file_signals()
        self._connect_override_pattern_signals()
        self._connect_application_signal()
        self._connect_sample_model_signals()
        self._connect_drop_paste_signals()
        self._connect_lane_signals()

    def _connect_notifications(self):
        self._main_window.samples_widget.selection_data.connect(
            self._status_bar.display_selection_data
        )
        self._compatibility_checker.dropped_not_allowed.connect(
            self._status_bar.display_error_msg
        )
        self._compatibility_checker.dropped_not_allowed_flash.connect(
            self._main_window.samples_widget.flash_table
        )

    def _connect_sample_model_signals(self):
        self._sample_model.dataChanged.connect(
            self._main_window.set_export_action_disabled
        )

    def _connect_application_signal(self):
        self._main_window.applications_widget.add_signal.connect(
            self._compatibility_checker.app_checker
        )
        self._compatibility_checker.app_allowed.connect(
            self._main_window.samples_widget.sample_view.set_application
        )
        self._main_window.applications_widget.remove_signal.connect(
            self._main_window.samples_widget.sample_view.remove_application
        )

        self._compatibility_checker.app_not_allowed.connect(
            self._status_bar.display_error_msg
        )

    def _connect_drop_paste_signals(self):
        self._sample_model.dropped_data.connect(
            self._compatibility_checker.dropped_checker
        )
        self._compatibility_checker.dropped_allowed.connect(
            self._sample_model.set_dropped_data
        )

    def _connect_file_signals(self):
        self._main_window.file_widget.new_samplesheet_btn.clicked.connect(
            self._sample_model.set_empty_strings
        )

    def _connect_left_tool_action_signals(self):
        """Connect UI signals to controller slots"""
        # Connect menu actions to handler

        action_handler = self._main_window.handle_left_toolbar_action

        actions = [
            self._main_window.file_action,
            self._main_window.run_action,
            self._main_window.apps_action,
            self._main_window.indexes_action,
            self._main_window.override_action,
            self._main_window.lane_action,
            self._main_window.settings_action,
            self._main_window.validate_action,
            self._main_window.export_action,
        ]

        for action in actions:
            action.triggered.connect(action_handler)

    def _connect_validation_signals(self):
        """Connect UI signals to validation slots"""

        self._main_validator.pre_validator.data_ready.connect(
            self._main_window.validation_widget.pre_validation_widget.populate
        )
        self._main_validator.index_distance_validator.data_ready.connect(
            self._main_window.validation_widget.main_index_validation_widget.populate
        )
        self._main_validator.color_balance_validator.data_ready.connect(
            self._main_window.validation_widget.main_color_balance_validation_widget.populate
        )
        self._main_validator.dataset_validator.data_ready.connect(
            self._main_window.validation_widget.dataset_validation_widget.populate
        )
        self._main_window.validation_widget.validate_button.clicked.connect(
            self._main_validator.validate
        )
        self._main_validator.clear_validator_widgets.connect(
            self._main_window.validation_widget.clear_validation_widgets
        )
        self._main_validator.prevalidator_status.connect(
            self._main_window.update_export_action_state
        )

    def _connect_override_pattern_signals(self):
        self._main_window.samples_widget.sample_view.override_patterns_ready.connect(
            self._main_window.override_widget.set_override_pattern
        )
        self._main_window.override_widget.get_selected_overrides_btn.clicked.connect(
            self._main_window.samples_widget.sample_view.get_override_pattern
        )
        self._main_window.override_widget.custom_override_pattern_ready.connect(
            self._compatibility_checker.override_cycles_checker
        )
        self._compatibility_checker.override_pattern_invalid.connect(
            self._main_window.override_widget.on_invalid_result
        )

    def _connect_run_signals(self):
        self._config_manager.users_changed.connect(
            self._main_window.run_setup_widget.populate_investigators
        )
        self._config_manager.run_data_error.connect(
            self._main_window.run_setup_widget.show_error
        )
        self._main_window.run_setup_widget.setup_commited.connect(
            self._run_data_model.set_run_data
        )
        self._run_data_model.run_data_ready.connect(
            self._main_window.run_info_view.set_data
        )
        self._run_data_model.run_data_changed.connect(
            self._main_window.set_override_action_enabled
        )
        self._run_data_model.run_data_changed.connect(
            self._main_window.lane_widget.set_lanes
        )
        self._run_data_model.run_data_changed.connect(
            self._main_window.set_lanes_action_enabled
        )

    def _connect_lane_signals(self):
        self._main_window.lane_widget.lanes_ready.connect(
            self._main_window.samples_widget.sample_view.set_lanes
        )


# controllers/settings_controller.py
class SettingsController(QObject):
    def __init__(self, main_controller):
        super().__init__()
        self.main_controller = main_controller
        self.settings_dialog = None

    # def show_settings(self):
    #     """Create and show settings dialog"""
    #     if not self.settings_dialog:
    #         from ..views.dialogs.settings_dialog import SettingsDialog
    #
    #         self.settings_dialog = SettingsDialog()
    #         self.setup_settings_connections()
    #     self.settings_dialog.show()

    # def setup_settings_connections(self):
    #     """Connect settings dialog signals"""
    #     self.settings_dialog.settings_changed.connect(self.apply_settings)
    #
    # @Slot(dict)
    # def apply_settings(self, new_settings):
    #     """Apply new settings and update application state"""
    #     try:
    #         # Update application settings
    #         self.main_controller.data_model.update_settings(new_settings)
    #         # Refresh main window with new settings
    #         self.main_controller.main_window.apply_settings(new_settings)
    #     except Exception as e:
    #         self.logger.error(f"Error applying settings: {e}")
    #         self.settings_dialog.show_error("Failed to apply settings")
