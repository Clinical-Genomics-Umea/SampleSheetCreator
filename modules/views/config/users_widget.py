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
    def __init__(self, configuration_manager: ConfigurationManager):
        super().__init__()
        self._configuration_manager = configuration_manager

        self.setFixedSize(500, 300)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.input_layout = QHBoxLayout()

        # Widgets
        self.user_list_widget = QListWidget()
        self.user_input_field = QLineEdit()
        self.add_user_button = QPushButton("Add User")
        self.remove_user_button = QPushButton("Remove Selected User")

        # Setup input layout
        self.input_layout.addWidget(self.user_input_field)
        self.input_layout.addWidget(self.add_user_button)
        self.input_layout.addWidget(self.remove_user_button)

        # Add widgets to main layout
        self.layout.addLayout(self.input_layout)
        self.layout.addWidget(self.user_list_widget)

        # Connect signals and slots
        self.add_user_button.clicked.connect(self.add_user)
        self.remove_user_button.clicked.connect(self._remove_user)

        self._setup()

    def _setup(self):
        users = self._configuration_manager.users
        self.user_list_widget.clear()
        for user in users:
            self.user_list_widget.addItem(user)

    @Slot()
    def add_user(self):
        user = self.user_input_field.text().strip()
        if user:
            self._configuration_manager.add_user(user)
            self._setup()

    @Slot()
    def _remove_user(self):
        user = self.user_list_widget.currentItem().text()
        self._configuration_manager.remove_user(user)
        self._setup()
