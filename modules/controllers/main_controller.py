import logging
from pathlib import Path

from PySide6.QtCore import QObject, Qt

from modules.models.application.application_manager import ApplicationManager
from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.dataset.dataset_manager import DataSetManager
from modules.models.indexes.index_kit_manager import IndexKitManager
from modules.models.logging.log_widget_handler import LogWidgetHandler
from modules.models.logging.statusbar_handler import StatusBarLogHandler
from modules.models.methods.method_manager import MethodManager
from modules.models.override_cycles.OverrideCyclesModel import OverrideCyclesModel
from modules.models.rundata.rundata_model import RunDataModel
from modules.models.sample.sample_model import SampleModel, CustomProxyModel
from modules.models.state.state_model import StateModel
from modules.models.validation.color_balance.color_balance_validator import ColorBalanceValidator
from modules.models.validation.compatibility_tester import CompatibilityTester
from modules.models.validation.dataset.dataset_validator import DataSetValidator
from modules.models.validation.index_distance.index_distance_matrix_generator import IndexDistanceValidator
from modules.models.validation.main_validator import MainValidator
from modules.models.validation.prevalidator.prevalidator import PreValidator
from modules.models.worksheet.import_worksheet import WorkSheetImporter
from modules.views.config.configuration_widget import ConfigurationWidget
from modules.views.export.export import ExportWidget
from modules.views.drawer_tools.application.application_container import ApplicationContainerWidget
from modules.views.drawer_tools.file.file import FileView
from modules.views.drawer_tools.index.index_kit_toolbox import IndexKitToolbox
from modules.views.drawer_tools.lane.lane import LanesWidget
from modules.views.drawer_tools.override.override import OverrideCyclesWidget
from modules.views.drawer_tools.run_setup.run_setup import RunSetupWidget
from modules.views.log.log_widget import LogWidget
from modules.views.run.run_info_view import RunInfoView
from modules.views.sample.sample_view import SamplesWidget
from modules.views.statusbar.status import StatusBar
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

        self._application_manager = ApplicationManager(self._configuration_manager, self._logger)
        self._index_kit_manager = IndexKitManager(self._configuration_manager, self._logger)

        self._rundata_model = RunDataModel(self._configuration_manager, self._logger)

        self._sample_model = SampleModel(self._configuration_manager)
        self._sample_proxy_model = CustomProxyModel()
        self._sample_proxy_model.setSourceModel(self._sample_model)

        self._dataset_manager = DataSetManager(
            self._sample_model,
            self._application_manager,
            self._rundata_model,
            self._logger
        )

        self._state_model = StateModel(self._sample_model, self._configuration_manager, self._logger)

        self._override_cycles_model = OverrideCyclesModel(
            self._state_model, self._dataset_manager, self._logger
        )

        # validation widgets

        self._prevalidation_widget = PreValidationWidget()
        self._dataset_validation_widget = DataSetValidationWidget()
        self._index_distance_validation_widget = IndexDistanceValidationWidget()
        self._color_balance_validation_widget = ColorBalanceValidationWidget(self._dataset_manager)

        # validation models

        self._prevalidator = PreValidator(
            self._sample_model,
            self._configuration_manager,
            self._application_manager,
            self._dataset_manager,
            self._prevalidation_widget,
            self._logger
        )

        self._dataset_validator = DataSetValidator(
            self._sample_model,
            self._configuration_manager,
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

        self._validation_widget = MainValidationWidget(self._prevalidation_widget,
                                                       self._dataset_validation_widget,
                                                       self._index_distance_validation_widget,
                                                       self._color_balance_validation_widget,
                                                       self._main_validator)

        self._override_widget = OverrideCyclesWidget(self._override_cycles_model)
        self._lane_widget = LanesWidget(self._dataset_manager)
        self._file_widget = FileView()
        self._samples_widget = SamplesWidget(self._configuration_manager.samples_settings)
        self._run_setup_widget = RunSetupWidget(self._configuration_manager, self._state_model)
        self._run_info_view = RunInfoView()
        self._index_toolbox_widget = IndexKitToolbox(self._index_kit_manager)
        self._applications_container_widget = ApplicationContainerWidget(
            self._application_manager, self._dataset_manager
        )
        self._config_widget = ConfigurationWidget(self._configuration_manager)
        self._export_widget = ExportWidget(self._dataset_manager, self._configuration_manager)

        self._samples_widget.set_model(self._sample_proxy_model)

        self.main_window = MainWindow(
            self._override_widget,
            self._lane_widget,
            self._file_widget,
            self._samples_widget,
            self._run_setup_widget,
            self._run_info_view,
            self._validation_widget,
            self._index_toolbox_widget,
            self._applications_container_widget,
            self._config_widget,
            self._export_widget,
            self._log_widget,
        )
        self.main_window.setStatusBar(self._status_bar)
        self.main_window.addToolBar(Qt.LeftToolBarArea, self._toolbar)

        # self.main_window.samples_widget.set_model(self._sample_proxy_model)

        self._compatibility_tester = CompatibilityTester(
            self._state_model,
            self._dataset_manager,
            self._logger
        )

        self._method_manager = MethodManager(self._configuration_manager, self._application_manager, self._logger)
        self._worksheet_importer = WorkSheetImporter(self._sample_model, self._method_manager,
                                                     self._application_manager, self._logger)

        self._connect_signals()

        self._logger.info("Init done!")

    def _connect_signals(self):
        """
        Connect UI signals to controller slots.
        """
        self._connect_validation_signals()
        self._connect_file_signals()
        self._connect_override_pattern_signals()
        self._connect_application_signal()
        self._connect_drop_paste_signals()
        self._connect_lane_signals()
        self._connect_toolbar_signal()
        # self._connect_run_signals()
        self._connect_datastate_signals()
        # self._connect_state_model_signals()

        self._connect_sample_model_signals()

    def _connect_sample_model_signals(self):
        self._sample_model.dataChanged.connect(self._state_model.update_index_lengths)

    def _connect_datastate_signals(self):
        self._state_model.freeze_state_changed.connect(
            self._toolbar.set_export_action_state
        )

        self._state_model.date_changed.connect(self._run_info_view.set_date_label)
        self._state_model.investigator_changed.connect(self._run_info_view.set_investigator_label)
        self._state_model.run_name_changed.connect(self._run_info_view.set_run_name_label)
        self._state_model.run_description_changed.connect(self._run_info_view.set_run_desc_label)
        self._state_model.lanes_changed.connect(self._run_info_view.set_lanes_label)
        self._state_model.instrument_changed.connect(self._run_info_view.set_instrument_label)
        self._state_model.flowcell_changed.connect(self._run_info_view.set_flowcell_label)
        self._state_model.chemistry_changed.connect(self._run_info_view.set_chemistry_label)
        self._state_model.reagent_kit_changed.connect(self._run_info_view.set_reagent_kit_label)
        self._state_model.i5_seq_orientation_changed.connect(self._run_info_view.set_i5_seq_orientation_label)
        self._state_model.i5_samplesheet_orientation_bcl2fastq_changed.connect(self._run_info_view.set_bcl2fastq_ss_i5_orient_lbl)
        self._state_model.i5_samplesheet_orientation_bclconvert_changed.connect(self._run_info_view.set_bclconvert_ss_i5_orient_lbl)
        self._state_model.run_read1_cycles_changed.connect(self._run_info_view.set_read1_cycles_label)
        self._state_model.run_index1_cycles_changed.connect(self._run_info_view.set_index1_cycles_label)
        self._state_model.run_index2_cycles_changed.connect(self._run_info_view.set_index2_cycles_label)
        self._state_model.run_read2_cycles_changed.connect(self._run_info_view.set_read2_cycles_label)
        self._state_model.color_a_changed.connect(self._run_info_view.set_a_label)
        self._state_model.color_t_changed.connect(self._run_info_view.set_t_label)
        self._state_model.color_g_changed.connect(self._run_info_view.set_g_label)
        self._state_model.color_c_changed.connect(self._run_info_view.set_c_label)
        self._state_model.assess_color_balance_changed.connect(self._run_info_view.set_assess_color_balance_label)
        self._state_model.sample_index1_maxlen_changed.connect(self._run_info_view.set_current_index1_minlen_label)
        self._state_model.sample_index2_maxlen_changed.connect(self._run_info_view.set_current_index2_minlen_label)
        self._state_model.sample_index1_minlen_changed.connect(self._run_info_view.set_current_index1_maxlen_label)
        self._state_model.sample_index2_minlen_changed.connect(self._run_info_view. set_current_index2_maxlen_label)

        self._state_model.freeze_state_changed.connect(self._toolbar.set_export_action_state)

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

    def _connect_drop_paste_signals(self):
        self._sample_model.dropped_data.connect(
            self._compatibility_tester.index_drop_check
        )
        self._compatibility_tester.index_drop_ok.connect(
            self._sample_model.set_dropped_index_data
        )

    def _connect_file_signals(self):
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
        self._validation_widget.validate_button.clicked.connect(
            self._main_validator.validate
        )
        self._main_validator.clear_validator_widgets.connect(
            self._validation_widget.clear_validation_widgets
        )
        self._main_validator.prevalidation_failed.connect(
            self._state_model.unfreeze
        )
        self._main_validator.prevalidation_success.connect(
            self._state_model.freeze
        )

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

    # def _connect_run_signals(self):
        # self._configuration_manager.users_changed.connect(
        #     self._run_setup_widget._populate_investigators
        # )
        # self._configuration_manager.run_data_error.connect(
        #     self._run_setup_widget.show_error
        # )
        # self._run_setup_widget.setup_commited.connect(
        #     self._rundata_model.set_run_data
        # )
        # self._rundata_model.run_data_ready.connect(
        #     self._run_info_widget.set_data
        # )
        # self._rundata_model.run_data_ready.connect(
        #     self._lane_widget.set_lanes
        # )
        # self._rundata_model.index_lens_ready.connect(
        #     self._index_toolbox_widget.set_index_kit_status
        # )
        # self._rundata_model.run_data_ready.connect(
        #     self._toolbar.on_rundata_set
        # )

    def _connect_lane_signals(self):
        self._lane_widget.lanes_ready.connect(
            self._samples_widget.sample_view.set_lanes
        )

