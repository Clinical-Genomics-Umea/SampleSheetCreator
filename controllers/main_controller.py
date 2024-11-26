from PySide6.QtCore import QObject

from models.configuration import ConfigurationManager
from models.make_export import MakeJson
from models.samplesheet_model import SampleSheetModel, CustomProxyModel
from models.validation import MainValidator
from views.main_window import MainWindow


class MainController(QObject):
    def __init__(self):
        super().__init__()

        self.cfg_mgr = ConfigurationManager()

        # Initialize main window with sample settings
        self.main_window = MainWindow(self.cfg_mgr)

        # Set up sample model and proxy model
        self.sample_model = SampleSheetModel(self.cfg_mgr.samples_settings)
        self.sample_proxy_model = None
        self.setup_samplesheet_model()

        # Initialize main validator with necessary components
        self.main_validator = MainValidator(self.sample_model, self.cfg_mgr)

        self.make_json = MakeJson(self.sample_model, self.cfg_mgr)

        # Set up connections
        self.setup_validation_connections()
        self.setup_left_tool_action_connections()

        # Connect profile data signal
        self.main_window.application_profiles_widget.profile_mgr.profile_data.connect(
            self.main_window.samples_widget.sample_view.set_profile_data
        )
        self.setup_run_connections()
        self.setup_file_connections()

        self.setup_make_connections()

    def setup_make_connections(self):
        self.make_json.data_ready.connect(self.main_window.make_widget.populate)
        self.main_window.make_widget.mk_export.clicked.connect(self.make_json.mk_json)

    def setup_samplesheet_model(self):
        # Set up sample model and proxy model
        self.sample_proxy_model = CustomProxyModel()
        self.sample_proxy_model.setSourceModel(self.sample_model)

        # Configure sample widget
        self.main_window.samples_widget.set_model(self.sample_proxy_model)

    def setup_left_tool_action_connections(self):
        """Connect UI signals to controller slots"""
        # Connect menu actions to handler

        action_handler = self.main_window.handle_left_toolbar_action

        actions = [
            self.main_window.file_action,
            self.main_window.run_action,
            self.main_window.profiles_action,
            self.main_window.indexes_action,
            self.main_window.override_action,
            self.main_window.settings_action,
            self.main_window.validate_action,
            self.main_window.make_action,
        ]

        for action in actions:
            action.triggered.connect(action_handler)

    def setup_validation_connections(self):
        """Connect UI signals to validation slots"""

        self.main_validator.pre_validator.data_ready.connect(
            self.main_window.validation_widget.pre_validation_widget.populate
        )
        self.main_validator.index_distance_validator.data_ready.connect(
            self.main_window.validation_widget.main_index_validation_widget.populate
        )
        self.main_validator.color_balance_validator.data_ready.connect(
            self.main_window.validation_widget.main_color_balance_validation_widget.populate
        )
        self.main_window.validation_widget.validate_button.clicked.connect(
            self.main_validator.validate
        )

    def setup_run_connections(self):
        self.main_window.run_setup_widget.setup_commited.connect(
            self.cfg_mgr.set_run_data
        )
        self.cfg_mgr.run_setup_changed.connect(
            self.main_window.run_view_widget.set_data
        )
        self.cfg_mgr.users_changed.connect(
            self.main_window.run_setup_widget.populate_investigators
        )
        self.cfg_mgr.run_data_error.connect(
            self.main_window.run_setup_widget.show_error
        )

    def setup_file_connections(self):
        self.main_window.new_samplesheet_pushButton.clicked.connect(
            self.setup_samplesheet_model
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
