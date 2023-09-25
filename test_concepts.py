from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QApplication, QListWidget, QListWidgetItem, QVBoxLayout, QWidget, QPushButton


class CheckableListWidget(QListWidget):
    itemChecked = Signal(str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set the selection mode to ExtendedSelection
        self.setSelectionMode(QListWidget.ExtendedSelection)

        self.item_dict = {}

    def addItem(self, item_name):
        # Create a QListWidgetItem with a checkable flag
        list_item = QListWidgetItem(item_name)
        list_item.setFlags(list_item.flags() | Qt.ItemIsUserCheckable)
        list_item.setCheckState(Qt.Unchecked)
        super().addItem(list_item)
        self.item_dict[item_name] = list_item

    # def toggleSelectedItems(self):
    #     selected_items = self.selectedItems()
    #
    #     print(selected_items)
    #
    #     # Toggle the check state of the selected items
    #     for item in selected_items:
    #         if item.checkState() == Qt.Checked:
    #             item.setCheckState(Qt.Unchecked)
    #         else:
    #             item.setCheckState(Qt.Checked)
    #
    #         # Emit the itemChecked signal with the text and check state of the item
    #         self.itemChecked.emit(item.text(), item.checkState() == Qt.Checked)

    def toggleAllItems(self):
        for key, list_item in self.item_dict.items():
            if list_item.checkState() == Qt.Unchecked:
                list_item.setCheckState(Qt.Checked)
            else:
                list_item.setCheckState(Qt.Unchecked)

    def addCustomItems(self):
        self.addItem("Item 1")
        self.addItem("Item 2")
        self.addItem("Item 3")


app = QApplication([])
window = QWidget()

layout = QVBoxLayout()
button = QPushButton("Toggle")
list_widget = CheckableListWidget()

# Connect the itemChecked signal to a slot

def handle_item_checked(item, checked):
    print(f"Item '{item}' checked: {checked}")


list_widget.addCustomItems()
list_widget.toggleAllItems()

layout.addWidget(list_widget)
window.setLayout(layout)

window.show()

# Toggle the check state of the selected items

app.exec()