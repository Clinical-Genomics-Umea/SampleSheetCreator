from pathlib import Path
import yaml

from PySide6.QtWidgets import (QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy,
                               QSpacerItem, QLabel, QFormLayout, QFrame)

from PySide6.QtCore import Signal
from modules.sample_view import SampleTableView


def read_yaml_file(file):
    # Get the path to the directory of the current module

    try:
        with open(file, 'r') as file:
            # Load YAML data from the file
            data = yaml.safe_load(file)
        return data
    except FileNotFoundError:
        return None
    except Exception as e:
        return None


class Profiles(QWidget):
    def __init__(self, profile_base_path: Path, sample_tableview: SampleTableView):
        super().__init__()
        self.profile_mgr = ProfileMGR(Path(profile_base_path), sample_tableview)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        profiles_label = QLabel("Profiles")
        profiles_label.setStyleSheet("font-weight: bold")
        self.main_layout.addWidget(profiles_label)

        self.form_layout = QFormLayout()
        self.main_layout.addLayout(self.form_layout)

        self.setup()

    def setup(self):
        self.main_layout.setSpacing(5)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.form_layout.setSpacing(5)
        self.form_layout.setContentsMargins(0, 0, 0, 0)

        profile_widgets = self.profile_mgr.get_profile_widgets()
        for group in profile_widgets:
            group_label = QLabel(group)
            group_label.setStyleSheet("font-style: italic")
            self.form_layout.addRow(self.get_line())
            self.form_layout.addRow(group_label)
            for name in profile_widgets[group]:
                pw = profile_widgets[group][name]
                self.form_layout.addRow(QLabel(name), pw)

        self.main_layout.addSpacerItem(QSpacerItem(20, 40,
                                                   QSizePolicy.Minimum,
                                                   QSizePolicy.Expanding))
    @staticmethod
    def get_line():
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

class ProfileWidget(QWidget):
    profile_data_signal = Signal(dict)

    def __init__(self, profile_data: dict):
        super().__init__()

        self.profile_data = profile_data

        profile_button = QPushButton("apply")
        profile_button.setMaximumWidth(50)

        layout = QHBoxLayout(self)
        layout.addWidget(profile_button)

        layout.setContentsMargins(0, 0, 0, 0)

        profile_button.clicked.connect(self.send_profile_data)

        self.setLayout(layout)

    def send_profile_data(self):
        self.profile_data_signal.emit(self.profile_data)


    def profile_name(self):
        return self.profile_name['ProfileName']

class ProfileMGR:
    def __init__(self, profiles_dirpath: Path, sample_tableview: SampleTableView) -> None:
        # setup profile files

        profile_files = [f for f in profiles_dirpath.glob("**/*.yaml")]

        self.profile_widgets = {}

        for file in profile_files:
            if not file.is_file():
                continue

            profile_data = read_yaml_file(file)
            group = file.parent.name
            profile_name = profile_data['ProfileName']

            pw = ProfileWidget(profile_data)

            if group not in self.profile_widgets:
                self.profile_widgets[group] = {}

            self.profile_widgets[group][profile_name] = pw
            pw.profile_data_signal.connect(sample_tableview.set_profile_data)

    def get_profile_widgets(self):
        return self.profile_widgets
