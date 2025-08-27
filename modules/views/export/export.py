from pathlib import Path

from PySide6.QtCore import Signal
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
from modules.models.state.state_model import StateModel


class ExportWidget(QWidget):

    samplesheet_v2_export_path_ready = Signal(object)
    json_export_path_ready = Signal(object)

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

        self._samplesheet_v2_textedit = QTextEdit()
        self._json_textedit = QTextEdit()

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        self.generate_btn = QPushButton("Generate")
        self._samplesheet_v2_export_btn = QPushButton("Export SampleSheet V2")
        self._json_export_btn = QPushButton("Export JSON")
        self._package_export_btn = QPushButton("Export SampleSheet V2 JSON package (zip)")


        # hbox.addWidget(self._fastq_extract_cb)
        hbox.addWidget(self.generate_btn)
        hbox.addWidget(self._samplesheet_v2_export_btn)
        hbox.addWidget(self._json_export_btn)
        hbox.addWidget(self._package_export_btn)
        hbox.addStretch()

        self.layout.addLayout(hbox)
        self.layout.addWidget(self._tab_widget)

        samplesheet_v2_layout = QVBoxLayout()
        samplesheet_v2_layout.addWidget(self._samplesheet_v2_export_btn)
        samplesheet_v2_layout.addWidget(self._samplesheet_v2_textedit)

        samplesheet_v2_tab = QWidget()
        samplesheet_v2_tab.setLayout(samplesheet_v2_layout)
        self._tab_widget.addTab(samplesheet_v2_tab, "SampleSheet V2")

        json_tree_layout = QVBoxLayout()
        json_tree_layout.addWidget(self._json_export_btn)
        json_tree_layout.addWidget(self._json_textedit)

        json_tree_tab = QWidget()
        json_tree_tab.setLayout(json_tree_layout)
        self._tab_widget.addTab(json_tree_tab, "JSON Data Structure")

        self._samplesheet_v2_export_btn.clicked.connect(self._export_samplesheet_v2)
        self._json_export_btn.clicked.connect(self._export_json)

    def populate_samplesheet_v2_text(self):

        text = self._state_model.samplesheet_v2

        self._samplesheet_v2_textedit.setText(text)

    def populate_json_text(self, text):
        self._json_textedit.setText(text)

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
            self.samplesheet_v2_export_path_ready.emit(Path(file_path))

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
            if file_path:
                self.json_export_path_ready.emit(Path(file_path))

