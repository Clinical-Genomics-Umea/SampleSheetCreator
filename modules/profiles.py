import json
from pathlib import Path
import pandas as pd
import yaml

from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget, QLineEdit, QTableView, QHeaderView, \
    QHBoxLayout, QSizePolicy, QSpacerItem, QAbstractItemView

from PySide6.QtCore import QSortFilterProxyModel, QMimeData, QAbstractTableModel, Qt


class ProfileButton(QPushButton):
    def __init__(self, profile_name):
        super().__init__()

        self.profile_name = profile_name
        self.setText(f"Add {profile_name}")


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


class ProfileMGR:
    def __init__(self):
        pass

    def init_indexes(self):
        pass

    def init_profiles(self):
        pass

    # index_sets = [index_set.name for index_set in Path("modules/indexes").iterdir() if index_set.is_dir()]
    #     self.index_modules = {}
    #     for index_set in index_sets:
    #         self.index_modules[index_set] = importlib.import_module(f"modules.indexes.{index_set}.index_widget")
    #
    #     profile_files = [profile for profile in Path("modules/profile_data").iterdir() if profile.is_file()]
    #
    #     self.profiles = {}
    #     for profile in profile_files:
    #         data = read_yaml_file(profile)
    #         self.profiles[data["ProfileName"]] = data
    #     self.profile_widgets = {}
    #     self.add_buttons = {}

    def get_profile(self, profile_name):
        return self.profiles[profile_name]

    def get_index_widget(self, index_set):
        return self.index_modules[index_set].IndexesWidget()

    def get_profile_widget(self, profile_name):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        button = ProfileButton(profile_name)
        layout.addWidget(button)

        self.add_buttons[profile_name] = button

        index_set = self.profiles[profile_name]["IndexAdapterKitName"]
        index_widget = self.index_modules[index_set].IndexesWidget(self.profiles[profile_name])

        layout.addWidget(index_widget)

        return widget

    def get_profile_names(self):
        return self.profiles.keys()


