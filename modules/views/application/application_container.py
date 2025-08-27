from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy

from modules.models.application.application_manager import ApplicationManager
from modules.models.state.state_model import StateModel
from modules.views.application.application_widget import ApplicationWidget
from modules.views.ui_components import HorizontalLine


class ApplicationContainerWidget(QWidget):

    add_application_profile_data = Signal(dict)
    remove_application_profile = Signal(dict)

    def __init__(
        self, application_manager: ApplicationManager, state_model: StateModel):
        super().__init__()

        self._application_manager = application_manager
        self._dataset_manager = state_model

        self._main_layout = QVBoxLayout()
        self.setLayout(self._main_layout)

        application_label = QLabel("Application Profiles")
        application_label.setStyleSheet("font-weight: bold")
        self._main_layout.addWidget(application_label)

        self._vertical_layout = QVBoxLayout()
        self._main_layout.addLayout(self._vertical_layout)

        self._application_widgets = []

        self._setup()

    def _setup(self):
        """Set up the main layout of the Applications widget."""

        self._main_layout.setSpacing(5)
        self._main_layout.setContentsMargins(0, 0, 0, 0)

        self._vertical_layout.setSpacing(5)
        self._vertical_layout.setContentsMargins(0, 0, 0, 0)

        application_hierarchy = self._application_manager.application_hierarchy

        for application_type in application_hierarchy:
            type_label = QLabel(application_type)
            type_label.setStyleSheet("font-style: italic")
            self._vertical_layout.addWidget(HorizontalLine())
            self._vertical_layout.addWidget(type_label)

            for application_name in application_hierarchy[application_type]:
                application_widget = ApplicationWidget(
                    application_hierarchy[application_type][application_name]
                )
                self._application_widgets.append(application_widget)
                self._vertical_layout.addWidget(application_widget)

                application_widget.add_app.connect(self._handle_add_click)
                application_widget.rem_app.connect(self._handle_remove_click)

        self._main_layout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

    @Slot(object)
    def _handle_add_click(self, data: object):
        self.add_application_profile_data.emit(data)

    @Slot(object)
    def _handle_remove_click(self, data):
        self.remove_application_profile.emit(data)
