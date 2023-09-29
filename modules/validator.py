import json

from pydantic import BaseModel, validator
from typing import List
import numpy as np
import pandas as pd
import pandera as pa


# Example 2D NumPy array with strings
def compare_rows(row1: np.array, row2: np.array):
    return np.sum(row1 != row2)

# validator models

def validate_unique(value):
    if not all(value):
        raise ValueError('All rows in the "Sample_ID" column must contain values')
    if len(set(value)) != len(value):
        raise ValueError('All values in the "Sample_ID" column must be unique')
    return value


def validate_string_numbers(value):
    rows = value.split(',')
    for row in rows:
        if not row.strip().isdigit():
            raise ValueError('All rows in the "Lane" column must contain numbers')

        if row.strip().isalpha():
            raise ValueError('Rows in the "Lane" column must cannot contain letters')

    return value


def validate_dna_mismatches(value_series):
    min_length = value_series.apply(len).min()
    truncated_df = value_series.apply(lambda x: x[:min_length])

    truncated_np_array = truncated_df.apply(list).apply(np.array).to_numpy()
    dna_mismatches = np.vectorize(compare_rows)(truncated_np_array[:, None], truncated_np_array)

    row_indices, col_indices = np.where((dna_mismatches < 4) &
                                        (np.arange(dna_mismatches.shape[0]) != np.arange(dna_mismatches.shape[0])[:,
                                                                               np.newaxis]))

    if row_indices:
        mismatch_le_4 = dna_mismatches[row_indices, col_indices]
        indices_pairs = list(zip(row_indices, col_indices))

        simlilar_indexes = [
            {"row_1": row, "row_2": col, "count": mismatch_count}
            for mismatch_count, (row, col) in zip(mismatch_le_4, indices_pairs)
        ]
        result = json.dumps(simlilar_indexes)
        raise ValueError(f'Indexes with mismatches greater than 4: {result}')

    return value_series


class PydanticDataModel(BaseModel):
    lane: str

    @validator('lane')
    def validate_lane(cls, value):
        rows = value.split(',')
        for row in rows:
            if not row.strip().isdigit():
                raise ValueError('All rows in the "Lane" column must contain numbers')
        return value

    sample_id: List[str]

    @validator('sample_id')
    def validate_sample_id(cls, value):
        if not all(value):
            raise ValueError('All rows in the "Sample_ID" column must contain values')
        if len(set(value)) != len(value):
            raise ValueError('All values in the "Sample_ID" column must be unique')
        return value








#- Lane
#- Sample_ID
#- ProfileName
#- Plate
#- WellPos
#- I7_Plate
#- I7_WellPos
#- I5_Plate
#- I5_WellPos
#- I7_IndexName
#- I7_Index
#- I5_IndexName
#- I5_Index
#- UsedCycles
#- BarcodeMismatchesIndex1
#- BarcodeMismatchesIndex2
#- AdapterRead1
#- AdapterRead2
#- FastqCompressionFormat
#- Pipeline
#- ReferenceGenomeDir
#- VariantCallingMode