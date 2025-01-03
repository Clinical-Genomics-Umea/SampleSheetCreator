from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy

from models.application.application_manager import ApplicationManager
from models.dataset.dataset_manager import DataSetManager
from views.leftmenu.application.application_widget import ApplicationWidget
from views.ui_components import HorizontalLine


class ApplicationContainerWidget(QWidget):

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
