"""Module containing validator functions for sample data pre-validation."""
from typing import Any, Dict, List, Optional, Set, Tuple
import re
import ast
import pandas as pd
from pathlib import Path

from modules.models.state.state_model import StateModel
from modules.models.application.application_manager import ApplicationManager
from modules.models.validation.application_validator import application_settings_check
from modules.models.validation.validation_result import ValidationResult, StatusLevel
from modules.utils.utils import is_list_of_ints_string, explode_df_lane_column,  \
    explode_df_application_profile_column
from modules.views.statusbar.status import StatusBar


def lane_sample_uniqueness_check(state_model: StateModel) -> ValidationResult:

    name = "lane sample uniqueness check"

    sample_df = state_model.sample_df

    if sample_df is None or sample_df.empty:
        return ValidationResult(
            name=name,
            message="No sample data available for validation",
            severity=StatusLevel.ERROR
        )

    try:
        # Check if required columns exist
        required_columns = {"Sample_ID", "Lane"}
        missing_columns = required_columns - set(sample_df.columns)
        
        if missing_columns:
            return ValidationResult(
                name=name,
                message=f"Required columns not found: {', '.join(sorted(missing_columns))}",
                severity=StatusLevel.ERROR
            )

        # Check for any empty or invalid sample IDs
        invalid_sample_ids = sample_df["Sample_ID"].isna() | (sample_df["Sample_ID"].astype(str).str.strip() == '')
        if invalid_sample_ids.any():
            return ValidationResult(
                name=name,
                message=f"Empty or invalid Sample_ID found at row(s): {', '.join(str(i+1) for i in invalid_sample_ids[invalid_sample_ids].index.tolist())}",
                severity=StatusLevel.ERROR
            )

        # Check for any empty or invalid lane values
        invalid_lanes = sample_df["Lane"].isna()
        if invalid_lanes.any():
            return ValidationResult(
                name=name,
                message=f"Empty or invalid Lane values found at row(s): {', '.join(str(i+1) for i in invalid_lanes[invalid_lanes].index.tolist())}",
                severity=StatusLevel.ERROR
            )

        # Check for duplicate sample-lane combinations

        df_lane_exploded = sample_df.explode("Lane", ignore_index=True)

        print(df_lane_exploded.to_string())

        duplicates = df_lane_exploded[df_lane_exploded.duplicated(subset=["Sample_ID", "Lane"], keep=False)]

        print(duplicates.to_string())

        if not duplicates.empty:

            duplicate_entries = []
            for _, row in duplicates.iterrows():
                sample_id = row["Sample_ID"]
                lane = str(row["Lane"])
                duplicate_entries.append(f"Sample '{sample_id}' in lane {lane}")
            
            return ValidationResult(
                name=name,
                message=f"Duplicate sample-lane combinations found:\n" +
                        "\n".join(f"  • {entry}" for entry in duplicate_entries),
                severity=StatusLevel.ERROR
            )
            
        return ValidationResult(
            name=name,
            message=f"All {len(df_lane_exploded)} sample-lane combinations are unique",
            severity=StatusLevel.INFO
        )
        
    except Exception as e:
        return ValidationResult(
            name=name,
            message=f"Error during validation: {str(e)}",
            severity=StatusLevel.ERROR
        )


