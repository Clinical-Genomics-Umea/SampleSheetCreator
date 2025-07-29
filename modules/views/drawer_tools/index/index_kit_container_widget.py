from PySide6.QtWidgets import QWidget, QHBoxLayout

from modules.models.indexes.index_kit import IndexKit
from modules.views.drawer_tools.index.index_kit_widget import IndexKitWidget


class IndexKitContainerWidget(QWidget):
    def __init__(self, iko: IndexKit) -> None:
        super().__init__()

        self.layout = QHBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self._index_i7_len = iko.index_i7_len
        self._index_i5_len = iko.index_i5_len

        for name in iko.index_set.keys():
            index_widget = IndexKitWidget(iko.index_set[name])
            self.layout.addWidget(index_widget)

    @property
    def index_i7_len(self):
        return self._index_i7_len

    @property
    def index_i5_len(self):
        return self._index_i5_len
