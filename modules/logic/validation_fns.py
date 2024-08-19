import re

import numpy as np
import pandas as pd
from PySide6.QtWidgets import QVBoxLayout, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt

pd.set_option('future.no_silent_downcasting', True)


# def explode_df_by_lane(df):
#     exploded_df = df.assign(Lane=df['Lane'].str.split(',')).explode('Lane')
#     exploded_df['Lane'] = exploded_df['Lane'].astype(int)
#     return exploded_df


def get_base(string, index):

    if index >= len(string):
        return np.nan
    else:
        return string[index]



def padded_index_df(df: pd.DataFrame, len: int, col_name: str, id_name: str) -> pd.DataFrame:

    index_type = col_name.replace("Index_", "")

    # Generate column names
    pos_names = [f"{index_type}_{i + 1}" for i in range(len)]

    # Extract i7 indexes
    i7_df = df[col_name].apply(lambda x: pd.Series(get_base(x, i) for i in range(len))).fillna(np.nan)
    i7_df.columns = pos_names

    # Concatenate indexes and return the resulting DataFrame
    return pd.concat([df[id_name], i7_df], axis=1)

# def lenadjust_i7_indexes(df: pd.DataFrame, i7_maxlen: int, i7_colname: str, id_name: str) -> pd.DataFrame:
#     """
#     Concatenate i7 and i5 indexes from the DataFrame.
#     Args:
#         df (pd.DataFrame): The input DataFrame containing the indexes.
#         i7_maxlen (int): The maximum length of i7 indexes.
#         i5_maxlen (int): The maximum length of i5 indexes.
#         i7_colname (str): The column name for i7 indexes.
#         i5_colname (str): The column name for i5 indexes.
#         id_name (str): The column name for the identifier.
#     Returns:
#         pd.DataFrame: A DataFrame with concatenated i7 and i5 indexes.
#     """
#     # Generate column names for i7 and i5 indexes
#     i7_names = [f"I7_{i + 1}" for i in range(i7_maxlen)]
#
#     # Extract i7 indexes
#     i7_df = df[i7_colname].apply(lambda x: pd.Series(get_base(x, i) for i in range(i7_maxlen))).fillna(np.nan)
#     i7_df.columns = i7_names
#
#     # Concatenate indexes and return the resulting DataFrame
#     lenadjust_indexes_df = pd.concat([df[id_name], i7_df], axis=1)
#     return lenadjust_indexes_df


# def lenadjust_i5_indexes(df: pd.DataFrame, i5_maxlen: int, i5_colname: str, id_name: str) -> pd.DataFrame:
#     """
#     Concatenate i7 and i5 indexes from the DataFrame.
#     Args:
#         df (pd.DataFrame): The input DataFrame containing the indexes.
#         i7_maxlen (int): The maximum length of i7 indexes.
#         i5_maxlen (int): The maximum length of i5 indexes.
#         i7_colname (str): The column name for i7 indexes.
#         i5_colname (str): The column name for i5 indexes.
#         id_name (str): The column name for the identifier.
#     Returns:
#         pd.DataFrame: A DataFrame with concatenated i7 and i5 indexes.
#     """
#     # Generate column names for i7 and i5 indexes
#     i5_names = [f"I7_{i + 1}" for i in range(i5_maxlen)]
#
#     # Extract i7 indexes
#     i5_df = df[i5_colname].apply(lambda x: pd.Series(get_base(x, i) for i in range(i5_maxlen))).fillna(np.nan)
#     i5_df.columns = i5_names
#
#     # Concatenate indexes and return the resulting DataFrame
#     lenadjust_indexes_df = pd.concat([df[id_name], i5_df], axis=1)
#     return lenadjust_indexes_df









# def split_df_by_lane(df):
#
#     exploded_df = explode_df_by_lane(df)
#     unique_lanes = exploded_df['Lane'].unique()
#
#     return {lane: exploded_df[exploded_df['Lane'] == lane] for lane in unique_lanes}


# def create_table_from_dataframe(dataframe):
#     layout = QVBoxLayout()
#     table_widget = QTableWidget()
#     layout.addWidget(table_widget)
#
#     num_rows, num_columns = dataframe.shape
#     table_widget.setRowCount(num_rows)
#     table_widget.setColumnCount(num_columns)
#     table_widget.setHorizontalHeaderLabels(dataframe.columns)
#
#     for row, values in enumerate(dataframe.itertuples(index=False), start=0):
#         for col, value in enumerate(values, start=0):
#             item = QTableWidgetItem()
#             item.setData(Qt.DisplayRole, str(value))
#             table_widget.setItem(row, col, item)
#
#     return table_widget
#





