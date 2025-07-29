from pathlib import Path

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBox, QLabel

from modules.models.indexes.index_kit_manager import IndexKitManager
from modules.models.indexes.index_kit_object import IndexKitObject
from modules.views.drawer_tools.index.index_kit_container_widget import IndexKitContainerWidget
from modules.views.ui_components import HorizontalLine


class IndexKitToolbox(QWidget):
    def __init__(self, index_kit_manager: IndexKitManager):
        super().__init__()

        self.index_kit_container_widgets = {
            index_kit_object.name: IndexKitContainerWidget(index_kit_object)
            for index_kit_object in index_kit_manager.index_kit_objects
        }

        self.layout = QVBoxLayout()
        self.toolbox = QToolBox()
        self.hidden_items = {}

        self._setup()

    @Slot(int, int)
    def set_index_kit_status(self, index_run_i5_len, index_run_i7_len):
        for i in range(self.toolbox.count()):
            index_kit_container_widget = self.toolbox.widget(i)
            index_kit_i5_len = index_kit_container_widget.index_i5_len
            index_kit_i7_len = index_kit_container_widget.index_i7_len

            if (
                index_run_i5_len >= index_kit_i5_len
                and index_run_i7_len >= index_kit_i7_len
            ):
                self.toolbox.setItemEnabled(i, True)
                widget = self.toolbox.widget(i)
                widget.setHidden(False)
            else:
                self.toolbox.setItemEnabled(i, False)
                widget = self.toolbox.widget(i)
                widget.setHidden(True)

    def _setup(self):

        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)

        indexes_label = QLabel("Indexes")
        indexes_label.setStyleSheet("font-weight: bold")

        self.layout.addWidget(indexes_label)
        self.layout.addWidget(HorizontalLine())
        self.layout.addWidget(self.toolbox)

        for name, ikcw in self.index_kit_container_widgets.items():
            self.toolbox.addItem(ikcw, name)

        self.setLayout(self.layout)

    @staticmethod
    def _ikd_list(index_dir_root: Path, index_schema_path: Path) -> list:

        index_files = [f for f in index_dir_root.glob("*.json")]

        return [IndexKitObject(f, index_schema_path) for f in index_files]
