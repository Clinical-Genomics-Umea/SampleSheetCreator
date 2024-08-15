import json

import numpy as np
import pandas as pd
import re
from pathlib import Path
from PySide6.QtCore import Qt, QSize, QEvent, QThread
from PySide6.QtGui import QStandardItemModel, QColor, QPen, QStandardItem, QPainter, QIntValidator, \
    QTextCursor, QTextDocument, QTextBlockFormat, QBrush
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy, QLabel, QHeaderView,
                               QAbstractScrollArea, QScrollArea,
                               QStyledItemDelegate, QTableView, QTabWidget, QFrame, QLineEdit,
                               QPushButton, QMenu, QTableWidget, QTableWidgetItem, QItemDelegate)

from modules.widgets.models import SampleSheetModel
from modules.widgets.run import RunInfoWidget
from modules.logic.validation_fns import (substitutions_heatmap_df, padded_index_df)
from modules.logic.validation import PreValidatorWorker
import pandera as pa
from modules.logic.validation_schema import prevalidation_schema
import yaml


def extract_numbers_from_string(input_string):
    """
    Extracts all numbers in a string that are one digit or longer.

    Parameters:
        input_string (str): The input string to extract numbers from.

    Returns:
        list: A list of all numbers found in the input string. If no numbers are found, returns an empty list.
    """

    numbers = re.findall(r'\d+', input_string)
    return numbers if numbers else []


def flowcell_validation(flowcell, instrument, settings):
    if instrument not in settings['flowcells']:
        return False, f"Instrument '{instrument}' not present in validation_settings.yaml ."
    if flowcell not in settings['flowcells'][instrument]['type']:
        return False, f"flowcell '{flowcell}' not present in validation_settings.yaml ."

    return True, ""


def lane_validation(df, flowcell, instrument, settings):
    allowed_lanes = set(map(int, settings['flowcells'][instrument]['type'][flowcell]))
    used_lanes = set(df['Lane'])

    disallowed_lanes = used_lanes.difference(allowed_lanes)

    if disallowed_lanes:
        return False, f"Lane(s) {disallowed_lanes} incompatible with selected flowcell {flowcell}."

    return True, ""


def sample_count_validation(df):
    if not isinstance(df, pd.DataFrame):
        return False, "Data could not be converted to a pandas dataframe."

    if df.empty:
        return False, "No data to validate (empty dataframe)."

    return True, ""


def load_from_yaml(config_file):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)


class PreValidationWidget(QTableWidget):
    def __init__(self, validation_settings_path: Path, model: SampleSheetModel, run_info: RunInfoWidget):
        super().__init__()

        self.thread = None
        self.worker = None

        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["Validator", "Status", "Message"])
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)

        self.model = model
        self.run_info = run_info
        self.validation_settings_path = validation_settings_path
        self.settings = load_from_yaml(validation_settings_path)

        self.flowcell = None
        self.instrument = None

        self.setColumnWidth(0, 200)
        self.setColumnWidth(1, 200)
        self.horizontalHeader().setStretchLastSection(True)

    def add_row(self, validator_text, is_valid, message):
        self.insertRow(self.rowCount())
        last_row = self.rowCount() - 1

        validator_item = QTableWidgetItem(validator_text)
        status_item = QTableWidgetItem("OK" if is_valid else "FAIL")
        status_item.setForeground(QBrush(QColor(0, 200, 0)) if is_valid else QBrush(QColor(200, 0, 0)))

        message_item = QTableWidgetItem(message)

        self.setItem(last_row, 0, validator_item)
        self.setItem(last_row, 1, status_item)
        self.setItem(last_row, 2, message_item)

    def populate_table(self, validation_results):
        self.insertRow(self.rowCount())

        for validator_text, (is_valid, message) in validation_results.items():
            self.add_row(validator_text, is_valid, message)


    def validate(self):
        self.setRowCount(0)

        self.thread = QThread()
        self.worker = PreValidatorWorker(self.validation_settings_path, self.model, self.run_info)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)

        self.worker.finished.connect(self.populate_table)



        worker.start()

        # statuses = []
        #
        # run_data = self.run_info.get_data()
        # df = self.model.to_dataframe()
        # df = df.replace(r'^\s*$', np.nan, regex=True)
        #
        # flowcell_type = run_data['Run_Extra']['FlowCellType']
        # instrument = run_data['Header']['Instrument']
        #
        # validations = [
        #     ("flowcell validation", flowcell_validation(flowcell_type, instrument, self.settings)),
        #     ("lane validation", lane_validation(df, flowcell_type, instrument, self.settings)),
        #     ("sample count validation", sample_count_validation(df))
        # ]
        #
        # for validation_name, (is_valid, message) in validations:
        #     print(validation_name, is_valid, message)
        #     self.add_row(validation_name, is_valid, message)
        #     statuses.append(is_valid)
        #
        # try:
        #     prevalidation_schema.validate(df)
        #     self.add_row("prevalidation schema", True, "")
        #     statuses.append(True)
        # except pa.errors.SchemaError as exc:
        #     self.add_row("prevalidation schema", False, str(exc))
        #     statuses.append(False)
        #
        # return all(statuses)


