from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QLabel,
    QVBoxLayout, QFileDialog, QDialog,
)

from modules.models.workdata.workdata_model import WorkDataModel
from modules.views.ui_components import HorizontalLine
from modules.views.workdata.workdata_view import FetchWorkDataView



class FileView(QWidget):

    worksheet_filepath_ready = Signal(object)

    def __init__(self, workdata_model: WorkDataModel):
        super().__init__()

        self._workdata_model = workdata_model

        profiles_label = QLabel("File")
        profiles_label.setStyleSheet("font-weight: bold")

        self._new_samplesheet_btn = QPushButton("New Samplesheet")
        self._import_worksheet_btn = QPushButton("Import Worksheet")
        self._fetch_work_data_btn = QPushButton("Fetch Workdata")


        layout = QVBoxLayout()

        layout.addWidget(profiles_label)
        layout.addWidget(HorizontalLine())
        layout.addWidget(self._new_samplesheet_btn)
        layout.addWidget(self._import_worksheet_btn)
        layout.addWidget(self._fetch_work_data_btn)

        layout.addStretch()

        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

        self._import_worksheet_btn.clicked.connect(self._import_worksheet)
        self._fetch_work_data_btn.clicked.connect(self._fetch_work_data)


    def _import_worksheet(self):

        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Import Worksheet",
            "",
            "CSV Files (*.csv);;All Files (*)",
        )

        if file_path:

            self.worksheet_filepath_ready.emit(file_path)

    def _fetch_work_data(self):
        self._workdata_view = FetchWorkDataView(self._workdata_model)
        self._workdata_view.show()
