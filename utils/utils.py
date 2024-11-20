from PySide6.QtGui import QStandardItemModel, QStandardItem

import pandas as pd
import numpy as np
import yaml
import json
import uuid6
import re


def uuid():
    return str(uuid6.uuid7())


def int_str_to_int_list(int_str):
    int_str_list = list(re.findall(r"\d+", int_str))
    int_list = map(int, int_str_list)
    return list(int_list)


def int_list_to_int_str(int_list):
    int_str = ", ".join(map(str, int_list))

    return f"[{int_str}]"


def explode_lane_column(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Explode a list-like column into separate rows.

    :param dataframe: DataFrame containing the list-like column
    :return: Exploded DataFrame
    """
    dataframe["Lane"] = dataframe["Lane"].apply(int_str_to_int_list)
    exploded_dataframe = dataframe.explode("Lane")
    # exploded_dataframe["Lane"] = exploded_dataframe["Lane"].astype(int)
    return exploded_dataframe


def dataframe_to_qstandarditemmodel(dataframe):
    """
    Convert a Pandas DataFrame to a QStandardItemModel.

    :param dataframe: Pandas DataFrame to convert.
    :return: QStandardItemModel representing the DataFrame.
    """
    model = QStandardItemModel()

    # Set the column headers as the model's horizontal headers
    model.setHorizontalHeaderLabels(dataframe.columns)

    for row_index, row_data in dataframe.iterrows():
        row_items = [QStandardItem(str(item)) for item in row_data]
        model.appendRow(row_items)

    return model


def reverse_complement(seq):
    complement = str.maketrans("ATCG", "TAGC")
    return seq.translate(complement)[::-1]


def model_to_dataframe(model):
    if not isinstance(model, QStandardItemModel):
        raise ValueError("Input must be a QStandardItemModel")

    column_names = [
        model.horizontalHeaderItem(i).text() for i in range(model.columnCount())
    ]
    df = pd.DataFrame(columns=column_names)

    for row_index in range(model.rowCount()):
        row_data = [
            model.item(row_index, col_index).text()
            for col_index in range(model.columnCount())
        ]
        df.loc[row_index] = row_data

    df = df.replace("", np.nan).dropna(how="all").reset_index(drop=True)
    df["Index_I5_RC"] = df["Index_I5"].apply(reverse_complement)

    return df


def read_yaml_file(yaml_path_obj):
    # Get the path to the directory of the current module

    try:
        with yaml_path_obj.open() as fp:
            # Load YAML data from the file
            data = yaml.safe_load(fp)
        return data
    except FileNotFoundError:
        return None
    except Exception as e:
        return None


def decode_bytes_json(data):
    """
    Decode bytes to JSON.

    Args:
        data (bytes): The bytes data to decode.

    Returns:
        dict: The decoded JSON data.

    Raises:
        ValueError: If there is an error decoding the JSON data.

    """
    try:
        decoded_data = bytes(data).decode()
        return json.loads(decoded_data)
    except json.JSONDecodeError as e:
        raise ValueError("Error decoding JSON data") from e
