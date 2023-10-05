import json
import re

import numpy as np
import pandas as pd
import pandera as pa
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QStandardItemModel, QColor, QBrush, QFont, QPen, QStandardItem, QPainter, QTextDocument, \
    QTextOption
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QFormLayout, \
    QTableWidget, QTableWidgetItem, QLabel, QHeaderView, QAbstractScrollArea, QScrollArea, QItemDelegate, \
    QStyledItemDelegate, QTableView, QTabWidget, QFrame, QProxyStyle, QStyleOptionViewItem, QStyle
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

    table.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
    table.setContentsMargins(0, 0, 0, 0)
    table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    last_row_index = table.standard_model.rowCount() - 1
    table.setRowHeight(last_row_index, 60)

    h_header_height = table.horizontalHeader().height()
    # row_height = table.rowHeight(0)

    tot_row_heights = 0
    for row in range(table.standard_model.rowCount()):
        tot_row_heights += table.rowHeight(row)

    table.setMaximumHeight(h_header_height + tot_row_heights)

    # table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)

    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.setFixedWidth(1400)

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

        button = QPushButton("Validate")
        button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        button.setMaximumHeight(30)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addWidget(button)
        button_layout.addSpacerItem(self.hspacer)

        self.validate_tabwidget = QTabWidget()
        self.validate_tabwidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.layout.addLayout(button_layout)
        self.layout.addWidget(self.validate_tabwidget)

        button.clicked.connect(self.validate)


    def validate(self):
        self.validate_tabwidget.clear()

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

            last_row = colorbalance_table.standard_model.rowCount() - 1

            colorbalance_table.setItemDelegateForRow(last_row, JsonDelegate())

            tab_main_layout.addWidget(colorbalance_table)
            tab_main_layout.addSpacerItem(vspacer)

            tab_scroll_area.setWidget(tab)
            self.validate_tabwidget.addTab(tab_scroll_area, f"Lane {lane}")

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


class ColorBalanceModel(QStandardItemModel):

    def __init__(self, dataframe: pd.DataFrame, parent):
        super(ColorBalanceModel, self).__init__(parent=parent)
        self.dataChanged.connect(self.update_summation)

    def update_summation(self):

        print("update_summation")

        for col_count in range(2, self.columnCount()):
            bases_count = {}
            for row_count in range(self.rowCount() - 1):
                proportion = int(self.item(row_count, 1).text())

                base = self.item(row_count, col_count).text()

                if base not in bases_count:
                    bases_count[base] = 0

                bases_count[self.item(row_count, col_count).text()] += 1 * proportion

            color_counts = self.translate_base_count_to_color_count(bases_count)
            normalized_color_counts = self.normalize_dict_values(color_counts)

            print(normalized_color_counts)

            norm_json = json.dumps(normalized_color_counts)

            last_row = self.rowCount() - 1
            self.setData(self.index(last_row, col_count), norm_json, Qt.EditRole)


    @staticmethod
    def normalize_dict_values(input_dict):
        # Calculate the sum of values in the input dictionary
        total = sum(input_dict.values())

        # Normalize the values and create a new dictionary
        normalized_dict = {key: round(value / total, 2) for key, value in input_dict.items()}

        return normalized_dict

    @staticmethod
    def translate_base_count_to_color_count(dict1):
        dict2 = {
            'Blue': 0,
            'Green': 0,
            'Black': 0,
        }

        for key, value in dict1.items():
            if key == 'A':
                dict2['Blue'] = value * 0.5
                dict2['Green'] = value * 0.5
            elif key == 'C':
                dict2['Blue'] = value
            elif key == 'T':
                dict2['Green'] = value
            elif key == 'G':
                dict2['Black'] = value

        return dict2


class JsonDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.isValid() and index.column() >= 2:
            json_data = index.data(Qt.DisplayRole)
            if json_data:
                painter.save()

                data = json.loads(json_data)

                lines = [f"{key}: {value}" for key, value in data.items()]

                # Create a QTextOption for aligning text
                text_option = QTextOption()
                text_option.setAlignment(Qt.AlignLeft)

                # Calculate the height of each line
                font_metrics = painter.fontMetrics()
                line_height = font_metrics.lineSpacing()

                # Draw each line of text
                for i, line in enumerate(lines):
                    y_offset = i * line_height
                    rect = option.rect.adjusted(5, y_offset, 0, 0)  # Adjust the rect for each line
                    painter.drawText(rect, line, text_option)

        elif index.isValid():
            super().paint(painter, option, index)

    # def sizeHint(self, option, index):
    #     text = index.data()
    #     if text:
    #         # Split the text into lines
    #         lines = text.split(',')
    #
    #         # Calculate the height required for all lines
    #         font_metrics = option.fontMetrics
    #         line_height = font_metrics.lineSpacing()
    #         total_height = len(lines) * line_height
    #
    #         print("sizehint", len(lines), total_height)
    #
    #         # Use the height and the width of the cell for size hint
    #         return QSize(option.rect.width(), total_height)

    def sizeHint(self, option, index):
        # Calculate the desired height based on the content
        # For demonstration purposes, use a fixed height here
        desired_height = 100  # Adjust as needed
        return option.rect.height(), desired_height


