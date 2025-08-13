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
from modules.views.validation.prevalidation_widget import PreValidationWidget


class MainValidationWidget(QWidget):
    def __init__(self,
                 prevalidation_widget,
                 sample_data_overview_widget,
                 index_distance_overview_widget,
                 color_balance_overview_widget,
                 main_validator):
        super().__init__()


        self._main_validator = main_validator

        self._prevalidation_widget = prevalidation_widget
        self._sample_data_overview_widget = sample_data_overview_widget
        self._index_distance_overview_widget = index_distance_overview_widget
        self._color_balance_overview_widget = color_balance_overview_widget

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget()

        self.tab_widget.addTab(self._prevalidation_widget, "general validation")
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

    def clear_validation_widgets(self):
        self._prevalidation_widget.clear()
        self._sample_data_overview_widget.clear()
        self._index_distance_overview_widget.clear()
        self._color_balance_overview_widget.clear()

