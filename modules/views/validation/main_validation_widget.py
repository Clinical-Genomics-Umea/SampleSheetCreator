from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QTabWidget,
    QPushButton,
)

from modules.views.validation.color_balance_widget import ColorBalanceValidationWidget
from modules.views.validation.sample_data_overview_widget import SampleDataOverviewWidget
from modules.views.validation.index_distance_overview_widget import (
    IndexDistanceOverviewWidget,
)
from modules.views.validation.general_validation_widget import GeneralValidationWidget


class MainValidationWidget(QWidget):
    def __init__(self,
                 general_validation_widget,
                 sample_data_overview_widget,
                 index_distance_overview_widget,
                 color_balance_overview_widget,
                 main_validator):
        super().__init__()

        self._main_validator = main_validator
        self._general_validation_widget = general_validation_widget
        self._sample_data_overview_widget = sample_data_overview_widget
        self._index_distance_overview_widget = index_distance_overview_widget
        self._color_balance_overview_widget = color_balance_overview_widget
        
        # Store the sample model reference and connection
        self._sample_model = None
        self._data_changed_connection = None

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget()

        self.tab_widget.addTab(self._general_validation_widget, "general validation")
        self.tab_widget.addTab(self._sample_data_overview_widget, "sample data view")
        self.tab_widget.addTab(self._index_distance_overview_widget, "index distance view")
        self.tab_widget.addTab(self._color_balance_overview_widget, "color balance view")

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        self.validate_button = QPushButton("Validate")
        hbox.addWidget(self.validate_button)
        hbox.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding))

        self.layout.addLayout(hbox)
        self.layout.addWidget(self.tab_widget)

    def set_sample_model(self, model):
        """Set the sample model and connect to its dataChanged signal."""
        self._sample_model = model
        self._connect_data_changed()

    def _connect_data_changed(self):
        """Connect to the sample model's dataChanged signal."""
        if self._sample_model and not self._data_changed_connection:
            self._data_changed_connection = self._sample_model.dataChanged.connect(
                self._on_data_changed
            )

    def _disconnect_data_changed(self):
        """Disconnect from the sample model's dataChanged signal."""
        if self._sample_model and self._data_changed_connection:
            self._sample_model.dataChanged.disconnect(self._data_changed_connection)
            self._data_changed_connection = None

    def _on_data_changed(self, top_left, bottom_right, roles=None):
        """Handler for dataChanged signal from the sample model."""
        self.clear_validation_widgets(False)

    def clear_validation_widgets(self, status):
        """Clear all validation widgets, temporarily disconnecting from the model."""
        # Disconnect from dataChanged signal to prevent recursive calls

        if not status:
            self._disconnect_data_changed()

            try:
                # Clear all widgets
                self._general_validation_widget.clear()
                self._sample_data_overview_widget.clear()
                self._index_distance_overview_widget.clear()
                self._color_balance_overview_widget.clear()
            finally:
                # Reconnect to dataChanged signal when done
                self._connect_data_changed()

