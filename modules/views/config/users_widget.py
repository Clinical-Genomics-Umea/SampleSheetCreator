from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QLineEdit,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)

from modules.models.configuration.configuration_manager import ConfigurationManager


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
