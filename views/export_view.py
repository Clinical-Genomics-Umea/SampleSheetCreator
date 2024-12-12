from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSizePolicy,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QTextEdit,
    QHBoxLayout,
    QPushButton,
    QHeaderView,
    QFileDialog,
)
from models.samplesheet import to_samplesheetv2, to_json


class ExportWidget(QWidget):
    def __init__(self, dataset_mgr, parent=None):
        super().__init__(parent)

        self.dataset_mgr = dataset_mgr

        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.json_tree = None
        self.samplesheet = None

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        self.show_json_btn = QPushButton("View Data")
        self.export_json_btn = QPushButton("Export Json")
        self.export_samplesheet_v2_btn = QPushButton("Export SampleSheet V2")

        hbox.addWidget(self.show_json_btn)
        hbox.addWidget(self.export_json_btn)
        hbox.addWidget(self.export_samplesheet_v2_btn)
        hbox.addStretch()

        self.layout.addLayout(hbox)
        self.layout.addWidget(self.tab_widget)
        self.show_json_btn.clicked.connect(self._show_data_tree)
        self.export_samplesheet_v2_btn.clicked.connect(self._export_samplesheet_v2)
        self.export_json_btn.clicked.connect(self._export_json)

    def del_data_tree(self):
        if self.json_tree:
            self.json_tree.deleteLater()
            self.json_tree = None

    def _show_data_tree(self):
        if self.json_tree:
            self.json_tree.deleteLater()

        data = self.dataset_mgr.samplesheet_obj_data()

        self.json_tree = JsonTreeWidget(data)
        header = self.json_tree.header()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tab_widget.addTab(self.json_tree, "Data Structure")

    def _export_samplesheet_v2(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "Save SampleSheet V2 File (csv)",
            "",
            "CSV Files (*.csv);;All Files (*)",
            options=options,
        )

        if file_path:
            f_obj = Path(file_path)

            data = self.dataset_mgr.samplesheet_v2()
            f_obj.write_text(data)

    def _export_json(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "Save JSON file (json)",
            "",
            "JSON Files (*.json);;All Files (*)",
            options=options,
        )

        if file_path:
            f_obj = Path(file_path)
            json_data = self.dataset_mgr.json_data()
            f_obj.write_text(json_data)

    def _export_samplesheet_v1(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "Save SampleSheet V1 file (json)",
            "",
            "SampleSheet Files (*.csv);;All Files (*)",
            options=options,
        )

        if file_path:
            f_obj = Path(file_path)
            data = self.dataset_mgr.samplesheet_obj()
            json_str = to_json(data)
            f_obj.write_text(json_str)


class JsonTreeWidget(QTreeWidget):
    def __init__(self, json_data, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(["Key", "Value"])
        self.setColumnCount(2)
        self.load_json(json_data)

    def load_json(self, json_data):
        """Populate the QTreeWidget with the JSON data."""
        self.clear()
        self._populate_tree(self, json_data)

    def _populate_tree(self, parent, json_data):
        """Recursive function to add JSON data to the tree."""
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                item = QTreeWidgetItem(parent, [key, ""])
                self._populate_tree(item, value)
        elif isinstance(json_data, list):
            for index, value in enumerate(json_data):
                item = QTreeWidgetItem(parent, [f"[{index}]", ""])
                self._populate_tree(item, value)
        else:
            # Primitive value, set as a leaf
            QTreeWidgetItem(parent, ["", str(json_data)])


class SampleSheetWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
