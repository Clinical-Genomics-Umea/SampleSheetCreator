from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, Signal, Slot


def toggle_checked(item):
    item.setCheckState(
        0, Qt.Checked if item.checkState(0) == Qt.Unchecked else Qt.Unchecked
    )


def has_checked_item(lst):
    return Qt.Checked in lst


class ColumnVisibilityWidget(QWidget):
    def __init__(self, samples_settings: dict, parent=None):
        super(ColumnVisibilityWidget, self).__init__(parent)
        self.column_visibility_control = ColumnVisibilityControl(samples_settings)
        layout = QVBoxLayout(self)
        layout.addWidget(self.column_visibility_control)
        self.setLayout(layout)
        self.setFixedWidth(250)


class ColumnVisibilityControl(QTreeWidget):
    field_visibility_state_changed = Signal(str, bool)

    def __init__(self, samples_settings: dict, parent=None):
        super(ColumnVisibilityControl, self).__init__(parent)
        self.setAcceptDrops(False)
        self.setDragEnabled(False)
        self.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.setStyleSheet("QTreeView { border: 0px; }")

        self.field_item_map = {}

        self._create_tree(samples_settings)
        self.setHeaderHidden(True)
        self.expandAll()

    def _create_tree(self, samples_settings: dict):

        all_fields = samples_settings["fields"]

        top_level_items = []
        for section, field_list in all_fields.items():
            section_item = QTreeWidgetItem(self, [section])
            section_item.setFlags(section_item.flags() | Qt.ItemIsUserCheckable)
            section_item.setCheckState(0, Qt.Checked)
            for field in field_list:

                field_item = QTreeWidgetItem(section_item, [field])
                field_item.setFlags(field_item.flags() | Qt.ItemIsUserCheckable)
                field_item.setCheckState(0, Qt.Checked)
                self.field_item_map[field] = field_item
                section_item.addChild(field_item)

        self.insertTopLevelItems(0, top_level_items)

        self.itemChanged.connect(self._on_item_changed)

    @Slot(QTreeWidgetItem, int)
    def _on_item_changed(self, item: QTreeWidgetItem) -> None:
        """
        Slot function connected to the `itemChanged` signal of the QTreeWidget.
        When a check box in the tree is changed, this function is called with the
        changed item and the column number (which is always 0 in this case).
        The function emits the `field_visibility_state_changed` signal with the
        field name and the new state of the check box.

        If the changed item is a top-level item, it sets the check state of all
        its children to the same state. If the changed item is a child item, it
        sets the check state of its parent item to `Qt.Checked` if any of its
        children are checked, and to `Qt.Unchecked` if none of them are checked.
        """
        state = item.checkState(0)

        if item.childCount() == 0:
            self.field_visibility_state_changed.emit(item.text(0), state == Qt.Checked)

        self.blockSignals(True)

        if item.childCount() > 0:
            for i in range(item.childCount()):
                child = item.child(i)
                child_state = child.checkState(0)
                if state != child_state:
                    child.setCheckState(0, state)

                    self.blockSignals(False)
                    self.field_visibility_state_changed.emit(
                        child.text(0), state == Qt.Checked
                    )
                    self.blockSignals(True)

        else:
            parent_item = item.parent()
            child_states = []
            for i in range(parent_item.childCount()):
                child_item = parent_item.child(i)
                child_state = child_item.checkState(0)
                child_states.append(child_state)

            if has_checked_item(child_states):
                parent_item.setCheckState(0, Qt.Checked)

            else:
                parent_item.setCheckState(0, Qt.Unchecked)

        self.blockSignals(False)

    # def emit_field_checked_state(self, item):
    #     self.field_visibility_state_changed.emit(item.text(), item.checkState() == Qt.CheckState.Checked)

    @Slot(str, bool)
    def set_column_visibility_state(self, field_name, state):
        item = self.field_item_map[field_name]
        item_state = item.checkState(0) == Qt.CheckState.Checked

        if item_state == state:
            return

        toggle_checked(item)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Space:
            selected_items = self.selectedItems()
            for item in selected_items:
                if item.childCount() == 0:
                    toggle_checked(item)

                item.setSelected(False)
