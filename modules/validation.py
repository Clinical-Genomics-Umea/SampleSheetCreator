import json
import re

import numpy as np
import pandas as pd
import pandera as pa
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QColor, QBrush, QFont, QPen, QStandardItem
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QFormLayout, \
    QTableWidget, QTableWidgetItem, QLabel, QHeaderView, QAbstractScrollArea, QScrollArea, QItemDelegate, \
    QStyledItemDelegate, QTableView, QTabWidget, QFrame
from pandera import String, Int, Column, Field, DataFrameSchema, Check, Index
import pandera.extensions as extensions
from pandera.errors import SchemaErrors

from modules.run_classes import RunInfo


# def delete_widgets_in_scrollarea(scroll_area):
#     # Get the scroll area's viewport to access its contents
#     viewport = scroll_area.viewport()
#
#     # Iterate through all child widgets in the viewport and delete them
#     for widget in viewport.findChildren(QWidget):
#         print(widget)
#         widget.deleteLater()


def set_heatmap_table_properties(table):

    table.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
    table.setContentsMargins(0, 0, 0, 0)
    table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    h_header_height = table.horizontalHeader().height()
    row_height = table.rowHeight(0)
    no_items = table.columnCount()
    table.setMaximumHeight(h_header_height + row_height * no_items)

    table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)

    return table


def set_colorbalance_table_properties(table):

    table.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
    table.setContentsMargins(0, 0, 0, 0)
    table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    h_header_height = table.horizontalHeader().height()
    row_height = table.rowHeight(0)
    no_items = table.model.rowCount()
    table.setMaximumHeight(h_header_height + row_height * no_items)

    table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)

    return table


class DataValidatioWidget(QWidget):
    def __init__(self, model: QStandardItemModel, runinfo: RunInfo):
        super().__init__()

        self.model = model
        self.runinfo = runinfo

        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.hspacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.vspacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)

        button = QPushButton("Validate")
        button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        button.setMaximumHeight(30)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addWidget(button)
        button_layout.addSpacerItem(self.hspacer)

        self.validate_tabwidget = QTabWidget()
        self.validate_tabwidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.validate_tabwidget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # self.validate_tabwidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.layout.addLayout(button_layout)
        self.layout.addWidget(self.validate_tabwidget)

        button.clicked.connect(self.validate)

    def validate(self):
        self.validate_tabwidget.clear()

        # data_widget = QWidget()
        # form_layout = QFormLayout()
        # data_v_layout = QVBoxLayout()
        # data_v_layout.setContentsMargins(0, 0, 0, 0)
        # data_v_layout.addLayout(form_layout)
        # data_v_layout.addSpacerItem(self.vspacer)

        df = qstandarditemmodel_to_dataframe(self.model)

        try:
            first_validation_schema(df, lazy=True)
        except SchemaErrors as err:
            print(err.failure_cases)  # dataframe of schema error
            return

        lanes_df = split_df_by_lane(df)

        for lane in lanes_df:
            hspacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
            vspacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
            vspacer_fixed = QSpacerItem(1, 20, QSizePolicy.Fixed, QSizePolicy.Fixed)

            tab_scroll_area = QScrollArea()
            tab_scroll_area.setFrameShape(QFrame.NoFrame)

            tab = QWidget()
            tab_main_layout = QVBoxLayout()
            tab_main_layout.setContentsMargins(0, 0, 0, 0)
            tab.setLayout(tab_main_layout)
            tab_main_layout.addWidget(QLabel(f"Index Heatmap for Lane {lane}"))


            heatmap_table = create_heatmap_table(substitutions_heatmap_df(lanes_df[lane], "I7_Index"))
            heatmap_table = set_heatmap_table_properties(heatmap_table)

            h_heatmap_layout = QHBoxLayout()
            h_heatmap_layout.setContentsMargins(0, 0, 0, 0)
            v_heatmap_layout = QVBoxLayout()
            v_heatmap_layout.setContentsMargins(0, 0, 0, 0)

            h_heatmap_layout.addWidget(heatmap_table)
            h_heatmap_layout.addSpacerItem(hspacer)
            v_heatmap_layout.addLayout(h_heatmap_layout)
            v_heatmap_layout.addSpacerItem(vspacer)

            tab_main_layout.addLayout(v_heatmap_layout)

            tab_main_layout.addSpacerItem(vspacer_fixed)
            tab_main_layout.addWidget(QLabel(f"Color Balance Table for Lane {lane}"))

            colorbalance_table = ColorBalanceWidget(lanes_df[lane])
            colorbalance_table = set_colorbalance_table_properties(colorbalance_table)
            colorbalance_table.setStyleSheet("QTableView::item:last { border-bottom: 2px solid black; }")

            h_colorbalance_layout = QHBoxLayout()
            h_colorbalance_layout.setContentsMargins(0, 0, 0, 0)
            v_colorbalance_layout = QVBoxLayout()
            v_colorbalance_layout.setContentsMargins(0, 0, 0, 0)

            h_colorbalance_layout.addWidget(colorbalance_table)
            h_colorbalance_layout.addSpacerItem(hspacer)
            v_colorbalance_layout.addLayout(h_colorbalance_layout)
            v_colorbalance_layout.addSpacerItem(vspacer)

            tab_main_layout.addLayout(v_colorbalance_layout)
            tab_main_layout.addSpacerItem(vspacer)

            tab_scroll_area.setWidget(tab)
            self.validate_tabwidget.addTab(tab_scroll_area, f"Lane {lane}")



            # color_balance_table = create_color_balance_table(lanes_df[lane])
            # print(QTableWidget())
            # v_layout.addWidget(ColorBalanceWidget(lanes_df[lane]))
            # v_layout.addSpacerItem(self.vspacer)
            #
            # form_layout.addRow(QLabel("Lane " + str(lane)), v_layout)

        # data_widget.setLayout(data_v_layout)
        # self.validate_tabwidget.setWidget(data_widget)

    @staticmethod
    def set_heatmap_table_properties(table):

        table.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        table.setContentsMargins(0, 0, 0, 0)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        h_header_height = table.horizontalHeader().height()
        row_height = table.rowHeight(0)
        no_items = table.columnCount()
        table.setMaximumHeight(h_header_height + row_height * no_items)

        table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)

        return table


