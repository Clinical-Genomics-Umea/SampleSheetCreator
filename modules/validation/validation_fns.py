import re

import numpy as np
import pandas as pd
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QVBoxLayout, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt

pd.set_option('future.no_silent_downcasting', True)


def explode_df_by_lane(df):
    exploded_df = df.assign(Lane=df['Lane'].str.split(',')).explode('Lane')
    exploded_df['Lane'] = exploded_df['Lane'].astype(int)
    return exploded_df


# def compare_rows(row1: np.array, row2: np.array):
#     return np.sum(row1 != row2)

def compare_rows(row1: np.array, row2: np.array):
    min_length = min(row1.size, row2.size)
    return np.sum(row1[:min_length] != row2[:min_length])


def row_differences(row1: np.array, row2: np.array):
    print(row1)
    print(row2)

    mask = np.logical_and(~np.isnan(row1), ~np.isnan(row2))

    print(mask)

    return np.sum(row1[mask] != row2[mask])


def string_to_ndarray(x):
    array = np.full(10, np.nan, dtype=object)
    array[:len(x)] = list(x)
    return array


def append_arrays(arr1, arr2):
    return np.append(arr1, arr2)


def get_base(string, index):

    if index >= len(string):
        return np.nan
    else:
        return string[index]


def concatenate_indexes(df, i7_maxlen, i5_maxlen, i7_colname, i5_colname, id_name) -> pd.DataFrame:
    i7_names = [f"I7_{i + 1}" for i in range(i7_maxlen)]
    i5_names = [f"I5_{i + 1}" for i in range(i5_maxlen)]

    i7_df = df[i7_colname].apply(lambda x: pd.Series(get_base(x, i) for i in range(i7_maxlen))).fillna(np.nan)
    i7_df.columns = i7_names

    i5_df = df[i5_colname].apply(lambda x: pd.Series(get_base(x, i) for i in range(i5_maxlen))).fillna(np.nan)
    i5_df.columns = i5_names

    concatenated_indexes_df = pd.concat([df[id_name], i7_df, i5_df], axis=1)
    return concatenated_indexes_df

def cmp_bases(v1, v2):
    if isinstance(v1, str) and isinstance(v2, str):
        return np.sum(v1 != v2)

    return 0


def get_row_mismatch_matrix(array: np.ndarray) -> np.ndarray:

    # Reshape A and B to 3D arrays with dimensions (N, 1, K) and (1, M, K), respectively
    array1 = array[:, np.newaxis, :]
    array2 = array[np.newaxis, :, :]

    # Apply the custom function using vectorized operations
    return np.sum(np.vectorize(cmp_bases)(array1, array2), axis=2)


def substitutions_heatmap_df(indexes_df: pd.DataFrame, id_colname="Sample_ID"):
    a = indexes_df.drop(id_colname, axis=1).to_numpy()

    header = list(indexes_df[id_colname])
    return pd.pandas.DataFrame(get_row_mismatch_matrix(a), index=header, columns=header)



def split_df_by_lane(df):

    exploded_df = explode_df_by_lane(df)
    unique_lanes = exploded_df['Lane'].unique()

    return {lane: exploded_df[exploded_df['Lane'] == lane] for lane in unique_lanes}


def create_table_from_dataframe(dataframe):
    layout = QVBoxLayout()
    table_widget = QTableWidget()
    layout.addWidget(table_widget)

    num_rows, num_columns = dataframe.shape
    table_widget.setRowCount(num_rows)
    table_widget.setColumnCount(num_columns)
    table_widget.setHorizontalHeaderLabels(dataframe.columns)

    for row, values in enumerate(dataframe.itertuples(index=False), start=0):
        for col, value in enumerate(values, start=0):
            item = QTableWidgetItem()
            item.setData(Qt.DisplayRole, str(value))
            table_widget.setItem(row, col, item)

    return table_widget

#
# def create_table_from_dataframe(dataframe):
#
#     # Create a QVBoxLayout for the main widget
#     layout = QVBoxLayout()
#
#     # Create the QTableWidget
#     table_widget = QTableWidget()
#     layout.addWidget(table_widget)
#
#     # Set the number of rows and columns in the QTableWidget
#     num_rows, num_columns = dataframe.shape
#     table_widget.setRowCount(num_rows)
#     table_widget.setColumnCount(num_columns)
#
#     # Set the table headers
#     table_widget.setHorizontalHeaderLabels(dataframe.columns)
#
#     # Populate the table with data from the DataFrame
#     for row in range(num_rows):
#         for col in range(num_columns):
#             item = QTableWidgetItem(str(dataframe.iloc[row, col]))
#             table_widget.setItem(row, col, item)
#
#     return table_widget


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

#
# def qstandarditemmodel_to_dataframe(model):
#     """
#     Converts a QStandardItemModel to a Pandas DataFrame, keeping rows with alphanumeric values in at least one column.
#
#     Args:
#         model (QStandardItemModel): The QStandardItemModel to convert.
#
#     Returns:
#         pd.DataFrame: The Pandas DataFrame representation of the QStandardItemModel with rows containing alphanumeric values in at least one column.
#     """
#     if not isinstance(model, QStandardItemModel):
#         raise ValueError("Input must be a QStandardItemModel")
#
#     # Create an empty DataFrame with column names
#     columns = [model.horizontalHeaderItem(col).text() for col in range(model.columnCount())]
#     df = pd.DataFrame(columns=columns)
#
#     # Iterate through the rows of the model and populate the DataFrame
#     for row in range(model.rowCount()):
#         row_data = []
#         has_alphanumeric = False  # Flag to track if the row contains alphanumeric values
#         for col in range(model.columnCount()):
#             item = model.item(row, col)
#             if item is not None:
#                 text = item.text()
#                 # Check if the text contains alphanumeric characters
#                 if re.search(r'\w', text):
#                     row_data.append(text)
#                     has_alphanumeric = True
#                 else:
#                     row_data.append(np.nan)
#             else:
#                 row_data.append(np.nan)
#         # Only add rows with at least one alphanumeric value
#         if has_alphanumeric:
#             df.loc[row] = row_data
#
#     df = df.infer_objects()
#
#     return df


def qsi_mmodel_to_dataframe(model):
    if not isinstance(model, QStandardItemModel):
        raise ValueError("Input must be a QStandardItemModel")

    column_names = [model.horizontalHeaderItem(i).text() for i in range(model.columnCount())]
    df = pd.DataFrame(columns=column_names)

    for row_index in range(model.rowCount()):
        row_data = [model.item(row_index, col_index).text() for col_index in range(model.columnCount())]
        df.loc[row_index] = row_data

    df = df.replace('', np.nan).dropna(how='all').reset_index(drop=True)

    return df
