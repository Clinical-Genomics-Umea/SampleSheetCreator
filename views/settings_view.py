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
    QGroupBox,
    QLabel,
)
from PySide6.QtCore import Slot

from models.settings import SettingsManager


class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.settings = SettingsManager()

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.main_layout.addWidget(UsersWidget(self.settings))

        self.main_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
        )


class UsersWidget(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings

        self.setFixedWidth(500)
        self.setFixedHeight(300)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.input_layout = QHBoxLayout()
        self.remove_layout = QHBoxLayout()

        # Widgets
        self.header_label = QLabel("Users")
        self.header_label.setStyleSheet("font-weight: bold;")
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

        self.load_users()

    @Slot()
    def add_user(self):
        user_name = self.user_input.text().strip()
        if user_name:
            self.user_list.addItem(user_name)
            self.user_input.clear()
            self.save_users()
        else:
            QMessageBox.warning(self, "Input Error", "User name cannot be empty!")

    def save_users(self):
        users = [self.user_list.item(i).text() for i in range(self.user_list.count())]
        self.settings.set_user(users)

    def load_users(self):
        users = self.settings.user()
        if not users:
            return

        for user in users:
            self.user_list.addItem(user)

    @Slot()
    def remove_user(self):
        selected_items = self.user_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "No user selected!")
            return
        for item in selected_items:
            self.user_list.takeItem(self.user_list.row(item))
