import numpy as np
import pandas as pd
import re
from PySide6.QtGui import QStandardItemModel, QStandardItem, QColor, QBrush, QFont
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QSizePolicy


def qstandarditemmodel_to_dataframe(model):
    """
    Converts a QStandardItemModel to a Pandas DataFrame, keeping rows with alphanumeric values in at least one column.

    Args:
        model (QStandardItemModel): The QStandardItemModel to convert.

    Returns:
        pd.DataFrame: The Pandas DataFrame representation of the QStandardItemModel with rows containing alphanumeric values in at least one column.
    """
    if not isinstance(model, QStandardItemModel):
        raise ValueError("Input must be a QStandardItemModel")

    # Create an empty DataFrame with column names
    columns = [model.horizontalHeaderItem(col).text() for col in range(model.columnCount())]
    df = pd.DataFrame(columns=columns)

    # Iterate through the rows of the model and populate the DataFrame
    for row in range(model.rowCount()):
        row_data = []
        has_alphanumeric = False  # Flag to track if the row contains alphanumeric values
        for col in range(model.columnCount()):
            item = model.item(row, col)
            if item is not None:
                text = item.text()
                # Check if the text contains alphanumeric characters
                if re.search(r'\w', text):
                    row_data.append(text)
                    has_alphanumeric = True
                else:
                    row_data.append(np.nan)
            else:
                row_data.append(np.nan)
        # Only add rows with at least one alphanumeric value
        if has_alphanumeric:
            df.loc[row] = row_data

    df = df.infer_objects()

    return df


def parse_integer_string(input_string):
    try:
        # Remove whitespaces from the input string and then split it by commas
        input_string = input_string.replace(" ", "")
        integers_list = [int(x) for x in input_string.split(',')]

        # Check if the number of integers is between 1 and 8
        if 1 <= len(integers_list) <= 8:
            return integers_list
        else:
            raise ValueError("Invalid number of integers in the input string")
    except ValueError:
        # Handle invalid input or conversion errors
        print("Error: Invalid input string")
        return None


def calculate_mismatches(str1, str2):
    return sum(c1 != c2 for c1, c2 in zip(str1, str2))


def color_cell_based_on_mismatches(table_widget, row, col, data):
    cell_value = data.iloc[row, col]
    num_mismatches = calculate_mismatches(cell_value, data.columns[row])
    color_intensity = min(255, 255 - (num_mismatches * 30))  # Adjust color intensity

    color = QColor(color_intensity, color_intensity, 255)  # Blueish color
    brush = cell_value_background_color(cell_value, color)
    item = QTableWidgetItem(cell_value)
    item.setBackground(brush)
    table_widget.setItem(row, col, item)


def create_color_balanced_table(data: pd.DataFrame) -> QTableWidget:
    table_widget = QTableWidget(rows=data.shape[0], columns=2)

    # Set column count
    table_widget.setColumnCount(2)

    # Set column headers
    table_widget.setHorizontalHeaderLabels(['Sample_ID', 'Index'])

    # Set row count
    table_widget.setRowCount(len(data))

    # Populate the QTableWidget from the DataFrame
    for row_index, row_data in data.iterrows():
        for col_index, value in enumerate(row_data):
            item = QTableWidgetItem(str(value))
            table_widget.setItem(row_index, col_index, item)

    font = QFont("Courier New", 12)  # You can adjust the font size as needed
    table_widget.horizontalHeaderItem(1).setFont(font)


    return table_widget


def create_heatmap_table(data: pd.DataFrame) -> QTableWidget:
    # Create a QTableWidget with the same dimensions as the DataFrame
    table_widget = QTableWidget(data.shape[0], data.shape[1])

    table_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    # Set column headers
    table_widget.setHorizontalHeaderLabels(data.columns)

    # Set row headers (vertical header)
    table_widget.setVerticalHeaderLabels(data.index)

    for row in range(data.shape[0]):
        for col in range(data.shape[1]):
            # Get the cell value
            cell_value = int(data.iat[row, col])

            # Skip coloring the diagonal cells
            if row == col:
                continue

            if cell_value < 5:
                red_intensity = int(192 + (255 - 192) * (cell_value / 4))  # Red shade
                color = QColor(red_intensity, 0, 0)
            else:
                green_intensity = int(192 + (255 - 192) * (1 - ((cell_value - 4) / (data.max().max() - 4))))  # Green shade
                color = QColor(0, green_intensity, 0)

            # Create a brush with the calculated color
            brush = QBrush(color)

            # Create a QTableWidgetItem with the cell value
            item = QTableWidgetItem(str(cell_value))

            # Set the background color for the cell
            item.setBackground(brush)

            # Set alignment to center
            item.setTextAlignment(Qt.AlignCenter)

            item.setFlags(Qt.ItemIsEnabled)

            # Add the item to the table
            table_widget.setItem(row, col, item)

    return table_widget

#
# def cell_value_background_color(cell_value, default_color):
#     # You can add more conditions or customize colors as needed
#     if "a" in cell_value:
#         return QColor(255, 128, 128)  # Red for cells containing "a"
#     else:
#         return default_color


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


def explode_df_by_lane(df):
    exploded_df = df.assign(Lane=df['Lane'].str.split(',')).explode('Lane')
    exploded_df['Lane'] = exploded_df['Lane'].astype(int)
    return exploded_df


def split_df_by_lane(df):
    # sourcery skip: dict-comprehension, inline-immediately-returned-variable, move-assign-in-block
    lane_dataframes = {}

    exploded_df = explode_df_by_lane(df)
    unique_lanes = exploded_df['Lane'].unique()

    for lane in unique_lanes:
        lane_dataframes[lane] = exploded_df[exploded_df['Lane'] == lane]

    return lane_dataframes
