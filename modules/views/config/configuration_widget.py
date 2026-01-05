from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFrame,
    QSpacerItem,
    QSizePolicy,
    QLabel, QScrollArea
)

from modules.views.config.configuration_paths_widget import ConfigPathsWidget
from modules.views.config.users_widget import UsersWidget
from modules.views.config.default_folders import DefaultFoldersPathsWidget
from modules.views.config.igene_key import IgeneKeyUrlWidget


class ConfigurationWidget(QWidget):
    def __init__(self, configuration_manager):
        super().__init__()
        self.configuration_manager = configuration_manager

        self._scroll = QScrollArea()

        self._setup_ui()
        self._setup_styles()

    def _setup_ui(self):
        # Main layout with consistent spacing
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # Remove outer margins
        self.setLayout(self.main_layout)

        # Create a scroll area
        self._scroll.setWidgetResizable(True)  # Allow the widget to be resized
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Only vertical scrolling

        # Create a container widget for the scroll area
        container = QWidget()
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scroll_layout = QVBoxLayout(container)
        self.scroll_layout.setContentsMargins(20, 15, 20, 15)
        self.scroll_layout.setSpacing(20)

        # Set the container as the scroll area's widget
        self._scroll.setWidget(container)

        # Add the scroll area to the main layout
        self.main_layout.addWidget(self._scroll)

        # Create widgets
        self.paths_widget = ConfigPathsWidget(self.configuration_manager)
        self.folders_widget = DefaultFoldersPathsWidget(self.configuration_manager)
        self.users_widget = UsersWidget(self.configuration_manager)
        self.igene_key_widget = IgeneKeyUrlWidget(self.configuration_manager)

        # Add widgets with section dividers to the scroll layout
        self._add_section("Configuration Paths", self.paths_widget)
        self._add_section("Default Folders", self.folders_widget)
        self._add_section("User Management", self.users_widget)
        self._add_section("iGene Url & Key", self.igene_key_widget)

        # Add stretch to push content to the top
        self.scroll_layout.addStretch()

    def _add_section(self, title: str, widget: QWidget):
        """Add a titled section with consistent styling."""
        # Section title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                padding: 5px 0;
                border-bottom: 1px solid #e0e0e0;
            }
        """)

        # Container frame for the widget
        container = QFrame()
        container.setFrameShape(QFrame.StyledPanel)

        # Layout for the container
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(10)
        container_layout.addWidget(widget)

        # Add to scroll layout instead of main layout
        self.scroll_layout.addWidget(title_label)
        self.scroll_layout.addWidget(container)
    
    def _setup_styles(self):
        """Set up the base styles for this widget."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2472a4;
            }
            QLineEdit, QListWidget, QComboBox {
                padding: 6px 8px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                min-height: 24px;
            }
            QLineEdit:focus, QListWidget:focus, QComboBox:focus {
                border: 1px solid #3498db;
                outline: none;
            }
        """)
