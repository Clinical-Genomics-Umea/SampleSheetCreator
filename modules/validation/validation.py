import json

import numpy as np
import pandas as pd
import re
from pathlib import Path
from PySide6.QtCore import Qt, QSize, QEvent
from PySide6.QtGui import QStandardItemModel, QColor, QPen, QStandardItem, QPainter, QIntValidator, \
    QTextCursor, QTextDocument, QTextBlockFormat, QBrush
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy, QLabel, QHeaderView,
                               QAbstractScrollArea, QScrollArea,
                               QStyledItemDelegate, QTableView, QTabWidget, QFrame, QLineEdit,
                               QPushButton, QMenu, QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem)
from pandera.errors import SchemaErrors

from modules.run import RunInfo
from modules.validation.heatmap import set_heatmap_table_properties, create_heatmap_table
from modules.validation.validation_fns import substitutions_heatmap_df, split_df_by_lane, \
    create_table_from_dataframe, qsi_mmodel_to_dataframe, concatenate_indexes
from modules.validation.validation_schema import prevalidation_schema
import yaml


def set_colorbalance_table_properties(table):

    table.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
    table.setContentsMargins(0, 0, 0, 0)
    table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    last_row = table.standard_model.rowCount() - 1
    table.setRowHeight(last_row, 140)
    table.setItemDelegate(ColorBalanceRowDelegate())

    table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.setFixedWidth(1500)

    return table


def extract_numbers_from_string(input_string):
    """
    Extracts all numbers in a string that are one digit or longer.

    Parameters:
        input_string (str): The input string to extract numbers from.

    Returns:
        list: A list of all numbers found in the input string.
    """
    return re.findall(r'\d+', input_string)


def flowcell_validation(flowcell, instrument, settings):
    if instrument not in settings['flowcell_type']:
        return False, f"Instrument '{instrument}' not present in validation_settings.yaml ."
    if flowcell not in settings['flowcell_type'][instrument]:
        return False, f"flowcell '{flowcell}' not present in validation_settings.yaml ."

    return True, ""


def lane_validation(df, flowcell, instrument, settings):
    allowed_lanes = set(settings['flowcell_type'][instrument][flowcell])
    lane_strs = set(df['Lane'])

    used_lanes = set()
    for lane_str in lane_strs:
        lanes_list = extract_numbers_from_string(lane_str)
        used_lanes.update(lanes_list)

    disallowed_lanes = used_lanes.difference(allowed_lanes)

    if disallowed_lanes:
        return False, f"Disallowed lane(s) '{disallowed_lanes}' present in the Lane column."

    return True, ""


def sample_count_validation(df):
    if not isinstance(df, pd.DataFrame):
        return False, "Data could not be converted to a pandas dataframe."

    if df.empty:
        return False, "No data to validate (empty dataframe)."

    return True, ""


def get_table_widget():
    tw = QTableWidget()
    tw.setColumnCount(3)
    tw.setHorizontalHeaderLabels(["validator", "status", "error"])

    tw.setColumnWidth(0, 150)
    tw.setColumnWidth(1, 100)

    header = tw.horizontalHeader()
    header.setSectionResizeMode(2, QHeaderView.Stretch)
    tw.setContentsMargins(0, 0, 0, 0)

    size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    tw.setSizePolicy(size_policy)

    tw.setMinimumHeight(100)
    tw.setMaximumHeight(130)

    return tw


def load_from_yaml(config_file):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)


class PreValidationWidget(QWidget):
    def __init__(self, validation_settings_path: Path, model: QStandardItemModel, run_info: RunInfo):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.table_widget = get_table_widget()
        self.layout.addWidget(self.table_widget)

        self.setContentsMargins(0, 0, 0, 0)
        self.table_widget.setContentsMargins(0, 0, 0, 0)

        self.settings = load_from_yaml(validation_settings_path)

        self.model = model
        self.run_info = run_info

        self.flowcell = None
        self.instrument = None

    def add_row(self, validator, is_valid, message):
        self.table_widget.insertRow(self.table_widget.rowCount())

        item1 = QTableWidgetItem(validator)

        if is_valid:
            item2 = QTableWidgetItem("OK")
            item2.setForeground(QBrush(QColor(0, 200, 0)))
        else:
            item2 = QTableWidgetItem(str("FAIL"))
            item2.setForeground(QBrush(QColor(200, 0, 0)))

        item3 = QTableWidgetItem(message)

        last_row = self.table_widget.rowCount() - 1

        self.table_widget.setItem(last_row, 0, item1)
        self.table_widget.setItem(last_row, 1, item2)
        self.table_widget.setItem(last_row, 2, item3)

    def validate(self):
        self.table_widget.setRowCount(0)

        run_data = self.run_info.get_data()
        df = qsi_mmodel_to_dataframe(self.model)

        flowcell = run_data['Run_Extra']['FlowCellType']
        instrument = run_data['Header']['Instrument']

        print(run_data)
        print(self.settings)

        is_valid, message = flowcell_validation(flowcell, instrument, self.settings)
        self.add_row("flowcell validation", is_valid, message)
        if not is_valid:
            return False

        is_valid, message = lane_validation(df, flowcell, instrument, self.settings)
        self.add_row("lane validation", is_valid, message)
        if not is_valid:
            return False

        is_valid, message = sample_count_validation(df)
        self.add_row("sample count validation", is_valid, message)
        if not is_valid:
            return False

        return True


