from PySide6.QtWidgets import (
    QPushButton,
    QWidget,
    QHBoxLayout,
    QSizePolicy,
    QSpacerItem,
)

from PySide6.QtCore import Signal

from modules.models.application.application_profile import ApplicationProfile
from modules.views.application.clickable_label import ClickableLabel


class ApplicationWidget(QWidget):

    add_app = Signal(object)
    rem_app = Signal(object)

    def __init__(self, profile: ApplicationProfile):
        super().__init__()

        self._profile = profile
        self._add_button = QPushButton("+")
        self._add_button.setMaximumWidth(50)
        self._remove_button = QPushButton("-")
        self._remove_button.setMaximumWidth(50)

        self.app_label = ClickableLabel(profile.ApplicationProfileName, profile)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.app_label)
        layout.addSpacerItem(
            QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        layout.addWidget(self._add_button)
        layout.addWidget(self._remove_button)
        layout.addSpacerItem(QSpacerItem(10, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        self.setLayout(layout)

        self._add_button.clicked.connect(self._add_clicked)
        self._remove_button.clicked.connect(self._rem_clicked)

    def _add_clicked(self) -> None:
        self.add_app.emit(self._profile)

    def _rem_clicked(self) -> None:
        self.rem_app.emit(self._profile)
