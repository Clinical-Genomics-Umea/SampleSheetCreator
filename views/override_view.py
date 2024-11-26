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


class OverrideCyclesWidget(QWidget):

    def __init__(self):
        super().__init__()

        profiles_label = QLabel("Set Custom OverrideCycles")
        profiles_label.setStyleSheet("font-weight: bold")

        self.oc_template_r1_lineedit = QLineEdit()
        self.oc_template_i1_lineedit = QLineEdit()
        self.oc_template_i2_lineedit = QLineEdit()
        self.oc_template_r2_lineedit = QLineEdit()

        self.oc_custom_r1_lineedit = QLineEdit()
        self.oc_custom_i1_lineedit = QLineEdit()
        self.oc_custom_i2_lineedit = QLineEdit()
        self.oc_custom_r2_lineedit = QLineEdit()

        template_layout = QHBoxLayout()
        template_layout.addWidget(self.oc_template_r1_lineedit)
        template_layout.addWidget(self.oc_template_i1_lineedit)
        template_layout.addWidget(self.oc_template_i2_lineedit)
        template_layout.addWidget(self.oc_template_r2_lineedit)

        custom_layout = QHBoxLayout()
        custom_layout.addWidget(self.oc_custom_r1_lineedit)
        custom_layout.addWidget(self.oc_custom_i1_lineedit)
        custom_layout.addWidget(self.oc_custom_i2_lineedit)
        custom_layout.addWidget(self.oc_custom_r2_lineedit)

        self.get_default_button = QPushButton("get default")
        self.set_custom_button = QPushButton("apply")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(profiles_label)
        layout.addWidget(self.get_line())

        form = QFormLayout()
        form.addRow("template", template_layout)
        form.addRow("custom", custom_layout)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.get_default_button)
        h_layout.addWidget(self.set_custom_button)

        layout.addLayout(form)
        layout.addLayout(h_layout)
        layout.addStretch()

        self.setLayout(layout)

    def set_override_cycles(self):
        pass

    @staticmethod
    def get_line():
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line
