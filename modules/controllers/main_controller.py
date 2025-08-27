import logging
from pathlib import Path

from PySide6.QtCore import QObject, Qt

from modules.models.application.application_manager import ApplicationManager
from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.export.export import ExportModel
from modules.models.indexes.index_kit_manager import IndexKitManager
from modules.models.logging.log_widget_handler import LogWidgetHandler
from modules.models.logging.statusbar_handler import StatusBarLogHandler
from modules.models.override_cycles.OverrideCyclesModel import OverrideCyclesModel
from modules.models.sample.sample_model import SampleModel, CustomProxyModel
from modules.models.state.state_model import StateModel
from modules.models.validation.color_balance.color_balance_data_generator import ColorBalanceDataGenerator
from modules.models.validation.compatibility_tester import CompatibilityTester
from modules.models.validation.sample_data_overview.sample_data_overview import SampleDataOverviewGenerator
from modules.models.validation.index_distance.index_distance_data_generator import IndexDistanceDataGenerator
from modules.models.validation.main_validator import MainValidator
from modules.models.validation.general_validation.general_validator import GeneralValidator
from modules.views.config.configuration_widget import ConfigurationWidget
from modules.views.export.export import ExportWidget
from modules.views.application.application_container import ApplicationContainerWidget
from modules.views.file.file import FileView
from modules.views.index.index_kit_toolbox import IndexKitToolbox
from modules.views.lane.lane import LanesWidget
from modules.views.override.override import OverrideCyclesWidget
from modules.views.run_setup.run_setup import RunSetupWidget
from modules.views.log.log_widget import LogWidget
from modules.views.run_info.run_info_view import RunInfoView
from modules.views.sample.sample_view import SamplesWidget
from modules.views.statusbar.status import StatusBar
from modules.views.main_window import MainWindow
from modules.views.toolbar.toolbar import ToolBar
from modules.views.validation.color_balance_widget import ColorBalanceValidationWidget
from modules.views.validation.sample_data_overview_widget import SampleDataOverviewWidget
from modules.views.validation.index_distance_overview_widget import IndexDistanceOverviewWidget
from modules.views.validation.main_validation_widget import MainValidationWidget
from modules.views.validation.general_validation_widget import GeneralValidationWidget

from PySide6.QtTest import QSignalSpy

