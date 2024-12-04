from pathlib import Path
import yaml
import qtawesome as qta

from PySide6.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QSizePolicy,
    QSpacerItem,
    QLabel,
    QFrame,
    QDialog,
    QTextEdit,
)

from PySide6.QtCore import Signal, Qt, QObject, Slot

from models.application_profile import ApplicationProfileManager
from utils.utils import read_yaml_file


class ClickableLabel(QLabel):
    def __init__(self, text, data, parent=None):
        super().__init__(text, parent)
        self.data = data
        self.name = data["ApplicationProfileName"]
        self.setCursor(Qt.PointingHandCursor)  # Change the cursor to a hand pointer

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.show_popup()

    def show_popup(self):
        # Create a popup dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(self.name)
        dialog.setWindowIcon(qta.icon("msc.symbol-method", options=[{"draw": "image"}]))

        # Add content to the popup dialog
        layout = QVBoxLayout(dialog)
        textedit = QTextEdit(self)
        textedit.setReadOnly(True)
        textedit.setPlainText(yaml.dump(self.data))
        layout.addWidget(textedit)

        dialog.show()


class ApplicationProfiles(QWidget):

    profile_data_ready = Signal(dict)

    def __init__(self, app_profile_mgr):
        super().__init__()
        self.profile_mgr = app_profile_mgr
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        profiles_label = QLabel("Application profiles")
        profiles_label.setStyleSheet("font-weight: bold")
        self.main_layout.addWidget(profiles_label)

        self.vertical_layout = QVBoxLayout()
        self.main_layout.addLayout(self.vertical_layout)

        self.profile_widgets = []

        self.setup()

    def setup(self):
        self.main_layout.setSpacing(5)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.vertical_layout.setSpacing(5)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)

        profiles = self.profile_mgr.application_group_name_profiles
        for group in profiles:
            group_label = QLabel(group)
            group_label.setStyleSheet("font-style: italic")
            self.vertical_layout.addWidget(self.get_line())
            self.vertical_layout.addWidget(group_label)
            for name in profiles[group]:

                profile_widget = ApplicationProfileWidget(profiles[group][name])
                self.profile_widgets.append(profile_widget)
                self.vertical_layout.addWidget(profile_widget)

                profile_widget.profile_data_ready.connect(
                    self._handle_profile_button_click
                )

        self.main_layout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

    @Slot(object)
    def _handle_profile_button_click(self, data):
        print("handle ..", data)
        self.profile_data_ready.emit(data)

    @staticmethod
    def get_line():
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line


class ApplicationProfileWidget(QWidget):

    profile_data_ready = Signal(object)

    def __init__(self, data: dict):
        super().__init__()

        self.profile_data = data
        self.profile_button = QPushButton("apply")

        self.profile_button.setMaximumWidth(50)
        self.label = ClickableLabel(data["ApplicationProfileName"], data)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.label)
        layout.addSpacerItem(
            QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        layout.addWidget(self.profile_button)
        layout.addSpacerItem(QSpacerItem(10, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        self.setLayout(layout)

        self.profile_button.clicked.connect(self.apply_clicked)

    def apply_clicked(self):

        print("apply", self.profile_data)

        self.profile_data_ready.emit(self.profile_data)
