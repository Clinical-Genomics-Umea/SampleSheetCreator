import json

import numpy as np
import pandas as pd
from PySide6.QtCore import Qt, QSize, QEvent
from PySide6.QtGui import QStandardItemModel, QColor, QPen, QStandardItem, QPainter, QIntValidator, \
    QTextCursor, QTextDocument, QTextBlockFormat
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy, QLabel, QHeaderView,
                               QAbstractScrollArea, QScrollArea,
                               QItemDelegate, QStyledItemDelegate, QTableView, QTabWidget, QFrame, QLineEdit,
                               QPushButton, QMenu)
from pandera.errors import SchemaErrors

from modules.run_classes import RunInfo
from modules.validation.heatmap import set_heatmap_table_properties, create_heatmap_table
from modules.validation.validation_fns import substitutions_heatmap_df, split_df_by_lane, \
    create_table_from_dataframe, qstandarditemmodel_to_dataframe, df_to_i7_i5_df
from modules.validation.validation_schema import prevalidation_schema


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

            indexes_df = df_to_i7_i5_df(
                lanes_df[lane],
                10,
                10,
                "I7_Index",
                "I5_Index",
                "Sample_ID"
            )

            heatmap_table = create_heatmap_table(substitutions_heatmap_df(indexes_df))
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
        df = self.split_string_column(dataframe, 'I7_Index', 'I5_Index')
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
        # self.wordWrap()

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


