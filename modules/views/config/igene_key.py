from PySide6.QtCore import Slot, QSettings
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QFormLayout
)

from modules.models.configuration.configuration_manager import ConfigurationManager


class IgeneKeyUrlWidget(QWidget):
    def __init__(self, configuration_manager: ConfigurationManager):
        super().__init__()
        self._configuration_manager = configuration_manager

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        # Create form layout for inputs
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        # URL row
        url_layout = QHBoxLayout()
        self.url_line_edit = QLineEdit()
        self.url_line_edit.setPlaceholderText("Enter iGene API URL...")
        self.save_url_button = QPushButton("Set URL")
        url_layout.addWidget(self.url_line_edit)
        url_layout.addWidget(self.save_url_button)
        form_layout.addRow("API URL:", url_layout)

        # API Key row
        key_layout = QHBoxLayout()
        self.key_line_edit = QLineEdit()
        self.key_line_edit.setPlaceholderText("Enter iGene API key...")
        self.key_line_edit.setEchoMode(QLineEdit.Password)
        self.add_key_button = QPushButton("Set Key")
        key_layout.addWidget(self.key_line_edit)
        key_layout.addWidget(self.add_key_button)
        form_layout.addRow("iGene API Key:", key_layout)

        # Add form layout to main layout
        main_layout.addLayout(form_layout)

        # Connect signals and slots
        self.add_key_button.clicked.connect(self._set_key)
        self.save_url_button.clicked.connect(self._set_url)

        self._setup()

    def _setup(self):
        # Load saved key and URL
        igene_key = self._configuration_manager.igene_key
        self.key_line_edit.setText(igene_key)

        # Load saved URL if exists
        igene_url = self._configuration_manager.igene_url
        self.url_line_edit.setText(igene_url)


    @Slot()
    def _set_key(self):
        key = self.key_line_edit.text().strip()
        if key:
            self._configuration_manager.set_igene_key(key)

    @Slot()
    def _set_url(self):
        url = self.url_line_edit.text().strip()
        if url:
            self._configuration_manager.set_igene_url(url)