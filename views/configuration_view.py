from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QSpacerItem,
    QSizePolicy,
    QLabel,
    QFormLayout,
)
from PySide6.QtCore import Slot


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

        self.setup()

    def setup(self):
        paths_dict = self.cfg_mgr.all_config_paths
        for name, path in paths_dict.items():

            self.form_layout.addRow(name, QLabel(str(path)))


class UsersWidget(QWidget):
    def __init__(self, cfg_mgr):
        super().__init__()
        self.cfg_mgr = cfg_mgr

        self.setFixedWidth(500)
        self.setFixedHeight(300)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.input_layout = QHBoxLayout()
        self.remove_layout = QHBoxLayout()

        # Widgets
        self.header_label = QLabel("Users")
        self.header_label.setStyleSheet("font-weight: bold; font-size: 16pt;")
        self.user_list = QListWidget()
        self.user_input = QLineEdit()
        self.add_button = QPushButton("Add User")
        self.remove_button = QPushButton("Remove Selected User")

        # Setting up input layout
        self.input_layout.addWidget(self.user_input)
        self.input_layout.addWidget(self.add_button)

        # Adding widgets to main layout
        self.main_layout.addWidget(self.header_label)
        self.main_layout.addLayout(self.input_layout)
        self.main_layout.addWidget(self.user_list)

        self.remove_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        self.remove_layout.addWidget(self.remove_button)
        self.main_layout.addLayout(self.remove_layout)

        self.setLayout(self.main_layout)

        # Connecting signals and slots
        self.add_button.clicked.connect(self.add_user)
        self.remove_button.clicked.connect(self.remove_user)

        self.setup()

    def setup(self):
        users = self.cfg_mgr.users
        self.user_list.clear()
        for user in users:
            self.user_list.addItem(user)

    @Slot()
    def add_user(self):
        user = self.user_input.text().strip()
        if user:
            self.cfg_mgr.add_user(user)
            self.setup()

    @Slot()
    def remove_user(self):
        user = self.user_list.currentItem().text()
        self.cfg_mgr.remove_user(user)
        self.setup()
