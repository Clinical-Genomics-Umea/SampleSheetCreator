from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QListView
from PySide6.QtCore import Qt, Signal


def toggle_checked(item):
    item.setCheckState(Qt.CheckState.Checked if item.checkState() == Qt.CheckState.Unchecked else Qt.CheckState.Unchecked)


class ColumnsWidget(QListView):
    itemChecked = Signal(str, bool)
    #
    # status_changed = Signal(dict)

    def __init__(self, parent=None):
        super(ColumnsWidget, self).__init__(parent)
        self.setAcceptDrops(False)
        self.setDragEnabled(False)
        self.setSelectionMode(QListView.ExtendedSelection)

        self.items = {}

        self.model = QStandardItemModel()
        self.setModel(self.model)

    def set_items(self, columns_status: dict):
        self.model.clear()
        for column, status in columns_status.items():
            self.items[column] = QStandardItem(column)
            self.items[column].setFlags(self.items[column].flags() | Qt.ItemIsUserCheckable)
            if status:
                self.items[column].setCheckState(Qt.CheckState.Checked)
            else:
                self.items[column].setCheckState(Qt.CheckState.Unchecked)

            self.model.appendRow(self.items[column])

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            selected_indexes = self.selectedIndexes()

            for index in selected_indexes:
                item = self.model.itemFromIndex(index)
                if item.checkState() == Qt.Checked:
                    item.setCheckState(Qt.Unchecked)
                else:
                    item.setCheckState(Qt.Checked)

                # Emit the itemChecked signal with the text and check state of the item
                self.itemChecked.emit(item.text(), item.checkState() == Qt.Checked)

        super().keyPressEvent(event)

    # def column_status_changed(self):
    #     item = self.sender()
    #     column_name = item.text()
    #     # self.status_changed.emit({column_name: item.checkState() == Qt.CheckState.Checked})

    # def update_item(self, column_status: dict):
    #     for column, status in column_status.items():
    #         if self.items[column].checkState() != status:
    #             toggle_checked(self.items[column])

