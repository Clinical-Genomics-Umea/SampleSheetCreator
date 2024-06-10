import json
from pathlib import Path
import pandas as pd


from PySide6.QtWidgets import QVBoxLayout, QWidget, QLineEdit, QTableView, QHeaderView, \
    QHBoxLayout, QSizePolicy, QSpacerItem, QAbstractItemView, QToolBox, QLabel

from PySide6.QtCore import QSortFilterProxyModel, QMimeData, QAbstractTableModel, Qt

from modules.logic.indexes import IndexKitDefinition


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
            chained_models[model_name].setSourceModel(chained_models[previous_model_name])

    return chained_models


class TableModel(QAbstractTableModel):
    def __init__(self, dataframe: pd.DataFrame):
        super(TableModel, self).__init__()

        self.dataframe = dataframe

    def data(self, index, role):
        """
        Retrieves data from the model for the given index and role.
        Args:
            index (QModelIndex): The index of the data to retrieve.
            role (int): The role of the data to retrieve.
        Returns:
            str: The retrieved data as a string.
        """
        if role == Qt.DisplayRole:
            value = self.dataframe.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        """
        Returns the number of rows in the data.
        Parameters:
            index (int): The index of the data.
        Returns:
            int: The number of rows in the data.
        """
        return self.dataframe.shape[0]

    def columnCount(self, index):
        """
        Returns the number of columns in the data.
        Parameters:
            index (int): The index of the data.
        Returns:
            int: The number of columns in the data.
        """
        return self.dataframe.shape[1]

    def headerData(self, section, orientation, role):
        """
        Get the header data for the given section, orientation, and role.
        Parameters:
            section (int): The index of the column/row.
            orientation (int): The orientation of the header (Qt.Horizontal or Qt.Vertical).
            role (int): The role of the header data (Qt.DisplayRole).
        Returns:
            str: The header data for the given section, or None if the role is not Qt.DisplayRole.
        """
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.dataframe.columns[section])

            if orientation == Qt.Vertical:
                return str(self.dataframe.index[section])

    def flags(self, index):
        """
        Generate the flags for the given index.
        Args:
            index (QModelIndex): The index for which to generate the flags.
        Returns:
            int: The flags generated for the index.
        """
        flags = super().flags(index)
        if index.isValid():
            flags |= Qt.ItemIsDragEnabled
        return flags

    def mimeData(self, indexes):
        """
        Generates a QMimeData object containing the data to be transferred to external applications.

        Parameters:
            indexes (List[QModelIndex]): A list of QModelIndex objects representing the selected indexes.

        Returns:
            QMimeData: The QMimeData object containing the transferred data.
        """
        mime_data = QMimeData()
        row_indexes = {index.row() for index in indexes}
        df = pd.DataFrame(self.dataframe, index=list(row_indexes))
        records = df.to_dict(orient='records')

        # Convert the records to JSON
        json_data = json.dumps(records)

        bytes_data = bytes(json_data, 'utf-8')
        mime_data.setData("application/json", bytes_data)

        return mime_data


class IndexWidget(QWidget):
    def __init__(self, index_df: pd.DataFrame, ikd_name: str = None) -> None:

        super().__init__()

        self.index_df = index_df
        self.index_df['IndexDefinitionKitName'] = ikd_name
        self.shown_fields = self.get_shown_fields()

        # setup sortfilterproxies
        self.sortfilterproxy = {field: QSortFilterProxyModel() for field in self.shown_fields}

        # create filter lineedits
        self.filter_editlines_layout = QHBoxLayout()
        self.filter_editlines = {field: QLineEdit() for field in self.shown_fields}

        # Add lineedits to filter layout
        for field, editline in self.filter_editlines.items():
            editline.setObjectName(field)
            self.filter_editlines_layout.addWidget(editline)

        self.filter_editlines_layout.addItem(QSpacerItem(16, 16, QSizePolicy.Fixed, QSizePolicy.Fixed))

        # setup main layout
        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(self.filter_editlines_layout)

        # create model and chained proxies

        self.model = TableModel(self.index_df)
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

        possible_fields = ["Name_I7", "Name_I5", "FixedPos"]
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
            header_item = header.model().headerData(column, Qt.Horizontal, Qt.DisplayRole)

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


class IndexKitDefinitionWidget(QWidget):
    def __init__(self, ikd: IndexKitDefinition) -> None:
        super().__init__()

        self.layout = QHBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.index_kit_definition = ikd

        self.index_widget_list = []

        if ikd.has_fixed_indexes and ikd.index_strategy == "DualOnly":
            self.index_widget_list.append(IndexWidget(ikd.fixed_indexes, ikd.name))

        elif not ikd.has_fixed_indexes and ikd.index_strategy == "DualOnly":
            self.index_widget_list.append(IndexWidget(ikd.indexes_i7, ikd.name))
            self.index_widget_list.append(IndexWidget(ikd.indexes_i5, ikd.name))

        for index_widget in self.index_widget_list:
            self.layout.addWidget(index_widget)


class IndexPanelWidgetMGR:
    def __init__(self, index_dir_root: Path) -> None:

        self.idk_widgets = {}
        idk_dict = self.get_idk_dict(index_dir_root)

        for name in idk_dict:
            self.idk_widgets[name] = IndexKitDefinitionWidget(idk_dict[name])

    @staticmethod
    def get_idk_dict(index_dir_root) -> dict:
        index_files = [f for f in index_dir_root.glob("**/*.tsv")]

        idk_dict = {}

        for f in index_files:
            ikd = IndexKitDefinition(f)
            idk_dict[ikd.name] = ikd

        return idk_dict


    def get_index_panel_widget(self, idk_name):
        return self.idk_widgets[idk_name]

    def get_index_panel_widget_names(self):
        return self.idk_widgets.keys()


class Indexes(QWidget):
    def __init__(self, indexes_base_path: Path):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.index_toolbox = QToolBox()
        self.index_panel_mgr = IndexPanelWidgetMGR(indexes_base_path)
        self.index_widgets = {}

        self.setup()

    def setup(self):

        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)

        indexes_label = QLabel("Indexes")
        indexes_label.setStyleSheet("font-weight: bold")

        self.layout.addWidget(indexes_label)
        self.layout.addWidget(self.index_toolbox)

        index_kit_names = self.index_panel_mgr.get_index_panel_widget_names()

        for name in index_kit_names:
            self.index_widgets[name] = self.index_panel_mgr.get_index_panel_widget(name)
            self.index_toolbox.addItem(self.index_widgets[name], name)




