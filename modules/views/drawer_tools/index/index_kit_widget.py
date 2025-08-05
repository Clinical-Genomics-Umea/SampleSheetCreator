from PySide6.QtWidgets import QWidget, QHBoxLayout

from modules.models.indexes.index_kit_model import IndexKitModel
from modules.views.drawer_tools.index.index_table_column_widget import SingleIndexWidget


class IndexKitWidget(QWidget):
    def __init__(self, index_kit_dataset: dict) -> None:
        super().__init__()

        self.layout = QHBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self._index_i7_len = index_kit_dataset.get("IndexI7Len")
        self._index_i5_len = index_kit_dataset.get("IndexI5Len")
        self._name = index_kit_dataset.get("IndexKitName")
        self._type = index_kit_dataset.get("Type")
        self._layout = index_kit_dataset.get("Layout")


        for index_set_name, index_set in index_kit_dataset["IndexSets"].items():
            index_widget = SingleIndexWidget(index_set_name, index_set)
            self.layout.addWidget(index_widget)

    @property
    def index_i7_len(self):
        return self._index_i7_len

    @property
    def index_i5_len(self):
        return self._index_i5_len

    @property
    def name(self):
        return self._name
