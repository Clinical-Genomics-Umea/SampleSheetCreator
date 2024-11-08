import json

import numpy as np
import pandas as pd
from PySide6.QtCore import Qt, QSize, QEvent, QThread, Slot
from PySide6.QtGui import (
    QColor,
    QPen,
    QStandardItem,
    QPainter,
    QIntValidator,
    QTextCursor,
    QTextDocument,
    QTextBlockFormat,
    QBrush,
)
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QLabel,
    QHeaderView,
    QAbstractScrollArea,
    QScrollArea,
    QStyledItemDelegate,
    QTableView,
    QTabWidget,
    QFrame,
    QLineEdit,
    QPushButton,
    QMenu,
    QTableWidget,
    QTableWidgetItem,
    QItemDelegate,
)

from models.validation import IndexColorBalanceModel


class ValidationWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget()

        self.pre_validation_widget = PreValidationWidget()
        self.index_validation_widget = IndexDistanceValidationWidget()
        self.color_balance_validation_widget = MainColorBalanceWidget()
        self.tab_widget.addTab(self.pre_validation_widget, "pre-validation")
        self.tab_widget.addTab(self.index_validation_widget, "index validation")
        self.tab_widget.addTab(
            self.color_balance_validation_widget, "color balance validation"
        )

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        self.validate_button = QPushButton("Validate")
        hbox.addWidget(self.validate_button)
        hbox.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding))

        self.layout.addLayout(hbox)
        self.layout.addWidget(self.tab_widget)


class PreValidationWidget(QTableWidget):
    def __init__(self):
        super().__init__()

        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["Validator", "Status", "Message"])
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)

        self.setColumnWidth(0, 200)
        self.setColumnWidth(1, 200)
        self.horizontalHeader().setStretchLastSection(True)

    def _add_row(self, validator_text, is_valid, message):
        self.insertRow(self.rowCount())
        last_row = self.rowCount() - 1

        validator_item = QTableWidgetItem(validator_text)
        status_item = QTableWidgetItem("OK" if is_valid else "FAIL")
        status_item.setForeground(
            QBrush(QColor(0, 200, 0)) if is_valid else QBrush(QColor(200, 0, 0))
        )

        message_item = QTableWidgetItem(message)

        self.setItem(last_row, 0, validator_item)
        self.setItem(last_row, 1, status_item)
        self.setItem(last_row, 2, message_item)

    @Slot(dict)
    def populate(self, results):
        print("view", results)

        self.setRowCount(0)

        for validation_name, is_valid, message in results:
            self._add_row(validation_name, is_valid, message)


