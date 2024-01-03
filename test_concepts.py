from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QApplication, QStyledItemDelegate, QTableView, QVBoxLayout, QWidget, QLineEdit, QSpinBox
from PySide6.QtCore import Qt


class OddRowDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        # Create a custom editor for even rows (e.g., QSpinBox)
        editor = QSpinBox(parent)
        return editor

    def setEditorData(self, editor, index):
        # Set data in the editor for even rows
        value = index.data(Qt.DisplayRole)
        editor.setValue(int(value))


class EvenRowDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        # Create a custom editor for even rows (e.g., QSpinBox)
        editor = QSpinBox(parent)
        return editor

    def setEditorData(self, editor, index):
        # Set data in the editor for even rows
        value = index.data(Qt.DisplayRole)
        editor.setValue(int(value))


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        table_model = QStandardItemModel(self)
        table_model.setColumnCount(3)
        table_model.setRowCount(5)

        for row in range(5):
            for col in range(3):
                item = QStandardItem(f"Value {row * 3 + col}")
                table_model.setItem(row, col, item)

        table_view = QTableView(self)
        table_view.setModel(table_model)

        # Set different delegates for odd and even rows
        odd_delegate = OddRowDelegate()
        even_delegate = EvenRowDelegate()

        for row in range(table_model.rowCount()):
            if row % 2 == 0:
                table_view.setItemDelegateForRow(row, even_delegate)
            else:
                table_view.setItemDelegateForRow(row, odd_delegate)

        layout = QVBoxLayout(self)
        layout.addWidget(table_view)

        self.setLayout(layout)
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle('QTableView with Different Delegates for Rows')
        self.show()


if __name__ == '__main__':
    app = QApplication([])
    mainWin = MainWindow()
    app.exec()

