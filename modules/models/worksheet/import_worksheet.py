from logging import Logger
from pathlib import Path
from pprint import pprint

import pandas as pd
from PySide6.QtCore import QObject, Slot

from modules.models.application.application_manager import ApplicationManager
from modules.models.methods.method_manager import MethodManager
from modules.models.sample.sample_model import SampleModel


class WorkSheetImporter(QObject):
    def __init__(self,
                 sample_model: SampleModel,
                 method_manager: MethodManager,
                 application_manager: ApplicationManager,
                 logger: Logger):
        super().__init__()
        self._sample_model = sample_model
        self._method_manager = method_manager
        self._application_manager = application_manager
        self._logger = logger

    def _worksheet_validation(self, df):
        print("Starting worksheet validation.")

        if "Sample_ID" not in df.columns:
            self._logger.error(f"required column Sample_ID does not exist in worksheet")
            print("Validation failed: 'Sample_ID' column missing.")
            return False

        if "Method" not in df.columns:
            self._logger.error(f"required column Method does not exist in worksheet")
            print("Validation failed: 'Method' column missing.")
            return False

        num_rows = df.shape[0]
        print(f"Number of rows in dataframe: {num_rows}")

        if num_rows < 1:
            self._logger.error(f"no rows in worksheet dataframe")
            print("Validation failed: no rows in dataframe.")
            return False

        missing_values = df[df[['Sample_ID', 'Method']].isnull().any(axis=1)]
        print(f"Number of rows with missing values: {missing_values.shape[0]}")

        if not missing_values.empty:
            self._logger.error("samplesheet data is incomplete, missing data.")
            print("Validation failed: incomplete samplesheet data.")
            return False

        duplicates = df[df.duplicated(subset='Sample_ID', keep=False)]
        print(f"Number of duplicate 'Sample_ID' values: {duplicates.shape[0]}")

        if not duplicates.empty:
            self._logger.error("duplicate Sample_ID values exist in samplesheet.")
            print("Validation failed: duplicate 'Sample_ID' values found.")
            return False

        print("Worksheet validation passed.")
        return True


    @Slot(str)
    def load_worksheet(self, path: str):
        """Load a worksheet from a csv file, validate it, and import it into the sample model."""
        worksheet_path = Path(path)
        dataframe = pd.read_csv(worksheet_path)

        if not self._worksheet_validation(dataframe):
            self._logger.error("worksheet data could not be imported.")
            return

        dataframe['ApplicationProfile'] = dataframe['Method'].apply(self._method_manager.application_profiles_list)

        profile_data_keys = set()
        for _, row in dataframe.iterrows():
            application_profiles = row['ApplicationProfile']
            for profile in application_profiles:
                application_profile_obj = self._application_manager.app_profile_to_app_prof_obj(profile)

                pprint(application_profile_obj)

                profile_data_keys.update(application_profile_obj['Data'].keys())

        for key in profile_data_keys:
            dataframe[key] = None

        for index, row in dataframe.iterrows():
            application_profiles = row['ApplicationProfile']
            for profile in application_profiles:
                application_profile_obj = self._application_manager.app_profile_to_app_prof_obj(profile)
                for key, value in application_profile_obj['Data'].items():
                    dataframe.loc[index, key] = value

        self._sample_model.set_worksheet_data(dataframe)
