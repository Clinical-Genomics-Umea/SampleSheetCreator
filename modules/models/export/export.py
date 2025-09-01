import json
import zipfile
from dataclasses import asdict
from datetime import datetime
from logging import Logger
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.application.application_manager import ApplicationManager
from modules.models.export.samplesheet_v2.samplesheet_v2 import IlluminaSampleSheetV2
from modules.models.override_cycles.OverrideCyclesModel import OverrideCyclesModel
from modules.models.state.state_model import StateModel


class ExportModel(QObject):
    samplesheet_v2_ready = Signal(object)

    def __init__(self, state_model: StateModel,
                 configuration_manager: ConfigurationManager,
                 application_manager: ApplicationManager,
                 override_cycles_model: OverrideCyclesModel,
                 logger: Logger
                 ):
        super().__init__()

        if state_model is None:
            raise ValueError("model cannot be None")

        if configuration_manager is None:
            raise ValueError("configuration manager cannot be None")

        self._state_model = state_model
        self._configuration_manager = configuration_manager
        self._application_manager = application_manager
        self._override_cycles_model = override_cycles_model
        self._logger = logger


        self._json_data = None
        self._samplesheet_v1_data = None
        self._samplesheet_v2_data = None

    def generate(self):
        self.generate_samplesheet_v2()
        self.generate_json()

    def generate_json(self):

        run_info_dict = asdict(self._state_model.run_info)
        run_info_dict.update({"json": ""})
        run_info_dict.update({"samplesheet_v2": ""})

        df = self._state_model.sample_df.copy()
        df["OverrideCycles"] = df["OverrideCyclesPattern"].apply(self._override_cycles_model.pattern_to_cycles)

        df = df.to_dict(orient="records")

        json_dict = {
            "run_info": run_info_dict,
            "samples": df
        }

        json_str = json.dumps(json_dict, indent=4)
        self._state_model.json = json_str

    def generate_samplesheet_v2(self):

        file_format_version = "2"

        illumina_samplesheet_v2 = IlluminaSampleSheetV2()

        illumina_samplesheet_v2.set_header_field("RunName", self._state_model.run_name)
        illumina_samplesheet_v2.set_header_field("RunDescription", self._state_model.run_description)
        illumina_samplesheet_v2.set_header_field("FileFormatVersion", file_format_version)
        illumina_samplesheet_v2.set_header_field("InstrumentType", self._state_model.instrument)
        illumina_samplesheet_v2.set_header_field("Custom_uuid", self._state_model.uuid)

        illumina_samplesheet_v2.set_read_field("Index1Cycles", str(self._state_model.index1_cycles))
        illumina_samplesheet_v2.set_read_field("Index2Cycles", str(self._state_model.index2_cycles))
        illumina_samplesheet_v2.set_read_field("Read1Cycles", str(self._state_model.read1_cycles))
        illumina_samplesheet_v2.set_read_field("Read2Cycles", str(self._state_model.read2_cycles))

        illumina_samplesheet_v2.set_sequencing_field("LibraryPrepKits", str(None))

        df_base = self._state_model.sample_df

        for profile_name in self._state_model.sample_application_profile_names:

            application_name = self._application_manager.application_profile_to_app(profile_name)
            settings = self._application_manager.profile_name_to_settings(profile_name)
            translate = self._application_manager.profile_name_to_translate(profile_name)

            data_fields = self._application_manager.profile_name_to_data_fields(profile_name)

            exploded_app_df = df_base.explode("ApplicationProfileName")
            exploded_app_profile_df = exploded_app_df[exploded_app_df["ApplicationProfileName"] == profile_name].copy()

            if "Lane" in data_fields:
                exploded_app_profile_df = exploded_app_profile_df.explode("Lane")

            for key, value in self._application_manager.profile_name_to_data(profile_name).items():
                exploded_app_profile_df[key] = value

            if "OverrideCycles" in data_fields:
                exploded_app_profile_df["OverrideCycles"] = exploded_app_profile_df["OverrideCyclesPattern"].apply(self._override_cycles_model.pattern_to_cycles)

            new = [field for field in data_fields if field not in exploded_app_profile_df.columns]

            for new_field in new:
                exploded_app_profile_df[new_field] = None

            df = exploded_app_profile_df[data_fields].copy()
            if translate:
                df.rename(columns=translate, inplace=True)

            illumina_samplesheet_v2.set_application(application_name, settings, df)

        samplesheet_v2_data = illumina_samplesheet_v2.generate()
        self._state_model.samplesheet_v2 = samplesheet_v2_data


    def export_package(self, save_path: Path) -> bool:
        """Save samplesheet_v2 data to a zip file.

        Args:
            save_path: Path where the zip file should be saved

        Returns:
            bool: True if save was successful, False otherwise
        """
        if not self._state_model.samplesheet_v2:
            self._logger.warning("No samplesheet_v2 data available to save")
            return False

        if not self._state_model.json:
            self._logger.warning("No sample json data available to save")
            return False

        try:
            save_path = save_path.with_suffix(".zip")
            # Ensure the save directory exists
            save_path.parent.mkdir(parents=True, exist_ok=True)

            # Create a timestamp for the filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            samplesheet_filename = f"SampleSheet_{timestamp}.csv"
            sample_json_filename = f"SampleJson_{timestamp}.json"
            readme_filename = "README.txt"

            with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add the samplesheet as a file in the zip
                zipf.writestr(samplesheet_filename, self._state_model.samplesheet_v2)
                zipf.writestr(sample_json_filename, self._state_model.json)

                # Add a README file with metadata
                readme_content = f"""SampleSheet Package
    =================

    Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    Run: {self._state_model.run_name}
    Instrument: {self._state_model.instrument}
    """
                zipf.writestr(readme_filename, readme_content)

            self._logger.info(f"Successfully saved package to {save_path}")
            return True

        except Exception as e:
            self._logger.error(f"Failed to save package: {str(e)}")
            return False

    def export_samplesheet_v2(self, path: Path):
        path = path.with_suffix(".csv")
        path.write_text(self._state_model.samplesheet_v2)

    def export_json(self, path: Path):
        path = path.with_suffix(".json")
        path.write_text(self._state_model.json)


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

