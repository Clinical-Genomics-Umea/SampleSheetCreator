from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QLineEdit,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QLabel,
    QFormLayout,
)
from PySide6.QtCore import Slot
from models.configuration.configuration import ConfigurationManager


class ConfigurationWidget(QWidget):
    def __init__(self, cfg_mgr):
        super().__init__()

        self.cfg_mgr = cfg_mgr

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.main_layout.addWidget(ConfigPathsWidget(self.cfg_mgr))
        self.main_layout.addSpacerItem(
            QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Fixed)
        )
        self.main_layout.addWidget(UsersWidget(self.cfg_mgr))

        self.main_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
        )


class ConfigPathsWidget(QWidget):
    def __init__(self, cfg_mgr):
        super().__init__()

        font = QFont()
        font.setPointSize(18)

        self.cfg_mgr = cfg_mgr

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.header_label = QLabel("Configuration paths")
        self.header_label.setStyleSheet("font-weight: bold; font-size: 16pt;")
        self.main_layout.addWidget(self.header_label)

        self.form_layout = QFormLayout()
        self.main_layout.addLayout(self.form_layout)

        self.main_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
        )

        self._setup()

    def _setup(self):
        paths_dict = self.cfg_mgr.all_config_paths
        for name, path in paths_dict.items():
            self.form_layout.addRow(name, QLabel(str(path)))


class UsersWidget(QWidget):
    def __init__(self, cfg_mgr: ConfigurationManager):
        super().__init__()
        self.cfg_mgr = cfg_mgr

        self.setFixedSize(500, 300)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.input_layout = QHBoxLayout()
        self.action_layout = QHBoxLayout()

        # Widgets
        self.title_label = QLabel("Users")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 16pt;")
        self.user_list_widget = QListWidget()
        self.user_input_field = QLineEdit()
        self.add_user_button = QPushButton("Add User")
        self.remove_user_button = QPushButton("Remove Selected User")

        # Setup input layout
        self.input_layout.addWidget(self.user_input_field)
        self.input_layout.addWidget(self.add_user_button)

        # Add widgets to main layout
        self.layout.addWidget(self.title_label)
        self.layout.addLayout(self.input_layout)
        self.layout.addWidget(self.user_list_widget)

        self.action_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        self.action_layout.addWidget(self.remove_user_button)
        self.layout.addLayout(self.action_layout)

        # Connect signals and slots
        self.add_user_button.clicked.connect(self.add_user)
        self.remove_user_button.clicked.connect(self._remove_user)

        self._setup()

    def _setup(self):
        users = self.cfg_mgr.users
        self.user_list_widget.clear()
        for user in users:
            self.user_list_widget.addItem(user)

    @Slot()
    def add_user(self):
        user = self.user_input_field.text().strip()
        if user:
            self.cfg_mgr.add_user(user)
            self._setup()

    @Slot()
    def _remove_user(self):
        user = self.user_list_widget.currentItem().text()
        self.cfg_mgr.remove_user(user)
        self._setup()
