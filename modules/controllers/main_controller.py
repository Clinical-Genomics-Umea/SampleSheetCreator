import logging
from pathlib import Path

from PySide6.QtCore import QObject, Qt

from modules.models.application.application_manager import ApplicationManager
from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.dataset.dataset_manager import DataSetManager
from modules.models.datastate.datastate_model import DataStateModel
from modules.models.indexes.index_kit_manager import IndexKitManager
from modules.models.logging.statusbar_handler import StatusBarLogHandler
from modules.models.methods.method_manager import MethodManager
from modules.models.override_cycles.OverrideCyclesModel import OverrideCyclesModel
from modules.models.rundata.rundata_model import RunDataModel
from modules.models.sample.sample_model import SampleModel, CustomProxyModel
from modules.models.validation.color_balance_validator import ColorBalanceValidator
from modules.models.validation.data_compatibility_checker import DataCompatibilityTest
from modules.models.validation.dataset_validator import DataSetValidator
from modules.models.validation.index_distance_matrix_generator import IndexDistanceValidator
from modules.models.validation.main_validator import MainValidator
from modules.models.validation.prevalidator import PreValidator
from modules.models.worksheet.import_worksheet import WorkSheetImporter
from modules.views.config.configuration_widget import ConfigurationWidget
from modules.views.export.export import ExportWidget
from modules.views.drawer_tools.application.application_container import ApplicationContainerWidget
from modules.views.drawer_tools.file.file import FileView
from modules.views.drawer_tools.index.index_kit_toolbox import IndexKitToolbox
from modules.views.drawer_tools.lane.lane import LanesWidget
from modules.views.drawer_tools.override.override import OverrideCyclesWidget
from modules.views.drawer_tools.run_setup.run_setup import RunSetupWidget
from modules.views.run.run_info_view import RunInfoView
from modules.views.sample.sample_view import SamplesWidget
from modules.views.status.status import StatusBar
from modules.views.main_window import MainWindow
from modules.views.toolbar.toolbar import ToolBar
from modules.views.validation.color_balance_widget import ColorBalanceValidationWidget
from modules.views.validation.dataset_validation_widget import DataSetValidationWidget
from modules.views.validation.index_distance_validation_widget import IndexDistanceValidationWidget
from modules.views.validation.main_validation_widget import MainValidationWidget
from modules.views.validation.prevalidation_widget import PreValidationWidget


