"""Module for pre-validation of sample data before processing."""

from dataclasses import dataclass
from enum import Enum, auto
from logging import Logger
from typing import Optional, Dict, List, Tuple, Callable, Any, Set

import pandas as pd
from PySide6.QtCore import QObject, Signal

from modules.models.application.application_manager import ApplicationManager
from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.sample.sample_model import SampleModel
from modules.models.state.state_model import StateModel
from modules.views.validation.prevalidation_widget import PreValidationWidget


class ValidationSeverity(Enum):
    """Severity levels for validation results."""
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


@dataclass(frozen=True)
class PreValidationResult:
    """Container for validation results.
    
    Attributes:
        name: Name of the validation check
        status: Boolean indicating if validation passed
        message: Optional detailed message about the validation result
        severity: Severity level of the validation result
    """
    name: str
    status: bool
    message: str = ""
    severity: ValidationSeverity = ValidationSeverity.ERROR
    
    def __post_init__(self) -> None:
        """Post-initialization validation."""
        if not self.status and not self.message:
            object.__setattr__(self, 'message', f"{self.name} validation failed")


@dataclass
class PreValidationResult:
    name: str
    status: bool
    message: str = ""


class PreValidator(QObject):
    """Validates sample data before processing.
    
    This class performs various validations on sample data to ensure it meets
    the required format and constraints before further processing.
    
    Attributes:
        data_ready: Signal emitted when validation is complete
    """
    
    data_ready = Signal(list)
    
    def __init__(
        self,
        configuration_manager: ConfigurationManager,
        application_manager: ApplicationManager,
        state_model: StateModel,
        prevalidation_widget: PreValidationWidget,
        logger: Logger,
    ) -> None:
        """Initialize the PreValidator.
        
        Args:
            sample_model: The sample model containing sample data
            configuration_manager: Configuration manager for validation rules
            application_manager: Application manager for application-specific validations
            state_model: Current application state
            prevalidation_widget: UI widget for displaying validation results
            logger: Logger instance for logging validation messages
        """
        super().__init__()
        self._configuration_manager = configuration_manager
        self._application_manager = application_manager
        self._state_model = state_model
        self._logger = logger
        self._prevalidation_widget = prevalidation_widget

        self.dataframe: Optional[pd.DataFrame] = None
        self.rundata: Optional[Dict[str, Any]] = None
        
        # Cache for application settings to avoid repeated lookups
        self._app_settings_cache: Dict[str, Any] = {}

    def _run_validators(self, validators: List[Callable[[], PreValidationResult]]) -> List[PreValidationResult]:
        """Run a series of validation methods and collect results.
        
        Args:
            validators: List of validation methods to run
            
        Returns:
            List of PreValidationResult objects containing validation outcomes
            
        Note:
            Each validator should return a PreValidationResult object.
            Any exceptions in validators are caught and logged.
        """
        results: List[PreValidationResult] = []
        for validator in validators:
            try:
                result = validator()
                if not isinstance(result, PreValidationResult):
                    result = PreValidationResult(
                        name=validator.__name__,
                        status=False,
                        message=f"Validator {validator.__name__} returned invalid result type: {type(result)}",
                        severity=ValidationSeverity.ERROR
                    )
                results.append(result)
            except Exception as e:
                self._logger.exception(f"Error running validator {validator.__name__}")
                results.append(PreValidationResult(
                    name=validator.__name__,
                    status=False,
                    message=f"Validation error: {str(e)}",
                    severity=ValidationSeverity.ERROR
                ))
        return results

    def validate(self) -> bool:
        """Run comprehensive validations on the dataset.
        
        Returns:
            bool: True if all validations pass, False otherwise
            
        Note:
            Updates the prevalidation widget with the results of all validations
            and emits the data_ready signal with failed validations.
        """
        self.dataframe = self._state_model.sample_df
        self.rundata = self._state_model.rundata
        
        # Define validators in order of execution
        validators: List[Callable[[], PreValidationResult]] = [
            self.dataframe_type_validation,  # Should run first
            self.rundata_is_set,            # Need run data for subsequent validations
            self.run_lanes_int_validation,  # Validate lanes before other lane checks
            self.required_cols_populated,
            self.empty_sample_id_validation,
            self.application_settings_validation,
            self.allowed_lanes_validation,
            self.validate_unique_sample_lane_combinations,
        ]

        # Run all validators
        results = self._run_validators(validators)
        
        # Determine overall status
        status = all(result.status for result in results)
        
        # Log results
        if status:
            self._logger.info("All pre-validations passed successfully")
        else:
            failed = [r.name for r in results if not r.status]
            self._logger.warning(f"Prevalidation failed for: {', '.join(failed)}")
        
        # Update UI with results
        results_list = [
            (r.name, r.status, r.message, r.severity.name.lower()) 
            for r in results
        ]
        self._prevalidation_widget.populate(results_list)
        
        # Emit signal with failed validations
        self.data_ready.emit([r for r in results if not r.status])
        
        return status

    def rundata_is_set(self) -> PreValidationResult:
        """Validate if run data is properly set.
        
        Returns:
            PreValidationResult: Result indicating if run data is available
            
        Note:
            This is a critical validation that should run early as other validations
            depend on run data being available.
        """
        if not self._state_model.has_run_info or not self.rundata:
            return PreValidationResult(
                name="Run Data Validation",
                status=False,
                message="Run data has not been set or is invalid",
                severity=ValidationSeverity.ERROR
            )
        return PreValidationResult(
            name="Run Data Validation",
            status=True,
            message="Run data is properly configured",
            severity=ValidationSeverity.INFO
        )

    def required_cols_populated(self) -> PreValidationResult:
        """Validate that all required columns are populated.
        
        Returns:
            PreValidationResult: Result indicating if all required columns are populated
            
        Raises:
            AttributeError: If sample dataframe is not available
        """
        if self.dataframe is None:
            return PreValidationResult(
                name="Required Fields Validation",
                status=False,
                message="No sample data available for validation",
                severity=ValidationSeverity.ERROR
            )
            
        required_columns = self._configuration_manager.required_sample_fields
        if not required_columns:
            return PreValidationResult(
                name="Required Fields Validation",
                status=False,
                message="No required columns defined in configuration",
                severity=ValidationSeverity.WARNING
            )
            
        # Check if required columns exist in dataframe
        missing_columns = [col for col in required_columns if col not in self.dataframe.columns]
        if missing_columns:
            return PreValidationResult(
                name="Required Fields Validation",
                status=False,
                message=f"Missing required columns in sample data: {', '.join(missing_columns)}",
                severity=ValidationSeverity.ERROR
            )
            
        # Check for null values in required columns
        null_columns = []
        for column in required_columns:
            if self.dataframe[column].isnull().any():
                null_count = self.dataframe[column].isnull().sum()
                null_columns.append(f"{column} ({null_count} missing values)")
                
        if null_columns:
            return PreValidationResult(
                name="Required Fields Validation",
                status=False,
                message=f"Missing values in required columns: {', '.join(null_columns)}",
                severity=ValidationSeverity.ERROR
            )
            
        return PreValidationResult(
            name="Required Fields Validation",
            status=True,
            message="All required fields are properly populated",
            severity=ValidationSeverity.INFO
        )
        """Validate that required columns are populated"""
        required_columns = self._configuration_manager.required_sample_fields
        df = self._state_model.sample_df

        missing_columns = [
            column for column in required_columns if df[column].isnull().any()
        ]

        if missing_columns:
            return PreValidationResult(
                name="required fields populated",
                status=False,
                message=f"Required fields are not populated: {', '.join(missing_columns)}",
            )
        return PreValidationResult(name="required fields populated", status=True)

    def application_settings_validation(self) -> PreValidationResult:
        """Validate consistency of application settings across samples.
        
        Returns:
            PreValidationResult: Result of the application settings validation
            
        Note:
            This validation ensures that all samples with the same application type
            have identical settings configured.
        """
        if self.dataframe is None or 'ApplicationProfile' not in self.dataframe.columns:
            return PreValidationResult(
                name="Application Settings Validation",
                status=False,
                message="Missing required 'ApplicationProfile' column in sample data",
                severity=ValidationSeverity.ERROR
            )
            
        try:
            # Create a copy to avoid modifying the original dataframe
            app_exploded_df = self.dataframe.explode("ApplicationProfile", ignore_index=True)
            
            # Get unique application profiles
            unique_profiles = [p for p in app_exploded_df["ApplicationProfile"].unique() 
                             if pd.notna(p) and str(p).strip()]
            
            if not unique_profiles:
                return PreValidationResult(
                    name="Application Settings Validation",
                    status=False,
                    message="No valid application profiles found in sample data",
                    severity=ValidationSeverity.ERROR
                )
            
            # Group settings by application type
            app_settings: Dict[str, List[Dict[str, Any]]] = {}
            for appname in unique_profiles:
                try:
                    app = self._application_manager.app_profile_to_app_prof_obj(appname)
                    app_type = app.get("Application")
                    
                    if not app_type:
                        return PreValidationResult(
                            name="Application Settings Validation",
                            status=False,
                            message=f"Application type not found for profile: {appname}",
                            severity=ValidationSeverity.ERROR
                        )
                        
                    if app_type not in app_settings:
                        app_settings[app_type] = []
                    app_settings[app_type].append(app.get("Settings", {}))
                    
                except Exception as e:
                    self._logger.error(f"Error processing application profile {appname}: {str(e)}")
                    return PreValidationResult(
                        name="Application Settings Validation",
                        status=False,
                        message=f"Error processing application profile {appname}: {str(e)}",
                        severity=ValidationSeverity.ERROR
                    )
            
            # Check for consistent settings within each application type
            inconsistent_apps = []
            for app_type, settings_list in app_settings.items():
                if not all(settings == settings_list[0] for settings in settings_list[1:]):
                    inconsistent_apps.append(app_type)
            
            if inconsistent_apps:
                return PreValidationResult(
                    name="Application Settings Validation",
                    status=False,
                    message=f"Inconsistent settings found for application(s): {', '.join(inconsistent_apps)}",
                    severity=ValidationSeverity.ERROR
                )
                
            return PreValidationResult(
                name="Application Settings Validation",
                status=True,
                message=f"All application settings are consistent across {len(app_settings)} application type(s)",
                severity=ValidationSeverity.INFO
            )
            
        except Exception as e:
            self._logger.exception("Unexpected error during application settings validation")
            return PreValidationResult(
                name="Application Settings Validation",
                status=False,
                message=f"Unexpected error during validation: {str(e)}",
                severity=ValidationSeverity.ERROR
            )

    def empty_sample_id_validation(self) -> PreValidationResult:
        """Validate that no Sample_ID entries are empty or invalid.
        
        Returns:
            PreValidationResult: Result of the sample ID validation
            
        Note:
            This validation checks for empty or whitespace-only sample IDs.
        """
        if self.dataframe is None:
            return PreValidationResult(
                name="Sample ID Validation",
                status=False,
                message="No sample data available for validation",
                severity=ValidationSeverity.ERROR
            )
            
        if 'Sample_ID' not in self.dataframe.columns:
            return PreValidationResult(
                name="Sample ID Validation",
                status=False,
                message="Required 'Sample_ID' column is missing",
                severity=ValidationSeverity.ERROR
            )
            
        try:
            # Check for NaN/None values
            empty_mask = self.dataframe["Sample_ID"].isna()
            empty_indices = empty_mask[empty_mask].index.tolist()
            
            # Check for empty strings or whitespace-only strings
            if not empty_indices:  # Only check if no NaN values
                empty_mask = self.dataframe["Sample_ID"].astype(str).str.strip() == ''
                empty_indices = empty_mask[empty_mask].index.tolist()
            
                # Convert to 1-based indexing for user-friendly reporting
                row_numbers = [str(i + 1) for i in empty_indices]
                return PreValidationResult(
                    name="Sample ID Validation",
                    status=False,
                    message=f"Empty or invalid Sample_ID found at row(s): {', '.join(row_numbers)}",
                    severity=ValidationSeverity.ERROR
                )
                
            return PreValidationResult(
                name="Sample ID Validation",
                status=True,
                message="All sample IDs are valid",
                severity=ValidationSeverity.INFO
            )
            
        except Exception as e:
            self._logger.exception("Error during sample ID validation")
            return PreValidationResult(
                name="Sample ID Validation",
                status=False,
                message=f"Error during validation: {str(e)}",
                severity=ValidationSeverity.ERROR
            )

    def validate_unique_sample_lane_combinations(self) -> PreValidationResult:
        """Validate that each sample-lane combination is unique.
        
        Returns:
            PreValidationResult: Result of the sample-lane uniqueness validation
            
        Note:
            This validation ensures that no sample is assigned to the same lane multiple times.
            It checks for duplicate (Sample_ID, Lane) combinations in the sample data.
        """
        try:
            # Check if required columns exist
            required_columns = {"Sample_ID", "Lane"}
            missing_columns = required_columns - set(self.dataframe.columns)
            
            if missing_columns:
                return PreValidationResult(
                    name="Sample-Lane Uniqueness Validation",
                    status=False,
                    message=f"Required columns not found: {', '.join(sorted(missing_columns))}",
                    severity=ValidationSeverity.ERROR
                )

            # Check for any empty or invalid sample IDs
            invalid_sample_ids = self.dataframe["Sample_ID"].isna() | (self.dataframe["Sample_ID"].astype(str).str.strip() == '')
            if invalid_sample_ids.any():
                return PreValidationResult(
                    name="Sample-Lane Uniqueness Validation",
                    status=False,
                    message=f"Empty or invalid Sample_ID found at row(s): {', '.join(str(i+1) for i in invalid_sample_ids[invalid_sample_ids].index.tolist())}",
                    severity=ValidationSeverity.ERROR
                )

            # Check for any empty or invalid lane values
            invalid_lanes = self.dataframe["Lane"].isna() | (self.dataframe["Lane"].astype(str).str.strip() == '')
            if invalid_lanes.any():
                return PreValidationResult(
                    name="Sample-Lane Uniqueness Validation",
                    status=False,
                    message=f"Empty or invalid Lane values found at row(s): {', '.join(str(i+1) for i in invalid_lanes[invalid_lanes].index.tolist())}",
                    severity=ValidationSeverity.ERROR
                )

            # Check for duplicate sample-lane combinations
            duplicates = self.dataframe.duplicated(subset=["Sample_ID", "Lane"], keep=False)
            if duplicates.any():
                duplicate_rows = self.dataframe[duplicates][["Sample_ID", "Lane"]].drop_duplicates()
                
                # Format the duplicate entries for the error message
                duplicate_entries = []
                for _, row in duplicate_rows.iterrows():
                    sample_id = row["Sample_ID"]
                    lane = row["Lane"]
                    duplicate_entries.append(f"Sample '{sample_id}' in lane {lane}")
                
                return PreValidationResult(
                    name="Sample-Lane Uniqueness Validation",
                    status=False,
                    message=f"Duplicate sample-lane combinations found:\n" + 
                            "\n".join(f"  • {entry}" for entry in duplicate_entries),
                    severity=ValidationSeverity.ERROR
                )
                
            return PreValidationResult(
                name="Sample-Lane Uniqueness Validation",
                status=True,
                message=f"All {len(self.dataframe)} sample-lane combinations are unique",
                severity=ValidationSeverity.INFO
            )
            
        except Exception as e:
            self._logger.exception("Error during sample-lane uniqueness validation")
            return PreValidationResult(
                name="Sample-Lane Uniqueness Validation",
                status=False,
                message=f"Error during validation: {str(e)}",
                severity=ValidationSeverity.ERROR
            )

    def allowed_lanes_validation(self) -> PreValidationResult:
        """Validate that all lanes in the sample sheet are within the allowed range.
        
        Returns:
            PreValidationResult: Result of the allowed lanes validation
            
        Note:
            This validation checks that all lane values in the sample sheet are within
            the range of lanes specified in the run configuration.
        """
        try:
            # Check if rundata and lanes are available
            if self.rundata is None:
                return PreValidationResult(
                    name="Allowed Lanes Validation",
                    status=False,
                    message="Run data is not available",
                    severity=ValidationSeverity.ERROR
                )
                
            if "Lanes" not in self.rundata or not self.rundata["Lanes"]:
                return PreValidationResult(
                    name="Allowed Lanes Validation",
                    status=False,
                    message="No lane configuration found in run data",
                    severity=ValidationSeverity.ERROR
                )
            
            allowed_lanes = set(self.rundata["Lanes"])
            
            # Check if 'Lane' column exists and has values
            if "Lane" not in self.dataframe.columns:
                return PreValidationResult(
                    name="Allowed Lanes Validation",
                    status=False,
                    message="Required 'Lane' column is missing from sample data",
                    severity=ValidationSeverity.ERROR
                )
                
            if self.dataframe["Lane"].isna().all():
                return PreValidationResult(
                    name="Allowed Lanes Validation",
                    status=False,
                    message="No lane information found in the sample sheet",
                    severity=ValidationSeverity.ERROR
                )

            # Check for invalid lane values and collect all sample lanes
            invalid_lanes = set()
            sample_lanes = set()
            invalid_rows = []
            
            for idx, lane in enumerate(self.dataframe["Lane"], 1):
                if pd.isna(lane) or (isinstance(lane, str) and lane.strip() == ''):
                    invalid_rows.append(f"Row {idx}: Empty lane value")
                    continue
                    
                try:
                    # Handle lane ranges (e.g., "1-4") and single lanes
                    if "-" in str(lane):
                        try:
                            start, end = map(int, str(lane).split("-"))
                            if start > end:
                                invalid_rows.append(f"Row {idx}: Invalid lane range '{lane}' (start > end)")
                                continue
                            lanes = range(start, end + 1)
                        except (ValueError, AttributeError):
                            invalid_rows.append(f"Row {idx}: Invalid lane range format '{lane}'")
                            continue
                    else:
                        try:
                            lanes = [int(lane)]
                        except (ValueError, AttributeError):
                            invalid_rows.append(f"Row {idx}: Invalid lane value '{lane}'")
                            continue
                    
                    # Check each lane in the range
                    for l in lanes:
                        if l <= 0:
                            invalid_rows.append(f"Row {idx}: Invalid lane number {l} (must be positive)")
                        sample_lanes.add(l)
                        
                except Exception as e:
                    self._logger.warning(f"Error processing lane value '{lane}' at row {idx}: {str(e)}")
                    invalid_rows.append(f"Row {idx}: Error processing lane value '{lane}'")
            
            # Report any invalid lane values
            if invalid_rows:
                return PreValidationResult(
                    name="Allowed Lanes Validation",
                    status=False,
                    message="Invalid lane values found:\n" + 
                           "\n".join(f"  • {row}" for row in invalid_rows[:10]) + 
                           ("\n  ... (more errors not shown)" if len(invalid_rows) > 10 else ""),
                    severity=ValidationSeverity.ERROR
                )
            
            # Check if all sample lanes are in allowed lanes
            invalid_sample_lanes = sample_lanes - allowed_lanes
            if invalid_sample_lanes:
                return PreValidationResult(
                    name="Allowed Lanes Validation",
                    status=False,
                    message=(
                        f"The following lanes are used in the sample sheet but are not in the allowed lanes ({sorted(allowed_lanes)}):\n" +
                        "  • " + 
                        ", ".join(map(str, sorted(invalid_sample_lanes)))
                    ),
                    severity=ValidationSeverity.ERROR
                )
            
            # If we got here, all lanes are valid
            return PreValidationResult(
                name="Allowed Lanes Validation",
                status=True,
                message=f"All {len(sample_lanes)} lane(s) in the sample sheet are within the allowed range",
                severity=ValidationSeverity.INFO
            )
            
        except Exception as e:
            self._logger.exception("Error during allowed lanes validation")
            return PreValidationResult(
                name="Allowed Lanes Validation",
                status=False,
                message=f"Unexpected error during validation: {str(e)}",
                severity=ValidationSeverity.ERROR
            )

    def dataframe_type_validation(self) -> PreValidationResult:
        """Validate that the sample data is in the correct format.
        
        Returns:
            PreValidationResult: Result of the dataframe validation
            
        Note:
            This is typically the first validation that runs to ensure the
            data is in the expected format before other validations proceed.
        """
        if not hasattr(self, '_state_model') or not hasattr(self._state_model, 'sample_df'):
            return PreValidationResult(
                name="Data Format Validation",
                status=False,
                message="Sample data model is not properly initialized",
                severity=ValidationSeverity.ERROR
            )
            
        if self._state_model.sample_df is None:
            return PreValidationResult(
                name="Data Format Validation",
                status=False,
                message="No sample data available for validation",
                severity=ValidationSeverity.ERROR
            )
            
        if not isinstance(self._state_model.sample_df, pd.DataFrame):
            return PreValidationResult(
                name="Data Format Validation",
                status=False,
                message=f"Sample data must be a pandas DataFrame, got {type(self._state_model.sample_df).__name__}",
                severity=ValidationSeverity.ERROR
            )
            
        if self._state_model.sample_df.empty:
            return PreValidationResult(
                name="Data Format Validation",
                status=False,
                message="Sample data is empty",
                severity=ValidationSeverity.ERROR
            )
            
        # Set the dataframe for other validations to use
        self.dataframe = self._state_model.sample_df
        
        return PreValidationResult(
            name="Data Format Validation",
            status=True,
            message=f"Validated sample data with {len(self.dataframe)} rows and {len(self.dataframe.columns)} columns",
            severity=ValidationSeverity.INFO
        )

    def validate_unique_sample_lane_combinations(self) -> PreValidationResult:
        """Validate unique sample-lane combinations"""
        df_tmp = self.dataframe.copy(deep=True)
        df_tmp["sample_lane"] = df_tmp["Sample_ID"] + "_" + df_tmp["Lane"].astype(str)

        try:
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
        except Exception as e:
            return PreValidationResult(
                name="unique sample lane validation",
                status=False,
                message=f"Error: {e}",
            )


    @staticmethod
    def sample_id_validation(df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
        """Static method for standalone sample ID validation
        
        Args:
            df: The pandas DataFrame containing sample data
            
        Returns:
            Tuple[bool, Optional[str]]: A tuple containing:
                - bool: True if validation passes, False otherwise
                - str: Error message if validation fails, None otherwise
        """
        if not isinstance(df, pd.DataFrame):
            return False, "Data could not be converted to a pandas dataframe."
        if df.empty:
            return False, "No data to validate (empty dataframe)."
        return True, None
