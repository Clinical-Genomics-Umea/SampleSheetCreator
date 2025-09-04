from logging import Logger

import pandas as pd
from PySide6.QtCore import Signal

from modules.models.test.test_profile_manager import TestProfileManager


class ImportModel:

    sample_test_data_ready = Signal(object)

    def __init__(self, test_profile_manager: TestProfileManager, logger: Logger):
        self._test_profile_manager = test_profile_manager
        self._logger = logger
        self._test_profile_col_name = "Test"
        self._required_worksheet_columns = ["Sample_ID", self._test_profile_col_name]

    def import_worksheet(self, file_path: str) -> None:
        df = pd.read_csv(file_path)

        if not self._validate_worksheet_data(df):
            self._logger.error("worksheet data could not be imported.")
            return

        df = df[self._required_worksheet_columns]
        df["TestProfileId"] = None
        df["ApplicationProfileId"] = None

        for index, row in df.iterrows():
            ws_test_id = row[self._test_profile_col_name]
            test_profile_id = self._test_profile_manager.latest_test_profile_id_by_worksheet_test(ws_test_id)
            if test_profile_id is None:
                self._logger.error(f"Invalid TestProfile value found: {ws_test_id}")
                return
            df.at[index, "TestProfileId"] = test_profile_id

            application_profile_ids = self._test_profile_manager.application_profile_ids_by_test_profile_id(test_profile_id)
            df.at[index, "ApplicationProfileId"] = application_profile_ids

        self.sample_test_data_ready.emit(df)

    def _validate_worksheet_data(self, df: pd.DataFrame) -> bool:
        """
        Validate the worksheet data.

        Args:
            df: DataFrame containing the worksheet data

        Returns:
            bool: True if validation passes, False otherwise
        """
        # Check required columns

        for column in self._required_worksheet_columns:
            if column not in df.columns:
                self._logger.error(f"Required column '{column}' does not exist in worksheet")
                return False

        # Check for duplicate Sample_IDs
        duplicate_ids = df[df.duplicated('Sample_ID', keep=False)]['Sample_ID'].unique()
        if len(duplicate_ids) > 0:
            self._logger.error(f"Duplicate Sample_IDs found: {', '.join(duplicate_ids)}")
            return False

        # Check for empty or invalid Sample_IDs
        if df['Sample_ID'].isna().any() or (df['Sample_ID'].str.strip() == '').any():
            self._logger.error("Sample_ID cannot be empty")
            return False

        for index, row in df.iterrows():
            test_profile_version = row['TestProfile']
            test_profile, test_version = test_profile_version.split('.')
            if not self._test_profile_manager.has_test_profile(test_profile, test_version):
                self._logger.error(f"Invalid TestProfile value found: {test_profile}")
                return False

        return True

    def _get_valid_test_profiles(self) -> set[str]:
        """Get a set of all valid test profiles in the format 'TestName.Version'"""
        valid_profiles = set()
        for test_profile in self._test_profile_manager._test_profiles:
            valid_profiles.add(f"{test_profile.TestName}.{test_profile.Version}")
        return valid_profiles




