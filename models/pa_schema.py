from typing import Any

import pandas as pd
from pandera import DataFrameSchema, Column, Check, Index
import pandera as pa

from utils.utils import int_str_to_int_list


def is_valid_lane_series(lane_series: pd.Series):
    lane_elements = [
        element.strip()
        for elements in lane_series.str.split(",")
        for element in elements
    ]
    valid_series = pd.Series(
        [
            all(check_lane_element(element) for element in elements)
            for elements in lane_elements
        ]
    )
    return valid_series


def check_lane_element(element):
    return 0 <= int(element) <= 8 if element.isdigit() else False


def is_valid_i5_index(input_series: pd.Series):
    """
    Validate a pandas Series containing strings composed of 'A', 'T', 'C', 'G', or NaN (empty).

    Args:
        input_series (pandas.Series): The input Series to validate.

    Returns:
        pandas.Series: A Series of boolean values indicating if each item meets the conditions.
    """
    return pd.Series(
        input_series.isna() | input_series.str.contains(r"^[ATCG]*$"), dtype=bool
    )


def is_valid_lane_entry(series: pd.Series) -> pd.Series:
    """
    Check if each element in the series can be converted to an integer
    or a list of integers.
    """

    def check_value(value):

        # Check if it's an integer
        if isinstance(value, int):
            return True

        # Check if it's a string representation of an integer
        if isinstance(value, str) and value.isdigit():
            return True

        # Check if it's a string representation of a list of integers
        if isinstance(value, str):
            parsed_value = int_str_to_int_list(value)
            if isinstance(parsed_value, list) and all(
                isinstance(i, int) for i in parsed_value
            ):
                return True

        return False

    return series.apply(check_value)


def is_valid_used_cycles(series: pd.Series) -> pd.Series:
    """
    Validate a pandas Series where each item contains a string of 4 integers separated by semicolons.

    Args:
        series (pandas.Series): The input Series to validate.

    Returns:
        pandas.Series: A Series of boolean values indicating if each item meets the condition.
    """
    pattern = r"^\d{1,3}-\d{1,2}-\d{1,2}-\d{1,3}$"
    return series.str.contains(pattern, na=False)


def check_index_combination_uniqueness(df: pd.DataFrame) -> pd.Series:
    # Group by 'Index_I7' and 'Index_I5' and check the number of unique 'Sample_ID's
    return df.groupby(["IndexI7", "IndexI5"])["Sample_ID"].nunique() <= 1


def check_combination_uniqueness(df: pd.DataFrame) -> pd.Series:
    """
    Check if all combinations of items in two columns are unique.

    Args:
        df (pandas.DataFrame): The input DataFrame.
        col1 (str): The name of the first column.
        col2 (str): The name of the second column.

    Returns:
        pandas.Series: A Series of boolean values indicating if each combination is unique.
    """

    # print(df.groupby(['Lane', 'Sample_ID']).size().eq(1))

    return df.groupby(["Lane", "Sample_ID"]).size().eq(1)


prevalidation_schema = DataFrameSchema(
    {
        "Lane": Column(nullable=False, unique=False),
        "Sample_ID": Column(
            str,
            coerce=True,
            unique=False,
            nullable=False,
            checks=pa.Check(
                lambda s: s.str.len() >= 3, error="Sample_ID is too short."
            ),
        ),
        "FixedPos": Column(str, coerce=True, nullable=True),
        "IndexI7Name": Column(str, coerce=True, nullable=True),
        "IndexI7": Column(
            str,
            checks=[
                pa.Check(lambda s: s.str.len() >= 8, error="Index is too short."),
                pa.Check(lambda s: s.str.len() <= 10, error="Index is too long."),
                pa.Check(
                    lambda s: s.str.match(r"^[ATCG]*$"),
                    error="Contains invalid characters. Only capital letters A, T, C, and G are allowed.",
                ),
            ],
            nullable=False,
        ),
        "IndexI5Name": Column(str, coerce=True, nullable=True),
        "IndexI5": Column(
            str,
            coerce=True,
            nullable=True,
            checks=[
                pa.Check(lambda s: s.str.len() >= 8, error="Index is too short."),
                pa.Check(lambda s: s.str.len() <= 10, error="Index is too long."),
                pa.Check(
                    is_valid_i5_index,
                    error="Contains invalid characters. Seq can be empty or contain only A, T, C, G.",
                ),
            ],
        ),
        "IndexI5RC": Column(
            str,
            coerce=True,
            nullable=True,
            checks=[
                pa.Check(lambda s: s.str.len() >= 8, error="Index is too short."),
                pa.Check(lambda s: s.str.len() <= 10, error="Index is too long."),
                pa.Check(
                    is_valid_i5_index,
                    error="Contains invalid characters. Seq can be empty or contain only A, T, C, G.",
                ),
            ],
        ),
        "BarcodeMismatchesIndex1": Column(
            int, checks=Check.in_range(0, 4, include_min=True, include_max=True)
        ),
        "BarcodeMismatchesIndex2": Column(
            int, checks=Check.in_range(0, 4, include_min=True, include_max=True)
        ),
        "OverrideCyclesPattern": Column(str, coerce=True, nullable=True),
        "IndexKitDefinitionName": Column(str, coerce=True, nullable=True),
        "ApplicationName": Column(str, coerce=True, nullable=True),
    },
    checks=[
        pa.Check(
            check_index_combination_uniqueness,
            element_wise=False,
            error="Combination of Index_I7 and Index_I5 is not unique across different Sample_ID.",
        ),
        pa.Check(
            check_combination_uniqueness,
            element_wise=False,
            error="Sample_ID is duplicated within the same Lane.",
        ),
    ],
    index=Index(int),
    strict=True,
    coerce=True,
)
