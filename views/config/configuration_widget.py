from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSpacerItem,
    QSizePolicy,
)

from views.config.configuration_paths_widget import ConfigPathsWidget
from views.config.users_widget import UsersWidget


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
