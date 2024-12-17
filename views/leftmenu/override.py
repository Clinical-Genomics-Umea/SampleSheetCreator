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
)

from views.ui_components import HorizontalLine


class OverrideCyclesWidget(QWidget):

    custom_override_pattern_ready = Signal(str)

    def __init__(self):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)

        profiles_label = QLabel("Set Custom OverrideCycles")
        profiles_label.setStyleSheet("font-weight: bold")

        self.oc_custom_r1_lineedit = QLineEdit()
        self.oc_custom_i1_lineedit = QLineEdit()
        self.oc_custom_i2_lineedit = QLineEdit()
        self.oc_custom_r2_lineedit = QLineEdit()

        self.oc_lineedits = [
            self.oc_custom_r1_lineedit,
            self.oc_custom_i1_lineedit,
            self.oc_custom_i2_lineedit,
            self.oc_custom_r2_lineedit,
        ]

        oc_header_layout = QHBoxLayout()
        oc_header_layout.addWidget(QLabel("R1"))
        oc_header_layout.addWidget(QLabel("I1"))
        oc_header_layout.addWidget(QLabel("I2"))
        oc_header_layout.addWidget(QLabel("R2"))

        custom_layout = QHBoxLayout()
        custom_layout.setContentsMargins(0, 0, 0, 0)
        custom_layout.addWidget(self.oc_custom_r1_lineedit)
        custom_layout.addWidget(self.oc_custom_i1_lineedit)
        custom_layout.addWidget(self.oc_custom_i2_lineedit)
        custom_layout.addWidget(self.oc_custom_r2_lineedit)

        self.get_selected_overrides_btn = QPushButton("get selected override patterns")
        self.apply_button = QPushButton("apply")

        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(profiles_label)
        layout.addWidget(HorizontalLine())

        form = QFormLayout()
        form.addRow("", oc_header_layout)
        form.addRow("custom", custom_layout)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.get_selected_overrides_btn)
        h_layout.addWidget(self.apply_button)

        layout.addLayout(form)
        layout.addLayout(h_layout)
        layout.addStretch()

        self.setLayout(layout)

        self.apply_button.clicked.connect(self.transfer_override_pattern)

    @Slot(list)
    def set_override_pattern(self, data):
        data_set = set(data)
        if len(data_set) == 1:
            pattern = next(iter(data_set))
            parts = pattern.split("-")

            for i, part in enumerate(parts):
                self.oc_lineedits[i].setText(part)

    def transfer_override_pattern(self):

        pattern_list = []

        for lineedit in self.oc_lineedits:
            sub_pattern = lineedit.text()
            if sub_pattern:
                pattern_list.append(sub_pattern)
            else:
                break
        pattern = "-".join(pattern_list)

        self.custom_override_pattern_ready.emit(pattern)
