from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QTabWidget,
    QPushButton,
)

from modules.views.validation.color_balance_container_widget import ColorBalanceContainerWidget
from modules.views.validation.dataset_validation_widget import DataSetValidationWidget
from modules.views.validation.index_distance_container import (
    IndexDistanceValidationContainerWidget,
)
from modules.views.validation.prevalidation_widget import PreValidationWidget


class MainValidationWidget(QWidget):
    def __init__(self, dataset_mgr):
        super().__init__()

        self.dataset_mgr = dataset_mgr
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget()

        self.pre_validation_widget = PreValidationWidget()
        self.dataset_validation_widget = DataSetValidationWidget()
        self.main_index_validation_widget = IndexDistanceValidationContainerWidget()
        self.color_balance_validation_container_widget = ColorBalanceContainerWidget(
            self.dataset_mgr
        )

        self.tab_widget.addTab(self.pre_validation_widget, "pre-validation")
        self.tab_widget.addTab(self.dataset_validation_widget, "dataset validation")
        self.tab_widget.addTab(self.main_index_validation_widget, "index distance")
        self.tab_widget.addTab(
            self.color_balance_validation_container_widget, "color balance"
        )

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        self.validate_button = QPushButton("Validate")
        hbox.addWidget(self.validate_button)
        hbox.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding))

        self.layout.addLayout(hbox)
        self.layout.addWidget(self.tab_widget)

    def clear_validation_widgets(self):
        self.pre_validation_widget.clear()
        self.dataset_validation_widget.clear()
        self.main_index_validation_widget.clear()
        self.color_balance_validation_container_widget.clear()


#
# class NonEditableDelegate(QItemDelegate):
#     def createEditor(self, parent, option, index):
#         # Return None to make the item non-editable
#         return None
