from PySide6.QtWidgets import QScrollArea, QWidget, QFrame, QVBoxLayout, QLabel

from modules.views.validation.index_distance_lane_widget import IndexDistanceLaneWidget


class IndexDistanceLaneAreaWidget(QScrollArea):

    def __init__(self, lane_index_distances):
        super().__init__()
        self.content_widget = QWidget()
        self.setFrameShape(QFrame.NoFrame)
        self.layout = QVBoxLayout(self.content_widget)

        for index_dataset, heatmap_name in (
            ("i7_i5", "I7 + I5 concat"),
            ("i7", "I7"),
            ("i5", "I5"),
        ):
            self.layout.addWidget(QLabel(f"{heatmap_name} distances "))

            heatmap_table = IndexDistanceLaneWidget(lane_index_distances[index_dataset])
            self.layout.addWidget(heatmap_table)

        self.layout.addStretch()

        self.setWidget(self.content_widget)
        self.setWidgetResizable(True)
