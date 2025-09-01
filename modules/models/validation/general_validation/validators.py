"""Module containing validator functions for sample data pre-validation."""
from typing import Any, Dict, List, Optional, Set, Tuple
import re
import ast
import pandas as pd
from pathlib import Path

from modules.models.export.samplesheet_v1 import samplesheet_v1
from modules.models.state.state_model import StateModel
from modules.models.application.application_manager import ApplicationManager
from modules.models.validation.application_validator import application_settings_check
from modules.models.validation.validation_result import ValidationResult, StatusLevel
from modules.utils.utils import is_list_of_ints_string, explode_df_lane_column,  \
    explode_df_application_profile_column
from modules.views.statusbar.status import StatusBar



def check_sample_dataframe_overall_consistency(sample_df: pd.DataFrame) -> ValidationResult:
    name = "sample dataframe overall check"

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


def lanes_general_check(sample_df: pd.DataFrame, allowed_lanes: List[int]) -> ValidationResult:
    """
    Validate that all lane values in the sample sheet are within the allowed range.

    Args:
        state_model: The application state model containing sample data and configuration

    Returns:
        ValidationResult: Result of the lane validation check
    """
    name = "lanes general check"

    # Input validation
    if sample_df is None:
        return ValidationResult(
            name=name,
            message="No sample data available for validation",
            severity=StatusLevel.ERROR
        )

    if not allowed_lanes:
        return ValidationResult(
            name=name,
            message="No allowed lanes configuration provided",
            severity=StatusLevel.ERROR
        )

    if "Lane" not in sample_df.columns:
        return ValidationResult(
            name=name,
            message="Required 'Lane' column is missing from sample data",
            severity=StatusLevel.ERROR
        )

    if sample_df["Lane"].isna().all():
        return ValidationResult(
            name=name,
            message="No lane information found in the sample sheet",
            severity=StatusLevel.ERROR
        )

    for idx, row in sample_df.iterrows():
        if not isinstance(row["Lane"], list):
            return ValidationResult(
                name=name,
                message="Lane data in row " + str(idx + 1) + " must be a list",
                severity=StatusLevel.ERROR
            )
        for value in row["Lane"]:
            if not isinstance(value, int):
                return ValidationResult(
                    name=name,
                    message="Lane values in row " + str(idx + 1) + " must be integers",
                    severity=StatusLevel.ERROR
                )

    # Process lane values
    invalid_rows = []
    allowed_lanes_set = set(allowed_lanes)

    used_lanes = set()

    for idx, row in sample_df.iterrows():
        lanes_list = row["Lane"]

        # If it's a string, try to evaluate it as a list
        try:
            lanes_set = set(lanes_list)

            used_lanes.update(lanes_set)

            if not lanes_set.issubset(allowed_lanes_set):
                invalid_rows.append(
                    f"Row {row + 1}: Lane values {lanes_list} not in allowed range {sorted(allowed_lanes_set)}")
        except Exception as e:
            invalid_rows.append(f"Row {row + 1}: Error processing lane values: {str(e)}")

    # Report any validation errors
    if invalid_rows:
        error_msg = "Invalid lane values found:\n"
        error_msg += "\n".join(f"  • {row}" for row in invalid_rows[:10])
        if len(invalid_rows) > 10:
            error_msg += "\n  ... (more errors not shown)"

        return ValidationResult(
            name=name,
            message=error_msg,
            severity=StatusLevel.ERROR
        )

    if used_lanes != allowed_lanes_set:
        return ValidationResult(
            name=name,
            message=f"Some flowcell lanes are not used in the sample sheet: {sorted(allowed_lanes_set - used_lanes)}. But no errors were found",
            severity=StatusLevel.WARNING
        )

    # All lanes are valid
    return ValidationResult(
        name=name,
        message=f"All lane(s) in the sample sheet are within the allowed range",
        severity=StatusLevel.INFO
    )


def lane_sample_uniqueness_check(sample_df: pd.DataFrame) -> ValidationResult:

    name = "lane sample uniqueness check"

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

        duplicates = df_lane_exploded[df_lane_exploded.duplicated(subset=["Sample_ID", "Lane"], keep=False)]

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



