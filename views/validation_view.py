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
    QPalette,
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
    QFormLayout,
)

from models.validation.dataset_validation import IndexColorBalanceModel


class MainValidationWidget(QWidget):
    def __init__(self, dataset_mgr):
        super().__init__()

        self.dataset_mgr = dataset_mgr
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget()

        self.pre_validation_widget = PreValidationWidget()
        self.dataset_validation_widget = DataSetValidationWidget()
        self.main_index_validation_widget = MainIndexDistanceValidationWidget()
        self.main_color_balance_validation_widget = MainColorBalanceWidget(
            self.dataset_mgr
        )

        self.tab_widget.addTab(self.pre_validation_widget, "pre-validation")
        self.tab_widget.addTab(self.dataset_validation_widget, "dataset validation")
        self.tab_widget.addTab(self.main_index_validation_widget, "index validation")
        self.tab_widget.addTab(
            self.main_color_balance_validation_widget, "color balance validation"
        )

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        self.validate_button = QPushButton("Validate")
        hbox.addWidget(self.validate_button)
        hbox.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding))

        self.layout.addLayout(hbox)
        self.layout.addWidget(self.tab_widget)

    def clear_validation_widgets(self):
        self.pre_validation_widget.clear()
        self.dataset_validation_widget.clear()
        self.main_index_validation_widget.clear()
        self.main_color_balance_validation_widget.clear()


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

    def clear(self):
        self.setRowCount(0)

    @Slot(dict)
    def populate(self, validation_results):

        self.setRowCount(0)

        for validation_name, is_valid, message in validation_results:
            self._add_row(validation_name, is_valid, message)


