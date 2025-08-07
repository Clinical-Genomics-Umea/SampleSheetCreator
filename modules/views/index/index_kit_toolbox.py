from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBox, QLabel

from modules.models.indexes.index_kit_manager import IndexKitManager
from modules.views.ui_components import HorizontalLine


class IndexKitToolbox(QWidget):
    def __init__(self, index_kit_manager: IndexKitManager):
        super().__init__()

        self._index_kit_manager = index_kit_manager

        self._layout = QVBoxLayout()
        self._toolbox = QToolBox()

        self._index_kit_manager.index_kits_changed.connect(self.set_index_kits)

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
        index_kit_widgets = self._index_kit_manager.index_kit_widgets
        
        print("index_kit_widgets:", index_kit_widgets)
        
        if not index_kit_widgets:
            empty_widget = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(QLabel("No index kits match the criteria in run info"))
            empty_widget.setLayout(layout)
            self._toolbox.addItem(empty_widget, "No index kits available")

        else:
            for index_kit_widget in index_kit_widgets:
                if index_kit_widget is not None and hasattr(index_kit_widget, 'name'):
                    print(f"Adding index kit widget: {index_kit_widget.name}")
                    # Create a container widget to hold the index kit widget
                    container = QWidget()
                    layout = QVBoxLayout()
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.addWidget(index_kit_widget)
                    container.setLayout(layout)
                    
                    # Add the container to the toolbox
                    self._toolbox.addItem(container, index_kit_widget.name)
                else:
                    print(f"Skipping invalid index kit widget: {index_kit_widget}")


    def _clear_toolbox_index_kits(self) -> None:
        """Clear all items from the toolbox."""
        for i in reversed(range(self._toolbox.count())):
            widget = self._toolbox.widget(i)
            self._toolbox.removeItem(i)
            widget.deleteLater()

