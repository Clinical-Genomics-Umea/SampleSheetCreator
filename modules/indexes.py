import json
import yaml
import argparse
from pathlib import Path
import pandas as pd
from io import StringIO
from camel_converter import to_snake

from PySide6.QtWidgets import QVBoxLayout, QWidget, QLineEdit, QTableView, QHeaderView, \
    QHBoxLayout, QSizePolicy, QSpacerItem, QAbstractItemView, QToolBox, QLabel

from PySide6.QtCore import QSortFilterProxyModel, QMimeData, QAbstractTableModel, Qt


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

        # print(chained_models)

        if i > 0:
            chained_keys = list(chained_models.keys())
            previous_model_name = chained_keys[i - 1]
            chained_models[model_name].setSourceModel(chained_models[previous_model_name])

    return chained_models


class TableModel(QAbstractTableModel):
    def __init__(self, dataframe: pd.DataFrame, profile_data: dict = None):
        super(TableModel, self).__init__()

        self.dataframe = dataframe
        self.profile_data = profile_data

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

        print(records)
        print(self.profile_data)

        if self.profile_data is not None:
            self.add_profile_data(records)

        print(records)

        # Convert the records to JSON
        json_data = json.dumps(records)

        print(json_data)

        bytes_data = bytes(json_data, 'utf-8')
        mime_data.setData("application/json", bytes_data)

        return mime_data

    def add_profile_data(self, records):
        for r in records:
            r.update(self.profile_data)


class IndexKitDefinition:
    strategies = ("NoIndex", "SingleOnly", "DualOnly", "SingleAndDual", "NoAndSingle", "NoAndDual", "All")
    required_sections = ("IndexKit", "Resources", "Indices", "SupportedLibraryPrepKits")

    def __init__(self, index_file: Path):
        self.index_file = index_file
        self.indexes_all = pd.DataFrame()
        self.resources = []
        self.supported_library_prep_kits = []
        self.f_positions = pd.DataFrame()
        self.indexes_i7 = pd.DataFrame()
        self.indexes_i5 = pd.DataFrame()
        self.fixed_indexes = pd.DataFrame()

        if self.validate():
            self.valid = True
            self.parse_index_file()
        else:
            self.valid = False

        self.has_fixed_indexes = True if not self.fixed_indexes.empty else False
        self.has_i7_indexes = True if not self.indexes_i7.empty else False
        self.has_i5_indexes = True if not self.indexes_i5.empty else False

    def validate(self) -> bool:
        sections = {}
        current_section = None

        try:
            content = self.index_file.read_text(encoding="utf-8")

            for line in content.splitlines():
                line = line.strip()

                if not line:
                    continue

                if line.startswith('[') and line.endswith(']'):
                    current_section = line[1:-1]
                    sections[current_section] = []
                else:
                    sections[current_section].append(line)

        except Exception as e:
            print(e)
            return False

        for section in self.required_sections:
            if section not in sections:
                print(f"Section '{section}' not found in the index kit definition file.")
                return False

        return True

    def parse_index_file(self):
        sections = {}
        current_section = None

        content = self.index_file.read_text(encoding="utf-8")

        for line in content.splitlines():
            line = line.strip()

            if not line:
                continue

            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                sections[current_section] = []
            else:
                sections[current_section].append(line)

        if 'IndexKit' in sections:
            for line in sections['IndexKit']:
                key, value = line.strip().split('\t')
                setattr(self, to_snake(key), value)

        elif 'Kit' in sections:
            for line in sections['Kit']:
                key, value = line.strip().split('\t')
                setattr(self, to_snake(key), value)

        if 'Resources' in sections:
            resources_content = '\n'.join(sections['Resources'])
            self.resources = pd.read_csv(StringIO(resources_content), sep='\t', header=0)
            self.process_resources()

        if 'Indices' in sections:
            indexes_content = '\n'.join(sections['Indices'])
            self.indexes_all = pd.read_csv(StringIO(indexes_content), sep='\t', header=0)
            self.process_indexes()

        if 'SupportedLibraryPrepKits' in sections:
            self.supported_library_prep_kits = sections['SupportedLibraryPrepKits']

    def process_resources(self):
        _meta = self.resources[self.resources['Type'] != 'FixedIndexPosition']
        for row in _meta.itertuples():
            setattr(self, to_snake(row.Name), row.Value)

        if hasattr(self, "fixed_layout"):
            setattr(self, "fixed_layout", self.convert_to_boolean(self.fixed_layout))

        _fixed_index_positions = self.resources[self.resources['Type'] == 'FixedIndexPosition'].copy()
        self.f_positions = _fixed_index_positions[["Name", "Value"]]

    def process_indexes(self):
        _indexes_i7 = (
            self.indexes_all[self.indexes_all['IndexReadNumber'] == 1]
            .rename(columns={"Sequence": "Index_I7", "Name": "Name_I7"})
            .drop(columns=['IndexReadNumber'])
        )

        _indexes_i5 = (
            self.indexes_all[self.indexes_all['IndexReadNumber'] == 2]
            .rename(columns={"Sequence": "Index_I5", "Name": "Name_I5"})
            .drop(columns=['IndexReadNumber'])
        )

        if not _indexes_i7.empty:
            self.indexes_i7 = _indexes_i7

        if not _indexes_i5.empty:
            self.indexes_i5 = _indexes_i5

        if not self.f_positions.empty:
            _f_indexes = self.f_positions.copy()
            _f_indexes.rename(columns={'Name': 'FixedPos'}, inplace=True)
            _f_indexes[['Name_I7', 'Name_I5']] = _f_indexes['Value'].str.split(pat='-', expand=True)
            _f_indexes = _f_indexes.drop('Value', axis=1)

            if not _indexes_i7.empty:
                _f_indexes = pd.merge(_f_indexes, _indexes_i7, on='Name_I7', how='outer')

            if not _indexes_i5.empty:
                _f_indexes = pd.merge(_f_indexes, _indexes_i5, on='Name_I5', how='outer')

            self.fixed_indexes = _f_indexes

    @staticmethod
    def convert_to_boolean(value):
        value_lower = value.lower()
        if value_lower == "true":
            return True
        elif value_lower == "false":
            return False
        else:
            return None