# class MultiLabelDelegate(QStyledItemDelegate):
#     def createEditor(self, parent, option, index):
#         if index.row() == index.model().rowCount() - 1 and index.column() >= 2:
#             data = index.data()
#             print(data)
#             return MultiLabelWidget(data)
#         return super().createEditor(parent, option, index)
#
#     def setEditorData(self, editor, index):
#         data = index.data()
#         editor.setData(data)
#
#     def setModelData(self, editor, model, index):
#         data = editor.getData()
#         model.setData(index, data, Qt.EditRole)
#
#     def updateEditorGeometry(self, editor, option, index):
#         editor.setGeometry(option.rect)


# class MultiLabelWidget(QWidget):
#     def __init__(self, data):
#         super().__init__()
#         self.layout = QHBoxLayout()
#         self.label1 = QLabel()
#         self.label2 = QLabel()
#         self.label3 = QLabel()
#         self.layout.addWidget(self.label1)
#         self.layout.addWidget(self.label2)
#         self.layout.addWidget(self.label3)
#         self.setLayout(self.layout)
#
#         self.setData(data)
#
#     def setData(self, data):
#         try:
#             json_data = json.loads(data)
#             self.label1.setText(json_data.get("label1", ""))
#             self.label2.setText(json_data.get("label2", ""))
#             self.label3.setText(json_data.get("label3", ""))
#         except json.JSONDecodeError:
#             # Handle invalid JSON gracefully
#             self.label1.setText("")
#             self.label2.setText("")
#             self.label3.setText("Invalid JSON")
#
#     def getData(self):
#         data = {
#             "label1": self.label1.text(),
#             "label2": self.label2.text(),
#             "label3": self.label3.text()
#         }
#         return json.dumps(data)


class ColorBalanceWidget(QTableView):
    def __init__(self, dataframe: pd.DataFrame, parent=None):
        super(ColorBalanceWidget, self).__init__(parent)
        dataframe.reset_index()
        dataframe['Proportion'] = "1"
        df = self.split_string_column(dataframe, 'I7_Index')
        df.insert(0, 'Sample_ID', dataframe['Sample_ID'])
        df.insert(1, "Proportion", dataframe['Proportion'])
        last_row_index = df.index[-1]
        df.loc[last_row_index + 1] = pd.Series()
        df.iloc[-1, 0] = "Summary"
        df.iloc[-1, 1] = ""

        self.standard_model = self.dataframe_to_colorbalance_model(df)
        self.setModel(self.standard_model)
        self.standard_model.update_summation()
        self.verticalHeader().setVisible(False)
        self.wordWrap()

    def dataframe_to_colorbalance_model(self, dataframe):
        """
        Convert a Pandas DataFrame to a QStandardItemModel.

        :param dataframe: Pandas DataFrame to convert.
        :return: QStandardItemModel representing the DataFrame.
        """
        model = ColorBalanceModel(dataframe, parent=self)

        # Set the column headers as the model's horizontal headers
        model.setHorizontalHeaderLabels(dataframe.columns)

        for row_index, row_data in dataframe.iterrows():
            row_items = [QStandardItem(str(item)) for item in row_data]
            model.appendRow(row_items)

        return model

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())

        # Get the last row index
        last_row_index = self.model().rowCount() - 1

        # Get the rect for the last row

        for col in range(self.model().columnCount()):

            last_row_rect = self.visualRect(self.model().index(last_row_index, col))

            # Draw the thick line before the last row
            painter.setPen(QPen(QColor("dark gray"), 2, Qt.SolidLine))
            painter.drawLine(last_row_rect.topLeft(), last_row_rect.topRight())



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
        super().paint(painter, option, index)

        if index.row() == index.model().rowCount() - 1 and not index.parent().isValid():
            # Create a thicker border at the bottom
            rect = option.rect
            rect.setTop(rect.bottom() - 2)  # Make the border 2 pixels thick
            painter.setPen(Qt.black)
            painter.drawRect(rect)


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
