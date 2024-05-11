from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QApplication, QTableView, QVBoxLayout, QWidget, QPushButton, QHeaderView, QAbstractItemView
from PySide6.QtCore import Qt, Signal, QRect, QSize, QItemSelectionModel


class CustomHeaderView(QHeaderView):
    buttonClicked = Signal(int, bool)  # Signal to emit when a button is clicked

    def __init__(self, parent=None):
        super().__init__(Qt.Vertical, parent)
        self.setSectionsClickable(True)
        self.setSectionResizeMode(QHeaderView.Fixed)
        self.setDefaultSectionSize(30)  # Increase the default section size to make it wider
        self.setMinimumSectionSize(30)  # Ensure minimum section size
        self.setFixedWidth(100)  # Set the width of the vertical header

        self.buttons = {}

    def paintSection(self, painter, rect, logicalIndex):
        # We're not painting buttons manually anymore
        pass

    def add_button(self, logicalIndex):
        button = QPushButton(f"Button {logicalIndex}", self)
        button.setCheckable(True)
        button.clicked.connect(lambda checked, index=logicalIndex: self.buttonClicked.emit(index, checked))
        self.buttons[logicalIndex] = button


    def mousePressEvent(self, event):
        for logicalIndex, button in self.buttons.items():
            if button.geometry().contains(event.pos()):
                button.click()
                break
        super().mousePressEvent(event)

class TableViewWithButtons(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.tableview = QTableView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Column 1', 'Column 2', 'Column 3'])  # Example headers

        # Populate the model with data
        for i in range(5):
            row = [QStandardItem(f"Item {i},{j}") for j in range(3)]
            self.model.appendRow(row)

        self.tableview.setModel(self.model)
        self.tableview.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Disable editing

        # Set custom header for vertical header
        self.header = CustomHeaderView()
        self.tableview.setVerticalHeader(self.header)

        # Add buttons to the header
        for i in range(self.model.rowCount()):
            self.header.add_button(i)

        self.layout.addWidget(self.tableview)
        self.setLayout(self.layout)

    def handleButtonClicked(self, index, checked):
        print(f"Button {index} clicked, checked: {checked}")

        # Select the corresponding row when the button is checked
        if checked:
            selectionModel = self.tableview.selectionModel()
            selectionModel.clear()
            selectionModel.select(self.model.index(index, 0), QItemSelectionModel.Select | QItemSelectionModel.Rows)

if __name__ == "__main__":
    app = QApplication([])
    window = TableViewWithButtons()
    window.setGeometry(100, 100, 600, 400)
    window.show()
    app.exec()
