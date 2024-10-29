from PySide6.QtCore import QObject

from models.samplesheet_model import SampleSheetModel, CustomProxyModel
from models.validation_models import MainValidator
from views.main_window import MainWindow
from utils.utils import read_yaml_file


class MainController(QObject):
    def __init__(self):
        super().__init__()

        sample_settings = read_yaml_file("config/sample_settings.yaml")
        validation_settings = read_yaml_file(
            "config/validation/validation_settings.yaml"
        )

        self.main_window = MainWindow(sample_settings)

        self.samples_model = SampleSheetModel(sample_settings)
        self.samples_proxy_model = CustomProxyModel()
        self.samples_proxy_model.setSourceModel(self.samples_model)

        self.main_window.sample_widget.set_model(self.samples_proxy_model)
        self.main_window.sample_widget_setup()

        # Connect signals from the view to controller slots

        self.main_validator = MainValidator(
            self.samples_model, self.main_window.run_info_widget, validation_settings
        )
        self.setup_validation_conns()

        self.setup_left_tool_action_conns()

        self.main_window.application_profiles_widget.profile_mgr.profile_data.connect(
            self.main_window.sample_widget.sample_view.set_profile_data
        )

    def setup_left_tool_action_conns(self):
        """Connect UI signals to controller slots"""
        # Connect menu actions

        handler = self.main_window.handle_left_toolbar_action

        self.main_window.file_action.triggered.connect(handler)
        self.main_window.run_action.triggered.connect(handler)
        self.main_window.profiles_action.triggered.connect(handler)
        self.main_window.indexes_action.triggered.connect(handler)
        self.main_window.settings_action.triggered.connect(handler)
        self.main_window.validate_action.triggered.connect(handler)
        self.main_window.make_action.triggered.connect(handler)

        # self.main_window.run_validate.connect(self.validate)

    def setup_validation_conns(self):

        self.main_validator.pre_validator.data_ready.connect(
            self.main_window.validation_widget.pre_validation_widget.populate
        )
        self.main_validator.index_distance_validator.data_ready.connect(
            self.main_window.validation_widget.index_validation_widget.populate
        )
        self.main_validator.color_balance_validator.data_ready.connect(
            self.main_window.validation_widget.color_balance_validation_widget.populate
        )
        self.main_window.validation_widget.validate_button.clicked.connect(
            self.main_validator.validate
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
