import json
from pathlib import Path
import pandas as pd
import yaml

from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget, QLineEdit, QTableView, QHeaderView, \
    QHBoxLayout, QSizePolicy, QSpacerItem, QAbstractItemView

from PySide6.QtCore import QSortFilterProxyModel, QMimeData, QAbstractTableModel, Qt, Signal

from modules.indexes import IndexesWidget


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

    def __init__(self, profile_data, indexes_widget):
        super().__init__()

        self.profile_data = profile_data
        print(profile_data)

        indexes_widget.set_profile_meta(profile_data)
        profile_button = ProfileButton("Set profile for selected sample rows")
        layout = QVBoxLayout(self)
        layout.addWidget(profile_button)
        layout.addWidget(indexes_widget)

        layout.setContentsMargins(0, 0, 0, 0)

        profile_button.clicked.connect(self.send_profile_data)

        self.setLayout(layout)

    def send_profile_data(self):
        self.profile_data_signal.emit(self.profile_data)


class ProfilesMGR:
    def __init__(self, profiles_dirpath, indexes_manager):

        self.indexes_manager = indexes_manager

        files = [index for index in Path(profiles_dirpath).iterdir() if index.is_file()]
        self.profile_files = {self.retrieve_profile_name(file): file for file in files}


    def retrieve_profile_name(self, file):
        profile = read_yaml_file(file)
        return profile['ProfileName']

    def get_profiles_names(self):
        return self.profile_files.keys()

    def get_profile_widget(self, profile_name):
        profile_data = read_yaml_file(self.profile_files[profile_name])
        print(profile_data)
        index_set_name = profile_data['IndexAdapterKitName']
        indexes_widget = self.indexes_manager.get_indexes_widget(index_set_name)

        return ProfileWidget(profile_data['PipelineData'], indexes_widget)


