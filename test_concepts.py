import sys
import pandas as pd
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem


def calculate_mismatches(str1, str2):
    return sum(c1 != c2 for c1, c2 in zip(str1, str2))


def color_cell_based_on_mismatches(table_widget, row, col, data):
    cell_value = data.iloc[row, col]
    num_mismatches = calculate_mismatches(cell_value, data.columns[row])
    color_intensity = min(255, 255 - (num_mismatches * 30))  # Adjust color intensity

    color = QColor(color_intensity, color_intensity, 255)  # Blueish color
    brush = cell_value_background_color(cell_value, color)
    item = QTableWidgetItem(cell_value)
    item.setBackground(brush)
    table_widget.setItem(row, col, item)


def cell_value_background_color(cell_value, default_color):
    # You can add more conditions or customize colors as needed
    if "a" in cell_value:
        return QColor(255, 128, 128)  # Red for cells containing "a"
    else:
        return default_color


class HeatmapTable(QTableWidget):
    def __init__(self, data):
        super().__init__(len(data), len(data.columns))
        self.data = data
        self.initUI()

    def initUI(self):
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                color_cell_based_on_mismatches(self, row, col, self.data)
                self.setItem(row, col, QTableWidgetItem(self.data.iloc[row, col]))

        self.setHorizontalHeaderLabels(self.data.columns)
        self.setVerticalHeaderLabels(self.data.index)
        self.horizontalHeader().setSectionResizeMode(QTableWidget.Stretch)
        self.verticalHeader().setSectionResizeMode(QTableWidget.Stretch)


class MainWindow(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle('Heatmap in QTableWidget')
        self.setGeometry(100, 100, 800, 600)
        self.heatmap_table = HeatmapTable(data)
        self.setCentralWidget(self.heatmap_table)

def main():
    app = QApplication(sys.argv)
    data = pd.DataFrame({
        'abc': ['abcdef', 'abcdeg', 'abcdeg', 'abcdff', 'abcefg'],
        'xyz': ['xyz123', 'xya123', 'xzz123', 'xyz124', 'xyy123']
    })

    window = MainWindow(data)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()