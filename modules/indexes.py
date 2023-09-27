import json
from pathlib import Path
import pandas as pd
import yaml

from PySide6.QtWidgets import QVBoxLayout, QWidget, QLineEdit, QTableView, QHeaderView, \
    QHBoxLayout, QSizePolicy, QSpacerItem, QAbstractItemView

from PySide6.QtCore import QSortFilterProxyModel, QMimeData, QAbstractTableModel, Qt

def reorder_dataframe_fields(dataframe: pd.DataFrame, field_order: list) -> pd.DataFrame:
    """
    Reorders the fields in a Pandas DataFrame so that fields with names in a list are placed first,
    maintaining the same order as in the list.

    Args:
        dataframe (pd.DataFrame): The Pandas DataFrame to be reordered.
        field_order (list): The list of field names specifying the desired order.

    Returns:
        pd.DataFrame: The reordered Pandas DataFrame.

    """
    existing_fields = list(dataframe.columns)

    # Ensure only existing fields are included in the new order
    field_order_filtered = [field for field in field_order if field in existing_fields]

    return dataframe[
        field_order_filtered
        + [
            field
            for field in existing_fields
            if field not in field_order_filtered
        ]
    ]

def import_yaml_file(file_path: Path) -> dict:
    """
    Imports a YAML file into a dictionary.

    Args:
        file_path (Path): The path to the YAML file.

    Returns:
        dict: The dictionary containing the YAML file data.
    """
    with open(file_path, 'r') as file:
        yaml_data = yaml.safe_load(file)

    return yaml_data


def import_csv_file(file_path: Path) -> pd.DataFrame:
    """
    Imports a CSV file into a Pandas DataFrame.

    Args:
        file_path (Path): The path to the CSV file.

    Returns:
        pd.DataFrame: The Pandas DataFrame containing the CSV file data.
    """
    return pd.read_csv(file_path, delimiter=';', quotechar='|')


def verify_directory_contents(directory_path: Path) -> bool:
    """
    Verifies if a directory contains the files 'meta.yaml' and 'indexes.csv'.

    Args:
        directory_path (Path): The path to the directory to be verified.

    Returns:
        bool: True if the directory contains the required files, False otherwise.
    """
    required_files = ['meta.yaml', 'indexes.csv']

    for file_name in required_files:
        file_path = directory_path / file_name
        if not file_path.is_file():
            return False

    return True


def validate_metadata(data: dict) -> bool:
    # sourcery skip: assign-if-exp, boolean-if-exp-identity, reintroduce-else
    """
    Validates the metadata dictionary.

    Args:
        data (dict): The dictionary containing the metadata information.

    Returns:
        bool: True if the metadata is valid, False otherwise.
    """
    required_keys = ['IndexAdapterKitName', 'IndexAdapterKitNameReadable', 
                     'ShownFields', 'FieldCorrespondence', 'IndexMetaData', 'RequiredIndexesSourcefileFields']

    if any(key not in data for key in required_keys):
        print(f"Metadata is missing the following keys: {required_keys}")
        return False

    if not validate_list_items_as_dict_keys(data['ShownFields'], data['FieldCorrespondence']):
        print("Metadata is missing keys in FieldCorrespondence")
        return False
    
    if not validate_dict_keys_present_in_another_dict(data['IndexMetaData'], data['FieldCorrespondence']):
        print("Metadata IndexMetaData missing keys")
        return False

    if not validate_list_items_in_another_list(data['ShownFields'], data['RequiredIndexesSourcefileFields']):
        print("Metadata is missing keys in ShownFields")
        return False

    return True


def validate_list_items_in_another_list(items: list, reference_list: list) -> bool:
    """
    Validates if all items in one list exist in another list.

    Args:
        items (list): The list of items to be validated.
        reference_list (list): The list to be checked against.

    Returns:
        bool: True if all items in the items list exist in the reference_list, False otherwise.
    """
    return all(item in reference_list for item in items)


def validate_list_items_as_dict_keys(items: list, data: dict) -> bool:
    """
    Validates if all items in a list exist as keys in a dictionary.

    Args:
        items (list): The list of items to be validated.
        data (dict): The dictionary to be checked against.

    Returns:
        bool: True if all items in the list exist as keys in the dictionary, False otherwise.
    """
    return all(item in data for item in items)


def validate_dict_keys_present_in_another_dict(data_keys: dict, reference_dict: dict) -> bool:
    """
    Validates if all keys in one dictionary exist as keys in another dictionary.

    Args:
        data_keys (dict): The dictionary containing the keys to be validated.
        reference_dict (dict): The dictionary to be checked against.

    Returns:
        bool: True if all keys in the data_keys dictionary exist as keys in the reference_dict, False otherwise.
    """
    return all(key in reference_dict for key in data_keys)


def validate_dataframe(dataframe: pd.DataFrame, items: list) -> bool:
    """
    Validates if the header of a Pandas DataFrame contains all items in a list.

    Args:
        dataframe (pd.DataFrame): The Pandas DataFrame to be validated.
        items (list): The list of items to be checked in the DataFrame header.

    Returns:
        bool: True if all items exist in the DataFrame header, False otherwise.
    """

    if not validate_dataframe_rows(dataframe):
        print("DataFrame does not have more than one row")
        return False

    header = dataframe.columns.tolist()
    print(items)
    print(header)

    return all(item in header for item in items)


def validate_dataframe_rows(dataframe: pd.DataFrame) -> bool:
    """
    Validates if a Pandas DataFrame has more than one row.

    Args:
        dataframe (pd.DataFrame): The Pandas DataFrame to be validated.

    Returns:
        bool: True if the DataFrame has more than one row, False otherwise.
    """
    num_rows = len(dataframe)

    return num_rows > 1