class ColorBalanceWidget(QTableView):
    def __init__(self, dataframe: pd.DataFrame, parent=None):
        super(ColorBalanceWidget, self).__init__(parent)
        dataframe.reset_index()
        dataframe['Proportion'] = 1
        df = self.split_string_column(dataframe, 'I7_Index')
        df.insert(0, 'Sample_ID', dataframe['Sample_ID'])
        df.insert(1, "Proportion", dataframe['Proportion'])

        print(df.to_string())

        self.model = self.dataframe_to_qstandarditemmodel(df)

        self.setModel(self.model)



        #
        # # df = dataframe[['Sample_ID', 'I7_Index']].copy()
        # # df["Proportion"] = "1"
        # # df.reset_index(inplace=True)
        #
        # df_index = self.split_string_column(dataframe, 'I7_Index')
        #
        # print(df.to_string())
        #
        # table_widget = QTableWidget(df.shape[0] + 1, df.shape[1])
        #
        # table_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        # table_widget.setHorizontalHeaderLabels(data.columns)
        # table_widget.setVerticalHeaderLabels(data.index)
        #
        # for row in range(df.shape[0]):
        #     print("row", row)
        #     for col in range(df.shape[1]):
        #         print("col", col)
        #         # Get the cell value
        #         cell_value = df.iloc[row, col]
        #
        #         print(cell_value)
        #
        #         item = QTableWidgetItem(str(cell_value))
        #         table_widget.setItem(row, col, item)
        #
        # table_widget.setItemDelegateForColumn(0, NonEditableDelegate())
        # table_widget.setItemDelegateForColumn(1, NonEditableDelegate())
        # table_widget.setItemDelegate(ThickLineDelegate())

    @staticmethod
    def split_string_column(dataframe, column_name):
        """
        Split a column of strings into multiple columns with one character per column.

        :param dataframe: Pandas DataFrame containing the string column.
        :param column_name: Name of the column containing the strings.
        :return: DataFrame with one column per character in the strings.
        """
        # Create an empty DataFrame with columns for each character
        split_df = pd.DataFrame()

        # Iterate through the rows of the original DataFrame
        for index, row in dataframe.iterrows():
            string_value = row[column_name]
            # Create a list of characters from the string
            characters = list(string_value)

            # Create new columns for each character and assign values
            for i, char in enumerate(characters):
                col_name = f"{column_name}_{i + 1}"  # New column name
                split_df.at[index, col_name] = char

        return split_df

    def dataframe_to_qstandarditemmodel(self, dataframe):
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


class NonEditableDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        # Return None to make the item non-editable
        return None


class ThickLineDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.row() == index.model().rowCount() - 1:
            # Draw a thick line for the last row
            painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
            painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
        else:
            # For other rows, delegate the painting to the default delegate
            super().paint(painter, option, index)


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
#
# # - Lane
# # - Sample_ID
# # - ProfileName
# # - Plate
# # - WellPos
# # - I7_Plate
# # - I7_WellPos
# # - I5_Plate
# # - I5_WellPos
# # - I7_IndexName
# # - I7_Index
# # - I5_IndexName
# # - I5_Index
# # - UsedCycles
# # - BarcodeMismatchesIndex1
# # - BarcodeMismatchesIndex2
# # - AdapterRead1
# # - AdapterRead2
# # - FastqCompressionFormat
# # - Pipeline
# # - ReferenceGenomeDir
# # - VariantCallingMode
#
# if __name__ == "__main__":
#     print("hej")
#
#


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


def cell_value_background_color(cell_value, default_color):
    # You can add more conditions or customize colors as needed
    if "a" in cell_value:
        return QColor(255, 128, 128)  # Red for cells containing "a"
    else:
        return default_color


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
    # sourcery skip: dict-comprehension, inline-immediately-returned-variable, move-assign-in-block
    lane_dataframes = {}

    exploded_df = explode_df_by_lane(df)
    unique_lanes = exploded_df['Lane'].unique()

    for lane in unique_lanes:
        lane_dataframes[lane] = exploded_df[exploded_df['Lane'] == lane]

    return lane_dataframes


def explode_df_by_lane(df):
    exploded_df = df.assign(Lane=df['Lane'].str.split(',')).explode('Lane')
    exploded_df['Lane'] = exploded_df['Lane'].astype(int)
    return exploded_df


# def create_color_balanced_table(data: pd.DataFrame) -> QTableWidget:
#     table_widget = QTableWidget(rows=data.shape[0], columns=2)
#
#     # Set column count
#     table_widget.setColumnCount(2)
#
#     # Set column headers
#     table_widget.setHorizontalHeaderLabels(['Sample_ID', 'Index'])
#
#     # Set row count
#     table_widget.setRowCount(len(data))
#
#     # Populate the QTableWidget from the DataFrame
#     for row_index, row_data in data.iterrows():
#         for col_index, value in enumerate(row_data):
#             item = QTableWidgetItem(str(value))
#             table_widget.setItem(row_index, col_index, item)
#
#     font = QFont("Courier New", 12)  # You can adjust the font size as needed
#     table_widget.horizontalHeaderItem(1).setFont(font)
#
#
#     return table_widget


def color_cell_based_on_mismatches(table_widget, row, col, data):
    cell_value = data.iloc[row, col]
    num_mismatches = calculate_mismatches(cell_value, data.columns[row])
    color_intensity = min(255, 255 - (num_mismatches * 30))  # Adjust color intensity

    color = QColor(color_intensity, color_intensity, 255)  # Blueish color
    brush = cell_value_background_color(cell_value, color)
    item = QTableWidgetItem(cell_value)
    item.setBackground(brush)
    table_widget.setItem(row, col, item)


def calculate_mismatches(str1, str2):
    return sum(c1 != c2 for c1, c2 in zip(str1, str2))


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
