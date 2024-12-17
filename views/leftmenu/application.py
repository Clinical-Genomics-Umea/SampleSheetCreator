import yaml
import qtawesome as qta

from PySide6.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QSizePolicy,
    QSpacerItem,
    QLabel,
    QDialog,
    QTextEdit,
)

from PySide6.QtCore import Signal, Qt, Slot

from models.application.application import ApplicationManager
from models.dataset.dataset import DataSetManager
from views.ui_components import HorizontalLine


class ClickableLabel(QLabel):
    def __init__(self, text: str, data: dict, parent=None):
        super().__init__(text, parent)
        self.data = data
        self.name = data["ApplicationName"]
        self.setCursor(Qt.PointingHandCursor)  # Change the cursor to a hand pointer

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._show_popup()

    def _show_popup(self):
        # Create a popup dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(self.name)
        dialog.setWindowIcon(qta.icon("msc.symbol-method", options=[{"draw": "image"}]))

        # Add content to the popup dialog
        layout = QVBoxLayout(dialog)
        textedit = QTextEdit(self)
        textedit.setReadOnly(True)
        textedit.setPlainText(yaml.dump(self.data))
        layout.addWidget(textedit)

        dialog.show()


class Applications(QWidget):

    add_signal = Signal(dict)
    remove_signal = Signal(dict)

    def __init__(self, app_mgr: ApplicationManager, dataset_mgr: DataSetManager):
        super().__init__()
        self.app_mgr = app_mgr
        self.dataset_mgr = dataset_mgr
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        apps_label = QLabel("Applications")
        apps_label.setStyleSheet("font-weight: bold")
        self.main_layout.addWidget(apps_label)

        self.vertical_layout = QVBoxLayout()
        self.main_layout.addLayout(self.vertical_layout)

        self.app_widgets = []

        self._setup()

    def _setup(self):
        """Set up the main layout of the Applications widget."""

        self.main_layout.setSpacing(5)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.vertical_layout.setSpacing(5)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)

        app_hierarchy = self.app_mgr.app_hierarchy

        for group in app_hierarchy:
            group_label = QLabel(group)
            group_label.setStyleSheet("font-style: italic")
            self.vertical_layout.addWidget(HorizontalLine())
            self.vertical_layout.addWidget(group_label)

            for app_name in app_hierarchy[group]:
                app_widget = ApplicationWidget(app_hierarchy[group][app_name])
                self.app_widgets.append(app_widget)
                self.vertical_layout.addWidget(app_widget)

                app_widget.add_app.connect(self._handle_add_click)
                app_widget.rem_app.connect(self._handle_remove_click)

        self.main_layout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

    @Slot(object)
    def _handle_add_click(self, data):
        self.add_signal.emit(data)

    @Slot(object)
    def _handle_remove_click(self, data):
        self.remove_signal.emit(data)


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
