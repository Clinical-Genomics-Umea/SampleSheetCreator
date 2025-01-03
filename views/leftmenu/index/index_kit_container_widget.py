from PySide6.QtWidgets import QWidget, QHBoxLayout

from models.indexes.index_kit_object import IndexKitObject
from views.leftmenu.index.index_kit_widget import IndexKitWidget


class IndexKitContainerWidget(QWidget):
    def __init__(self, iko: IndexKitObject) -> None:
        super().__init__()

        self.layout = QHBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.i7_len = 0
        self.i5_len = 0

        for name in iko.index_sets.keys():
            index_widget = IndexKitWidget(iko.index_sets[name])

            iko.index_sets[name]

            self.layout.addWidget(index_widget)
