from PySide6.QtWidgets import (
    QPushButton,
    QWidget,
    QHBoxLayout,
    QSizePolicy,
    QSpacerItem,
)

from PySide6.QtCore import Signal

from views.leftmenu.application.clickable_label import ClickableLabel


class ApplicationWidget(QWidget):

    add_app = Signal(object)
    rem_app = Signal(object)

    def __init__(self, data: dict):
        super().__init__()

        self.app_data = data
        self.app_add_btn = QPushButton("+")
        self.app_add_btn.setMaximumWidth(50)
        self.app_rem_btn = QPushButton("-")
        self.app_rem_btn.setMaximumWidth(50)

        self.label = ClickableLabel(data["ApplicationName"], data)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.label)
        layout.addSpacerItem(
            QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        layout.addWidget(self.app_add_btn)
        layout.addWidget(self.app_rem_btn)
        layout.addSpacerItem(QSpacerItem(10, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        self.setLayout(layout)

        self.app_add_btn.clicked.connect(self._add_clicked)
        self.app_rem_btn.clicked.connect(self._rem_clicked)

    def _add_clicked(self) -> None:
        self.add_app.emit(self.app_data)

    def _rem_clicked(self) -> None:
        self.rem_app.emit(self.app_data)
