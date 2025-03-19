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
from modules.views.validation.dataset_validation_widget import DataSetValidationWidget
from modules.views.validation.index_distance_validation_widget import (
    IndexDistanceValidationWidget,
)
from modules.views.validation.prevalidation_widget import PreValidationWidget


class MainValidationWidget(QWidget):
    def __init__(self,
                 prevalidation_widget,
                 dataset_validation_widget,
                 index_distance_validation_widget,
                 color_balance_validation_container_widget,
                 main_validator):
        super().__init__()


        self._main_validator = main_validator

        self._prevalidation_widget = prevalidation_widget
        self._dataset_validation_widget = dataset_validation_widget
        self._index_distance_validation_widget = index_distance_validation_widget
        self._color_balance_validation_container_widget = color_balance_validation_container_widget

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget()

        self.tab_widget.addTab(self._prevalidation_widget, "pre-validation")
        self.tab_widget.addTab(self._dataset_validation_widget, "dataset validation")
        self.tab_widget.addTab(self._index_distance_validation_widget, "index distance")
        self.tab_widget.addTab(self._color_balance_validation_container_widget, "color balance")

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        self.validate_button = QPushButton("Validate")
        hbox.addWidget(self.validate_button)
        hbox.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding))

        self.layout.addLayout(hbox)
        self.layout.addWidget(self.tab_widget)

    def clear_validation_widgets(self):
        self._prevalidation_widget.clear()
        self._dataset_validation_widget.clear()
        self._index_distance_validation_widget.clear()
        self._color_balance_validation_container_widget.clear()

