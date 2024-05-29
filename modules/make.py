from dataclasses import dataclass

import pandas as pd
from PySide6.QtWidgets import (QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy,
                               QSpacerItem, QLabel, QFormLayout, QFrame)

from modules.run import RunInfo
from modules.sample_view import SampleTableView


class Make(QWidget):
    def __init__(self, run_info: RunInfo, sample_tableview: SampleTableView):
        super().__init__()
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

