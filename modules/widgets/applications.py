from pathlib import Path
import yaml
import qtawesome as qta

from PySide6.QtWidgets import (QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy,
                               QSpacerItem, QLabel, QFrame, QDialog, QTextEdit)

from PySide6.QtCore import Signal, Qt
from modules.widgets.sample_view import SampleTableView
from modules.logic.utils import read_yaml_file


class ClickableLabel(QLabel):
    def __init__(self, text, data, parent=None):
        super().__init__(text, parent)
        self.data = data
        self.name = data['ApplicationProfile']
        self.setCursor(Qt.PointingHandCursor)  # Change the cursor to a hand pointer

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.show_popup()

    def show_popup(self):
        # Create a popup dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(self.name)
        dialog.setWindowIcon(qta.icon('msc.symbol-method', options=[{'draw': 'image'}]))

        # Add content to the popup dialog
        layout = QVBoxLayout(dialog)
        textedit = QTextEdit(self)
        textedit.setReadOnly(True)
        textedit.setPlainText(yaml.dump(self.data))
        layout.addWidget(textedit)

        dialog.show()


class ApplicationProfiles(QWidget):
    def __init__(self, application_profile_basepath: Path, sample_tableview: SampleTableView):
        super().__init__()
        self.profile_mgr = ApplicationProfileMGR(Path(application_profile_basepath), sample_tableview)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        profiles_label = QLabel("Application profiles")
        profiles_label.setStyleSheet("font-weight: bold")
        self.main_layout.addWidget(profiles_label)

        self.vertical_layout = QVBoxLayout()
        self.main_layout.addLayout(self.vertical_layout)

        self.setup()

    def setup(self):
        self.main_layout.setSpacing(5)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.vertical_layout.setSpacing(5)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)

        profile_widgets = self.profile_mgr.get_profile_widgets()
        for group in profile_widgets:
            group_label = QLabel(group)
            group_label.setStyleSheet("font-style: italic")
            self.vertical_layout.addWidget(self.get_line())
            self.vertical_layout.addWidget(group_label)
            for name in profile_widgets[group]:
                pw = profile_widgets[group][name]
                self.vertical_layout.addWidget(pw)

        self.main_layout.addSpacerItem(QSpacerItem(20, 40,
                                                   QSizePolicy.Minimum,
                                                   QSizePolicy.Expanding))
    @staticmethod
    def get_line():
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line


class ApplicationProfileWidget(QWidget):
    profile_data_signal = Signal(dict)

    def __init__(self, data: dict):
        super().__init__()

        self.data = data
        profile_button = QPushButton("apply")
        profile_button.setMaximumWidth(50)
        label = ClickableLabel(self.data['ApplicationProfile'], self.data)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(label)
        layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addWidget(profile_button)
        layout.addSpacerItem(QSpacerItem(10, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        profile_button.clicked.connect(self.send_profile_data)

        self.setLayout(layout)

    def send_profile_data(self):
        self.profile_data_signal.emit(self.data)

    def profile_name(self):
        return self.profile_name['ProfileName']



class ApplicationProfileMGR:
    def __init__(self, applicationprofiles_dirpath: Path, sample_tableview: SampleTableView) -> None:
        # setup profile files

        application_files = [f for f in applicationprofiles_dirpath.glob("**/*.yaml")]
        self.profile_widgets = {}

        for file in application_files:
            if not file.is_file():
                continue

            profile_data = read_yaml_file(file)
            group = file.parent.name
            profile_name = profile_data['ApplicationProfile']

            pw = ApplicationProfileWidget(profile_data)

            if group not in self.profile_widgets:
                self.profile_widgets[group] = {}

            self.profile_widgets[group][profile_name] = pw
            pw.profile_data_signal.connect(sample_tableview.set_profile_data)

    def get_profile_widgets(self):
        return self.profile_widgets
