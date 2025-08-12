"""Module for pre-validation of sample data before processing."""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import pandas as pd
from logging import Logger
from PySide6.QtCore import QObject, Signal

from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.application.application_manager import ApplicationManager
from modules.models.state.state_model import StateModel
from modules.models.validation.prevalidation.validators import (
    ValidationResult, check_sample_dataframe_overall_consistency, lanes_check, lane_sample_uniqueness_check,
    application_settings_check,
)

class PreValidator(QObject):

    prevalidation_results_ready = Signal(object)
    success = Signal()

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
        validation_results = [
            check_sample_dataframe_overall_consistency(self._state_model),
            lanes_check(self._state_model),
            lane_sample_uniqueness_check(self._state_model),
            application_settings_check(self._state_model, self._application_manager)

        ]

        self.prevalidation_results_ready.emit(validation_results)


        # validation_results.append(run_sample_id_validation(self._state_model.sample_data))
        # validation_results.append(run_sample_lane_uniqueness(self._state_model.sample_data))
        # validation_results.append(run_allowed_lanes_validation(self._state_model.sample_data))
        # validation_results.append(dataframe_overall_consistency(self._state_model.sample_data))