class DataSetValidationWidget(QTabWidget):
    def __init__(self):
        super().__init__()

        self.content_widget = QWidget()
        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setLayout(self.layout)

        self.layout = QVBoxLayout()

        self.setContentsMargins(0, 0, 0, 0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setLayout(self.layout)

    def clear(self):
        # Remove and delete each tab widget
        while self.count() > 0:
            widget = self.widget(0)  # Get the first widget in the tab widget
            self.removeTab(0)  # Remove the tab
            widget.deleteLater()

    def populate(self, samples_dfs):

        # Add main data tab
        self.addTab(self.get_widget_table(samples_dfs["no_explode"]), "all data")

        # Add application profile names tab
        app_profile_tab = QTabWidget()
        self.addTab(app_profile_tab, "application profile")
        unique_app_profile_names = samples_dfs["apn_explode"][
            "ApplicationName"
        ].unique()

        for app_profile_name in unique_app_profile_names:
            df_app_profile = samples_dfs["apn_explode"][
                samples_dfs["apn_explode"]["ApplicationName"] == app_profile_name
            ]
            app_profile_widget = self.get_widget_table(df_app_profile)
            app_profile_tab.addTab(app_profile_widget, app_profile_name)

        # Add lanes tab
        lane_tab = QTabWidget()
        self.addTab(lane_tab, "lanes")
        unique_lanes = samples_dfs["lane_explode"]["Lane"].unique()

        for lane in unique_lanes:
            lane_name = f"lane {lane}"
            df_lane = samples_dfs["lane_explode"][
                samples_dfs["lane_explode"]["Lane"] == lane
            ]
            lane_widget = self.get_widget_table(df_lane)
            lane_tab.addTab(lane_widget, lane_name)

    @staticmethod
    def get_widget_table(dataframe):
        widget = QWidget()
        table = QTableWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        layout.addWidget(table)

        # Set row and column count
        table.setRowCount(dataframe.shape[0])
        table.setColumnCount(dataframe.shape[1])

        # Set column headers
        table.setHorizontalHeaderLabels(dataframe.columns)

        # Populate the table with DataFrame data
        for row_idx in range(dataframe.shape[0]):
            for col_idx in range(dataframe.shape[1]):
                cell_value = str(dataframe.iloc[row_idx, col_idx])
                table.setItem(row_idx, col_idx, QTableWidgetItem(cell_value))

        return widget


class MainIndexDistanceValidationWidget(QTabWidget):
    def __init__(self):
        super().__init__()

        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setLayout(self.layout)

        self.hspacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.vspacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vspacer_fixed = QSpacerItem(1, 20, QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    @Slot(object)
    def populate(self, results):

        if isinstance(results, str):
            self.addTab(QLabel(results), "Error")
            return

        for lane in results:
            tab = LaneIndexDistanceWidget(results[lane])
            self.addTab(tab, f"lane {lane}")

    def clear(self):
        print("clearing main index distance validation widget")
        # Remove and delete each tab widget
        while self.count() > 0:
            widget = self.widget(0)  # Get the first widget in the tab widget
            self.removeTab(0)  # Remove the tab
            widget.deleteLater()


class LaneIndexDistanceWidget(QScrollArea):

    def __init__(self, lane_substitutions):
        super().__init__()
        self.content_widget = QWidget()
        self.setFrameShape(QFrame.NoFrame)
        self.layout = QVBoxLayout(self.content_widget)

        for heatmap_type, heatmap_name in (
            ("i7_i5_substitutions", "index I7 + I5 mismatch"),
            ("i7_substitutions", "index I7 mismatch"),
            ("i5_substitutions", "index I5 mismatch"),
        ):
            self.layout.addWidget(QLabel(f"{heatmap_name} heatmap "))

            heatmap_table = IndexDistanceHeatMap(lane_substitutions[heatmap_type])
            self.layout.addWidget(heatmap_table)

        self.setWidget(self.content_widget)
        self.setWidgetResizable(True)


class IndexDistanceHeatMap(QTableWidget):
    def __init__(self, substitutions):
        super().__init__()

        h_labels = list(substitutions.columns)
        v_labels = list(substitutions.index)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setContentsMargins(0, 0, 0, 0)

        self._setup(substitutions)

        self.setHorizontalHeaderLabels(h_labels)
        self.setVerticalHeaderLabels(v_labels)

        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setItemDelegate(IndexDistanceColorDelegate())

    def _setup(self, substitutions):
        self.setRowCount(substitutions.shape[0])
        self.setColumnCount(substitutions.shape[1])

        for row in range(substitutions.shape[0]):
            for col in range(substitutions.shape[1]):
                cell_value = int(substitutions.iat[row, col])

                if row == col:
                    continue

                self.setItem(row, col, QTableWidgetItem(str(cell_value)))

        h_header_height = self.horizontalHeader().height()
        row_height = self.rowHeight(0)
        no_items = self.columnCount()
        self.setFixedHeight(h_header_height + row_height * no_items + 5)

        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)


class MainColorBalanceWidget(QTabWidget):

    def __init__(self, dataset_mgr):
        super().__init__()

        self.dataset_mgr = dataset_mgr

        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setLayout(self.layout)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def clear(self):
        print("clearing color balance widget")
        # Remove and delete each tab widget
        while self.count() > 0:
            widget = self.widget(0)  # Get the first widget in the tab widget
            self.removeTab(0)  # Remove the tab
            widget.deleteLater()

    @Slot(object)
    def populate(self, results):

        for lane in results:
            tab_scroll_area = QScrollArea()
            tab_scroll_area.setFrameShape(QFrame.NoFrame)

            color_balance_table = ColorBalanceWidget(
                results[lane], self.dataset_mgr.base_colors
            )

            self.addTab(color_balance_table, f"lane {lane}")


class ColorBalanceWidget(QTableView):
    def __init__(self, indexes_df, base_colors, parent=None):
        super(ColorBalanceWidget, self).__init__(parent)
        df = indexes_df.copy()

        df["Proportion"] = "1"

        cols = ["Sample_ID", "Proportion"] + [
            col for col in df.columns if col not in ["Sample_ID", "Proportion"]
        ]
        df = df[cols]

        last_row_index = df.index[-1]
        df.loc[last_row_index + 1] = pd.Series()
        df.iloc[-1, 0] = "Summary"
        df.iloc[-1, 1] = ""

        self.color_balance_model = self._create_color_balance_model(df, base_colors)
        self.setModel(self.color_balance_model)
        self.color_balance_model.update_summation()
        self.verticalHeader().setVisible(False)
        self.setup(base_colors)

    def setup(self, base_colors):
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setContentsMargins(0, 0, 0, 0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        last_row = self.color_balance_model.rowCount() - 1
        self.setRowHeight(last_row, 140)
        self.setItemDelegate(ColorBalanceRowDelegate())

        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setFixedWidth(1500)

    @staticmethod
    def _create_color_balance_model(
        df: pd.DataFrame, base_colors: dict
    ) -> IndexColorBalanceModel:
        """Create a color balance model from a dataframe and a set of base colors."""

        model = IndexColorBalanceModel(base_colors, parent=None)

        # Set the column headers as the model's horizontal headers
        model.setHorizontalHeaderLabels(
            [col.replace("Index", "") for col in df.columns]
        )

        # Populate the model with data from the dataframe
        for index, row in df.iterrows():
            row_items = [QStandardItem(str(item)) for item in row]
            model.appendRow(row_items)

        return model

    def paintEvent(self, event):
        """
        Paint a grid on top of the QTableView, to separate the color balance columns from the rest of the columns.
        """
        super().paintEvent(event)
        painter = QPainter(self.viewport())

        model = self.model()
        column_count = model.columnCount()
        row_count = model.rowCount()

        last_row_index = row_count - 1

        thick_pen = QPen(QColor("dark gray"), 2, Qt.SolidLine)
        painter.setPen(thick_pen)

        # Paint a horizontal line at the bottom of the table
        last_row_rect = self.visualRect(model.index(last_row_index, 0))
        painter.drawLine(last_row_rect.topLeft(), last_row_rect.topRight())

        # Paint vertical lines between the color balance columns and the rest of the columns
        for row in range(row_count):
            i5_i7_rect = self.visualRect(model.index(row, 11))
            painter.drawLine(i5_i7_rect.topRight(), i5_i7_rect.bottomRight())

            first_col_rect = self.visualRect(model.index(row, 0))
            painter.drawLine(first_col_rect.topRight(), first_col_rect.bottomRight())

            second_col_rect = self.visualRect(model.index(row, 1))
            painter.drawLine(second_col_rect.topRight(), second_col_rect.bottomRight())

    # @staticmethod
    # def split_string_column(input_df, column_name1, column_name2):
    #     """
    #     Split a column of strings into multiple columns with one character per column.
    #
    #     :param dataframe: Pandas DataFrame containing the string column.
    #     :param column_name: Name of the column containing the strings.
    #     :return: DataFrame with one column per character in the strings.
    #     """
    #     df1 = input_df[column_name1].apply(lambda x: pd.Series(list(x)))
    #     df1.columns = [f"{column_name1}_{i + 1}" for i in range(10)]
    #
    #     df2 = input_df[column_name2].apply(lambda x: pd.Series(list(x)))
    #     df2.columns = [f"{column_name2}_{i + 1}" for i in range(10)]
    #
    #     return pd.concat([df1, df2], axis=1)


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
        """
        If the value at the current index and the value at the adjacent index are both "G",
        paint the background of the cell a light red color.
        """
        adjacent_index = index.model().index(index.row(), 3)
        current_value = index.data(Qt.DisplayRole)
        adjacent_value = adjacent_index.data(Qt.DisplayRole)

        if current_value == adjacent_value == "G":
            painter.save()
            painter.fillRect(option.rect, QColor(255, 127, 127))
            super().paint(painter, option, index)
            painter.restore()
        else:
            super().paint(painter, option, index)

    # Cleaned up by standardizing variable names, removing debugging statements, and improving readability.

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
        if not json_data:
            return

        data = json.loads(json_data)
        color_text = "\n".join(
            [f"{color}: {count}" for color, count in data["colors"].items()]
        )
        bases_text = "\n".join(
            [f"{base}: {count}" for base, count in data["bases"].items()]
        )
        full_text = f"{color_text}\n----\n{bases_text}"

        document = QTextDocument()
        document.setPlainText(full_text)

        if data["colors"].get("G", 0) < 0.1:
            self.setNoGreenBackgroundColorWarning(document, QColor(255, 127, 127))

        document.setTextWidth(option.rect.width())

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


class NonEditableDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        # Return None to make the item non-editable
        return None


class IndexDistanceColorDelegate(QStyledItemDelegate):

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)

        # Get the cell value and check if it's numeric
        try:
            value = int(index.data())
        except (TypeError, ValueError):
            value = None

        # Set background color based on the value
        if value is not None:
            if value < 5:
                color = QColor(139, 0, 1)
            else:
                color = QColor(0, 100, 1)

            option.backgroundBrush = color
