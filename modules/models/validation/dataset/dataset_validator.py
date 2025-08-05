from logging import Logger

from PySide6.QtCore import Signal, QObject

from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.dataset.dataset_manager import DataSetManager
from modules.models.sample.sample_model import SampleModel
from modules.models.state.state_model import StateModel
from modules.views.validation.dataset_validation_widget import DataSetValidationWidget


class DataSetValidator(QObject):

    def __init__(
        self,
        state_model: StateModel,
        dataset_validation_widget: DataSetValidationWidget,
        logger: Logger
    ):
        super().__init__()
        self._logger = logger
        self._state_model = state_model

        self._dataset_validation_widget = dataset_validation_widget

        if state_model is None:
            self._logger.error("sample_model cannot be None")
            return

        if not state_model.sample_df is None:
            self._logger.error("dataset manager cannot be None")
            return

        self._logger = logger

    @staticmethod
    def _appname_explode(df):
        df = df[df["ApplicationProfile"].apply(lambda x: x != [])]
        if not df.empty:
            return df.explode("ApplicationProfile", ignore_index=True)

        return df

    @staticmethod
    def _lane_explode(self, df):
        return df.explode("Lane", ignore_index=True)

    def validate(self):
        sample_df = self._state_model.sample_df

        df_tuple = (sample_df, self._appname_explode(sample_df), self._lane_explode(sample_df))

        self._dataset_validation_widget.populate(df_tuple)

