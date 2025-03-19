from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QSizePolicy, QScrollArea, QFrame
from modules.views.validation.color_balance_lane_widget import ColorBalanceLaneWidget


class ColorBalanceValidationWidget(QTabWidget):

    def __init__(self, dataset_manager):
        super().__init__()

        self._dataset_manager = dataset_manager

        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setLayout(self.layout)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def clear(self):
        # Remove and delete each tab widget
        while self.count() > 0:
            widget = self.widget(0)  # Get the first widget in the tab widget
            self.removeTab(0)  # Remove the tab
            widget.deleteLater()

    def populate(self, results):
        self.clear()

        for lane in results:
            tab_scroll_area = QScrollArea()
            tab_scroll_area.setFrameShape(QFrame.NoFrame)

            color_balance_table = ColorBalanceLaneWidget(
                results[lane], self._dataset_manager.base_colors
            )

            self.addTab(color_balance_table, f"lane {lane}")