class DataValidationWidget(QWidget):
    def __init__(self, model: QStandardItemModel, run_info: RunInfo):
        super().__init__()

        self.model = model
        self.run_info_data = run_info.get_data()

        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.hspacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.vspacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vspacer_fixed = QSpacerItem(1, 20, QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.validate_tabwidget = QTabWidget()
        self.validate_tabwidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.layout.addWidget(self.validate_tabwidget)
        self.layout.addSpacerItem(self.vspacer)

    def get_tab(self, lane, lanes_df):

        tab_scroll_area = QScrollArea()
        tab_scroll_area.setFrameShape(QFrame.NoFrame)

        tab_content = QWidget()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        tab_content.setLayout(main_layout)

        main_layout.addWidget(QLabel(f"Index Heatmap for Lane {lane}"))

        indexes_df = concatenate_indexes(
            lanes_df[lane],
            10,
            10,
            "Index_I7",
            "Index_I5",
            "Sample_ID"
        )

        substitution_df = substitutions_heatmap_df(indexes_df)
        heatmap_table = create_heatmap_table(substitution_df)

        h_heatmap_layout = QHBoxLayout()
        h_heatmap_layout.setContentsMargins(0, 0, 0, 0)
        v_heatmap_layout = QVBoxLayout()
        v_heatmap_layout.setContentsMargins(0, 0, 0, 0)

        h_heatmap_layout.addWidget(heatmap_table)
        h_heatmap_layout.addSpacerItem(self.hspacer)
        v_heatmap_layout.addLayout(h_heatmap_layout)
        v_heatmap_layout.addSpacerItem(self.vspacer)

        tab_main_layout.addLayout(v_heatmap_layout)

        tab_main_layout.addSpacerItem(self.vspacer_fixed)
        tab_main_layout.addWidget(QLabel(f"Color Balance Table for Lane {lane}"))

        color_balance_table = ColorBalanceWidget(lanes_df[lane])
        tab_main_layout.addWidget(color_balance_table)
        tab_main_layout.addSpacerItem(self.vspacer)

        tab_scroll_area.setWidget(tab_content)

        return tab_scroll_area

    def validate(self):
        self.validate_tabwidget.clear()

        df = qsi_mmodel_to_dataframe(self.model)
        lanes_df = split_df_by_lane(df)

        for lane in lanes_df:
            tab = self.set_tab(lane, lanes_df)
            self.validate_tabwidget.addTab(tab, f"Lane {lane}")


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


class IndexColorBalanceModel(QStandardItemModel):

    def __init__(self, parent):
        super(IndexColorBalanceModel, self).__init__(parent=parent)
        self.dataChanged.connect(self.update_summation)

    def update_summation(self):

        for col in range(2, self.columnCount()):
            bases_count = {'A': 0, 'C': 0, 'G': 0, 'T': 0}
            merged = {}

            for row in range(self.rowCount() - 1):
                proportion = int(self.item(row, 1).text())
                base = self.item(row, col).text()
                bases_count[base] += proportion

            color_counts = self.base_to_color_count(bases_count)
            normalized_color_counts = self.normalize(color_counts)
            normalized_base_counts = self.normalize(bases_count)

            merged['colors'] = normalized_color_counts
            merged['bases'] = normalized_base_counts
            norm_json = json.dumps(merged)

            last_row = self.rowCount() - 1
            self.setData(self.index(last_row, col), norm_json, Qt.EditRole)

    @staticmethod
    def merge(dict1, dict2):
        res = dict1 | {'--': '---'} | dict2
        return res

    @staticmethod
    def normalize(input_dict):
        # Calculate the sum of values in the input dictionary
        total = sum(input_dict.values())

        # Normalize the values and create a new dictionary
        normalized_dict = {key: round(value / total, 2) for key, value in input_dict.items()}

        return normalized_dict

    @staticmethod
    def base_to_color_count(dict1):
        color_count = {
            'B': 0,
            'G': 0,
            'D': 0,
        }

        for base, count in dict1.items():
            if base == 'A':
                color_count['B'] = count
            elif base == 'C':
                color_count['B'] = count * 0.5
                color_count['G'] = count * 0.5
            elif base == 'T':
                color_count['G'] = count
            elif base == 'G':
                color_count['D'] = count

        return color_count


class ColorBalanceRowDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):

        last_row = index.model().rowCount() - 1

        if index.isValid() and index.column() >= 2 and index.row() == last_row:
            self.paint_color_balance_row(painter, option, index)

        elif index.isValid() and index.column() == 2:
            self.paint_gg_i1_1_row(painter, option, index)

        elif index.isValid() and index.column() == 3:
            self.paint_gg_i1_2_row(painter, option, index)

        elif index.isValid() and index.column() == 12:
            self.paint_gg_i2_1_row(painter, option, index)

        elif index.isValid() and index.column() == 13:
            self.paint_gg_i2_2_row(painter, option, index)

        elif index.isValid():
            super().paint(painter, option, index)

    def paint_gg_i1_1_row(self, painter, option, index):
        index_other = index.model().index(index.row(), 3)
        value = index.data(Qt.DisplayRole)
        value_other = index_other.data(Qt.DisplayRole)

        if value == value_other == 'G':
            painter.save()
            painter.fillRect(option.rect, QColor(255, 127, 127))
            super().paint(painter, option, index)
            painter.restore()
        else:
            super().paint(painter, option, index)

    def paint_gg_i1_2_row(self, painter, option, index):
        index_other = index.model().index(index.row(), 2)
        value = index.data(Qt.DisplayRole)
        value_other = index_other.data(Qt.DisplayRole)

        if value == value_other == 'G':
            painter.save()
            painter.fillRect(option.rect, QColor(255, 127, 127))
            super().paint(painter, option, index)
            painter.restore()
        else:
            super().paint(painter, option, index)

    def paint_gg_i2_1_row(self, painter, option, index):
        index_other = index.model().index(index.row(), 13)
        value = index.data(Qt.DisplayRole)
        value_other = index_other.data(Qt.DisplayRole)

        if value == value_other == 'G':
            painter.save()
            painter.fillRect(option.rect, QColor(255, 127, 127))
            super().paint(painter, option, index)
            painter.restore()
        else:
            super().paint(painter, option, index)

    def paint_gg_i2_2_row(self, painter, option, index):
        index_other = index.model().index(index.row(), 12)
        value = index.data(Qt.DisplayRole)
        value_other = index_other.data(Qt.DisplayRole)

        if value == value_other == 'G':
            painter.save()
            painter.fillRect(option.rect, QColor(255, 127, 127))
            super().paint(painter, option, index)
            painter.restore()
        else:
            super().paint(painter, option, index)


    def paint_color_balance_row(self, painter, option, index):
        json_data = index.data(Qt.DisplayRole)
        if json_data:
            data = json.loads(json_data)

            color_lines = "\n".join([f"{key}: {value}" for key, value in data['colors'].items()])
            bases_lines = "\n".join([f"{key}: {value}" for key, value in data['bases'].items()])
            multiline = color_lines + '\n----\n' + bases_lines

            document = QTextDocument()
            document.setPlainText(multiline)

            # if data['colors']['Da'] > 0.5:
            #     self.setDarkBackgroundColorWarning(document, QColor(255, 127, 127))

            if data['colors']['G'] < 0.1:
                self.setNoGreenBackgroundColorWarning(document, QColor(255, 127, 127))

            # Adjust the document size to the cell size
            document.setTextWidth(option.rect.width())

            # Render the document
            painter.save()
            painter.translate(option.rect.topLeft())
            document.drawContents(painter)
            painter.restore()


    def setDarkBackgroundColorWarning(self, document, color):
        cursor = QTextCursor(document)
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.NextBlock)
        cursor.movePosition(QTextCursor.NextBlock)

        # Set the background color for the first block
        block_format = QTextBlockFormat()
        block_format.setBackground(color)
        cursor.setBlockFormat(block_format)

    def setNoGreenBackgroundColorWarning(self, document, color):
        cursor = QTextCursor(document)
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.NextBlock)

        # Set the background color for the first block
        block_format = QTextBlockFormat()
        block_format.setBackground(color)
        cursor.setBlockFormat(block_format)

    def sizeHint(self, option, index):

        last_row = index.model().rowCount() - 1

        if index.isValid() and index.column() >= 2 and index.row() == last_row:

            document = QTextDocument()
            document.setPlainText(index.model().data(index, Qt.DisplayRole))

            # Adjust the document size to the cell size
            document.setTextWidth(option.rect.width())

            return QSize(document.idealWidth(), document.size().height())

        else:
            return super().sizeHint(option, index)

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonDblClick and index.column() == 0:
            menu = QMenu()
            menu.addAction("Action 1", lambda: self.menuAction(index, "Action 1"))
            menu.addAction("Action 2", lambda: self.menuAction(index, "Action 2"))
            menu.addAction("Action 3", lambda: self.menuAction(index, "Action 3"))
            menu.exec_(event.globalPos())
            return True  # Consume the event

        else:
            return super().editorEvent(event, model, option, index)

    def menuAction(self, index, action_text):
        print(f"Double-clicked cell at row {index.row()}, column {index.column()}. Action: {action_text}")


    def commitAndCloseEditor(self):
        print("hello")
        editor = self.sender()
        if isinstance(editor, QPushButton):
            self.commitData.emit(editor)
            self.closeEditor.emit(editor, QStyledItemDelegate.EditNextItem)

    def createIntValidationEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setValidator(QIntValidator())  # Set an integer validator
        return editor


