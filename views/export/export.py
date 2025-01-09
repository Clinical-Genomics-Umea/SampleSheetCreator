from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSizePolicy,
    QTabWidget,
    QTextEdit,
    QHBoxLayout,
    QPushButton,
    QHeaderView,
    QFileDialog,
    QComboBox,
)

from models.configuration.configuration_manager import ConfigurationManager
from models.dataset.dataset_manager import DataSetManager
from models.sample.samplesheet_fns import to_json
from views.export.export_tree_widget import JsonTreeWidget

from models.export.samplesheet_v2 import samplesheet_v2
from models.export.samplesheet_v1 import samplesheet_v1


class ExportWidget(QWidget):
    def __init__(
        self, dataset_mgr: DataSetManager, cfg_mgr: ConfigurationManager, parent=None
    ):
        super().__init__(parent)

        self.dataset_mgr = dataset_mgr
        self.cfg_mgr = cfg_mgr

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
        self.fastq_extract_cb = QComboBox()

        hbox.addWidget(self.show_json_btn)
        hbox.addWidget(self.fastq_extract_cb)
        hbox.addWidget(self.export_json_btn)
        hbox.addWidget(self.export_samplesheet_v2_btn)

        hbox.addStretch()

        self.layout.addLayout(hbox)
        self.layout.addWidget(self.tab_widget)
        self.show_json_btn.clicked.connect(self._show_data_tree)
        self.export_samplesheet_v2_btn.clicked.connect(self._export_samplesheet_v2)
        self.export_json_btn.clicked.connect(self._export_json)

        self._populate_fastq_extract_tool()

    def _populate_fastq_extract_tool(self):
        self.fastq_extract_cb.addItems(self.cfg_mgr.fastq_extract_tool)

    def del_data_tree(self):
        if self.json_tree:
            self.json_tree.deleteLater()
            self.json_tree = None

    def _show_data_tree(self):
        if self.json_tree:
            self.json_tree.deleteLater()

        data = self.dataset_mgr.data_obj()

        self.json_tree = JsonTreeWidget(data)
        header = self.json_tree.header()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tab_widget.addTab(self.json_tree, "Data Structure")

    def _export_samplesheet_v2(self):

        fastq_extract_tool = self.fastq_extract_cb.currentText()

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

            data = self.dataset_mgr.data_obj()
            ss = samplesheet_v2(data, self.fastq_extract_cb.currentText())

            f_obj.write_text(ss)

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


class SampleSheetWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
