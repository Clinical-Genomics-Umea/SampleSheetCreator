#! python
# -*- coding: utf-8 -*-

import re
import numpy as np
import pandas as pd
from pandas_schema import Column, Schema
from pandas_schema.validation import CustomElementValidation, LeadingWhitespaceValidation, TrailingWhitespaceValidation, \
    CanConvertValidation, MatchesPatternValidation, IsDistinctValidation, InRangeValidation, InListValidation
from jellyfish import *


class IsDistinctValidationMod(IsDistinctValidation):
    def __init__(self):
        super().__init__()

    def validate(self, series: pd.Series) -> pd.Series:
        return ~series.duplicated(keep=False)

#
# class OnlyOneValueValidation(IsDistinctValidation):
#     def __init__(self):
#         super().__init__()
#
#     def validate(self, series: pd.Series) -> pd.Series:
#         ### index starts with 1, therefore series[1] ###
#         first_value = series[1]
#         print("only_one_value")
#         print(first_value)
#         print(series.isin([first_value]))
#         return series.isin([first_value])


def hamming(a, b):
    return len([i for i in filter(lambda x: x[0] != x[1], zip(a, b))])


def validate_df(df, model_fields_dict):

    def isempty(row):
        totlen = 0
        for item in row:
            totlen += len(str(item))
        if totlen == 0:
            return False
        else:
            return True

    res = df.apply(isempty, axis=1)
    df_populated_rows = df[res.values]

    print("validating ..")

    model_fields_dict = model_fields_dict

    str_validation = CustomElementValidation(lambda d: len(str(d)) > 0, 'value is too short')
    null_validation = CustomElementValidation(lambda d: d is not np.nan, 'this field cannot be null')

    def complex_validation_func_group(x):
        pattern1 = "^$|^\d$"
        p = re.compile(pattern1)
        res1 = p.search(x)
        if res1:
            return True

        pattern2 = "^(\d),(\d)$"
        p = re.compile(pattern2)
        res2 = p.search(x)
        if res2:
            val1 = res2.group(1)
            val2 = res2.group(2)
            if val1 != val2:
                return True

        return False

    complex_validation_group = CustomElementValidation(complex_validation_func_group, 'multiple groups must be different')

    validator_list = list()

    for field, subdict in model_fields_dict.items():
        print("adding validator functions,", field)
        validator_functions = []

        if subdict['required']:
            validator_functions.append(str_validation)
            validator_functions.append(null_validation)

        if not subdict['duplicates_ok']:
            validator_functions.append(IsDistinctValidationMod())

        if subdict['value_constraints']:
            validator_functions.append(InListValidation(subdict['value_constraints']))

        if subdict['value_validate_regex']:
            validator_functions.append(MatchesPatternValidation(subdict['value_validate_regex']))

        if not subdict['multiple_values_ok']:
            unique_values = list(df_populated_rows[field].unique())
            print(field, unique_values)
            validator_functions.append(InListValidation([unique_values[0]], "Multiple values not allowed in field"))

        if len(validator_functions) == 0:
            validator_list.append(Column(field, allow_empty=True))
        else:
            validator_list.append(Column(field, validator_functions))

    print("done adding functions ...")

    schema = Schema(validator_list)

    errors = schema.validate(df_populated_rows)

    for error in errors:
        print(error)

    for index, value in df_populated_rows['index+index2'].items():
        values = []
        for index_2, value_2 in df_populated_rows['index+index2'].items():
            if index != index_2:
                if len(str(value)) > 3 and len(str(value_2)) > 3:
                    print(str(index), str(value), str(index_2), str(value_2))
                    if len(value) == len(value_2):
                        values.append(hamming_distance(value, value_2))
                    else:
                        values.append(-1)

        if values:
            mval = min(values)
            if 0 <= mval < 3:
                outstr = "{row: " + str(index) + ", column: \"index+index2\"}: \"" + str(mval) + "\" indices too similar (<3)"
                errors.append(outstr)
            if mval < 0:
                outstr = "{row: " + str(index) + ", column: \"index+index2\"}: \"dist " + str(mval) + "\" indices have different lengths"
                errors.append(outstr)
        else:
            outstr = "{row: " + str(index) + ", column: \"index+index2\"}: \"no_hamming\" no_hamming distances were found"
            errors.append(outstr)

    return errors