def create_chained_sort_filter_proxies(model_names: list) -> dict:
    """
    Creates chained QSortFilterProxyModels from a list, where each model is chained to the next one.

    Args:
        model_names (list): The list of models to be chained.

    Returns:
        dict: A dictionary mapping each model to its chained QSortFilterProxyModel.

    """
    print(model_names)
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


class IndexesWidget(QWidget):
    def __init__(self, index_dirpath: Path):

        super().__init__()

        # initial imports and validations
        # print("validate directory contents", verify_directory_contents(index_dirpath))

        self.meta = import_yaml_file(index_dirpath / "meta.yaml")
        self.profile_meta = {}

        # print("validate metadata", validate_metadata(self.meta))
        
        self.indexes = import_csv_file(index_dirpath / "indexes.csv")
        # print("validate dataframe", validate_dataframe(self.indexes, self.meta['RequiredIndexesSourcefileFields']))

        self.indexes = reorder_dataframe_fields(self.indexes, self.meta['ShownFields'])

        # setup sortfilterproxies
        self.sortfilterproxy = {field: QSortFilterProxyModel() for field in self.meta['ShownFields']}

        # create filter lineedits
        self.filter_editlines_layout = QHBoxLayout()
        self.filter_editlines = {field: QLineEdit() for field in self.meta['ShownFields']}

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
        self.layout.setSpacing(5)


        # create model and chained proxies
        self.model = TableModel(self.indexes, self.meta)
        self.chained_proxies = create_chained_sort_filter_proxies(self.meta['ShownFields'])

        # setup tableview
        self.tableview = QTableView()
        self.tableview.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.tableview.verticalHeader().hide()
        self.tableview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableview.setDragEnabled(True)
        self.tableview.setDragDropMode(QAbstractItemView.DragOnly)
        self.tableview.setSelectionBehavior(QAbstractItemView.SelectRows)

        # link tableview to model via chained proxies
        self.chained_proxies[self.meta['ShownFields'][0]].setSourceModel(self.model)
        self.tableview.setModel(self.chained_proxies[self.meta['ShownFields'][-1]])

        self.hide_columns_not_in_list(self.meta['ShownFields'])

        self.layout.addWidget(self.tableview)
        self.setLayout(self.layout)

        for editline in self.filter_editlines.values():
            editline.textChanged.connect(self.filter)

    def set_profile_meta(self, profile_data: dict):
        self.profile_meta = profile_data

    def get_name(self):
        return self.meta['IndexAdapterKitName']

    def get_name_readable(self):
        return self.meta['IndexAdapterKitNameReadable']

    def hide_columns_not_in_list(self, shown_fields: list):
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

            if header_item not in shown_fields:
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

    def data_to_model(self, data_path):
        """ Read csv file with data and convert to QStandardItemModel """

        df = pd.read_csv(data_path, delimiter=';', quotechar='|')
        return TableModel(df)

    def set_profile_meta(self, profile_meta):
        self.model.set_profile_meta(profile_meta)


class TableModel(QAbstractTableModel):
    def __init__(self, dataframe: pd.DataFrame, meta: dict):
        super(TableModel, self).__init__()

        self.dataframe = dataframe
        self.meta = meta
        self.profile_meta = {}
        self.field_translation = self.meta['FieldCorrespondence']

    def set_profile_meta(self, profile_meta):
        self.profile_meta = profile_meta


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
            flags |= Qt.ItemFlags.ItemIsDragEnabled
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

        # Get the unique row indexes
        row_indexes = {index.row() for index in indexes}

        # Create a temporary DataFrame with the selected rows
        df = pd.DataFrame(self.dataframe, index=list(row_indexes))
        df['IndexAdapterKitName'] = self.meta['IndexAdapterKitName']

        # Add the data from the profile to the DataFrame
        for field, value in self.meta["IndexMetaData"].items():
            df[field] = value

        for field, value in self.profile_meta.items():
            df[field] = value

        # Convert the DataFrame to a list of dictionaries
        records = df.to_dict(orient='records')

        print(records)

        # Create a dictionary with the records and translation data
        data = {'records': records, 'translate': self.field_translation}

        # Convert the data to JSON
        json_data = json.dumps(data)

        # Set the JSON data as MIME data with the "application/json" mimetype
        bytes_data = bytes(json_data, 'utf-8')
        mime_data.setData("application/json", bytes_data)

        return mime_data


def read_yaml_file(file):
    # Get the path to the directory of the current module

    try:
        with open(file, 'r') as file:
            # Load YAML data from the file
            data = yaml.safe_load(file)
        return data
    except FileNotFoundError:
        print(f"File '{file}' not found in the module directory.")
        return None
    except Exception as e:
        print(f"An error occurred while reading '{file}': {e}")
        return None


class IndexesMGR:
    def __init__(self, indexes_dirpath):
        folders = [index for index in Path(indexes_dirpath).iterdir() if index.is_dir()]
        self.indexes_folders = {self.retrieve_index_name(folder): folder for folder in folders}

    def get_indexes_widget(self, indexes_name):

        indexes_folder = self.indexes_folders[indexes_name]
        return IndexesWidget(indexes_folder)

    def get_indexes_names(self):
        return self.indexes_folders.keys()

    def retrieve_index_name(self, folder):
        meta = read_yaml_file(folder / "meta.yaml")
        return meta['IndexAdapterKitName']
