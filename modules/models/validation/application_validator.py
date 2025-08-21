from pprint import pprint
from typing import Any, Dict, List, Optional

import pandas as pd

from modules.models.application.application_manager import ApplicationManager
from modules.models.state.state_model import StateModel
from modules.models.validation.validation_result import ValidationResult, StatusLevel
from modules.utils.utils import explode_df_application_profile_column


def keys_with_different_values(list_of_dicts):
    key_values = {}
    for d in list_of_dicts:
        for k, v in d.items():
            if k not in key_values:
                key_values[k] = []
            key_values[k].append(v)

    # Keep keys that appear in at least 2 dicts and have different values
    diff_keys = {
        k for k, vals in key_values.items()
        if len(vals) >= 2 and len(set(vals)) > 1
    }

    return diff_keys


def application_settings_check(sample_df: pd.DataFrame, application_manager: ApplicationManager) -> ValidationResult:
    """Check application settings consistency.
    
    Args:
        sample_df:
        application_manager: The application manager
        
    Returns:
        ValidationResult indicating the result of the check
        
    Note:
        The state_model should contain a sample_df attribute with an 'ApplicationProfile' column
    """

    name = "application settings check"

    if sample_df is None or 'ApplicationProfile' not in sample_df.columns:
        return ValidationResult(
            name=name,
            message="Missing required 'ApplicationProfile' column in sample data",
            severity=StatusLevel.ERROR
        )
        
    try:
        # Create a copy to avoid modifying the original dataframe
        profile_exploded_df = sample_df.explode("ApplicationProfile", ignore_index=True)

        # Get unique application profiles
        unique_profile_names = [p for p in profile_exploded_df["ApplicationProfile"].unique()
                         if pd.notna(p) and str(p).strip()]
        
        if not unique_profile_names:
            return ValidationResult(
                name=name,
                message="No valid application profiles found in sample data",
                severity=StatusLevel.ERROR
            )
        
        # Group settings by application type
        app_settings: Dict[str, List[Dict[str, Any]]] = {}
        pprint(unique_profile_names)
        for profile_name in unique_profile_names:
            try:
                profile = application_manager.profile_name_to_profile(profile_name)
                if not profile:
                    return ValidationResult(
                        name=name,
                        message=f"Application profile not found for: {profile_name}",
                        severity=StatusLevel.ERROR
                    )
                    
                app_type = profile.get("ApplicationType")
                if not app_type:
                    return ValidationResult(
                        name=name,
                        message=f"ApplicationType type not found for profile: {profile_name}",
                        severity=StatusLevel.ERROR
                    )
                    
                if app_type not in app_settings:
                    app_settings[app_type] = []
                app_settings[app_type].append(profile.get("Settings", {}))
                
            except Exception as e:
                return ValidationResult(
                    name=name,
                    message=f"Error processing application profile {profile_name}: {str(e)}",
                    severity=StatusLevel.ERROR
                )
        
        # Check for consistent settings within each application type

        for app_type, settings_list in app_settings.items():
            diff_keys = keys_with_different_values(settings_list)
            if diff_keys:
                return ValidationResult(
                    name=name,
                    message=f"Non-identical shared settings keys with different values for: {app_type}, {diff_keys}",
                    severity=StatusLevel.ERROR
                )

        return ValidationResult(
            name=name,
            message=f"All application settings are consistent across {len(app_settings)} application type(s)",
            severity=StatusLevel.INFO
        )
        
    except Exception as e:
        return ValidationResult(
            name=name,
            message=f"Unexpected error during validation: {str(e)}",
            severity=StatusLevel.ERROR
        )