class DataValidationWidget(QWidget):
    def __init__(self, validation_settings_path: Path, model: SampleSheetModel, run_info: RunInfoWidget):
        super().__init__()

        self.model = model
        self.run_info_data = run_info.get_data()

        instrument = self.run_info_data['Header']['Instrument']
        settings = load_from_yaml(validation_settings_path)
        self.index_i5_rc = settings['flowcells'][instrument]

        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setLayout(self.layout)

        self.hspacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.vspacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vspacer_fixed = QSpacerItem(1, 20, QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.validate_tabwidget = QTabWidget()
        self.validate_tabwidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.layout.addWidget(self.validate_tabwidget)


    def get_widget_hlayout(self, table_widget):
        h_heatmap_layout = QHBoxLayout()
        h_heatmap_layout.addWidget(table_widget)
        h_heatmap_layout.addSpacerItem(self.hspacer)
        return h_heatmap_layout

    def get_tab(self, df):

        lane = df["Lane"].iloc[0]

        tab_scroll_area = QScrollArea()
        tab_scroll_area.setFrameShape(QFrame.NoFrame)

        tab_content = QWidget()
        tab_content_layout = QVBoxLayout()
        tab_content.setLayout(tab_content_layout)

        indexes_i7_padded = padded_index_df(df, 10, "IndexI7", "Sample_ID")

        if not self.index_i5_rc:
            indexes_i5_padded = padded_index_df(df, 10, "IndexI5", "Sample_ID")
        else:
            indexes_i5_padded = padded_index_df(df, 10, "IndexI5RC", "Sample_ID")

        indexes_i7_i5_padded = pd.merge(indexes_i7_padded, indexes_i5_padded, on="Sample_ID")

        i7_i5_substitution_df = substitutions_heatmap_df(indexes_i7_i5_padded)
        i7_i5_heatmap_table = create_heatmap_table(i7_i5_substitution_df)

        i7_substitution_df = substitutions_heatmap_df(indexes_i7_padded)
        i7_heatmap_table = create_heatmap_table(i7_substitution_df)

        i5_substitution_df = substitutions_heatmap_df(indexes_i5_padded)
        i5_heatmap_table = create_heatmap_table(i5_substitution_df)

        h_i7_i5_heatmap_layout = self.get_widget_hlayout(i7_i5_heatmap_table)
        h_i7_heatmap_layout = self.get_widget_hlayout(i7_heatmap_table)
        h_i5_heatmap_layout = self.get_widget_hlayout(i5_heatmap_table)

        v_heatmap_layout = QVBoxLayout()
        v_heatmap_layout.addWidget(QLabel(f"index I7 + I5 mismatch heatmap "))
        v_heatmap_layout.addLayout(h_i7_i5_heatmap_layout)
        v_heatmap_layout.addSpacerItem(self.vspacer)
        v_heatmap_layout.addWidget(QLabel(f"index I7 mismatch heatmap "))
        v_heatmap_layout.addLayout(h_i7_heatmap_layout)
        v_heatmap_layout.addSpacerItem(self.vspacer)
        v_heatmap_layout.addWidget(QLabel(f"index I5 mismatch heatmap "))
        v_heatmap_layout.addLayout(h_i5_heatmap_layout)
        v_heatmap_layout.addSpacerItem(self.vspacer)

        tab_content_layout.addLayout(v_heatmap_layout)
        tab_content_layout.addSpacerItem(self.vspacer_fixed)
        tab_content_layout.addWidget(QLabel(f"Color Balance Table for Lane {lane}"))

        color_balance_table = ColorBalanceWidget(df, self.index_i5_rc)
        tab_content_layout.addWidget(color_balance_table)
        tab_content_layout.addSpacerItem(self.vspacer)

        tab_scroll_area.setWidget(tab_content)

        return tab_scroll_area

    def validate(self):
        self.validate_tabwidget.clear()

        df = self.model.to_dataframe()

        used_lanes = list(df['Lane'].unique())
        for lane in used_lanes:

            df_lane = df[df['Lane'] == lane]

            tab = self.get_tab(df_lane)

            self.validate_tabwidget.addTab(tab, f"Lane {lane}")


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

        if total == 0:
            total = 0.00001

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
    def __init__(self, df: pd.DataFrame, is_i5_rc, parent=None):
        super(ColorBalanceWidget, self).__init__(parent)
        df = df.copy()
        df['Proportion'] = "1"
        if not is_i5_rc:
            df_seq = self.split_string_column(df, 'IndexI7', 'IndexI5')
        else:
            df_seq = self.split_string_column(df, 'IndexI7', 'IndexI5RC')

        df_seq.insert(0, 'Sample_ID', df['Sample_ID'])
        df_seq.insert(1, "Proportion", df['Proportion'])
        last_row_index = df.index[-1]
        df_seq.loc[last_row_index + 1] = pd.Series()
        df_seq.iloc[-1, 0] = "Summary"
        df_seq.iloc[-1, 1] = ""

        self.standard_model = self.dataframe_to_colorbalance_model(df_seq, is_i5_rc)
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

    def dataframe_to_colorbalance_model(self, dataframe, is_i5_rc):
        """
        Convert a Pandas DataFrame to a QStandardItemModel.

        :param dataframe: Pandas DataFrame to convert.
        :return: QStandardItemModel representing the DataFrame.

        Args:
            is_i5_rc:
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


# Heatmap

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


def create_heatmap_table(data: pd.DataFrame) -> QTableWidget:
    heatmap_table_widget = QTableWidget(data.shape[0], data.shape[1])
    heatmap_table_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
    heatmap_table_widget.setHorizontalHeaderLabels(data.columns)
    heatmap_table_widget.setVerticalHeaderLabels(data.index)

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

            heatmap_table_widget.setCellWidget(row, col, widget)

    heatmap_table_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
    heatmap_table_widget.setContentsMargins(0, 0, 0, 0)
    heatmap_table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    heatmap_table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    h_header_height = heatmap_table_widget.horizontalHeader().height()
    row_height = heatmap_table_widget.rowHeight(0)
    no_items = heatmap_table_widget.columnCount()
    heatmap_table_widget.setMaximumHeight(h_header_height + row_height * no_items + 5)

    heatmap_table_widget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)
    heatmap_table_widget.setItemDelegate(NonEditableDelegate())

    return heatmap_table_widget


class NonEditableDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        # Return None to make the item non-editable
        return None