class MainController(QObject):
    def __init__(self):
        """
        Initialize main controller, setting up models, views, and connections.
        """
        super().__init__()

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

        self._status_bar = StatusBar()
        self._log_widget = LogWidget()

        self._file_handler = logging.FileHandler(Path("log/log.txt"))
        self._status_handler = StatusBarLogHandler(self._status_bar)
        self._log_widget_handler = LogWidgetHandler(self._log_widget)
        self._logger.addHandler(self._file_handler)
        self._logger.addHandler(self._status_handler)
        self._logger.addHandler(self._log_widget_handler)

        self._toolbar = ToolBar()
        self._configuration_manager = ConfigurationManager(self._logger)

        self._sample_model = SampleModel(self._configuration_manager)
        self._sample_proxy_model = CustomProxyModel()
        self._sample_proxy_model.setSourceModel(self._sample_model)

        self._state_model = StateModel(self._sample_model, self._configuration_manager, self._logger)
        self._index_kit_manager = IndexKitManager(self._configuration_manager, self._state_model, self._logger)
        self._application_manager = ApplicationManager(self._configuration_manager, self._logger)

        self._override_cycles_model = OverrideCyclesModel(self._state_model, self._logger)

        self._export_model = ExportModel(self._state_model,
                                         self._configuration_manager,
                                         self._application_manager,
                                         self._override_cycles_model,
                                         self._logger)

        # validation widgets

        self._general_validation_widget = GeneralValidationWidget()
        self._sample_data_overview_widget = SampleDataOverviewWidget()
        self._index_distance_overview_widget = IndexDistanceOverviewWidget()
        self._color_balance_overview_widget = ColorBalanceValidationWidget(self._state_model)

        # validation models

        self._general_validator = GeneralValidator(
            self._configuration_manager,
            self._application_manager,
            self._state_model,
            self._logger
        )

        self._sample_data_overview_generator = SampleDataOverviewGenerator(
            self._state_model,
            self._logger
        )

        self._index_distance_data_generator = IndexDistanceDataGenerator(
            self._state_model,
            self._logger
        )

        self._color_balance_data_generator = ColorBalanceDataGenerator(
            self._state_model,
            self._logger
        )

        self._main_validator = MainValidator(
            self._general_validator,
            self._sample_data_overview_generator,
            self._index_distance_data_generator,
            self._color_balance_data_generator,
            self._state_model,
            self._logger
        )

        # widgets

        self._main_validation_widget = MainValidationWidget(self._general_validation_widget,
                                                            self._sample_data_overview_widget,
                                                            self._index_distance_overview_widget,
                                                            self._color_balance_overview_widget,
                                                            self._main_validator)

        self._override_widget = OverrideCyclesWidget(self._override_cycles_model)
        self._lane_widget = LanesWidget(self._state_model)
        self._file_widget = FileView()
        self._samples_widget = SamplesWidget(self._configuration_manager.samples_settings)
        self._run_setup_widget = RunSetupWidget(self._configuration_manager, self._state_model)
        self._run_info_view = RunInfoView()
        self._index_toolbox_widget = IndexKitToolbox(self._index_kit_manager)
        self._applications_container_widget = ApplicationContainerWidget(
            self._application_manager, self._state_model
        )
        self._config_widget = ConfigurationWidget(self._configuration_manager)
        self._export_widget = ExportWidget(self._state_model, self._configuration_manager)

        self._samples_widget.set_model(self._sample_proxy_model)

        self.main_window = MainWindow(
            self._override_widget,
            self._lane_widget,
            self._file_widget,
            self._samples_widget,
            self._run_setup_widget,
            self._run_info_view,
            self._main_validation_widget,
            self._index_toolbox_widget,
            self._applications_container_widget,
            self._config_widget,
            self._export_widget,
            self._log_widget,
        )
        self.main_window.setStatusBar(self._status_bar)
        self.main_window.addToolBar(Qt.LeftToolBarArea, self._toolbar)

        self._compatibility_tester = CompatibilityTester(
            self._state_model,
            self._logger
        )

        self._connect_signals()
        self._logger.info("Init done!")

    def _connect_signals(self):
        """
        Connect UI signals to controller slots.
        """
        self._connect_run_setup_signals()
        self._connect_validation_signals()
        self._connect_override_pattern_signals()
        self._connect_application_signal()
        self._connect_lane_signals()
        self._connect_toolbar_signal()
        self._connect_datastate_signals()
        self._connect_configuration_signals()
        self._connect_index_kit_signals()

        self._connect_sample_model_signals()

        self._connect_export_signals()


    def _connect_export_signals(self):
        self._export_widget.generate_btn.clicked.connect(self._export_model.generate)


    def _connect_run_setup_signals(self):
        self._run_setup_widget.run_setup_data_ready.connect(self._state_model.set_run_setup_data)

    def _connect_configuration_signals(self):
        self._configuration_manager.users_changed.connect(
            self._run_setup_widget.populate_investigators
        )

    def _connect_sample_model_signals(self):
        self._sample_model.dataChanged.connect(self._state_model.update_aggregate_sample_data)


    def _connect_datastate_signals(self):
        self._state_model.freeze_state_changed.connect(
            self._toolbar.set_export_action_state
        )

        self._state_model.date_changed.connect(self._run_info_view.set_date_label)
        self._state_model.investigator_changed.connect(self._run_info_view.set_investigator_label)
        self._state_model.run_name_changed.connect(self._run_info_view.set_run_name_label)
        self._state_model.run_description_changed.connect(self._run_info_view.set_run_desc_label)
        self._state_model.lanes_changed.connect(self._run_info_view.set_lanes_label)
        self._state_model.lanes_changed.connect(self._lane_widget.set_lanes)
        self._state_model.instrument_changed.connect(self._run_info_view.set_instrument_label)
        self._state_model.flowcell_changed.connect(self._run_info_view.set_flowcell_label)
        self._state_model.chemistry_changed.connect(self._run_info_view.set_chemistry_label)
        self._state_model.reagent_kit_changed.connect(self._run_info_view.set_reagent_kit_label)
        self._state_model.i5_seq_orientation_changed.connect(self._run_info_view.set_i5_seq_orientation_label)
        self._state_model.i5_samplesheet_orientation_bcl2fastq_changed.connect(self._run_info_view.set_bcl2fastq_ss_i5_orient_lbl)
        self._state_model.i5_samplesheet_orientation_bclconvert_changed.connect(self._run_info_view.set_bclconvert_ss_i5_orient_lbl)
        self._state_model.read1_cycles_changed.connect(self._run_info_view.set_read1_cycles_label)
        self._state_model.read2_cycles_changed.connect(self._run_info_view.set_read2_cycles_label)
        self._state_model.index1_cycles_changed.connect(self._run_info_view.set_index1_cycles_label)
        self._state_model.index2_cycles_changed.connect(self._run_info_view.set_index2_cycles_label)
        self._state_model.custom_cycles_changed.connect(self._run_info_view.set_custom_cycles_label)

        self._state_model.color_a_changed.connect(self._run_info_view.set_a_label)
        self._state_model.color_t_changed.connect(self._run_info_view.set_t_label)
        self._state_model.color_g_changed.connect(self._run_info_view.set_g_label)
        self._state_model.color_c_changed.connect(self._run_info_view.set_c_label)
        self._state_model.assess_color_balance_changed.connect(self._run_info_view.set_assess_color_balance_label)

        self._state_model.sample_index1_minlen_changed.connect(self._run_info_view.set_sample_index1_minlen_label)
        self._state_model.sample_index1_maxlen_changed.connect(self._run_info_view.set_sample_index1_maxlen_label)
        self._state_model.sample_index2_minlen_changed.connect(self._run_info_view.set_sample_index2_minlen_label)
        self._state_model.sample_index2_maxlen_changed.connect(self._run_info_view.set_sample_index2_maxlen_label)

        self._state_model.run_info_ready.connect(self._toolbar.enable_sample_data_actions)
        self._state_model.run_info_ready.connect(self._samples_widget.enable)
        self._state_model.run_info_ready.connect(self._index_kit_manager.on_run_cycles_changed)

        self._state_model.validation_status.connect(self._toolbar.set_validation_state)
        self._state_model.samplesheet_v2_changed.connect(self._export_widget.populate_samplesheet_v2_text)
        self._state_model.json_changed.connect(self._export_widget.populate_json_text)


    def _connect_index_kit_signals(self):
        self._index_kit_manager.index_kits_changed.connect(
            self._index_toolbox_widget.set_index_kits
        )

    def _connect_application_signal(self):
        self._applications_container_widget.add_application_profile_data.connect(
            self._compatibility_tester.verify_dragen_ver_compatibility
        )
        self._compatibility_tester.application_profile_ok.connect(
            self._samples_widget.sample_view.set_application
        )
        self._applications_container_widget.remove_application_profile.connect(
            self._samples_widget.sample_view.remove_application
        )

    def _connect_toolbar_signal(self):
        """Connect UI signals to controller slots"""
        # Connect toolbar signal to handler
        self._toolbar.action_triggered.connect(self.main_window.toolbar_action_handler)

    def _connect_validation_signals(self):
        """Connect UI signals to validation slots"""
        # Set up the sample model in the validation widget
        self._main_validation_widget.set_sample_model(self._sample_model)

        self._main_validation_widget.validate_button.clicked.connect(
            self._main_validator.general_validate
        )
        self._general_validator.general_validation_results_ready.connect(
            self._general_validation_widget.populate
        )

        self._general_validator.success.connect(self._main_validator.populate_manual_overview_widgets)
        self._sample_data_overview_generator.data_ready.connect(self._sample_data_overview_widget.populate)
        self._index_distance_data_generator.data_ready.connect(self._index_distance_overview_widget.populate)
        self._color_balance_data_generator.data_ready.connect(self._color_balance_overview_widget.populate)

        self._general_validator.success.connect(self._state_model.mark_as_validated)
        self._general_validator.fail.connect(self._index_distance_overview_widget.populate)

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

    def _connect_lane_signals(self):
        self._lane_widget.lanes_ready.connect(
            self._samples_widget.sample_view.set_lanes
        )

