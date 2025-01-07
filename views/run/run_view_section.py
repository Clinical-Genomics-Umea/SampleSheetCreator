from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QSizePolicy,
    QFormLayout,
    QFrame,
    QLabel,
)


class RunViewSection(QGroupBox):
    def __init__(self, view_widgets, title: str, data: dict):
        """
        Initialize a RunInfoSection.

        A RunInfoSection is a QGroupBox with a title and a form layout containing
        key-value pairs. It is used to display information about a run.

        Args:
            view_widgets (dict): A dictionary of widgets to be displayed in the view.
            title (str): The title of the section.
            data (dict): A dictionary of key-value pairs to be displayed in the section.
        """
        super().__init__()

        self._view_widgets = view_widgets

        data_items = list(data.items())

        self.setTitle(title)
        self.setContentsMargins(0, 0, 0, 0)

        self._fields = {}

        font = QFont()
        font.setPointSize(8)

        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(3, 5, 3, 3)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setLayout(h_layout)

        form_layout = None

        for i in range(0, len(data_items), 2):
            # Create a new form layout every two items
            form_layout = QFormLayout()

            # Add the form layout to the horizontal layout
            # If this isn't the first form layout, add a vertical line before it
            if h_layout.count() > 0:
                # Add a vertical line between form layouts
                v_line = QFrame()
                v_line.setFrameShape(QFrame.VLine)
                v_line.setFrameShadow(QFrame.Sunken)
                h_layout.addWidget(v_line)

            h_layout.addLayout(form_layout)

            # Add the first row
            field, _ = data_items[i]
            widget = QLabel("NA")

            form_layout.addRow(QLabel(field), widget)
            self._view_widgets[field] = widget

            # Check if there's a second row, if not, fill with empty strings
            if i + 1 < len(data_items):

                field2, _ = data_items[i + 1]
                widget2 = QLabel("NA")
                form_layout.addRow(QLabel(field2), widget2)
                self._view_widgets[field2] = widget2

            else:
                form_layout.addRow(QLabel(""), QLabel(""))  # Add empty row

        # If the last form layout has only one row, add an empty row
        if form_layout and form_layout.rowCount() < 2:
            form_layout.addRow(QLabel(""), QLabel(""))

    def _get_line(self):
        line = QFrame(self)
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)

        return line
