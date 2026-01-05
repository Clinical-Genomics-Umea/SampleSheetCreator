from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFormLayout,
    QSpacerItem,
    QSizePolicy, QLineEdit,
)


class ConfigPathsWidget(QWidget):
    def __init__(self, configuration_manager):
        super().__init__()

        self.configuration_manager = configuration_manager

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.form_layout = QFormLayout()
        self.main_layout.addLayout(self.form_layout)

        self.main_layout.addStretch()

        self._setup()

    def _setup(self):
        paths_dict = self.configuration_manager.all_config_paths
        for name, path in paths_dict.items():
            path_edit = QLineEdit(str(path))
            path_edit.setReadOnly(True)
            self.form_layout.addRow(name, path_edit)
