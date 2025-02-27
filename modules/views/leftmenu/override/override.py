from PySide6.QtCore import Slot, Signal
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QPushButton,
    QLabel,
    QFormLayout,
)

from modules.utils.utils import flash_widget
from modules.views.ui_components import HorizontalLine


class OverrideCyclesWidget(QWidget):

    custom_override_pattern_ready = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)

        self.fields = [
            "Read1Cycles",
            "Index1Cycles",
            "Index2Cycles",
            "Read2Cycles",
        ]
        profiles_label = QLabel("Set Custom OverrideCycles")
        profiles_label.setStyleSheet("font-weight: bold")

        self.oc_custom_r1_lineedit = QLineEdit()
        self.oc_custom_i1_lineedit = QLineEdit()
        self.oc_custom_i2_lineedit = QLineEdit()
        self.oc_custom_r2_lineedit = QLineEdit()

        self.oc_lineedits_list = [
            self.oc_custom_r1_lineedit,
            self.oc_custom_i1_lineedit,
            self.oc_custom_i2_lineedit,
            self.oc_custom_r2_lineedit,
        ]
        self._oc_lineedits_dict = {
            "Read1Cycles": self.oc_custom_r1_lineedit,
            "Index1Cycles": self.oc_custom_i1_lineedit,
            "Index2Cycles": self.oc_custom_i2_lineedit,
            "Read2Cycles": self.oc_custom_r2_lineedit,
        }

        form = QFormLayout()
        form.addRow(QLabel("Name"), QLabel("OverrideCyclePattern"))
        form.addRow(QLabel("Read1Cycles"), self.oc_custom_r1_lineedit)
        form.addRow(QLabel("Index1Cycles"), self.oc_custom_i1_lineedit)
        form.addRow(QLabel("Index2Cycles"), self.oc_custom_i2_lineedit)
        form.addRow(QLabel("Read2Cycles"), self.oc_custom_r2_lineedit)

        self.get_selected_overrides_btn = QPushButton("get selected override patterns")
        self.apply_button = QPushButton("apply")

        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(profiles_label)
        layout.addWidget(HorizontalLine())

        layout.addWidget(self.get_selected_overrides_btn)
        layout.addLayout(form)
        layout.addWidget(self.apply_button)
        layout.addStretch()

        self.setLayout(layout)

        self.apply_button.clicked.connect(self.emit_override_pattern)

    @Slot(list)
    def set_override_pattern(self, data):
        data_set = set(data)
        if len(data_set) == 1:
            pattern = next(iter(data_set))
            parts = pattern.split("-")

            for i, part in enumerate(parts):
                self.oc_lineedits_list[i].setText(part)

    def emit_override_pattern(self):
        pattern_dict = {}

        for key, lineedit in self._oc_lineedits_dict.items():
            sub_pattern = lineedit.text()
            if sub_pattern:
                pattern_dict[key] = sub_pattern

        self.custom_override_pattern_ready.emit(pattern_dict)

    @Slot()
    def on_invalid_result(self, error_fields):
        print(error_fields)

        for field in error_fields:
            flash_widget(self._oc_lineedits_dict[field])
