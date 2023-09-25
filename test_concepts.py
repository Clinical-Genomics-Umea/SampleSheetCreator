from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QApplication, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

class CheckableListWidget(QListWidget):
    itemChecked = Signal(str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set the selection mode to ExtendedSelection
        self.setSelectionMode(QListWidget.ExtendedSelection)

    # def addCustomItems(self, item):
    #     # Create a QListWidgetItem with a checkable flag
    #     list_item = QListWidgetItem(item)
    #     list_item.setFlags(list_item.flags() | Qt.ItemIsUserCheckable)
    #     list_item.setCheckState(Qt.Checked)
    #     super().addItem(list_item)

    def toggleSelectedItems(self):
        selected_items = self.selectedItems()

        print(selected_items)

        # Toggle the check state of the selected items
        for item in selected_items:
            if item.checkState() == Qt.Checked:
                item.setCheckState(Qt.Unchecked)
            else:
                item.setCheckState(Qt.Checked)

            # Emit the itemChecked signal with the text and check state of the item
            self.itemChecked.emit(item.text(), item.checkState() == Qt.Checked)

    def toggleAllItems(self):
        for item in self.items():
            if item.checkState() == Qt.Unchecked:
                item.setCheckState(Qt.Checked)

    def addCustomItems(self):
        self.addItem("Item 1")
        self.addItem("Item 2")
        self.addItem("Item 3")


app = QApplication([])
window = QWidget()

layout = QVBoxLayout()
list_widget = CheckableListWidget()

# Connect the itemChecked signal to a slot
def handle_item_checked(item, checked):
    print(f"Item '{item}' checked: {checked}")

list_widget.itemChecked.connect(handle_item_checked)

# Add items to the list widget
list_widget.addCustomItems()

for item in list_widget.items():
    item.setCheckState(Qt.Unchecked)

list_widget.toggleAllItems()


layout.addWidget(list_widget)
window.setLayout(layout)

window.show()

# Toggle the check state of the selected items
list_widget.toggleSelectedItems()

app.exec()