class ColorBalanceWidget(QTableView):
    def __init__(self, dataframe: pd.DataFrame, parent=None):
        super(ColorBalanceWidget, self).__init__(parent)
        dataframe.reset_index()
        dataframe['Proportion'] = "1"
        df = self.split_string_column(dataframe, 'Index_I7', 'Index_I5')
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
        self.setup()

    def setup(self):
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setContentsMargins(0, 0, 0, 0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        last_row = self.standard_model.rowCount() - 1
        self.setRowHeight(last_row, 140)
        self.setItemDelegate(ColorBalanceRowDelegate())

        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setFixedWidth(1500)

    def dataframe_to_colorbalance_model(self, dataframe):
        """
        Convert a Pandas DataFrame to a QStandardItemModel.

        :param dataframe: Pandas DataFrame to convert.
        :return: QStandardItemModel representing the DataFrame.
        """
        model = IndexColorBalanceModel(parent=self)

        column_names = [col_name.replace('Index_', '') for col_name in dataframe.columns]

        # Set the column headers as the model's horizontal headers
        model.setHorizontalHeaderLabels(column_names)

        for row_index, row_data in dataframe.iterrows():
            row_items = [QStandardItem(str(item)) for item in row_data]
            model.appendRow(row_items)

        return model

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())

        model = self.model()
        column_count = model.columnCount()
        row_count = model.rowCount()

        last_row_index = model.rowCount() - 1

        thick_pen = QPen(QColor("dark gray"), 2, Qt.SolidLine)
        painter.setPen(thick_pen)

        for col in range(column_count):
            last_row_rect = self.visualRect(model.index(last_row_index, col))
            painter.drawLine(last_row_rect.topLeft(), last_row_rect.topRight())

        for row in range(row_count):
            i5_i7_index_boundry_rect = self.visualRect(model.index(row, 11))
            painter.drawLine(i5_i7_index_boundry_rect.topRight(), i5_i7_index_boundry_rect.bottomRight())

        for row in range(row_count):
            i5_i7_index_boundry_rect = self.visualRect(model.index(row, 0))
            painter.drawLine(i5_i7_index_boundry_rect.topRight(), i5_i7_index_boundry_rect.bottomRight())

        for row in range(row_count):
            i5_i7_index_boundry_rect = self.visualRect(model.index(row, 1))
            painter.drawLine(i5_i7_index_boundry_rect.topRight(), i5_i7_index_boundry_rect.bottomRight())

    @staticmethod
    def split_string_column(input_df, column_name1, column_name2):
        """
        Split a column of strings into multiple columns with one character per column.

        :param dataframe: Pandas DataFrame containing the string column.
        :param column_name: Name of the column containing the strings.
        :return: DataFrame with one column per character in the strings.
        """
        # Use apply and pd.Series to split the string column into multiple columns
        df1 = input_df[column_name1].apply(lambda x: pd.Series(list(x)))
        # df1 = input_df[column_name1].apply(string_to_ndarray)
        df1.columns = [f"{column_name1}_{i + 1}" for i in range(10)]

        df2 = input_df[column_name2].apply(lambda x: pd.Series(list(x)))
        # df2 = input_df[column_name2].apply(string_to_ndarray)
        df2.columns = [f"{column_name2}_{i + 1}" for i in range(10)]

        return pd.concat([df1, df2], axis=1)


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


