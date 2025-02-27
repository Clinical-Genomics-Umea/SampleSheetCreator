import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QPainter, QPen, QColor
from PySide6.QtWidgets import QTableView, QSizePolicy, QAbstractScrollArea, QHeaderView

from modules.models.validation.index_color_balance_model import IndexColorBalanceModel
from modules.views.validation.color_balance_delegates import ColorBalanceRowDelegate


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
