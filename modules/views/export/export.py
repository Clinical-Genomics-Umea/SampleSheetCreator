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

from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.sample.samplesheet_fns import to_json
from modules.models.state.state_model import StateModel
from modules.views.export.export_tree_widget import JsonTreeWidget

from modules.models.export.samplesheet_v2 import samplesheet_v2


class ExportWidget(QWidget):
    def __init__(
        self, state_model: StateModel, configuration_manager: ConfigurationManager, parent=None
    ):
        super().__init__(parent)

        self._state_model = state_model
        self._configuration_manager = configuration_manager

        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)

        self._tab_widget = QTabWidget()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._json_tree = None
        self._samplesheet = None

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        self._show_json_btn = QPushButton("View Data")
        self._export_json_btn = QPushButton("Export Json")
        self._export_samplesheet_v2_btn = QPushButton("Export SampleSheet V2")
        self._fastq_extract_cb = QComboBox()

        hbox.addWidget(self._show_json_btn)
        hbox.addWidget(self._fastq_extract_cb)
        hbox.addWidget(self._export_json_btn)
        hbox.addWidget(self._export_samplesheet_v2_btn)

        hbox.addStretch()

        self.layout.addLayout(hbox)
        self.layout.addWidget(self._tab_widget)
        self._show_json_btn.clicked.connect(self._show_data_tree)
        self._export_samplesheet_v2_btn.clicked.connect(self._export_samplesheet_v2)
        self._export_json_btn.clicked.connect(self._export_json)

        self._populate_fastq_extract_tool()

    def _populate_fastq_extract_tool(self):
        self._fastq_extract_cb.addItems(self._configuration_manager.fastq_extract_tool)

    def del_data_tree(self):
        if self._json_tree:
            self._json_tree.deleteLater()
            self._json_tree = None

    def _show_data_tree(self):
        if self._json_tree:
            self._json_tree.deleteLater()

        data = self._state_model.data_obj()

        self._json_tree = JsonTreeWidget(data)
        header = self._json_tree.header()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self._tab_widget.addTab(self._json_tree, "Data Structure")

    def _export_samplesheet_v2(self):

        fastq_extract_tool = self._fastq_extract_cb.currentText()

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

            data = self._state_model.data_obj()
            ss = samplesheet_v2(data, self._fastq_extract_cb.currentText())

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
            json_data = self._state_model.json_data()
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
            data = self._state_model.samplesheet_obj()
            json_str = to_json(data)
            f_obj.write_text(json_str)


class SampleSheetWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
