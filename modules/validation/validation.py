import json

import numpy as np
import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QColor, QBrush, QPen, QStandardItem, QPainter, QTextOption, QIntValidator, \
    QPalette
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy, QTableWidget,
                               QTableWidgetItem, QLabel, QHeaderView, QAbstractScrollArea, QScrollArea,
                               QItemDelegate, QStyledItemDelegate, QTableView, QTabWidget, QFrame, QLineEdit)
from pandera.errors import SchemaErrors

from modules.run_classes import RunInfo
from modules.validation.validation_fns import compare_rows, substitutions_heatmap_df, split_df_by_lane, \
    create_table_from_dataframe, qstandarditemmodel_to_dataframe
from modules.validation.validation_schema import prevalidation_schema


def set_heatmap_table_properties(table):

    table.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
    table.setContentsMargins(0, 0, 0, 0)
    table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    h_header_height = table.horizontalHeader().height()
    row_height = table.rowHeight(0)
    no_items = table.columnCount()
    table.setMaximumHeight(h_header_height + row_height * no_items + 5)

    table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)

    table.setItemDelegate(NonEditableDelegate())

    return table


def set_colorbalance_table_properties(table):

    table.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
    table.setContentsMargins(0, 0, 0, 0)
    table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    last_row_index = table.standard_model.rowCount() - 1
    table.setRowHeight(last_row_index, 58)

    table.setItemDelegate(ColorTableDelegate())

    table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.setFixedWidth(1400)

    return table


class DataValidationWidget(QWidget):
    def __init__(self, model: QStandardItemModel, run_info: RunInfo):
        super().__init__()

        self.model = model
        self.run_info = run_info

        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.hspacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.vspacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.validate_tabwidget = QTabWidget()
        self.validate_tabwidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.layout.addWidget(self.validate_tabwidget)

    def validate(self):
        self.validate_tabwidget.clear()

        df = qstandarditemmodel_to_dataframe(self.model)

        if not isinstance(df, pd.DataFrame):
            tab = QWidget()
            tab_main_layout = QVBoxLayout()
            tab_main_layout.setContentsMargins(0, 0, 0, 0)
            tab.setLayout(tab_main_layout)

            tab_main_layout.addWidget(QLabel("Something went wrong. Data is could not"
                                             " be converted to a pandas dataframe."))
            tab_main_layout.addSpacerItem(self.vspacer)

            self.validate_tabwidget.addTab(tab, "Pre-Validation Errors")

            return

        if df.empty:
            tab = QWidget()
            tab_main_layout = QVBoxLayout()
            tab_main_layout.setContentsMargins(0, 0, 0, 0)
            tab.setLayout(tab_main_layout)

            tab_main_layout.addWidget(QLabel("No data to validate (empty dataframe)"))
            tab_main_layout.addSpacerItem(self.vspacer)

            self.validate_tabwidget.addTab(tab, "Pre-Validation Errors")

            return

        try:
            prevalidation_schema(df, lazy=True)
        except SchemaErrors as err:

            schema_errors_table = create_table_from_dataframe(err.failure_cases)

            tab = QWidget()
            tab_main_layout = QVBoxLayout()
            tab_main_layout.setContentsMargins(0, 0, 0, 0)
            tab.setLayout(tab_main_layout)

            schema_errors_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            tab_main_layout.addWidget(schema_errors_table)

            self.validate_tabwidget.addTab(tab, "Pre-Validation Errors")

            return

        lanes_df = split_df_by_lane(df)

        for lane in lanes_df:
            h_spacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
            v_spacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
            v_spacer_fixed = QSpacerItem(1, 20, QSizePolicy.Fixed, QSizePolicy.Fixed)

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
            h_heatmap_layout.addSpacerItem(h_spacer)
            v_heatmap_layout.addLayout(h_heatmap_layout)
            v_heatmap_layout.addSpacerItem(v_spacer)

            tab_main_layout.addLayout(v_heatmap_layout)

            tab_main_layout.addSpacerItem(v_spacer_fixed)
            tab_main_layout.addWidget(QLabel(f"Color Balance Table for Lane {lane}"))

            colorbalance_table = ColorBalanceWidget(lanes_df[lane])
            colorbalance_table = set_colorbalance_table_properties(colorbalance_table)

            tab_main_layout.addWidget(colorbalance_table)
            tab_main_layout.addSpacerItem(v_spacer)

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

    def __init__(self, parent):
        super(ColorBalanceModel, self).__init__(parent=parent)
        self.dataChanged.connect(self.update_summation)

    def update_summation(self):

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
        color_count = {
            'Blue': 0,
            'Green': 0,
            'Black': 0,
        }

        for base, count in dict1.items():
            if base == 'A':
                color_count['Blue'] = count * 0.5
                color_count['Green'] = count * 0.5
            elif base == 'C':
                color_count['Blue'] = count
            elif base == 'T':
                color_count['Green'] = count
            elif base == 'G':
                color_count['Black'] = count

        return color_count


class ColorTableDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):

        last_row = index.model().rowCount() - 1

        if index.isValid() and index.column() >= 2 and index.row() == last_row:
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

    def createEditor(self, parent, option, index):

        last_row = index.model().rowCount() - 1

        if index.column() == 1 and index.row() != last_row:
            return self.createIntValidationEditor(parent, option, index)

        else:
            return None

    def createIntValidationEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setValidator(QIntValidator())  # Set an integer validator
        return editor


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
        model = ColorBalanceModel(parent=self)

        # Set the column headers as the model's horizontal headers
        model.setHorizontalHeaderLabels(dataframe.columns)

        for row_index, row_data in dataframe.iterrows():
            row_items = [QStandardItem(str(item)) for item in row_data]
            model.appendRow(row_items)

        return model

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())

        model = self.model()
        column_count = model.columnCount()

        last_row_index = model.rowCount() - 1

        for col in range(column_count):
            last_row_rect = self.visualRect(model.index(last_row_index, col))

            thick_pen = QPen(QColor("dark gray"), 2, Qt.SolidLine)
            painter.setPen(thick_pen)
            painter.drawLine(last_row_rect.topLeft(), last_row_rect.topRight())

    @staticmethod
    def split_string_column(dataframe, column_name):
        """
        Split a column of strings into multiple columns with one character per column.

        :param dataframe: Pandas DataFrame containing the string column.
        :param column_name: Name of the column containing the strings.
        :return: DataFrame with one column per character in the strings.
        """
        # Use apply and pd.Series to split the string column into multiple columns
        split_df = dataframe[column_name].apply(lambda x: pd.Series(list(x)))
        split_df.columns = [f"{column_name}_{i + 1}" for i in range(split_df.shape[1])]

        return split_df
    #
    # @staticmethod
    # def split_string_column(dataframe, column_name):
    #     """
    #     Split a column of strings into multiple columns with one character per column.
    #
    #     :param dataframe: Pandas DataFrame containing the string column.
    #     :param column_name: Name of the column containing the strings.
    #     :return: DataFrame with one column per character in the strings.
    #     """
    #     # Create an empty DataFrame with columns for each character
    #     split_df = pd.DataFrame()
    #
    #     # Iterate through the rows of the original DataFrame
    #     for index, row in dataframe.iterrows():
    #         string_value = row[column_name]
    #         # Create a list of characters from the string
    #         characters = list(string_value)
    #
    #         # Create new columns for each character and assign values
    #         for i, char in enumerate(characters):
    #             col_name = f"{column_name}_{i + 1}"  # New column name
    #             split_df.at[index, col_name] = char
    #
    #     return split_df

    # def dataframe_to_qstandarditemmodel(self, dataframe):
    #     """
    #     Convert a Pandas DataFrame to a QStandardItemModel.
    #
    #     :param dataframe: Pandas DataFrame to convert.
    #     :return: QStandardItemModel representing the DataFrame.
    #     """
    #     model = QStandardItemModel()
    #
    #     # Set the column headers as the model's horizontal headers
    #     model.setHorizontalHeaderLabels(dataframe.columns)
    #
    #     for row_index, row_data in dataframe.iterrows():
    #         row_items = [QStandardItem(str(item)) for item in row_data]
    #         model.appendRow(row_items)
    #
    #     return model


class NonEditableDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        # Return None to make the item non-editable
        return None

#
# def valid_sequence_set(series):
#     min_length = series.apply(len).min()
#     truncated_df = series.apply(lambda x: x[:min_length])
#
#     truncated_np_array = truncated_df.apply(list).apply(np.array).to_numpy()
#     dna_mismatches = np.vectorize(compare_rows)(truncated_np_array[:, None], truncated_np_array)
#
#     row_indices, col_indices = np.where((dna_mismatches < 4) &
#                                         (np.arange(dna_mismatches.shape[0]) != np.arange(dna_mismatches.shape[0])[:,
#                                                                                np.newaxis]))
#
#     res = [True] * dna_mismatches.shape[0]
#
#     if len(row_indices) > 0:
#         for i in row_indices:
#             res[i] = False
#
#     return pd.Series(res)


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

#
# def create_heatmap_table(data: pd.DataFrame) -> QTableWidget:
#     # Create a QTableWidget with the same dimensions as the DataFrame
#     table_widget = QTableWidget(data.shape[0], data.shape[1])
#
#     table_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
#
#     # Set column headers
#     table_widget.setHorizontalHeaderLabels(data.columns)
#
#     # Set row headers (vertical header)
#     table_widget.setVerticalHeaderLabels(data.index)
#
#     for row in range(data.shape[0]):
#         for col in range(data.shape[1]):
#             # Get the cell value
#             cell_value = int(data.iat[row, col])
#
#             # Skip coloring the diagonal cells
#             if row == col:
#                 continue
#
#             if cell_value < 5:
#                 red_intensity = int(192 + (255 - 192) * (cell_value / 4))  # Red shade
#                 color = QColor(red_intensity, 0, 0)
#             else:
#                 green_intensity = int(192 + (255 - 192) * (1 - ((cell_value - 4) / (data.max().max() - 4))))  # Green shade
#                 color = QColor(0, green_intensity, 0)
#
#             # Create a brush with the calculated color
#             brush = QBrush(color)
#
#             # Create a QTableWidgetItem with the cell value
#             item = QTableWidgetItem(str(cell_value))
#
#             # Set the background color for the cell
#             item.setBackground(brush)
#
#             # Set alignment to center
#             item.setTextAlignment(Qt.AlignCenter)
#
#             item.setFlags(Qt.ItemIsEnabled)
#
#             # Add the item to the table
#             table_widget.setItem(row, col, item)
#
#     return table_widget


def create_heatmap_table(data: pd.DataFrame) -> QTableWidget:
    table_widget = QTableWidget(data.shape[0], data.shape[1])
    table_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
    table_widget.setHorizontalHeaderLabels(data.columns)
    table_widget.setVerticalHeaderLabels(data.index)

    for row in range(data.shape[0]):
        for col in range(data.shape[1]):
            cell_value = int(data.iat[row, col])

            if row == col:
                continue

            if cell_value < 5:
                red_intensity = int(192 + (255 - 192) * (cell_value / 4))
                color = QColor(red_intensity, 0, 0)
            else:
                green_intensity = int(192 + (255 - 192) * (1 - ((cell_value - 4) / (data.max().max() - 4))))
                color = QColor(0, green_intensity, 0)

            widget = QWidget()
            widget.setAutoFillBackground(True)
            widget.setStyleSheet(f"background-color: {color.name()};")

            layout = QVBoxLayout()
            label = QLabel(str(cell_value))
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
            widget.setLayout(layout)

            table_widget.setCellWidget(row, col, widget)

    return table_widget