class IndexDistanceValidationWidget(QTabWidget):
    def __init__(self):
        super().__init__()

        self.worker = None
        self.thread = None

        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setLayout(self.layout)

        self.hspacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.vspacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vspacer_fixed = QSpacerItem(1, 20, QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def _get_heatmap_hlayout(self, table_widget):
        h_heatmap_layout = QHBoxLayout()
        h_heatmap_layout.addWidget(table_widget)
        h_heatmap_layout.addSpacerItem(self.hspacer)
        return h_heatmap_layout

    def _get_tab(self, substitutions):

        tab_scroll_area = QScrollArea()
        tab_scroll_area.setFrameShape(QFrame.NoFrame)

        tab_content = QWidget()
        tab_content_layout = QVBoxLayout()
        tab_content.setLayout(tab_content_layout)

        i7_i5_heatmap_table = self.heatmap_tablewidget(
            substitutions["i7_i5_substitutions"]
        )
        i7_heatmap_table = self.heatmap_tablewidget(substitutions["i7_substitutions"])
        i5_heatmap_table = self.heatmap_tablewidget(substitutions["i5_substitutions"])

        h_i7_i5_heatmap_layout = self._get_heatmap_hlayout(i7_i5_heatmap_table)
        h_i7_heatmap_layout = self._get_heatmap_hlayout(i7_heatmap_table)
        h_i5_heatmap_layout = self._get_heatmap_hlayout(i5_heatmap_table)

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

        tab_scroll_area.setWidget(tab_content)

        return tab_scroll_area

    @staticmethod
    def heatmap_tablewidget(data: pd.DataFrame) -> QTableWidget:
        heatmap_tablewidget = QTableWidget(data.shape[0], data.shape[1])
        heatmap_tablewidget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        heatmap_tablewidget.setHorizontalHeaderLabels(data.columns)
        heatmap_tablewidget.setVerticalHeaderLabels(data.index)

        for row in range(data.shape[0]):
            for col in range(data.shape[1]):
                cell_value = int(data.iat[row, col])

                if row == col:
                    continue

                if cell_value < 5:
                    red_intensity = int(192 + (255 - 192) * (cell_value / 4))
                    color = QColor(red_intensity, 0, 0)
                else:
                    green_intensity = int(
                        192
                        + (255 - 192)
                        * (1 - ((cell_value - 4) / (data.max().max() - 4)))
                    )
                    color = QColor(0, green_intensity, 0)

                widget = QWidget()
                widget.setAutoFillBackground(True)
                widget.setStyleSheet(f"background-color: {color.name()};")

                layout = QVBoxLayout()
                label = QLabel(str(cell_value))
                label.setAlignment(Qt.AlignCenter)
                layout.addWidget(label)
                widget.setLayout(layout)

                heatmap_tablewidget.setCellWidget(row, col, widget)

        heatmap_tablewidget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        heatmap_tablewidget.setContentsMargins(0, 0, 0, 0)
        heatmap_tablewidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        heatmap_tablewidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        h_header_height = heatmap_tablewidget.horizontalHeader().height()
        row_height = heatmap_tablewidget.rowHeight(0)
        no_items = heatmap_tablewidget.columnCount()
        heatmap_tablewidget.setMaximumHeight(
            h_header_height + row_height * no_items + 5
        )

        heatmap_tablewidget.setSizeAdjustPolicy(
            QAbstractScrollArea.AdjustToContentsOnFirstShow
        )
        heatmap_tablewidget.setItemDelegate(NonEditableDelegate())

        return heatmap_tablewidget

    @Slot(object)
    def populate(self, results):

        print(results)

        self._delete_tabs()

        if isinstance(results, str):
            self.addTab(QLabel(results), "Error")
            return

        for lane in results:
            tab = self._get_tab(results[lane])
            self.addTab(tab, f"Lane {lane}")

    def _delete_tabs(self):
        # Remove and delete each tab widget
        while self.count() > 0:
            widget = self.widget(0)  # Get the first widget in the tab widget
            self.removeTab(0)  # Remove the tab
            self._clear_widget(widget)

    def _clear_widget(self, widget: QWidget):
        # Step 1: Clear the layout if it exists
        layout = widget.layout()
        if layout:
            # Clear the layout and delete its contents
            while layout.count() > 0:
                item = layout.takeAt(0)
                child_widget = item.widget()
                if child_widget:
                    child_widget.deleteLater()
                sub_layout = item.layout()
                if sub_layout:
                    self._clear_widget(sub_layout.widget())
                item.deleteLater()

            # Optionally, delete the layout itself
            widget.setLayout(None)

        for child in widget.findChildren(QWidget):
            child.deleteLater()


class MainColorBalanceWidget(QTabWidget):

    def __init__(self):
        super().__init__()

        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setLayout(self.layout)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def _clear_widget(self, widget: QWidget):
        layout = widget.layout()
        if layout:
            while layout.count() > 0:
                item = layout.takeAt(0)
                child_widget = item.widget()
                if child_widget:
                    child_widget.deleteLater()
                sub_layout = item.layout()
                if sub_layout:
                    self._clear_widget(sub_layout.widget())
                item.deleteLater()

            widget.setLayout(None)

        for child in widget.findChildren(QWidget):
            child.deleteLater()

    def _delete_tabs(self):
        # Remove and delete each tab widget
        while self.count() > 0:
            widget = self.widget(0)  # Get the first widget in the tab widget
            self.removeTab(0)  # Remove the tab
            self._clear_widget(widget)

    @Slot(object)
    def populate(self, results):
        self._delete_tabs()

        for lane in results:
            tab_scroll_area = QScrollArea()
            tab_scroll_area.setFrameShape(QFrame.NoFrame)

            color_balance_table = ColorBalanceWidget(results[lane])

            self.addTab(color_balance_table, f"Lane {lane}")


class ColorBalanceWidget(QTableView):
    def __init__(self, merged_df, parent=None):
        super(ColorBalanceWidget, self).__init__(parent)
        df = merged_df.copy()

        df["Proportion"] = "1"

        cols = ["Sample_ID", "Proportion"] + [
            col for col in df.columns if col not in ["Sample_ID", "Proportion"]
        ]
        df = df[cols]

        last_row_index = df.index[-1]
        df.loc[last_row_index + 1] = pd.Series()
        df.iloc[-1, 0] = "Summary"
        df.iloc[-1, 1] = ""

        self.cb_model = self.make_color_balance_model(df)
        self.setModel(self.cb_model)
        self.cb_model.update_summation()
        self.verticalHeader().setVisible(False)
        self.setup()

    def setup(self):
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setContentsMargins(0, 0, 0, 0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        last_row = self.cb_model.rowCount() - 1
        self.setRowHeight(last_row, 140)
        self.setItemDelegate(ColorBalanceRowDelegate())

        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setFixedWidth(1500)

    def make_color_balance_model(self, df):
        """
        Convert a Pandas DataFrame to a QStandardItemModel.

        :param df: Pandas DataFrame to convert.
        :return: QStandardItemModel representing the DataFrame.
        """
        model = IndexColorBalanceModel(parent=self)

        column_names = [col_name.replace("Index", "") for col_name in df.columns]

        # Set the column headers as the model's horizontal headers
        model.setHorizontalHeaderLabels(column_names)

        for row_index, row_data in df.iterrows():
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
            painter.drawLine(
                i5_i7_index_boundry_rect.topRight(),
                i5_i7_index_boundry_rect.bottomRight(),
            )

        for row in range(row_count):
            i5_i7_index_boundry_rect = self.visualRect(model.index(row, 0))
            painter.drawLine(
                i5_i7_index_boundry_rect.topRight(),
                i5_i7_index_boundry_rect.bottomRight(),
            )

        for row in range(row_count):
            i5_i7_index_boundry_rect = self.visualRect(model.index(row, 1))
            painter.drawLine(
                i5_i7_index_boundry_rect.topRight(),
                i5_i7_index_boundry_rect.bottomRight(),
            )

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

        if value == value_other == "G":
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

        if value == value_other == "G":
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

            color_lines = "\n".join(
                [f"{key}: {value}" for key, value in data["colors"].items()]
            )
            bases_lines = "\n".join(
                [f"{key}: {value}" for key, value in data["bases"].items()]
            )
            multiline = color_lines + "\n----\n" + bases_lines

            document = QTextDocument()
            document.setPlainText(multiline)

            # if data['colors']['Da'] > 0.5:
            #     self.setDarkBackgroundColorWarning(document, QColor(255, 127, 127))

            if data["colors"]["G"] < 0.1:
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
        print(
            f"Double-clicked cell at row {index.row()}, column {index.column()}. Action: {action_text}"
        )

    def commitAndCloseEditor(self):

        editor = self.sender()
        if isinstance(editor, QPushButton):
            self.commitData.emit(editor)
            self.closeEditor.emit(editor, QStyledItemDelegate.EditNextItem)

    def createIntValidationEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setValidator(QIntValidator())  # Set an integer validator
        return editor


# Heatmap

# def set_heatmap_table_properties(table):
#
#     table.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
#     table.setContentsMargins(0, 0, 0, 0)
#     table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
#     table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
#
#     h_header_height = table.horizontalHeader().height()
#     row_height = table.rowHeight(0)
#     no_items = table.columnCount()
#     table.setMaximumHeight(h_header_height + row_height * no_items + 5)
#
#     table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)
#
#     table.setItemDelegate(NonEditableDelegate())
#
#     return table


class NonEditableDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        # Return None to make the item non-editable
        return None
