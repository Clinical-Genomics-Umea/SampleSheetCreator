from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QSizePolicy, QSpacerItem, QLabel
from modules.views.validation.index_distance_lane_area_widget import IndexDistanceLaneAreaWidget


class IndexDistanceValidationWidget(QTabWidget):
    def __init__(self):
        super().__init__()

        self.setContentsMargins(0, 0, 0, 0)
        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setLayout(self._layout)

        self._hspacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self._vspacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self._vspacer_fixed = QSpacerItem(1, 20, QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


    def populate(self, results):

        self.clear()

        if isinstance(results, str):
            self.addTab(QLabel(results), "Error")
            return

        for lane in results:
            tab = IndexDistanceLaneAreaWidget(results[lane])
            self.addTab(tab, f"lane {lane}")

    def clear(self):
        # Remove and delete each tab widget
        while self.count() > 0:
            widget = self.widget(0)  # Get the first widget in the tab widget
            self.removeTab(0)  # Remove the tab
            widget.deleteLater()
