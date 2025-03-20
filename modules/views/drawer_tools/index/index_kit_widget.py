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
    QAbstractItemView,
)

from PySide6.QtCore import QSortFilterProxyModel, Qt

from modules.models.indexes.index_kit_table_model import IndexKitTableModel


def create_chained_sfproxies(model_names: list) -> dict:
    """
    Creates chained QSortFilterProxyModels from a list, where each model is chained to the next one.

    Args:
        model_names (list): The list of models to be chained.

    Returns:
        dict: A dictionary mapping each model to its chained QSortFilterProxyModel.

    """

    chained_models = {}

    for i in range(len(model_names)):
        model_name = model_names[i]
        chained_models[model_name] = QSortFilterProxyModel()
        chained_models[model_name].setFilterKeyColumn(i)

        if i > 0:
            chained_keys = list(chained_models.keys())
            previous_model_name = chained_keys[i - 1]
            chained_models[model_name].setSourceModel(
                chained_models[previous_model_name]
            )

    return chained_models


class IndexKitWidget(QWidget):
    def __init__(self, index_df: pd.DataFrame) -> None:

        super().__init__()

        self.index_df = index_df

        self.shown_fields = self.get_shown_fields()

        self.sfproxy = {field: QSortFilterProxyModel() for field in self.shown_fields}

        # create filter lineedits

        self.filter_editlines_layout = QHBoxLayout()
        self.filter_editlines = {field: QLineEdit() for field in self.shown_fields}

        # Add lineedits to filter layout
        for field, editline in self.filter_editlines.items():
            editline.setObjectName(field)
            self.filter_editlines_layout.addWidget(editline)

        self.filter_editlines_layout.addItem(
            QSpacerItem(16, 16, QSizePolicy.Fixed, QSizePolicy.Fixed)
        )

        # setup main layout
        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(self.filter_editlines_layout)

        # create model and chained proxies

        self.model = IndexKitTableModel(self.index_df)
        self.chained_proxies = create_chained_sfproxies(self.shown_fields)

        # setup tableview
        self.tableview = QTableView()
        self.tableview.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.tableview.verticalHeader().hide()
        self.tableview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableview.setDragEnabled(True)
        self.tableview.setDragDropMode(QAbstractItemView.DragOnly)
        self.tableview.setSelectionBehavior(QAbstractItemView.SelectRows)

        # link tableview to model via chained proxies
        self.chained_proxies[self.shown_fields[0]].setSourceModel(self.model)
        self.tableview.setModel(self.chained_proxies[self.shown_fields[-1]])

        self.set_shown_columns()

        self.layout.addWidget(self.tableview)
        self.setLayout(self.layout)

        for editline in self.filter_editlines.values():
            editline.textChanged.connect(self.filter)

    def get_shown_fields(self):

        possible_fields = ["IndexI7Name", "IndexI5Name", "Pos"]

        shown_fields = [f for f in self.index_df.columns if f in possible_fields]

        return shown_fields

    def set_shown_columns(self):
        """
        Hides columns in a QTableView that have names not present in the list of fields.

        Args:
            table_view (QTableView): The QTableView object.
            shown_fields (list): The list of field names to be checked against.

        """
        model = self.tableview.model()
        header = self.tableview.horizontalHeader()

        for column in range(model.columnCount()):
            header_item = header.model().headerData(
                column, Qt.Horizontal, Qt.DisplayRole
            )

            if header_item not in self.shown_fields:
                self.tableview.setColumnHidden(column, True)
            else:
                self.tableview.setColumnHidden(column, False)

    def filter(self, filter_text):
        """
        Filters the data based on the given filter text.
        Parameters:
            filter_text (str): The text to filter the data with.
        Returns:
            None
        """
        sender = self.sender()
        name = sender.objectName()

        self.chained_proxies[name].setFilterFixedString(filter_text)
