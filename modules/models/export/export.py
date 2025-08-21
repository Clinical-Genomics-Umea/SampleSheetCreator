from multiprocessing.managers import State

from PySide6.QtCore import QObject, Signal, Slot

from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.application.application_manager import ApplicationManager
from modules.models.export.samplesheet_v2.samplesheet_v2 import IlluminaSampleSheetV2
from modules.models.state.state_model import StateModel


class ExportModel(QObject):
    data_ready = Signal(object)

    def __init__(self, state_model: StateModel, configuration_manager: ConfigurationManager, application_manager: ApplicationManager):
        super().__init__()

        if state_model is None:
            raise ValueError("model cannot be None")

        if configuration_manager is None:
            raise ValueError("configuration manager cannot be None")

        self._state_model = state_model
        self._configuration_manager = configuration_manager
        self._application_manager = application_manager

        self._json_data = None
        self._samplesheet_v1_data = None
        self._samplesheet_v2_data = None

    def generate_samplesheet_v2(self):

        file_format_version = "2"

        illumina_samplesheet_v2 = IlluminaSampleSheetV2()

        illumina_samplesheet_v2.set_header_field("RunName", self._state_model.run_name)
        illumina_samplesheet_v2.set_header_field("RunDescription", self._state_model.run_description)
        illumina_samplesheet_v2.set_header_field("FileFormatVersion", file_format_version)
        illumina_samplesheet_v2.set_header_field("InstrumentType", self._state_model.instrument)

        illumina_samplesheet_v2.set_read_field("Index1Cycles", str(self._state_model.index1_cycles))
        illumina_samplesheet_v2.set_read_field("Index2Cycles", str(self._state_model.index2_cycles))
        illumina_samplesheet_v2.set_read_field("Read1Cycles", str(self._state_model.read1_cycles))
        illumina_samplesheet_v2.set_read_field("Read2Cycles", str(self._state_model.read2_cycles))

        illumina_samplesheet_v2.set_sequencing_field("LibraryPrepKits", str(None))



        for profile_name in self._state_model.sample_application_profile_names:
            profile = self._application_manager.profile_name_to_profile(profile_name)
            application_name = self._application_manager.application_profile_to_app(profile_name)
            settings = self._application_manager.profile_name_to_settings(profile_name)
            exploded_app_df = self._state_model.sample_df.explode("ApplicationProfile")
            df = exploded_app_df[exploded_app_df["ApplicationProfile"] == profile_name]

            if self._application_manager.lane_explode_by_profile_name(profile_name):
                df = df.explode("Lane")

            for key, value in self._application_manager.profile_name_to_data(profile_name).items():
                df[key] = value

            data = df[self._application_manager.profile_name_to_data_fields(profile_name)]

            illumina_samplesheet_v2.set_application(profile_name, settings, data)





        self.data_ready.emit(illumina_samplesheet_v2)



# class MakeJson(QObject):
#     data_ready = Signal(object)
#
#     def __init__(self, state_model: SampleModel, configuration_manager: ConfigurationManager):
#         super().__init__()
#
#         if state_model is None:
#             raise ValueError("model cannot be None")
#
#         if configuration_manager is None:
#             raise ValueError("cfg_mgr cannot be None")
#
#         self.state_model = state_model
#         self.configuration_manager = configuration_manager
#
#     @Slot()
#     def mk_json(self):
#         samples_df = self.state_model.to_dataframe()
#         run_data = self.configuration_manager.run_data
#
#         samples_run_data = {
#             "samples_data": samples_df.to_dict(orient="records"),
#             "state": self.state_model.state
#         }
#
#         self.data_ready.emit(samples_run_data)
#

