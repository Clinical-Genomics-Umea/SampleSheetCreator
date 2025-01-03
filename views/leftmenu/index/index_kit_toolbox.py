from pathlib import Path

from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBox, QLabel

from models.indexes.index_kit_manager import IndexKitManager
from models.indexes.index_kit_object import IndexKitObject
from views.leftmenu.index.index_kit_container_widget import IndexKitContainerWidget
from views.ui_components import HorizontalLine


class IndexKitToolbox(QWidget):
    def __init__(self, index_kit_manager: IndexKitManager):
        super().__init__()

        self.index_kit_container_widgets = {
            index_kit_object.name: IndexKitContainerWidget(index_kit_object)
            for index_kit_object in index_kit_manager.index_kit_objects
        }

        self.layout = QVBoxLayout()
        self.toolbox = QToolBox()

        self._setup()

    def _setup(self):

        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)

        indexes_label = QLabel("Indexes")
        indexes_label.setStyleSheet("font-weight: bold")

        self.layout.addWidget(indexes_label)
        self.layout.addWidget(HorizontalLine())
        self.layout.addWidget(self.toolbox)

        for name, ikdw in self.index_kit_container_widgets.items():
            self.toolbox.addItem(ikdw, name)

        self.setLayout(self.layout)

    @staticmethod
    def _ikd_list(index_dir_root: Path, index_schema_path: Path) -> list:

        index_files = [f for f in index_dir_root.glob("*.json")]

        return [IndexKitObject(f, index_schema_path) for f in index_files]
