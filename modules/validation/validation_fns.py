import re

import numpy as np
import pandas as pd
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QVBoxLayout, QTableWidget, QTableWidgetItem


def explode_df_by_lane(df):
    exploded_df = df.assign(Lane=df['Lane'].str.split(',')).explode('Lane')
    exploded_df['Lane'] = exploded_df['Lane'].astype(int)
    return exploded_df


def compare_rows(row1: np.array, row2: np.array):
    return np.sum(row1 != row2)


def substitutions_heatmap_df(df: pd.DataFrame, index_column_name: str) -> pd.DataFrame:
    min_length = df[index_column_name].apply(len).min()
    truncated_df = df[index_column_name].apply(lambda x: x[:min_length])
    truncated_np_array = truncated_df.apply(list).apply(np.array).to_numpy()
    dna_mismatches = np.vectorize(compare_rows)(truncated_np_array[:, None], truncated_np_array)

    dna_mismatches_df = pd.DataFrame(dna_mismatches)

    dna_mismatches_df.columns = df.Sample_ID
    dna_mismatches_df.index = df.Sample_ID

    return dna_mismatches_df


def split_df_by_lane(df):

    # lane_dataframes = {}

    exploded_df = explode_df_by_lane(df)
    unique_lanes = exploded_df['Lane'].unique()

    # for lane in unique_lanes:
    #     lane_dataframes[lane] = exploded_df[exploded_df['Lane'] == lane]

    return {lane: exploded_df[exploded_df['Lane'] == lane] for lane in unique_lanes}

    # return lane_dataframes


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


def qstandarditemmodel_to_dataframe(model):
    if not isinstance(model, QStandardItemModel):
        raise ValueError("Input must be a QStandardItemModel")

    columns = [model.horizontalHeaderItem(col).text() for col in range(model.columnCount())]
    df = pd.DataFrame(columns=columns)

    for row in range(model.rowCount()):
        row_data = [model.item(row, col).text() for col in range(model.columnCount())]
        df.loc[row] = row_data

    df.replace('', np.nan, inplace=True)
    df.dropna(how='all', inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df