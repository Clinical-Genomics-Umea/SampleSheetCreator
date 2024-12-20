from PySide6.QtCore import Slot, Signal
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QPushButton,
    QLabel,
    QFrame,
    QFormLayout,
    QHBoxLayout,
    QCheckBox,
)

from models.dataset.dataset import DataSetManager
from models.rundata.rundata_model import RunDataModel
from utils.utils import flash_widget
from views.ui_components import HorizontalLine


class LanesWidget(QWidget):

    lanes_ready = Signal(list)

    def __init__(self, dataset_manager: DataSetManager):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)

        self.dataset_mgr = dataset_manager

        profiles_label = QLabel("Lanes")
        profiles_label.setStyleSheet("font-weight: bold")

        self._toggle_btn = QPushButton("toggle")
        self._clear_btn = QPushButton("clear")
        self._apply_btn = QPushButton("apply")

        self._toggle_btn.clicked.connect(self._toggle_lanes)
        self._clear_btn.clicked.connect(self._clear_lanes)
        self._apply_btn.clicked.connect(self.emit_lanes)

        self.lanes_checkboxes = {}
        self.checkboxes_layout = QFormLayout()

        hbox = QHBoxLayout()
        hbox.addWidget(self._toggle_btn)
        hbox.addWidget(self._clear_btn)

        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(profiles_label)
        layout.addWidget(HorizontalLine())

        layout.addLayout(hbox)
        layout.addLayout(self.checkboxes_layout)
        layout.addWidget(self._apply_btn)
        layout.addStretch()

        self.setLayout(layout)

    def _toggle_lanes(self):
        for lane in self.lanes_checkboxes:
            self.lanes_checkboxes[lane].toggle()

    def _clear_lanes(self):
        for lane in self.lanes_checkboxes:
            self.lanes_checkboxes[lane].setChecked(False)

    def clear_form(self):
        """Remove all rows from the form layout"""
        while self.checkboxes_layout.rowCount() > 0:
            # Remove widgets from the first row until no rows are left
            self.checkboxes_layout.removeRow(0)

    @Slot()
    def set_lanes(self):
        self.clear_form()
        self.lanes_checkboxes = {}

        lanes = self.dataset_mgr.run_lanes
        self.checkboxes_layout.addRow("Lane designation", QLabel("Usage"))
        for lane in lanes:
            checkbox = QCheckBox()
            self.lanes_checkboxes[lane] = checkbox
            self.checkboxes_layout.addRow(f"Lane {lane}", self.lanes_checkboxes[lane])

    def emit_lanes(self):
        lanes = []

        for lane in self.lanes_checkboxes:
            if self.lanes_checkboxes[lane].isChecked():
                lanes.append(lane)

        self.lanes_ready.emit(lanes)
