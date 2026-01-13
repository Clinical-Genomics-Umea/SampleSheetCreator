from logging import Logger
from pathlib import Path

import pandas as pd
from PySide6.QtCore import QObject, Slot

from modules.models.application.application_manager import ApplicationManager
from modules.models.indexes.index_kit_manager import IndexKitManager
from modules.models.state.state_model import StateModel
from modules.models.test.test_profile_manager import TestProfileManager


class WorkDataImporter(QObject):
    def __init__(self,
                 sample_model: StateModel,
                 index_kit_manager: IndexKitManager,
                 test_profile_manager: TestProfileManager,
                 application_manager: ApplicationManager,
                 logger: Logger):
        super().__init__()
        self._sample_model = sample_model
        self._index_kit_manager = index_kit_manager
        self._application_manager = application_manager
        self._test_profile_manager = test_profile_manager
        self._logger = logger

    def _worksheet_validation(self, df):

        if "Sample_ID" not in df.columns:
            self._logger.error(f"required column Sample_ID does not exist in worksheet")
            return False

        if "TestProfileNameVersion" not in df.columns:
            self._logger.error(f"required column TestProfile does not exist in worksheet")
            return False

        num_rows = df.shape[0]

        if num_rows < 1:
            self._logger.error(f"no rows in worksheet dataframe")
            return False

        missing_values = df[df[['Sample_ID', 'TestProfileNameVersion']].isnull().any(axis=1)]

        if not missing_values.empty:
            self._logger.error("samplesheet data is incomplete, missing data.")
            return False

        duplicates = df[df.duplicated(subset='Sample_ID', keep=False)]

        if not duplicates.empty:
            self._logger.error("duplicate Sample_ID values exist in samplesheet.")
            return False

        for _, row in df.iterrows():
            test_profile_name_version = row['TestProfileNameVersion']

            parts = test_profile_name_version.split('.')
            test_profile_name = parts[0]
            test_profile_main_version = parts[1]

            if not self._test_profile_manager.has_test_profile(test_profile_name, test_profile_main_version):
                return False

        return True

    def load_worksheet(self, path: Path):
        """Load a worksheet from a csv file, validate it, and import it into the sample model."""
        df = pd.read_csv(path)

        if not self._worksheet_validation(df):
            self._logger.error("worksheet data could not be imported.")
            return

        df["ApplicationProfileNameVersion"] = None

        for _, row in df.iterrows():
            test_profile_name_version = row['TestProfileNameVersion']

            parts = test_profile_name_version.split('.')
            test_profile_name = parts[0]
            test_profile_main_version = parts[1]

            if self._test_profile_manager.has_test_profile(test_profile_name, test_profile_main_version):
                test_profiles = self._test_profile_manager.get_test_application_profiles(test_profile_name, test_profile_main_version)


    def _get_application_profile_name_versions(self, test_profile_name, test_profile_main_version):
        application_profile_name_versions = []
        for test_profile in self._test_profile_manager.get_test_application_profiles(test_profile_name, test_profile_main_version):
            application_profile_name_versions.append(test_profile.application_profile_name)


        # profile_data_keys = set()
        # for _, row in df.iterrows():
        #     application_profiles = row['ApplicationProfile']
        #     for profile in application_profiles:
        #         application_profile_obj = self._application_manager.profile_name_to_profile(profile)
        #
        #         profile_data_keys.update(application_profile_obj['Data'].keys())
        #
        # for key in profile_data_keys:
        #     df[key] = None
        #
        # for index, row in df.iterrows():
        #     application_profiles = row['ApplicationProfile']
        #     for profile in application_profiles:
        #         application_profile_obj = self._application_manager.profile_name_to_profile(profile)
        #         for key, value in application_profile_obj['Data'].items():
        #             df.loc[index, key] = value
        #
        # self._sample_model.set_worksheet_data(df)
