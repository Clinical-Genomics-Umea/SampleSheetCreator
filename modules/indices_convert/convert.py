from pathlib import Path

import pandas as pd
import csv

from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QFileDialog, QTableWidgetItem, QTableWidget, \
    QVBoxLayout, QLabel, QHBoxLayout, QHeaderView, QSpacerItem, QSizePolicy, QFormLayout, QLineEdit, QComboBox, \
    QGroupBox

from modules.indices_convert.ui.widget import Ui_Form
import qdarktheme
import sys


class IndexDefinitionConverter(QWidget, Ui_Form):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.stackedWidget.setCurrentWidget(self.csv_page_widget)
        self.csv_radioButton.setChecked(True)
        self.help_pushButton.setCheckable(True)

        self.table_widget_container = IndexTableContainer()
        self.tablewidget = self.table_widget_container.tablewidget

        self.csv_page_widget._layout().addWidget(self.table_widget_container)

        self.csv_radioButton.toggled.connect(self.change_view)
        self.csv_radioButton.toggled.connect(self.change_view)
        self.help_pushButton.clicked.connect(self.toggle_help)
        self.load_pushButton.clicked.connect(self.load_data)

    def toggle_help(self):
        if self.help_pushButton.isChecked():
            self.stackedWidget.setCurrentWidget(self.help_widget)
        else:
            if self.csv_radioButton.isChecked():
                self.stackedWidget.setCurrentWidget(self.csv_page_widget)
            if self.ilmn_radioButton.isChecked():
                self.stackedWidget.setCurrentWidget(self.ilmn_page_widget)

    def change_view(self):
        if self.help_pushButton.isChecked():
            return

        if self.csv_radioButton.isChecked():
            self.stackedWidget.setCurrentWidget(self.csv_page_widget)
        if self.ilmn_radioButton.isChecked():
            self.stackedWidget.setCurrentWidget(self.ilmn_page_widget)

    def load_data(self):
        file = self.open_file_dialog()
        self.load_csv(file)

    @staticmethod
    def get_delimiter(file_path, bytes=4096):
        sniffer = csv.Sniffer()
        data = open(file_path, "r").read(bytes)
        delimiter = sniffer.sniff(data).delimiter
        return delimiter

    def dataframe_to_qtablewidget(self, df):
        self.tablewidget.setRowCount(df.shape[0])
        self.tablewidget.setColumnCount(df.shape[1])
        self.tablewidget.setHorizontalHeaderLabels(df.columns)

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                self.tablewidget.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))

    def convert(self):
        pass

    def open_file_dialog(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        if self.ilmn_radioButton.isChecked():
            file_dialog.setNameFilter("ILMN Index TSV files (*.tsv)")
        elif self.csv_radioButton.isChecked():
            file_dialog.setNameFilter("Index CSV files (*.csv)")

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            return Path(file_path)

    def load_csv(self, file_path):
        df = pd.read_csv(file_path)
        self.dataframe_to_qtablewidget(df)

    def load_ikd_tsv(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        self.plainTextEdit.setPlainText(content)


class IndexKitSettings(QGroupBox):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()
        self.setTitle("Index Kit Settings")
        self.setFixedWidth(400)

        self.widgets = {
            "name": QLineEdit(),
            "display_name": QLineEdit(),
            'version': QLineEdit(),
            'description': QLineEdit(),
            'index_strategy': QComboBox()
        }

        self.widgets['index_strategy'].addItems(['dual', 'single'])

        layout.addRow("Name", self.widgets['name'])
        layout.addRow("Display Name", self.widgets['display_name'])
        layout.addRow("Version", self.widgets['version'])
        layout.addRow("Description", self.widgets['description'])
        layout.addRow("Index Strategy", self.widgets['index_strategy'])

        self.setLayout(layout)

    def get_settings(self):
        data = dict()
        for key, widget in self.widgets.items():
            if isinstance(widget, QLineEdit):
                data[key] = widget.text()
            elif isinstance(widget, QComboBox):
                data[key] = widget.currentText()

        return data


class ResourcesSettings(QGroupBox):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()
        self.setTitle("Resources Settings")
        self.setFixedWidth(400)

        self.widgets = {
            "adapter_read1": QLineEdit(),
            "adapter_read2": QLineEdit(),
            'layout': QComboBox(),
            'override_cycles_pattern_r1': QLineEdit(),
            'override_cycles_pattern_i1': QLineEdit(),
            'override_cycles_pattern_i2': QLineEdit(),
            'override_cycles_pattern_r2': QLineEdit(),
        }

        self.widgets['layout'].addItems(['fixed layout', 'standard layout'])

        override_layout = QHBoxLayout()
        override_layout.setContentsMargins(0, 0, 0, 0)
        override_layout.addWidget(self.widgets['override_cycles_pattern_r1'])
        override_layout.addWidget(self.widgets['override_cycles_pattern_i1'])
        override_layout.addWidget(self.widgets['override_cycles_pattern_i2'])
        override_layout.addWidget(self.widgets['override_cycles_pattern_r2'])

        override_widget = QWidget()

        override_widget.setLayout(override_layout)

        layout.addRow("Adapter Read1", self.widgets['adapter_read1'])
        layout.addRow("Adapter Read2", self.widgets['adapter_read2'])
        layout.addRow("Fixed Layout", self.widgets['layout'])
        layout.addRow("Override Cycles Pattern", override_widget)

        self.setLayout(layout)

    def get_settings(self):
        data = dict()
        for key, widget in self.widgets.items():
            if isinstance(widget, QLineEdit):
                data[key] = widget.text()
            elif isinstance(widget, QComboBox):
                data[key] = widget.currentText()

        return data


class IndexTableContainer(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.tablewidget = DroppableTableWidget(0, 0)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.draggable_labels_layout = QHBoxLayout()

        self.resources_settings = ResourcesSettings()
        self.index_kit_settings = IndexKitSettings()

        self.input_settings_layout = QHBoxLayout()

        self.input_settings_layout.addWidget(self.index_kit_settings)
        self.input_settings_layout.addWidget(self.resources_settings)
        self.input_settings_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.layout.addLayout(self.input_settings_layout)

        labels = [
            'not_used',
            'fixed_pos',
            'index_name',
            'index_i7_name',
            'index_i5_name',
            'index_i7',
            'index_i5',
        ]

        for label in labels:
            self.draggable_labels_layout.addWidget(DraggableLabel(label))

        self.draggable_labels_layout.addSpacerItem(QSpacerItem(40, 20,
                                                               QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.layout.addLayout(self.draggable_labels_layout)
        self.layout.addWidget(self.tablewidget)


class DraggableLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QLabel {
                border: 1px solid lightgrey;
                text-align: center;
            }
        """)
        self.setFixedWidth(100)
        self.setFixedHeight(30)
        self.setAlignment(Qt.AlignCenter)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(self.text())
            drag.setMimeData(mime_data)
            drag.exec(Qt.MoveAction)


class DroppableHeader(QHeaderView):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()


    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            index = self.logicalIndexAt(event.position().toPoint())
            self.model().setHeaderData(index, Qt.Horizontal, event.mimeData().text())
            event.acceptProposedAction()

class DroppableTableWidget(QTableWidget):
    def __init__(self, rows, columns, parent=None):
        super().__init__(rows, columns, parent)
        self.setHorizontalHeader(DroppableHeader(Qt.Horizontal, self))


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Index Definition Converter")
        convert_widget = IndexDefinitionConverter()

        # Set the central widget of the Window.
        self.setCentralWidget(convert_widget)


def main():
    app = QApplication(sys.argv)
    qdarktheme.setup_theme("light")
    window = MainWindow()
    window.setMinimumSize(600, 600)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

