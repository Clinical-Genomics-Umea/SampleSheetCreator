from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
)

from modules.models.configuration.configuration_manager import ConfigurationManager


class IgeneKeyWidget(QWidget):
    def __init__(self, configuration_manager: ConfigurationManager):
        super().__init__()
        self._configuration_manager = configuration_manager

        self.setFixedSize(500, 300)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.input_layout = QHBoxLayout()

        # Widgets
        self.key_line_widget = QLineEdit()
        self.add_key_button = QPushButton("Add key")

        # Setup input layout
        self.input_layout.addWidget(self.key_line_widget)
        self.input_layout.addWidget(self.add_key_button)

        # Add widgets to main layout

        self.setLayout(self.input_layout)

        # Connect signals and slots
        self.add_key_button.clicked.connect(self._set_key)

        self._setup()

    def _setup(self):
        igene_key = self._configuration_manager.igene_key
        self.key_line_widget.setText(igene_key)

    @Slot()
    def _set_key(self):
        key = self.key_line_widget.text().strip()
        if key:
            self._configuration_manager.set_igene_key(key)
            self._setup()