def lanes_general_check(state_model: StateModel) -> ValidationResult:
    """
    Validate that all lane values in the sample sheet are within the allowed range.
    
    Args:
        state_model: The application state model containing sample data and configuration
        
    Returns:
        ValidationResult: Result of the lane validation check
    """
    VALIDATION_NAME = "lanes general check"
    
    # Extract required data from state model with error handling
    try:
        sample_df = state_model.sample_df
        allowed_lanes = state_model.lanes
    except Exception as e:
        return ValidationResult(
            name=VALIDATION_NAME,
            message=f"Error accessing required data: {str(e)}",
            severity=StatusLevel.ERROR
        )
    
    # Input validation
    if sample_df is None:
        return ValidationResult(
            name=VALIDATION_NAME,
            message="No sample data available for validation",
            severity=StatusLevel.ERROR
        )
        
    if not allowed_lanes:
        return ValidationResult(
            name=VALIDATION_NAME,
            message="No allowed lanes configuration provided",
            severity=StatusLevel.ERROR
        )
    
    if "Lane" not in sample_df.columns:
        return ValidationResult(
            name=VALIDATION_NAME,
            message="Required 'Lane' column is missing from sample data",
            severity=StatusLevel.ERROR
        )
        
    if sample_df["Lane"].isna().all():
        return ValidationResult(
            name=VALIDATION_NAME,
            message="No lane information found in the sample sheet",
            severity=StatusLevel.ERROR
        )

    # Process lane values
    invalid_rows = []
    allowed_lanes_set = set(allowed_lanes)
    
    for idx, row in sample_df.iterrows():
        lanes_list = row["Lane"]

        # If it's a string, try to evaluate it as a list
        try:
            lanes_set = set(lanes_list)
            if not lanes_set.issubset(allowed_lanes_set):
                invalid_rows.append(f"Row {row + 1}: Lane values {lanes_list} not in allowed range {sorted(allowed_lanes_set)}")
        except Exception as e:
            invalid_rows.append(f"Row {row + 1}: Error processing lane values: {str(e)}")

    # Report any validation errors
    if invalid_rows:
        error_msg = "Invalid lane values found:\n"
        error_msg += "\n".join(f"  • {row}" for row in invalid_rows[:10])
        if len(invalid_rows) > 10:
            error_msg += "\n  ... (more errors not shown)"
            
        return ValidationResult(
            name=VALIDATION_NAME,
            message=error_msg,
            severity=StatusLevel.ERROR
        )

    # All lanes are valid
    return ValidationResult(
        name=VALIDATION_NAME,
        message=f"All lane(s) in the sample sheet are within the allowed range",
        severity=StatusLevel.INFO
    )


def check_sample_dataframe_overall_consistency(state_model: StateModel) -> ValidationResult:
    name = "sample dataframe overall check"

    try:
        sample_df = state_model.sample_df
    except Exception as e:
        return ValidationResult(
            name=name,
            message=f"Error during validation: {str(e)}",
            severity=StatusLevel.ERROR
        )

    if not isinstance(sample_df, pd.DataFrame):
        return ValidationResult(
            name=name,
            message=f"Data is not in a pandas DataFrame, got {type(sample_df).__name__}",
            severity=StatusLevel.ERROR
        )
        
    if sample_df.empty:
        return ValidationResult(
            name=name,
            message="Sample data is empty",
            severity=StatusLevel.ERROR
        )
        
    return ValidationResult(
        name=name,
        message=f"Validated sample data with {len(sample_df)} rows and {len(sample_df.columns)} columns",
        severity=StatusLevel.INFO
    )


def model_state_validation(state_model: StateModel) -> ValidationResult:
    if not state_model:
        return ValidationResult(
            name="Run Data Validation",
            message="Run data has not been set or is invalid",
            severity=StatusLevel.ERROR
        )
    return ValidationResult(
        name="Run Data Validation",
        message="Run data is properly configured",
        severity=StatusLevel.INFO
    )

