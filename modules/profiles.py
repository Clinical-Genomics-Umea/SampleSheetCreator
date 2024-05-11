import json
from pathlib import Path
import pandas as pd
import yaml

from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget, QLineEdit, QTableView, QHeaderView, \
    QHBoxLayout, QSizePolicy, QSpacerItem, QAbstractItemView, QTabWidget, QComboBox, QStackedWidget, QLabel

from PySide6.QtCore import QSortFilterProxyModel, QMimeData, QAbstractTableModel, Qt, Signal

from modules.indexes import IndexPanelWidget, IndexPanelWidgetMGR, IndexKitDefinition, IndexKitDefinitionMGR, IndexWidget
from modules.sample_view import SampleTableView


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


class Profiles(QWidget):
    def __init__(self, profile_base_path: Path, sample_tableview: SampleTableView):
        super().__init__()

        self.profile_mgr = ProfileMGR(Path(profile_base_path), sample_tableview)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setup()

    def setup(self):

        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)

        profiles_label = QLabel("Profiles")
        profiles_label.setStyleSheet("font-weight: bold")

        self.layout.addWidget(profiles_label)
        profile_widgets = self.profile_mgr.get_profile_widgets()

        for pw in profile_widgets:
            self.layout.addWidget(pw)

        self.layout.addSpacerItem(QSpacerItem(20, 40,
                                              QSizePolicy.Minimum,
                                              QSizePolicy.Expanding))


class ProfileWidget(QWidget):

    profile_data_signal = Signal(dict)

    def __init__(self, profile_name: str, profile_data: dict):
        super().__init__()

        self.profile_data = profile_data
        profile_button = ProfileButton(profile_name)

        layout = QVBoxLayout(self)
        layout.addWidget(profile_button)

        layout.setContentsMargins(0, 0, 0, 0)

        profile_button.clicked.connect(self.send_profile_data)

        self.setLayout(layout)

    def send_profile_data(self):
        self.profile_data_signal.emit(self.profile_data)


class ProfileMGR:
    def __init__(self, profiles_dirpath: Path, sample_tableview: SampleTableView) -> None:

        # setup profile files
        profile_files = [pf for pf in profiles_dirpath.iterdir() if pf.is_file()]
        self.profile_file_dict = {self.get_profile_name_from_yaml(file): file for file in profile_files}

        # setup profile data
        self.profile_widgets = []
        for name, file in self.profile_file_dict.items():
            profile_data = read_yaml_file(file)
            pw = ProfileWidget(name, profile_data)
            self.profile_widgets.append(pw)

            pw.profile_data_signal.connect(sample_tableview.set_profile_data)


    @staticmethod
    def get_profile_name_from_yaml(file) -> str:
        profile = read_yaml_file(file)
        return profile['ProfileName']

    def get_profile_widgets(self):
        return self.profile_widgets

