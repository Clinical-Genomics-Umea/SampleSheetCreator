import json
from pathlib import Path
import pandas as pd
import yaml

from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget, QLineEdit, QTableView, QHeaderView, \
    QHBoxLayout, QSizePolicy, QSpacerItem, QAbstractItemView, QTabWidget, QComboBox, QStackedWidget

from PySide6.QtCore import QSortFilterProxyModel, QMimeData, QAbstractTableModel, Qt, Signal

from modules.indexes import IndexPanelWidget, IndexPanelWidgetMGR, IndexKitDefinition, IndexKitDefinitionMGR, IndexWidget


class ProfileButton(QPushButton):
    def __init__(self, profile_name):
        super().__init__()

        self.profile_name = profile_name
        self.setText(f"{profile_name}")


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


class ProfileWidget(QWidget):

    profile_data_signal = Signal(dict)

    def __init__(self, idk_list: list, profile_data: dict):
        super().__init__()

        self.idk_list = idk_list
        self.profile_data = profile_data

        profile_button = ProfileButton("Set profile for selected sample rows")

        self.stacked_widget = QStackedWidget()
        self.index_cb = QComboBox()

        for idk in self.idk_list:
            ipw = IndexPanelWidget(idk, self.profile_data)
            self.stacked_widget.addWidget(ipw)
            self.index_cb.addItem(idk.name)

        self.index_cb.currentIndexChanged.connect(self.change_index_kit_definition)

        layout = QVBoxLayout(self)
        layout.addWidget(profile_button)
        layout.addWidget(self.index_cb)
        layout.addWidget(self.stacked_widget)

        layout.setContentsMargins(0, 0, 0, 0)

        profile_button.clicked.connect(self.send_profile_data)

        self.setLayout(layout)

    def change_index_kit_definition(self, index):
        # Change the selected tab based on the QComboBox selection
        self.stacked_widget.setCurrentIndex(index)

    def send_profile_data(self):
        self.profile_data_signal.emit(self.profile_data)


class ProfileWidgetMGR:
    def __init__(self, idk_mgr: IndexKitDefinitionMGR, profiles_dirpath: Path) -> None:

        # setup profile files
        profile_files = [pf for pf in profiles_dirpath.iterdir() if pf.is_file()]
        self.profile_file_dict = {self.get_profile_name_from_yaml(file): file for file in profile_files}

        # setup profile data
        self.profile_data = {}
        for name, file in self.profile_file_dict.items():
            self.profile_data[name] = read_yaml_file(file)

        # setup index kit definition files

        self.profile_widgets = {}

        for name in self.profile_data.keys():
            idk_names = self.profile_data[name]['IndexAdapterKitNames']

            idk_panel_set = []
            for idk_name in idk_names:
                idk_panel_set.append(idk_mgr.get_idk(idk_name))

            profile_data_clean = self.profile_data[name]
            del profile_data_clean['IndexAdapterKitNames']

            self.profile_widgets[name] = ProfileWidget(idk_panel_set, profile_data_clean)

    @staticmethod
    def get_profile_name_from_yaml(file) -> str:
        profile = read_yaml_file(file)
        return profile['ProfileName']

    @staticmethod
    def get_profile_index_kit_names(file) -> list:
        profile = read_yaml_file(file)
        return profile['IndexAdapterKitNames']

    @staticmethod
    def get_index_kit_definition_name(file: Path) -> str:
        with file.open(mode='r') as fh:
            for line in fh:
                if line.startswith('IndexAdapterKitName'):
                    return line.strip().split("\t")[1].strip()

        return "Empty"

    def get_profile_names(self):
        return self.profile_file_dict.keys()

    def get_profile_widget(self, profile_name):
        return self.profile_widgets[profile_name]