def overall_sample_data_validator(state_model: StateModel) -> ValidationResult:

    df = state_model.sample_df

    name = "overall_sample_data_validator"

    errors = []

    # --- Full schema ---
    all_fields = [
        "Lane", "Sample_ID", "Pos", "IndexI7Name", "IndexI7",
        "IndexI5Name", "IndexI5", "IndexKitName", "OverrideCyclesPattern",
        "BarcodeMismatchesIndex1", "BarcodeMismatchesIndex2",
        "AdapterRead1", "AdapterRead2", "ApplicationProfile"
    ]
    required_fields = ["Lane", "Sample_ID", "IndexI7", "ApplicationProfile"]

    # --- Column presence check ---
    missing_columns = [col for col in all_fields if col not in df.columns]
    if missing_columns:
        return ValidationResult(
            name=name,
            message=f"Sample data has missing columns: {missing_columns}",
            severity=StatusLevel.ERROR
        )

    # Patterns
    dna_pattern_strict = re.compile(r"^[ACGT]+$", re.IGNORECASE)  # For IndexI7 / IndexI5
    dna_pattern_plus = re.compile(r"^[ACGT+]+$", re.IGNORECASE)  # For AdapterRead1 / AdapterRead2

    for idx, row in df.iterrows():
        # Lane: must be list of ints (required)
        if not isinstance(row["Lane"], list) or not all(isinstance(x, int) for x in row["Lane"]):
            errors.append(f"Row {idx}: 'Lane' must be a list of ints")

        # Sample_ID: non-empty string (required)
        if not isinstance(row["Sample_ID"], str) or not row["Sample_ID"].strip():
            errors.append(f"Row {idx}: 'Sample_ID' must be a non-empty string")

        # IndexI7: DNA sequence (required, strict)
        if not isinstance(row["IndexI7"], str) or not dna_pattern_strict.match(row["IndexI7"]):
            errors.append(f"Row {idx}: 'IndexI7' must be a valid DNA sequence (ACGT)")

        # ApplicationProfile: list of strings (required)
        if not isinstance(row["ApplicationProfile"], list) or not all(
                isinstance(x, str) for x in row["ApplicationProfile"]):
            errors.append(f"Row {idx}: 'ApplicationProfile' must be a list of strings")

        # IndexI5 (optional but strict if present)
        if pd.notna(row["IndexI5"]) and str(row["IndexI5"]).strip():
            if not isinstance(row["IndexI5"], str) or not dna_pattern_strict.match(row["IndexI5"]):
                errors.append(f"Row {idx}: 'IndexI5' must be a valid DNA sequence (ACGT)")

        # AdapterRead1 / AdapterRead2 (optional, plus sign allowed)
        for field in ["AdapterRead1", "AdapterRead2"]:
            if pd.notna(row[field]) and str(row[field]).strip():
                if not isinstance(row[field], str) or not dna_pattern_plus.match(row[field]):
                    errors.append(f"Row {idx}: '{field}' must be a valid sequence (ACGT or '+')")

        # Conditional check: If IndexI5Name is present, IndexI5 must also be present and valid
        if pd.notna(row["IndexI5Name"]) and str(row["IndexI5Name"]).strip():
            if pd.isna(row["IndexI5"]) or not str(row["IndexI5"]).strip():
                errors.append(f"Row {idx}: 'IndexI5' must be present if 'IndexI5Name' is present")
            elif not dna_pattern_strict.match(str(row["IndexI5"])):
                errors.append(f"Row {idx}: 'IndexI5' must be a valid DNA sequence (ACGT) when 'IndexI5Name' is present")

    if not errors:
        return ValidationResult(
            name=name,
            message=f"Errors found in sample data: {errors}",
            severity=StatusLevel.ERROR
        )

    return ValidationResult(
        name=name,
        message="Run data is properly configured",
        severity=StatusLevel.INFO
    )



def override_cycles_pattern_validator(state_model: StateModel) -> ValidationResult:
    name: str = "override_cycles_pattern_validator"

    df = state_model.sample_df

    if "OverrideCyclesPattern" not in df.columns:
        return ValidationResult(
            name=name,
            message="Column 'OverrideCyclesPattern' not found, skipping validation.",
            severity=StatusLevel.INFO
        )

    pattern_reads = re.compile(r"^(Y\d+|N\d+|U\d+)*(Y+)(Y\d+|N\d+|U\d+)*$")
    pattern_indexes = re.compile(r"^(I\d+|N\d+|U\d+)*(I+)(I\d+|N\d+|U\d+)*$")

    errors: List[int] = []

    def validate(value):
        if not isinstance(value, str):
            return False
        parts = value.split('-')
        if len(parts) != 4:
            return False
        read1_pattern, index1_pattern, index2_pattern, read2_pattern = parts
        if not pattern_reads.fullmatch(read1_pattern):
            return False
        if not pattern_indexes.fullmatch(index1_pattern):
            return False
        if not pattern_indexes.fullmatch(index2_pattern):
            return False
        if not pattern_reads.fullmatch(read2_pattern):
            return False
        return True

    for idx, val in df["OverrideCyclesPattern"].items():
        if not validate(val):
            errors.append(idx)

    if errors:
        return ValidationResult(
            name=name,
            message=f"Errors found in overridecyclespatterns at rows: {errors}",
            severity=StatusLevel.ERROR
        )
    else:
        return ValidationResult(
            name=name,
            message="No errors found in overridecyclespatterns.",
            severity=StatusLevel.INFO
        )