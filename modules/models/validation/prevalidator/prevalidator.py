from dataclasses import dataclass
from logging import Logger
from typing import Optional, Dict, List, Tuple

import pandas as pd
from PySide6.QtCore import QObject, Signal

from modules.models.application.application_manager import ApplicationManager
from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.dataset.dataset_manager import DataSetManager
from modules.models.sample.sample_model import SampleModel
from modules.views.validation.prevalidation_widget import PreValidationWidget


@dataclass
class PreValidationResult:
    name: str
    status: bool
    message: str = ""


class PreValidator(QObject):
    data_ready = Signal(list)

    def __init__(
        self,
        sample_model: SampleModel,
        configuration_manager: ConfigurationManager,
        application_manager: ApplicationManager,
        dataset_manager: DataSetManager,
        prevalidation_widget: PreValidationWidget,
        logger: Logger,
    ):
        super().__init__()
        self._sample_model = sample_model
        self._configuration_manager = configuration_manager
        self._application_manager = application_manager
        self._dataset_manager = dataset_manager
        self._logger = logger

        self._prevalidation_widget = prevalidation_widget

        self.dataframe: Optional[pd.DataFrame] = None
        self.rundata: Optional[Dict] = None

    @staticmethod
    def _run_validators(validators: List[callable]) -> List[PreValidationResult]:
        """
        Run a series of validation methods and collect results.

        :param validators: List of validation methods to run
        :return: List of validation results
        """
        results = [validator() for validator in validators]
        return results

    def validate(self):
        """Run comprehensive validations on the dataset"""
        self.dataframe = self._dataset_manager.sample_dataframe_lane_explode()
        self.rundata = self._dataset_manager.rundata

        validators = [
            self.rundata_is_set,
            self.required_cols_populated,
            self.run_lanes_int_validation,
            self.empty_sample_id_validation,
            self.dataframe_type_validation,
            self.application_settings_validation,
            self.allowed_lanes_validation,
            self.validate_unique_sample_lane_combinations,
        ]

        results = self._run_validators(validators)
        status = all(result.status for result in results)

        results_list = [(r.name, r.status, r.message) for r in results]
        self._prevalidation_widget.populate(results_list)

        if not status:
            self._logger.error(f"Prevalidation failed")
            return False

        return True

    def rundata_is_set(self) -> PreValidationResult:
        """Validate if run data is set"""
        if not self._dataset_manager.has_rundata:
            return PreValidationResult(
                name="Run data set validator",
                status=False,
                message="Run data has not been set",
            )
        return PreValidationResult(name="Run data set validator", status=True)

    def required_cols_populated(self) -> PreValidationResult:
        """Validate that required columns are populated"""
        required_columns = self._configuration_manager.required_sample_fields
        dataframe = self._dataset_manager.sample_dataframe_lane_explode()

        missing_columns = [
            column for column in required_columns if dataframe[column].isnull().any()
        ]

        if missing_columns:
            return PreValidationResult(
                name="required fields populated",
                status=False,
                message=f"Required fields are not populated: {', '.join(missing_columns)}",
            )
        return PreValidationResult(name="required fields populated", status=True)

    def application_settings_validation(self) -> PreValidationResult:
        """Validate application settings consistency"""
        app_exploded_df = self.dataframe.explode("ApplicationProfile", ignore_index=True)

        print(app_exploded_df.to_string())

        unique_profiles = app_exploded_df["ApplicationProfile"].unique()

        # Group settings by application
        app_settings = {}
        for appname in unique_profiles:
            app = self._application_manager.app_profile_to_app_prof_obj(appname)
            app_type = app["Application"]

            if app_type not in app_settings:
                app_settings[app_type] = []
            app_settings[app_type].append(app["Settings"])

        # Check if all settings are identical within each application type
        for app_type, settings_list in app_settings.items():
            if not all(settings == settings_list[0] for settings in settings_list):
                return PreValidationResult(
                    name="application settings validation",
                    status=False,
                    message=f"Non-identical settings exist for: {app_type}",
                )

        return PreValidationResult(name="application settings validation", status=True)

    def empty_sample_id_validation(self) -> PreValidationResult:
        """Validate that no Sample_ID entries are empty"""
        empty_items = self.dataframe["Sample_ID"].isna()

        if empty_items.any():
            empty_row_indices = (self.dataframe.index[empty_items] + 1).tolist()
            return PreValidationResult(
                name="empty sample id validation",
                status=False,
                message=f"Empty items found in Sample_ID column at row numbers: {','.join(map(str, empty_row_indices))}",
            )
        return PreValidationResult(name="empty sample id validation", status=True)

    def run_lanes_int_validation(self) -> PreValidationResult:
        """Validate run lanes are a list of integers"""
        run_lanes = self.rundata["Lanes"]

        if not isinstance(run_lanes, list) or not all(
            isinstance(item, int) for item in run_lanes
        ):
            return PreValidationResult(
                name="set number of lanes validation",
                status=False,
                message="Lanes must be a list of integers",
            )
        return PreValidationResult(name="set number of lanes validation", status=True)

    def dataframe_type_validation(self) -> PreValidationResult:
        """Validate dataframe type and content"""
        if not isinstance(self.dataframe, pd.DataFrame):
            return PreValidationResult(
                name="dataframe basic validation",
                status=False,
                message="Data is not in a pandas dataframe format",
            )
        if self.dataframe.empty:
            return PreValidationResult(
                name="dataframe basic validation",
                status=False,
                message="No data to validate (empty dataframe)",
            )
        return PreValidationResult(name="dataframe basic validation", status=True)

    def validate_unique_sample_lane_combinations(self) -> PreValidationResult:
        """Validate unique sample-lane combinations"""
        df_tmp = self.dataframe.copy(deep=True)
        df_tmp["sample_lane"] = df_tmp["Sample_ID"] + "_" + df_tmp["Lane"].astype(str)

        if df_tmp["sample_lane"].duplicated().any():
            duplicates = df_tmp.loc[
                df_tmp["sample_lane"].duplicated(), "sample_lane"
            ].tolist()
            return PreValidationResult(
                name="unique sample lane validation",
                status=False,
                message=f"Duplicates of Sample_ID and Lane exists: {', '.join(duplicates)}",
            )
        return PreValidationResult(name="unique sample lane validation", status=True)

    def allowed_lanes_validation(self) -> PreValidationResult:
        """Validate used lanes are within allowed lanes"""
        allowed_lanes = set(self.rundata["Lanes"])
        used_lanes = set(self.dataframe["Lane"])

        disallowed_lanes = used_lanes.difference(allowed_lanes)

        if disallowed_lanes:
            return PreValidationResult(
                name="allowed lanes validation",
                status=False,
                message=f"Lane(s) {disallowed_lanes} not allowed, does not exist in flowcell",
            )
        return PreValidationResult(name="allowed lanes validation", status=True)

    @staticmethod
    def sample_id_validation(df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
        """Static method for standalone sample ID validation"""
        if not isinstance(df, pd.DataFrame):
            return False, "Data could not be converted to a pandas dataframe."
        if df.empty:
            return False, "No data to validate (empty dataframe)."
        return True, None
