from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QHBoxLayout,
    QMessageBox, QSpacerItem, QSizePolicy
)

from modules.models.configuration.configuration_manager import ConfigurationManager


class DefaultFoldersPathsWidget(QWidget):
    """Widget for managing default folder paths used in the application."""

    def __init__(self, configuration_manager: ConfigurationManager):
        super().__init__()
        self._configuration_manager = configuration_manager

        self.setFixedSize(500, 300)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # Widgets

        self.form = QFormLayout()
        
        # Create path input fields with browse buttons
        self.export_samplesheet_path = self._create_path_input("Export samplesheet v2 path")
        self.export_json_path = self._create_path_input("Export JSON path")
        self.export_package_path = self._create_path_input("Export package path")

        self.save_button = QPushButton("Save Paths")
        self.save_button.clicked.connect(self._save_paths)
        
        # Setup layout

        self.layout.addLayout(self.form)
        hbox = QHBoxLayout()
        hbox.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        hbox.addWidget(self.save_button)
        self.layout.addLayout(hbox)
        self.layout.addStretch()
        
        # Load saved paths
        self._load_paths()
    
    def _create_path_input(self, label_text: str) -> QLineEdit:
        """Create a path input field with a browse button."""
        layout = QHBoxLayout()
        
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Browse to select a folder...")
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(lambda _, le=line_edit: self._browse_folder(le))
        
        layout.addWidget(line_edit)
        layout.addWidget(browse_btn)
        
        self.form.addRow(label_text, layout)
        
        return line_edit
    
    def _browse_folder(self, line_edit: QLineEdit):
        """Open folder dialog and update the line edit with selected path."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if folder:
            line_edit.setText(folder)
    
    def _load_paths(self):
        """Load saved paths from configuration."""
        try:
            self.export_samplesheet_path.setText(
                self._configuration_manager.get_folder_path('export_samplesheet_path')
            )
            self.export_json_path.setText(
                self._configuration_manager.get_folder_path('export_json_path')
            )
            self.export_package_path.setText(
                self._configuration_manager.get_folder_path('export_package_path')
            )
        except Exception as e:
            print(f"Error loading folder paths: {e}")
    
    def _save_paths(self):
        """Save current paths to configuration."""
        try:
            self._configuration_manager.set_folder_path(
                'export_samplesheet_path', 
                self.export_samplesheet_path.text()
            )
            self._configuration_manager.set_folder_path(
                'export_json_path',
                self.export_json_path.text()
            )
            self._configuration_manager.set_folder_path(
                'export_package_path',
                self.export_package_path.text()
            )
            
            # Optional: Show success message
            QMessageBox.information(
                self,
                "Success",
                "Folder paths have been saved successfully.",
                QMessageBox.Ok
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save folder paths: {str(e)}",
                QMessageBox.Ok
            )
