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
from modules.views.export.json_highlighter import JsonHighlighter
from modules.views.export.samplesheet_v2_highlighter import IlluminaSamplesheetV2Highlighter


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
        self._samplesheet_v2_textedit.setReadOnly(True)
        self._json_textedit = QTextEdit()
        self._json_textedit.setReadOnly(True)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        self.generate_btn = QPushButton("Generate")

        hbox2 = QHBoxLayout()
        hbox2.setContentsMargins(0, 0, 0, 0)

        self._samplesheet_v2_export_btn = QPushButton("Export SampleSheet v2")
        self._json_export_btn = QPushButton("Export Json")
        self._package_export_btn = QPushButton("Export package")

        # hbox.addWidget(self._fastq_extract_cb)
        hbox.addWidget(self.generate_btn)
        hbox.addStretch()
        hbox2.addWidget(self._samplesheet_v2_export_btn)
        hbox2.addWidget(self._json_export_btn)
        hbox2.addWidget(self._package_export_btn)
        hbox2.addStretch()

        self.layout.addLayout(hbox)
        self.layout.addLayout(hbox2)
        self.layout.addWidget(self._tab_widget)

        samplesheet_v2_layout = QVBoxLayout()
        samplesheet_v2_layout.addWidget(self._samplesheet_v2_textedit)

        samplesheet_v2_tab = QWidget()
        samplesheet_v2_tab.setLayout(samplesheet_v2_layout)
        self._tab_widget.addTab(samplesheet_v2_tab, "SampleSheet v2")

        json_tree_layout = QVBoxLayout()
        json_tree_layout.addWidget(self._json_textedit)

        json_tree_tab = QWidget()
        json_tree_tab.setLayout(json_tree_layout)
        self._tab_widget.addTab(json_tree_tab, "Json")

        self._samplesheet_v2_export_btn.clicked.connect(self._export_samplesheet_v2)
        self._json_export_btn.clicked.connect(self._export_json)

    def populate_samplesheet_v2_text(self):

        text = self._state_model.samplesheet_v2

        self._samplesheet_v2_textedit.setText(text)
        IlluminaSamplesheetV2Highlighter(self._samplesheet_v2_textedit.document())

    def populate_json_text(self, text):

        self._json_textedit.setPlainText(text)
        # font = self._json_textedit.font()
        # font.setPointSize(12)
        # self._json_textedit.setFont(font)

        JsonHighlighter(self._json_textedit.document())


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

