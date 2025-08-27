
import pandas as pd
from PySide6.QtWidgets import QWidget, QHBoxLayout

from modules.views.index.index_table_column_widget import SingleIndexWidget


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

            override_cycles_pattern = index_kit_dataset.get("OverrideCyclesPattern")
            adapter_read_1 = index_kit_dataset.get("Adapters", {}).get("AdapterRead1")
            adapter_read_2 = index_kit_dataset.get("Adapters", {}).get("AdapterRead1")

            index_set_df = pd.DataFrame.from_dict(index_set)

            index_set_df["OverrideCyclesPattern"] = override_cycles_pattern
            index_set_df["AdapterRead1"] = adapter_read_1
            index_set_df["AdapterRead2"] = adapter_read_2
            index_set_df["IndexKitName"] = index_kit_dataset.get("IndexKitName")

            index_widget = SingleIndexWidget(index_set_name, index_set_df)
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
