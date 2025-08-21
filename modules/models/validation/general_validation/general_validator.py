"""Module for pre-validation of sample data before processing."""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import pandas as pd
from logging import Logger
from PySide6.QtCore import QObject, Signal

from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.application.application_manager import ApplicationManager
from modules.models.state.state_model import StateModel
from modules.models.validation.general_validation.validators import (
    ValidationResult, check_sample_dataframe_overall_consistency, lanes_general_check, lane_sample_uniqueness_check,
    application_settings_check, overall_sample_data_validator, override_cycles_pattern_validator,
    index_len_run_cycles_check, index_pair_uniqueness_check,
)
from modules.models.validation.validation_result import StatusLevel


class GeneralValidator(QObject):

    general_validation_results_ready = Signal(object)
    success = Signal()
    fail = Signal()

    def __init__(
        self,
        configuration_manager: ConfigurationManager,
        application_manager: ApplicationManager,
        state_model: StateModel,
        logger: Logger,
    ) -> None:
        super().__init__()
        self._configuration_manager = configuration_manager
        self._application_manager = application_manager
        self._state_model = state_model
        self._logger = logger


    def validate(self) -> None:

        sample_df = self._state_model.sample_df
        allowed_lanes = self._state_model.lanes
        index1_cycles: int = self._state_model.index1_cycles
        index2_cycles: int = self._state_model.index2_cycles

        validation_results = [
            check_sample_dataframe_overall_consistency(sample_df ),
            lanes_general_check(sample_df, allowed_lanes),
            lane_sample_uniqueness_check(sample_df),
            application_settings_check(sample_df, self._application_manager),
            overall_sample_data_validator(sample_df),
            override_cycles_pattern_validator(sample_df),
            index_len_run_cycles_check(sample_df, index1_cycles, index2_cycles),
            index_pair_uniqueness_check(sample_df),
        ]

        self.general_validation_results_ready.emit(validation_results)

        # validation_results.append(run_sample_id_validation(self._state_model.sample_data))
        # validation_results.append(run_sample_lane_uniqueness(self._state_model.sample_data))
        # validation_results.append(run_allowed_lanes_validation(self._state_model.sample_data))
        # validation_results.append(dataframe_overall_consistency(self._state_model.sample_data))

        if not self.has_errors(validation_results):
            self.success.emit()
            return

        self.fail.emit()



    @staticmethod
    def has_errors(validation_results: list[ValidationResult]) -> bool:
        return any(r.severity == StatusLevel.ERROR for r in validation_results)


