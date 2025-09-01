from logging import Logger

import pandas as pd

from modules.models.test.test_profile_manager import TestProfileManager


class ImportModel:
    def __init__(self, test_profile_manager: TestProfileManager, logger: Logger):
        self._test_profile_manager = test_profile_manager
        self._logger = logger

    def import_worksheet(self, file_path: str) -> None:
        df = pd.read_csv(file_path)

        if not self._validate_worksheet_data(df):
            self._logger.error("worksheet data could not be imported.")
            return



    def _validate_worksheet_data(self, df: pd.DataFrame) -> bool:
        """
        Validate the worksheet data.

        Args:
            df: DataFrame containing the worksheet data

        Returns:
            bool: True if validation passes, False otherwise
        """
        # Check required columns
        required_columns = ["Sample_ID", "TestProfile"]
        for column in required_columns:
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

        # Check if all TestProfile values are valid
        valid_test_profiles = self._get_valid_test_profiles()
        invalid_profiles = set(df['TestProfile']) - valid_test_profiles

        if invalid_profiles:
            self._logger.error(
                f"Invalid TestProfile values found: {', '.join(invalid_profiles)}. "
                f"Valid profiles are: {', '.join(valid_test_profiles)}"
            )
            return False

        return True

    def _get_valid_test_profiles(self) -> set[str]:
        """Get a set of all valid test profiles in the format 'TestName.Version'"""
        valid_profiles = set()
        for test_profile in self._test_profile_manager._test_profiles:
            valid_profiles.add(f"{test_profile.TestName}.{test_profile.Version}")
        return valid_profiles




