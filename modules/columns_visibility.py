from PySide6.QtGui import QStandardItemModel, QStandardItem, QKeyEvent
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QListView
from PySide6.QtCore import Qt, Signal, Slot


def toggle_checked(item):
    item.setCheckState(Qt.CheckState.Checked if item.checkState() == Qt.CheckState.Unchecked else Qt.CheckState.Unchecked)


class ColumnsWidget(QListWidget):
    field_visibility_state_changed = Signal(str, bool)

    def __init__(self, parent=None):
        super(ColumnsWidget, self).__init__(parent)
        self.setAcceptDrops(False)
        self.setDragEnabled(False)
        self.setSelectionMode(QListView.ExtendedSelection)
        self.setStyleSheet("QListView { border: 0px; }")
        self.setSpacing(2)

        self.field_index_mapping = {}

        self.itemChanged.connect(self.emit_field_checked_state)

    def set_items(self, fields_visibility_state: dict):
        self.clear()

        for field_name, state in fields_visibility_state.items():
            item = QListWidgetItem(field_name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            if state:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)

            self.addItem(item)

        for index in range(self.count()):
            item = self.item(index)
            self.field_index_mapping[item.text()] = index

    def emit_field_checked_state(self, item):
        self.field_visibility_state_changed.emit(item.text(), item.checkState() == Qt.CheckState.Checked)

    def set_field_state(self, field_state: dict):
        for field, state in field_state.items():
            index = self.field_index_mapping[field]
            item = self.item(index)
            item.setCheckState(Qt.CheckState.Checked if state else Qt.CheckState.Unchecked)

    @Slot(str, bool)
    def set_column_visibility_state(self, field_name, state):
        index = self.field_index_mapping[field_name]
        item = self.item(index)
        item_state = item.checkState() == Qt.CheckState.Checked

        if item_state == state:
            return

        toggle_checked(item)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Space:

            selected_items = self.selectedItems()
            for item in selected_items:
                toggle_checked(item)
                item.setSelected(False)


