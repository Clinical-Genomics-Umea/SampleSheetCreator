from PySide6.QtCore import QObject

from modules.models.application.application_manager import ApplicationManager
from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.dataset.dataset_manager import DataSetManager
from modules.models.indexes.index_kit_manager import IndexKitManager
from modules.models.rundata.rundata_model import RunDataModel
from modules.models.sample.sample_model import SampleModel, CustomProxyModel
from modules.models.validation.data_compatibility_checker import DataCompatibilityChecker
from modules.models.validation.main_validator import MainValidator
from modules.views.notify.notify import StatusBar
from modules.views.main_window import MainWindow


class MainController(QObject):
    def __init__(self):
        """
        Initialize main controller, setting up models, views, and connections.
        """
        super().__init__()

        self._config_manager = ConfigurationManager()
        self._application_manager = ApplicationManager(self._config_manager)
        self._status_bar = StatusBar()

        self._index_kit_manager = IndexKitManager(
            self._config_manager.index_kits_path,
            self._config_manager.index_kit_schema_path,
        )

        self._sample_model = SampleModel(self._config_manager.samples_settings)
        self._sample_proxy_model = CustomProxyModel()
        self._sample_proxy_model.setSourceModel(self._sample_model)

        self._run_data_model = RunDataModel(self._config_manager)

        self._dataset_manager = DataSetManager(
            self._sample_model,
            self._application_manager,
            self._run_data_model,
        )

        self.main_window = MainWindow(
            self._config_manager,
            self._application_manager,
            self._dataset_manager,
            self._index_kit_manager,
            self._status_bar,
        )
        self.main_window.samples_widget.set_model(self._sample_proxy_model)

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
        self.main_window.samples_widget.selection_data.connect(
            self._status_bar.display_selection_data
        )
        self._compatibility_checker.dropped_not_allowed.connect(
            self._status_bar.display_error_msg
        )
        self._compatibility_checker.dropped_not_allowed_flash.connect(
            self.main_window.samples_widget.flash_table
        )

    def _connect_sample_model_signals(self):
        self._sample_model.dataChanged.connect(
            self.main_window.set_export_action_disabled
        )

    def _connect_application_signal(self):
        self.main_window.applications_widget.add_signal.connect(
            self._compatibility_checker.app_checker
        )
        self._compatibility_checker.app_allowed.connect(
            self.main_window.samples_widget.sample_view.set_application
        )
        self.main_window.applications_widget.remove_signal.connect(
            self.main_window.samples_widget.sample_view.remove_application
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
        self.main_window.file_widget.new_samplesheet_btn.clicked.connect(
            self._sample_model.set_empty_strings
        )

    def _connect_left_tool_action_signals(self):
        """Connect UI signals to controller slots"""
        # Connect menu actions to handler

        action_handler = self.main_window.handle_left_toolbar_action

        actions = [
            self.main_window.file_action,
            self.main_window.run_action,
            self.main_window.apps_action,
            self.main_window.indexes_action,
            self.main_window.override_action,
            self.main_window.lane_action,
            self.main_window.settings_action,
            self.main_window.validate_action,
            self.main_window.export_action,
        ]

        for action in actions:
            action.triggered.connect(action_handler)

    def _connect_validation_signals(self):
        """Connect UI signals to validation slots"""

        self._main_validator.pre_validator.data_ready.connect(
            self.main_window.validation_widget.pre_validation_widget.populate
        )
        self._main_validator.index_distance_validator.data_ready.connect(
            self.main_window.validation_widget.main_index_validation_widget.populate
        )
        self._main_validator.color_balance_validator.data_ready.connect(
            self.main_window.validation_widget.color_balance_validation_container_widget.populate
        )
        self._main_validator.dataset_validator.data_ready.connect(
            self.main_window.validation_widget.dataset_validation_widget.populate
        )
        self.main_window.validation_widget.validate_button.clicked.connect(
            self._main_validator.validate
        )
        self._main_validator.clear_validator_widgets.connect(
            self.main_window.validation_widget.clear_validation_widgets
        )
        self._main_validator.prevalidator_status.connect(
            self.main_window.update_export_action_state
        )

    def _connect_override_pattern_signals(self):
        self.main_window.samples_widget.sample_view.override_patterns_ready.connect(
            self.main_window.override_widget.set_override_pattern
        )
        self.main_window.override_widget.get_selected_overrides_btn.clicked.connect(
            self.main_window.samples_widget.sample_view.get_override_pattern
        )
        self.main_window.override_widget.custom_override_pattern_ready.connect(
            self._compatibility_checker.override_cycles_checker
        )
        self._compatibility_checker.override_pattern_invalid.connect(
            self.main_window.override_widget.on_invalid_result
        )

    def _connect_run_signals(self):
        self._config_manager.users_changed.connect(
            self.main_window.run_setup_widget.populate_investigators
        )
        self._config_manager.run_data_error.connect(
            self.main_window.run_setup_widget.show_error
        )
        self.main_window.run_setup_widget.setup_commited.connect(
            self._run_data_model.set_run_data
        )
        self._run_data_model.run_data_ready.connect(
            self.main_window.run_info_view.set_data
        )
        self._run_data_model.run_data_changed.connect(
            self.main_window.set_override_action_enabled
        )
        self._run_data_model.run_data_changed.connect(
            self.main_window.lane_widget.set_lanes
        )
        self._run_data_model.run_data_changed.connect(
            self.main_window.set_lanes_action_enabled
        )
        self._run_data_model.run_data_changed.connect(
            self.main_window.set_index_apps_actions_enabled
        )
        self._run_data_model.index_lens_ready.connect(
            self.main_window.index_toolbox_widget.set_index_kit_status
        )

    def _connect_lane_signals(self):
        self.main_window.lane_widget.lanes_ready.connect(
            self.main_window.samples_widget.sample_view.set_lanes
        )