def overall_sample_data_validator(sample_df: pd.DataFrame) -> ValidationResult:

    name = "overall_sample_data_validator"

    errors = []

    # --- Full schema ---
    all_fields = [
        "Lane", "Sample_ID", "Pos", "IndexI7Name", "IndexI7",
        "IndexI5Name", "IndexI5", "IndexKitName", "OverrideCyclesPattern",
        "BarcodeMismatchesIndex1", "BarcodeMismatchesIndex2",
        "AdapterRead1", "AdapterRead2", "ApplicationProfileName"
    ]
    required_fields = ["Lane", "Sample_ID", "IndexI7", "ApplicationProfileName"]

    # --- Column presence check ---
    missing_columns = [col for col in all_fields if col not in sample_df.columns]
    if missing_columns:
        return ValidationResult(
            name=name,
            message=f"Sample data has missing columns: {missing_columns}",
            severity=StatusLevel.ERROR
        )

    # Patterns
    dna_pattern_strict = re.compile(r"^[ACGT]+$", re.IGNORECASE)  # For IndexI7 / IndexI5
    dna_pattern_plus = re.compile(r"^[ACGT+]+$", re.IGNORECASE)  # For AdapterRead1 / AdapterRead2

    for idx, row in sample_df.iterrows():


        lane = row["Lane"]
        sample_id = row["Sample_ID"].strip()
        index_i7_name = row["IndexI7Name"].strip()
        index_i7 = row["IndexI7"].strip()
        application_profile = row["ApplicationProfileName"]
        index_i5_name = row["IndexI5Name"].strip()
        index_i5 = row["IndexI5"].strip()
        adapter_read1 = row["AdapterRead1"].strip()
        adapter_read2 = row["AdapterRead2"].strip()
        barcode_mismatches_index1 = row["BarcodeMismatchesIndex1"]
        barcode_mismatches_index2 = row["BarcodeMismatchesIndex2"]

        # Lane: must be list of ints (required)

        if not isinstance(lane, list):
            errors.append(f"Row {idx+1}: 'Lane' must be a list of ints")
            continue
        else:
            if not all(isinstance(x, int) for x in lane):
                errors.append(f"Row {idx+1}: 'Lane' must be a list of ints")
                continue

        if not isinstance(barcode_mismatches_index1, int):
            errors.append(f"Row {idx+1}: 'BarcodeMismatchesIndex1' must be an int")
            continue

        if not isinstance(barcode_mismatches_index2, int):
            errors.append(f"Row {idx+1}: 'BarcodeMismatchesIndex2' must be an int")

        # Lane: must be list of ints (required)
        if not all(isinstance(x, int) for x in lane):
            errors.append(f"Row {idx+1}: 'Lane' must be a list of ints")
            continue

        # Sample_ID: non-empty string (required)
        if not sample_id:
            errors.append(f"Row {idx+1}: 'Sample_ID' must be a non-empty string")
            continue

        # IndexI7: DNA sequence (required, strict)
        if not index_i7 or not dna_pattern_strict.match(index_i7):
            errors.append(f"Row {idx+1}: 'IndexI7' must be a valid DNA sequence (ACGT)")

        # ApplicationProfile: list of strings (required)
        if not application_profile or not all(isinstance(x, str) for x in application_profile):
            errors.append(f"Row {idx+1}: 'ApplicationProfile' must be a list of strings")

        # IndexI5 (optional but strict if present)
        if index_i5:
            if not dna_pattern_strict.match(index_i5):
                errors.append(f"Row {idx+1}: 'IndexI5' must be a valid DNA sequence (ACGT)")

        if index_i5_name:
            if not dna_pattern_strict.match(index_i5):
                errors.append(f"Row {idx+1}: 'IndexI5' must be a valid DNA sequence (ACGT) when 'IndexI5Name' is present")

        if adapter_read1:
            if not dna_pattern_plus.match(adapter_read1):
                errors.append(f"Row {idx+1}: 'AdapterRead1' if exists must be a valid sequence (ACGT or '+')")

        if adapter_read2:
            if not dna_pattern_plus.match(adapter_read2):
                errors.append(f"Row {idx+1}: 'AdapterRead2' if exists must be a valid sequence (ACGT or '+')")

        # Conditional check: If IndexI5Name is present, IndexI5 must also be present and valid

    if errors:
        return ValidationResult(
            name=name,
            message=f"Errors found in sample data:\n {"\n".join(errors)}",
            severity=StatusLevel.ERROR
        )

    return ValidationResult(
        name=name,
        message="Run data is properly configured",
        severity=StatusLevel.INFO
    )