class IndexKitDefinitionMGR:
    def __init__(self, index_dir_root: Path) -> None:
        self.index_files = [f for f in index_dir_root.glob("**/*.tsv")]

        self.idk_dict = {}

        for f in self.index_files:
            ikd = IndexKitDefinition(f)
            self.idk_dict[ikd.name] = ikd

    def get_idk(self, name: str) -> IndexKitDefinition:
        return self.idk_dict[name]

    def get_idk_names(self) -> list:
        return list(self.idk_dict.keys())


class IndexWidget(QWidget):
    def __init__(self, index_df: pd.DataFrame, profile_data: dict = None, idk_name: str = None) -> None:

        super().__init__()

        self.index_df = index_df
        self.profile_data = profile_data

        self.index_df['IndexDefinitionKitName'] = idk_name

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

        self.model = TableModel(self.index_df, self.profile_data)
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
        s_fields = [f for f in self.index_df.columns if "Index" not in f]
        return s_fields

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

        print(name)

        self.chained_proxies[name].setFilterFixedString(filter_text)

    # def data_to_model(self, data_path):
    #     """ Read csv file with data and convert to QStandardItemModel """
    #
    #     df = pd.read_csv(data_path, delimiter=';', quotechar='|')
    #     return TableModel(df)


class IndexPanelWidget(QWidget):
    def __init__(self, idk: IndexKitDefinition, profile_data: dict = None) -> None:
        super().__init__()

        self.layout = QHBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.index_kit_definition = idk
        self.profile_data = profile_data

        self.index_widget_list = []

        if idk.has_fixed_indexes and idk.index_strategy == "DualOnly":
            self.index_widget_list.append(IndexWidget(idk.fixed_indexes, self.profile_data, idk.name))

        elif not idk.has_fixed_indexes and idk.index_strategy == "DualOnly":
            self.index_widget_list.append(IndexWidget(idk.indexes_i7, self.profile_data, idk.name))
            self.index_widget_list.append(IndexWidget(idk.indexes_i5, self.profile_data, idk.name))

        for index_widget in self.index_widget_list:
            self.layout.addWidget(index_widget)


class IndexPanelWidgetMGR:
    def __init__(self, idk_mgr: IndexKitDefinitionMGR) -> None:
        self.index_panel_widgets = {}

        for idk_name in idk_mgr.get_idk_names():
            self.index_panel_widgets[idk_name] = IndexPanelWidget(idk_mgr.get_idk(idk_name))

    def get_index_panel_widget(self, index_def_name):
        return self.index_panel_widgets[index_def_name]

    def get_index_panel_widget_names(self):
        return self.index_panel_widgets.keys()


# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-i', '--ilmn_index_file', type=str, required=True,
#                         help='Illumina local run manager index file')
#
#     args = parser.parse_args()
#     index_path = Path(args.ilmn_index_file)
#
#     index_data = IndexKitDefinition(index_path)
#     # #
#     print(index_data.has_fixed_indexes)
#     print(index_data.indexes_i5)
#     print(index_data.indexes_i7)


class Indexes(QWidget):
    def __init__(self, indexes_base_path: Path):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.index_mgr = IndexKitDefinitionMGR(indexes_base_path)
        self.index_toolbox = QToolBox()
        self.index_panel_mgr = IndexPanelWidgetMGR(self.index_mgr)
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


#
# if __name__ == "__main__":
#     main()
