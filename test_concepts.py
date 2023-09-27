from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem

app = QApplication([])

# Create a QTreeWidget
tree_widget = QTreeWidget()
tree_widget.setHeaderLabels(["Items"])

# Set the check state of child items to match the check state of the top-level item
def setChildItemCheckState(item, state):
    for i in range(item.childCount()):
        child = item.child(i)
        child.setCheckState(0, state)
        tree_widget.model().emitDataChanged(QModelIndex(), QModelIndex())

# Create the top-level items
top_item1 = QTreeWidgetItem(tree_widget)
top_item1.setText(0, "Top Item 1")
top_item1.setFlags(top_item1.flags() | Qt.ItemIsUserCheckable)
top_item1.setCheckState(0, Qt.Unchecked)

top_item2 = QTreeWidgetItem(tree_widget)
top_item2.setText(0, "Top Item 2")
top_item2.setFlags(top_item2.flags() | Qt.ItemIsUserCheckable)
top_item2.setCheckState(0, Qt.Unchecked)

# Create the child items under top-level item 1
child_item11 = QTreeWidgetItem(top_item1)
child_item11.setText(0, "Child Item 1-1")
child_item11.setFlags(child_item11.flags() | Qt.ItemIsUserCheckable)
child_item11.setCheckState(0, Qt.Unchecked)

child_item12 = QTreeWidgetItem(top_item1)
child_item12.setText(0, "Child Item 1-2")
child_item12.setFlags(child_item12.flags() | Qt.ItemIsUserCheckable)
child_item12.setCheckState(0, Qt.Unchecked)

child_item13 = QTreeWidgetItem(top_item1)
child_item13.setText(0, "Child Item 1-3")
child_item13.setFlags(child_item13.flags() | Qt.ItemIsUserCheckable)
child_item13.setCheckState(0, Qt.Unchecked)

# Create the child items under top-level item 2
child_item21 = QTreeWidgetItem(top_item2)
child_item21.setText(0, "Child Item 2-1")
child_item21.setFlags(child_item21.flags() | Qt.ItemIsUserCheckable)
child_item21.setCheckState(0, Qt.Unchecked)

child_item22 = QTreeWidgetItem(top_item2)
child_item22.setText(0, "Child Item 2-2")
child_item22.setFlags(child_item22.flags() | Qt.ItemIsUserCheckable)
child_item22.setCheckState(0, Qt.Unchecked)

child_item23 = QTreeWidgetItem(top_item2)
child_item23.setText(0, "Child Item 2-3")
child_item23.setFlags(child_item23.flags() | Qt.ItemIsUserCheckable)
child_item23.setCheckState(0, Qt.Unchecked)

# Connect the check state change signal of the top-level items to update the child items
top_item1.stateChanged.connect(lambda state: setChildItemCheckState(top_item1, state))
top_item2.stateChanged.connect(lambda state: setChildItemCheckState(top_item2, state))

tree_widget.show()
app.exec()