def override_cycles_pattern_validator(sample_df) -> ValidationResult:

    name: str = "override_cycles_pattern_validator"

    if "OverrideCyclesPattern" not in sample_df.columns:
        return ValidationResult(
            name=name,
            message="Column 'OverrideCyclesPattern' not found, must be present.",
            severity=StatusLevel.ERROR
        )

    pattern_reads = re.compile(r"^(Y\d+|N\d+|U\d+|Y{r})$")
    pattern_indexes = re.compile(r"^(I\d+|N\d+|U\d+|I{i})$")

    errors: List[str] = []

    for idx, val in sample_df["OverrideCyclesPattern"].items():

        if not isinstance(val, str):
            errors.append(f"Row {idx+1}: 'OverrideCyclesPattern' must be a string")
            continue

        parts = val.split('-')
        if len(parts) != 4:
            errors.append(f"Row {idx+1}: 'OverrideCyclesPattern' must be a string of the form 'R1-I1-I2-R2'")
            continue

        read1_pattern, index1_pattern, index2_pattern, read2_pattern = parts

        if not pattern_reads.fullmatch(read1_pattern):
            errors.append(f"Row {idx+1}: 'read1_pattern' must be a valid read pattern")

        if not pattern_indexes.fullmatch(index1_pattern):
            errors.append(f"Row {idx+1}: 'index1_pattern' must be a valid read pattern")

        if not pattern_indexes.fullmatch(index2_pattern):
            errors.append(f"Row {idx+1}: 'index2_pattern' must be a valid read pattern")

        if not pattern_reads.fullmatch(read2_pattern):
            errors.append(f"Row {idx+1}: 'read2_pattern' must be a valid read pattern")


    if errors:
        return ValidationResult(
            name=name,
            message=f"Errors found in override cycles patterns at rows: \n{"\n".join(errors)}",
            severity=StatusLevel.ERROR
        )
    else:
        return ValidationResult(
            name=name,
            message="No errors found in override cycles patterns.",
            severity=StatusLevel.INFO
        )


def index_len_run_cycles_check(sample_df, index1_cycles, index2_cycles) -> ValidationResult:
    name: str = "index length run cycles check"

    errors: List[str] = []

    for idx, row in sample_df.iterrows():
        i7 = row["IndexI7"]
        i5 = row["IndexI5"]

        i7_len = None
        i5_len = None

        try:
            i7_len = len(i7.strip())
        except TypeError:
            errors.append(f"Row {idx+1}: 'IndexI7' must be a string")

        try:
            i5_len = len(i5.strip())
        except TypeError:
            errors.append(f"Row {idx+1}: 'IndexI5' must be a string")


        if i7_len:
            if index1_cycles < i7_len:
                errors.append(f"Row {idx+1}: 'IndexI7' length ({i7_len}) longer than 'Index1Cycles' ({index1_cycles})")

        if i5_len:
            if index2_cycles < i5_len:
                errors.append(f"Row {idx+1}: 'IndexI5' length ({i5_len}) longer than 'Index2Cycles' ({index2_cycles})")

    if errors:
        return ValidationResult(
            name=name,
            message=f"Index length errors at rows: \n{"\n".join(errors)}",
            severity=StatusLevel.ERROR
        )
    else:
        return ValidationResult(
            name=name,
            message="No errors found for index lengths.",
            severity=StatusLevel.INFO
        )


def index_pair_uniqueness_check(sample_df: pd.DataFrame) -> ValidationResult:
    name = "index pair uniqueness check"

    # First, explode the Lane column to get one row per sample-lane combination
    df_exploded = sample_df.explode('Lane').reset_index(drop=True)

    lane_conflicts = []

    # Group by lane to check uniqueness within each lane
    for lane, lane_group in df_exploded.groupby('Lane'):

        # Get all samples in this lane
        samples = lane_group.to_dict('records')

        # Compare each pair of samples in the lane
        for i, sample1 in enumerate(samples):
            for j, sample2 in enumerate(samples):
                if i >= j:  # Skip duplicate comparisons and self-comparison
                    continue

                # Get index sequences
                idx1_i7 = str(sample1['IndexI7']).strip().upper()
                idx1_i5 = str(sample1['IndexI5']).strip().upper()
                idx2_i7 = str(sample2['IndexI7']).strip().upper()
                idx2_i5 = str(sample2['IndexI5']).strip().upper()

                # Compare up to shortest common length for each index
                min_len_i7 = min(len(idx1_i7), len(idx2_i7))
                min_len_i5 = min(len(idx1_i5), len(idx2_i5))

                i7_match = idx1_i7[:min_len_i7] == idx2_i7[:min_len_i7] if min_len_i7 > 0 else True
                i5_match = idx1_i5[:min_len_i5] == idx2_i5[:min_len_i5] if min_len_i5 > 0 else True

                # If both indexes match up to their common length, it's a conflict
                if i7_match and i5_match:
                    conflict = f"{sample1["Sample_ID"]} and {sample2["Sample_ID"]} have the same index pair in lane {lane}"
                    lane_conflicts.append(conflict)

    if lane_conflicts:
        return ValidationResult(
            name=name,
            message=f"Index length errors at rows: \n{"\n".join(lane_conflicts)}",
            severity=StatusLevel.ERROR
        )

    return ValidationResult(
        name=name,
        message="No errors found for index lengths.",
        severity=StatusLevel.INFO
    )