class MainController(QObject):
    def __init__(self):
        """
        Initialize main controller, setting up models, views, and connections.
        """
        super().__init__()

        self._config_manager = ConfigurationManager()
        self._logger = logging.getLogger(__name__)
        self._status_bar = StatusBar()
        self._toolbar = ToolBar()

        self._file_handler = logging.FileHandler(Path("log/log.txt"))
        self._status_handler = StatusBarLogHandler(self._status_bar)
        self._logger.addHandler(self._file_handler)
        self._logger.addHandler(self._status_handler)

        self._application_manager = ApplicationManager(self._config_manager)

        self._index_kit_manager = IndexKitManager(
            self._config_manager, self._logger
        )

        self._sample_model = SampleModel(self._config_manager.samples_settings)
        self._sample_proxy_model = CustomProxyModel()
        self._sample_proxy_model.setSourceModel(self._sample_model)

        self._rundata_model = RunDataModel(self._config_manager)

        self._dataset_manager = DataSetManager(
            self._sample_model,
            self._application_manager,
            self._rundata_model,
        )

        self._datastate_model = DataStateModel(
            self._sample_model,
            self._rundata_model,
            self._application_manager,
            self._logger
        )

        self._override_cycles_model = OverrideCyclesModel(
            self._datastate_model, self._dataset_manager, self._logger
        )

        # validation widgets

        self._prevalidation_widget = PreValidationWidget()
        self._dataset_validation_widget = DataSetValidationWidget()
        self._index_distance_validation_widget = IndexDistanceValidationWidget()
        self._color_balance_validation_widget = ColorBalanceValidationWidget(self._dataset_manager)


        # validation models

        self._prevalidator = PreValidator(
            self._sample_model,
            self._config_manager,
            self._application_manager,
            self._dataset_manager,
            self._prevalidation_widget,
            self._logger
        )

        self._dataset_validator = DataSetValidator(
            self._sample_model,
            self._config_manager,
            self._dataset_manager,
            self._dataset_validation_widget,
            self._logger
        )

        self._index_distance_validator = IndexDistanceValidator(
            self._sample_model,
            self._dataset_manager,
            self._index_distance_validation_widget,
            self._logger
        )

        self._color_balance_validator = ColorBalanceValidator(
            self._sample_model,
            self._dataset_manager,
            self._color_balance_validation_widget,
            self._logger
        )

        self._main_validator = MainValidator(
            self._prevalidator,
            self._dataset_validator,
            self._index_distance_validator,
            self._color_balance_validator,
            self._dataset_manager,
            self._logger
        )


        # widgets

        ## validation widgets

        self._validation_widget = MainValidationWidget(self._prevalidation_widget,
                                                       self._dataset_validation_widget,
                                                       self._index_distance_validation_widget,
                                                       self._color_balance_validation_widget,
                                                       self._main_validator)

        self._override_widget = OverrideCyclesWidget(self._override_cycles_model)
        self._lane_widget = LanesWidget(self._dataset_manager)
        self._file_widget = FileView()
        self._samples_widget = SamplesWidget(self._config_manager.samples_settings)
        self._run_setup_widget = RunSetupWidget(self._config_manager, self._dataset_manager)
        self._run_info_widget = RunInfoView(self._config_manager)
        self._index_toolbox_widget = IndexKitToolbox(self._index_kit_manager)
        self._applications_widget = ApplicationContainerWidget(
            self._application_manager, self._dataset_manager
        )
        self._config_widget = ConfigurationWidget(self._config_manager)
        self._export_widget = ExportWidget(self._dataset_manager, self._config_manager)

        self._samples_widget.set_model(self._sample_proxy_model)

        self.main_window = MainWindow(
            self._override_widget,
            self._lane_widget,
            self._file_widget,
            self._samples_widget,
            self._run_setup_widget,
            self._run_info_widget,
            self._validation_widget,
            self._index_toolbox_widget,
            self._applications_widget,
            self._config_widget,
            self._export_widget,
        )
        self.main_window.setStatusBar(self._status_bar)
        self.main_window.addToolBar(Qt.LeftToolBarArea, self._toolbar)

        # self.main_window.samples_widget.set_model(self._sample_proxy_model)

        self._compatibility_checker = DataCompatibilityTest(
            self._datastate_model,
            self._dataset_manager,
            self._logger
        )

        self._method_manager = MethodManager(self._config_manager, self._application_manager, self._logger)
        self._worksheet_importer = WorkSheetImporter(self._sample_model, self._method_manager,
                                                     self._application_manager, self._logger)

        self._connect_signals()

    def _connect_signals(self):
        """
        Connect UI signals to controller slots.
        """
        self._connect_notifications()
        self._connect_validation_signals()
        self._connect_toolbar_signal()
        self._connect_run_signals()
        self._connect_file_signals()
        self._connect_override_pattern_signals()
        self._connect_application_signal()
        self._connect_sample_model_signals()
        self._connect_drop_paste_signals()
        self._connect_lane_signals()

    def _connect_notifications(self):
        self._samples_widget.selection_data.connect(
            self._status_bar.display_selection_data
        )

    def _connect_sample_model_signals(self):
        self._datastate_model.validated_changed.connect(
            self.main_window.set_export_action_disabled
        )

    def _connect_application_signal(self):
        self._applications_widget.add_signal.connect(
            self._compatibility_checker.app_check
        )
        self._compatibility_checker.app_ok.connect(
            self._samples_widget.sample_view.set_application
        )
        self._applications_widget.remove_signal.connect(
            self._samples_widget.sample_view.remove_application
        )


    def _connect_drop_paste_signals(self):
        self._sample_model.dropped_data.connect(
            self._compatibility_checker.drop_check
        )
        self._compatibility_checker.drop_ok.connect(
            self._sample_model.set_dropped_data
        )

    def _connect_file_signals(self):
        # self._file_widget.worksheet_file.connect(
        #     self._sample_model.set_empty_strings
        # )
        self._file_widget.worksheet_filepath_ready.connect(
            self._worksheet_importer.load_worksheet
        )


    def _connect_toolbar_signal(self):
        """Connect UI signals to controller slots"""
        # Connect toolbar signal to handler
        self._toolbar.action_triggered.connect(self.main_window.toolbar_action_handler)

    def _connect_validation_signals(self):
        """Connect UI signals to validation slots"""

        self._prevalidator.data_ready.connect(
            self._prevalidation_widget.populate
        )
        # self._index_distance_validator.data_ready.connect(
        #     self._index_distance_validation_widget.populate
        # )
        # self._color_balance_validator.data_ready.connect(
        #     self._color_balance_validation_widget.populate
        # )
        # self._dataset_validator.data_ready.connect(
        #     self._dataset_validation_widget.populate
        # )
        self._validation_widget.validate_button.clicked.connect(
            self._main_validator.validate
        )
        self._main_validator.clear_validator_widgets.connect(
            self._validation_widget.clear_validation_widgets
        )
        # self._main_validator.pre_validator_status.connect(
        #     self.main_window.update_export_action_state
        # )

    def _connect_override_pattern_signals(self):
        self._samples_widget.sample_view.override_patterns_ready.connect(
            self._override_widget.set_override_pattern
        )
        self._override_widget.get_selected_overrides_btn.clicked.connect(
            self._samples_widget.sample_view.get_override_pattern
        )
        self._override_widget.custom_override_pattern_ready.connect(
            self._samples_widget.sample_view.set_override_pattern
        )

    def _connect_run_signals(self):
        self._config_manager.users_changed.connect(
            self._run_setup_widget.populate_investigators
        )
        self._config_manager.run_data_error.connect(
            self._run_setup_widget.show_error
        )
        self._run_setup_widget.setup_commited.connect(
            self._rundata_model.set_run_data
        )
        self._rundata_model.run_data_ready.connect(
            self._run_info_widget.set_data
        )
        self._rundata_model.run_data_changed.connect(
            self.main_window.set_override_action_enabled
        )
        self._rundata_model.run_data_changed.connect(
            self._lane_widget.set_lanes
        )
        self._rundata_model.run_data_changed.connect(
            self.main_window.set_lanes_action_enabled
        )
        self._rundata_model.run_data_changed.connect(
            self.main_window.set_index_apps_actions_enabled
        )
        self._rundata_model.index_lens_ready.connect(
            self._index_toolbox_widget.set_index_kit_status
        )

    def _connect_lane_signals(self):
        self._lane_widget.lanes_ready.connect(
            self._samples_widget.sample_view.set_lanes
        )

