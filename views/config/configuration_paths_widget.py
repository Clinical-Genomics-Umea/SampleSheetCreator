from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFormLayout,
    QSpacerItem,
    QSizePolicy,
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
