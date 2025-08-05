from pathlib import Path

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBox, QLabel

from modules.models.indexes.index_kit_manager import IndexKitManager
from modules.models.indexes.index_kit_model import IndexKitModel
from modules.views.drawer_tools.index.index_kit_widget import IndexKitWidget
from modules.views.ui_components import HorizontalLine


class IndexKitToolbox(QWidget):
    def __init__(self, index_kit_manager: IndexKitManager):
        super().__init__()

        self._index_kit_manager = index_kit_manager

        self._layout = QVBoxLayout()
        self._toolbox = QToolBox()

        self._layout.setSpacing(5)
        self._layout.setContentsMargins(0, 0, 0, 0)

        indexes_label = QLabel("Indexes")
        indexes_label.setStyleSheet("font-weight: bold")

        self._layout.addWidget(indexes_label)
        self._layout.addWidget(HorizontalLine())
        self._layout.addWidget(self._toolbox)
        self.setLayout(self._layout)

    def set_index_kits(self):

        self._clear_toolbox_index_kits()
        print("set_index_kits")

        index_kit_widgets = self._index_kit_manager.index_kit_widgets

        for index_kit_widget in index_kit_widgets:
            self._toolbox.addItem(index_kit_widget, index_kit_widget.name)


    def _clear_toolbox_index_kits(self) -> None:
        """Clear all items from the toolbox."""
        while self._toolbox.count() > 0:
            # Remove the widget from the toolbox
            widget = self._toolbox.widget(0)
            self._toolbox.removeItem(0)
            # Delete the widget to free memory
            if widget:
                widget.setParent(None)
                widget.deleteLater()

