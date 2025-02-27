from PySide6.QtCore import Slot
from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QSizePolicy, QSpacerItem, QLabel

from modules.views.validation.lane_index_distance_widget import LaneIndexDistanceWidget


class IndexDistanceValidationContainerWidget(QTabWidget):
    def __init__(self):
        super().__init__()

        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setLayout(self.layout)

        self.hspacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.vspacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vspacer_fixed = QSpacerItem(1, 20, QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    @Slot(object)
    def populate(self, results):

        if isinstance(results, str):
            self.addTab(QLabel(results), "Error")
            return

        for lane in results:
            print(results[lane])
            tab = LaneIndexDistanceWidget(results[lane])
            self.addTab(tab, f"lane {lane}")

    def clear(self):
        print("clearing main index distance validation widget")
        # Remove and delete each tab widget
        while self.count() > 0:
            widget = self.widget(0)  # Get the first widget in the tab widget
            self.removeTab(0)  # Remove the tab
            widget.deleteLater()
