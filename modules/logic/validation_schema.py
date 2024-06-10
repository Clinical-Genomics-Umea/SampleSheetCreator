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


def is_valid_used_cycles(series: pd.Series) -> pd.Series:
    """
    Validate a pandas Series where each item contains a string of 4 integers separated by semicolons.

    Args:
        series (pandas.Series): The input Series to validate.

    Returns:
        pandas.Series: A Series of boolean values indicating if each item meets the condition.
    """
    pattern = r'^\d{1,3}-\d{1,2}-\d{1,2}-\d{1,3}$'
    return series.str.contains(pattern, na=False)


def check_index_combination_uniqueness(df: pd.DataFrame) -> pd.Series:
    # Group by 'Index_I7' and 'Index_I5' and check the number of unique 'Sample_ID's
    return df.groupby(['Index_I7', 'Index_I5'])['Sample_ID'].nunique() <= 1


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

    print(df.groupby(['Lane', 'Sample_ID']).size().eq(1))

    return df.groupby(['Lane', 'Sample_ID']).size().eq(1)

prevalidation_schema = DataFrameSchema(
    {
        "Lane": Column(int, nullable=False),
        "Sample_ID": Column(str, coerce=True,
                            unique=False,
                            nullable=False,
                            checks=pa.Check(lambda s: s.str.len() >= 3,
                                            error="Sample_ID is too short.")
                            ),
        "FixedPos": Column(str, coerce=True, nullable=True),
        "Name_I7": Column(str, coerce=True, nullable=True),
        "Index_I7": Column(str,
                           checks=[pa.Check(lambda s: s.str.len() >= 8,
                                            error="Index is too short."),
                                   pa.Check(lambda s: s.str.len() <= 10,
                                            error="Index is too long."),
                                   pa.Check(lambda s: s.str.match(r'^[ATCG]*$'),
                                            error="Contains invalid characters. Only capital letters A, T, C, and G are allowed.")
                                   ],
                           nullable=False),

        "Name_I5": Column(str, coerce=True, nullable=True),
        "Index_I5": Column(str,
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
        "Index_I5_RC": Column(str,
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
        "IndexDefinitionKitName": Column(str, coerce=True, nullable=True),
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
        "Application": Column(str, coerce=True, nullable=True),
        "ApplicationProfile": Column(str, coerce=True, nullable=True),
        "ApplicationSettings": Column(str, coerce=True, nullable=True),
        "ApplicationData": Column(str, coerce=True, nullable=True),
        "ApplicationDataFields": Column(str, coerce=True, nullable=True),
        "SoftwareVersion": Column(str, coerce=True, nullable=False)
    },
    checks=[pa.Check(
                check_index_combination_uniqueness,
                element_wise=False,
                error="Combination of Index_I7 and Index_I5 is not unique across different Sample_ID."
            ),
            pa.Check(
                check_combination_uniqueness,
                element_wise=False,
                error="Sample_ID is duplicated within the same Lane."
            )
    ],
    index=Index(int),
    strict=True,
    coerce=True,
)
