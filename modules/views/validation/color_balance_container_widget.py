from PySide6.QtCore import Slot
from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QSizePolicy, QScrollArea, QFrame

from modules.views.validation.color_balance_widget import ColorBalanceWidget


class ColorBalanceContainerWidget(QTabWidget):

    def __init__(self, dataset_mgr):
        super().__init__()

        self.dataset_mgr = dataset_mgr

        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setLayout(self.layout)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def clear(self):
        print("clearing color balance widget")
        # Remove and delete each tab widget
        while self.count() > 0:
            widget = self.widget(0)  # Get the first widget in the tab widget
            self.removeTab(0)  # Remove the tab
            widget.deleteLater()

    @Slot(object)
    def populate(self, results):
        print("color balance populate", results)

        for lane in results:
            tab_scroll_area = QScrollArea()
            tab_scroll_area.setFrameShape(QFrame.NoFrame)

            color_balance_table = ColorBalanceWidget(
                results[lane], self.dataset_mgr.base_colors
            )

            self.addTab(color_balance_table, f"lane {lane}")
