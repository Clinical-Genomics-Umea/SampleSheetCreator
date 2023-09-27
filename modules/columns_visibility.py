from PySide6.QtGui import QStandardItemModel, QStandardItem, QKeyEvent
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QListView, QTreeWidget, QTreeView, QTreeWidgetItem
from PySide6.QtCore import Qt, Signal, Slot


def toggle_checked(item):
    item.setCheckState(0, Qt.Checked if item.checkState(0) == Qt.Unchecked else Qt.Unchecked)


def has_checked_item(lst):
    return Qt.Checked in lst


class ColumnsTreeWidget(QTreeWidget):
    field_visibility_state_changed = Signal(str, bool)

    def __init__(self, section_fields, parent=None):
        super(ColumnsTreeWidget, self).__init__(parent)
        self.setAcceptDrops(False)
        self.setDragEnabled(False)
        self.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.setStyleSheet("QTreeView { border: 0px; }")
        # self.setSpacing(2)

        self.field_index_mapping = {}

        self.field_item_map = {}

        self.create_tree(section_fields)
        self.setHeaderHidden(True)
        self.expandAll()

        # self.itemChanged.connect(self.emit_field_checked_state)

    def create_tree(self, section_fields: dict):
        top_level_items = []
        for section, field_list in section_fields.items():
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

        self.itemChanged.connect(self.on_item_changed)

    @Slot(QTreeWidgetItem, int)
    def on_item_changed(self, item, state):

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
                    self.field_visibility_state_changed.emit(child.text(0), state == Qt.Checked)
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

    def set_items(self, section_fields: dict, fields_visibility_state: dict):
        self.clear()

        # for section in section_fields:
        #     item = QListWidgetItem(section)
        #     self.addItem(item)
        #
        #     for fields in section_fields[section]:
        #         item = QListWidgetItem(fields)
        #         item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        #         self.addItem(item)


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
            print(selected_items)
            for item in selected_items:
                if item.childCount() == 0:
                    toggle_checked(item)

                item.setSelected(False)


