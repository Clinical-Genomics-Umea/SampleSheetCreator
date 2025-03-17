from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QSizePolicy,
    QVBoxLayout,
    QPushButton,
    QWidget,
    QHBoxLayout,
    QSpacerItem,
    QFormLayout,
    QLabel,
)

from modules.utils.utils import int_list_to_int_str


class RunInfoView(QGroupBox):
    def __init__(self, configuration_manager=None, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.defaults = configuration_manager.run_view_widgets_config

        # Main layout for the group box
        self.main_layout = QVBoxLayout(self)
        # self.main_layout.setContentsMargins(5, 0, 0, 0)

        self.arrow_button = QPushButton()
        self.arrow_button.setFixedSize(20, 20)
        self.arrow_button.setStyleSheet(
            """
            border: none;
            background-color: transparent;
        """
        )

        title = "Run Info"

        self.open_box = "⮟  " + title
        self.closed_box = "⮞  " + title

        self.setTitle(self.open_box)
        self.arrow_button.clicked.connect(self.toggle_content)

        # Content frame
        self.content_frame = QWidget()
        self.content_frame.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.content_layout = QHBoxLayout(self.content_frame)
        self.main_layout.addWidget(self.content_frame)

        # Initial state
        self.is_expanded = True

        self.orig_style = self.styleSheet()
        self.run_info_data = {}

        self._setup()

    def _setup(self):
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        for section_name, data in self.defaults.items():
            vbox = QVBoxLayout()
            vbox.setContentsMargins(0, 0, 0, 0)
            form = QFormLayout()
            form.setContentsMargins(0, 0, 0, 0)
            form.addRow(QLabel(section_name))

            for field in data:
                label = QLabel("None")
                form.addRow(QLabel(field), label)
                self.run_info_data[field] = label

            vbox.addLayout(form)
            # vbox.addStretch()
            self.content_layout.addLayout(vbox)

        self.content_layout.addStretch()

    def mousePressEvent(self, event):
        # Check if the click is on the title area
        if event.button() == Qt.LeftButton and self.childAt(event.pos()) is None:
            self.toggle_content()
        super().mousePressEvent(event)

    def toggle_content(self):
        """Toggle the visibility of the content instantly"""
        if self.is_expanded:
            # Collapse
            self.content_frame.hide()
            self.setStyleSheet(
                """
                    QGroupBox {
                        border: none;
                    }
                """
            )
            self.setTitle(self.closed_box)
        else:
            # Expand
            self.content_frame.show()
            self.setStyleSheet(self.orig_style)
            self.setTitle(self.open_box)

        self.is_expanded = not self.is_expanded

    def add_widget(self, widget):
        """Add a widget to the content layout"""
        self.content_layout.addWidget(widget)

    def set_data(self, data):
        for key, value in data.items():
            if key in self.run_info_data:
                if isinstance(value, list):
                    value = int_list_to_int_str(value)
                if isinstance(value, int):
                    value = str(value)

                self.run_info_data[key].setText(value)
