import pandas as pd


from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QTableView,
    QHeaderView,
    QHBoxLayout,
    QSizePolicy,
    QSpacerItem,
    QAbstractItemView, QStyleOptionHeader, QStyle, QStyledItemDelegate,
)

from PySide6.QtCore import QSortFilterProxyModel, Qt, QModelIndex

from modules.models.indexes.all_column_filter_proxy_model import AllColumnFilterProxyModel
from modules.models.indexes.index_table_model import IndexTableModel



class SingleIndexWidget(QWidget):
    def __init__(self, index_set_name: str, index_set: dict) -> None:

        super().__init__()

        self._index_set_name = index_set_name
        self._index_df = pd.DataFrame.from_dict(index_set)

        self._shown_fields = self._get_shown_fields()

        self._index_table_model = IndexTableModel(self._index_df)

        self._proxy_model = AllColumnFilterProxyModel()
        self._proxy_model.setSourceModel(self._index_table_model)
        self._proxy_model.set_filter_columns(self._shown_fields)

        self._filter_lineedit = QLineEdit()

        # Add line_edits to filter layout


        # setup main layout
        self._layout = QVBoxLayout()
        self._layout.setSpacing(5)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._filter_lineedit)

        # setup tableview
        self._tableview = QTableView()
        self._tableview.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self._tableview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tableview.setDragEnabled(True)
        self._tableview.setDragDropMode(QAbstractItemView.DragOnly)
        self._tableview.setSelectionBehavior(QAbstractItemView.SelectRows)

        # link tableview to model via chained proxies
        self._tableview.setModel(self._proxy_model)

        self._set_shown_columns()

        self._filter_lineedit.textChanged.connect(self._proxy_model.set_filter_text)

        self._layout.addWidget(self._tableview)
        self.setLayout(self._layout)

    def _get_shown_fields(self):

        possible_fields = ["IndexI7Name", "IndexI5Name", "Pos"]
        return [f for f in self._index_df.columns if f in possible_fields]

    def _set_shown_columns(self):
        """
        Hides columns in a QTableView that have names not present in the list of fields.

        Args:
            table_view (QTableView): The QTableView object.
            shown_fields (list): The list of field names to be checked against.

        """
        model = self._tableview.model()
        header = self._tableview.horizontalHeader()

        for column in range(model.columnCount()):
            header_item = header.model().headerData(
                column, Qt.Horizontal, Qt.DisplayRole
            )

            if header_item not in self._shown_fields:
                self._tableview.setColumnHidden(column, True)
            else:
                self._tableview.setColumnHidden(column, False)



