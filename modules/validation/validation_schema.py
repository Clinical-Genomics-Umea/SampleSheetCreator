import pandas as pd
from pandera import DataFrameSchema, Column, Check, Index
import pandera as pa


def is_valid_lane_series(lane_series: pd.Series):
    lane_elements = [element.strip() for elements in lane_series.str.split(",") for element in elements]
    valid_series = pd.Series([all(check_lane_element(element) for element in elements) for elements in lane_elements])
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
    return pd.Series(input_series.isna() | input_series.str.contains(r'^[ATCG]*$'), dtype=bool)

def is_valid_used_cycles(series):
    """
    Validate a pandas Series containing strings composed of 'A', 'T', 'C', 'G', or NaN (empty).

    Args:
        series (pandas.Series): The input Series to validate.

    Returns:
        pandas.Series: A Series of boolean values indicating if each item meets the conditions.
    """
    # Create a mask to check for valid conditions
    mask = (series.isna()) | (series.str.match(r'^[ATCG]*$'))
    result = mask.astype(bool)

    return result

#
# def is_valid_used_cycles(series):
#     """
#     Validate a pandas Series where each item contains a string of 4 integers separated by semicolons.
#
#     Args:
#         series (pandas.Series): The input Series to validate.
#
#     Returns:
#         pandas.Series: A Series of boolean values indicating if each item meets the condition.
#     """
#     # Create a regex pattern to match the required format
#     pattern = r'^\d{1,3};\d{1,2};\d{1,2};\d{1,3}$'
#
#     # Use the str.match method to apply the regex pattern and return a boolean Series
#     result = series.str.match(pattern, na=False)
#
#     return result


def is_valid_used_cycles(series: pd.Series) -> pd.Series:
    """
    Validate a pandas Series where each item contains a string of 4 integers separated by semicolons.

    Args:
        series (pandas.Series): The input Series to validate.

    Returns:
        pandas.Series: A Series of boolean values indicating if each item meets the condition.
    """
    pattern = r'^\d{2,3};\d{1,2};\d{1,2};\d{1,3}$'
    return series.str.contains(pattern, na=False)


prevalidation_schema = DataFrameSchema(
    {
        "Lane": Column(str, checks=Check(is_valid_lane_series), nullable=False),
        "Sample_ID": Column(str, coerce=True,
                            unique=True,
                            nullable=False,
                            checks=pa.Check(lambda s: s.str.len() >= 5,
                                            error="Sample_ID is too short.")
                            ),
        "ProfileName": Column(str, coerce=True, nullable=True),
        "Plate": Column(str, coerce=True, nullable=True),
        "WellPos": Column(str, coerce=True, nullable=True),
        "I7_Plate": Column(str, coerce=True, nullable=True),
        "I7_WellPos": Column(str, coerce=True, nullable=True),
        "I5_Plate": Column(str, coerce=True, nullable=True),
        "I5_WellPos": Column(str, coerce=True, nullable=True),
        "I7_IndexName": Column(str, coerce=True, nullable=True),
        "I7_Index": Column(str,
                           checks=[pa.Check(lambda s: s.str.len() >= 8,
                                            error="Index is too short."),
                                   pa.Check(lambda s: s.str.len() <= 10,
                                            error="Index is too long."),
                                   pa.Check(lambda s: s.str.match(r'^[ATCG]*$'),
                                            error="Contains invalid characters. Only capital letters A, T, C, and G are allowed.")
                                   ],
                           nullable=False),

        "I5_IndexName": Column(str, coerce=True, nullable=True),
        "I5_Index": Column(str,
                           coerce=True,
                           nullable=True,
                           checks=[pa.Check(lambda s: s.str.len() >= 8,
                                            error="Index is too short."),
                                   pa.Check(lambda s: s.str.len() <= 10,
                                            error="Index is too long."),
                                   pa.Check(is_valid_i5_index,
                                            error="Contains invalid characters. Seq can be empty or contain only A, T, C, G.")
                                   ],
                           ),
        "UsedCycles": Column(str,
                             checks=pa.Check(is_valid_used_cycles,
                                             error="Invalid used cycles string"),
                             coerce=True,
                             nullable=False),
        "BarcodeMismatchesIndex1": Column(int,
                                          checks=Check.in_range(0, 4,
                                                                include_min=True,
                                                                include_max=True)
                                          ),
        "BarcodeMismatchesIndex2": Column(int,
                                          checks=Check.in_range(0, 4,
                                                                include_min=True,
                                                                include_max=True)
                                          ),

        "AdapterRead1": Column(str,
                               coerce=True,
                               nullable=True,
                               checks=pa.Check(lambda s: s.str.len() >= 10,
                                            error="Index is too short")
                               ),
        "AdapterRead2": Column(str, coerce=True, nullable=True),
        "FastqCompressionFormat": Column(str, coerce=True, nullable=True),
        "Pipeline": Column(str, coerce=True, nullable=True),
        "ReferenceGenomeDir": Column(str, coerce=True, nullable=True),
        "VariantCallingMode": Column(str, coerce=True, nullable=True),
    },
    index=Index(int),
    strict=True,
    coerce=True,
)
