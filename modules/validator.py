import json
import numpy as np
import pandas as pd
import pandera as pa
from pandera import String, Int, Column, Field, DataFrameSchema, Check, Index
import pandera.extensions as extensions


def compare_rows(row1: np.array, row2: np.array):
    return np.sum(row1 != row2)


def valid_sequence_set(series):
    min_length = series.apply(len).min()
    truncated_df = series.apply(lambda x: x[:min_length])

    truncated_np_array = truncated_df.apply(list).apply(np.array).to_numpy()
    dna_mismatches = np.vectorize(compare_rows)(truncated_np_array[:, None], truncated_np_array)

    row_indices, col_indices = np.where((dna_mismatches < 4) &
                                        (np.arange(dna_mismatches.shape[0]) != np.arange(dna_mismatches.shape[0])[:,
                                                                               np.newaxis]))

    res = [True] * dna_mismatches.shape[0]

    if len(row_indices) > 0:
        for i in row_indices:
            res[i] = False

    return pd.Series(res)


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


# Lane validation

def check_lane_element(element):
    return 0 <= int(element) <= 8 if element.isdigit() else False


def is_valid_lane(lane_string: str):
    lane_string.replace(" ", "")
    elements = lane_string.split(",")

    res = [check_lane_element(element) for element in elements]
    return all(res)


def is_valid_lane_series(lane_series: pd.Series):
    return lane_series.apply(is_valid_lane)


first_validation_schema = DataFrameSchema(
    {
        "Lane": Column(str, checks=Check(is_valid_lane_series), nullable=False),
        "Sample_ID": Column(str, coerce=True, unique=True, nullable=False),
        "ProfileName": Column(str, coerce=True, nullable=True),
        "Plate": Column(str, coerce=True, nullable=True),
        "WellPos": Column(str, coerce=True, nullable=True),
        "I7_Plate": Column(str, coerce=True, nullable=True),
        "I7_WellPos": Column(str, coerce=True, nullable=True),
        "I5_Plate": Column(str, coerce=True, nullable=True),
        "I5_WellPos": Column(str, coerce=True, nullable=True),
        "I7_IndexName": Column(str, coerce=True, nullable=True),
        "I7_Index": Column(str, checks=[Check.str_length(min_value=8, max_value=10),
                                        # Check(valid_sequence_set)
                                        ]),

        # "I7_Index": Column(str, coerce=True, nullable=True),
        "I5_IndexName": Column(str, coerce=True, nullable=True),
        "I5_Index": Column(str, coerce=True, nullable=True),
        "UsedCycles": Column(str, coerce=True, nullable=True),
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

        "AdapterRead1": Column(str, coerce=True, nullable=True),
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

# - Lane
# - Sample_ID
# - ProfileName
# - Plate
# - WellPos
# - I7_Plate
# - I7_WellPos
# - I5_Plate
# - I5_WellPos
# - I7_IndexName
# - I7_Index
# - I5_IndexName
# - I5_Index
# - UsedCycles
# - BarcodeMismatchesIndex1
# - BarcodeMismatchesIndex2
# - AdapterRead1
# - AdapterRead2
# - FastqCompressionFormat
# - Pipeline
# - ReferenceGenomeDir
# - VariantCallingMode

if __name__ == "__main__":
    print("hej")
