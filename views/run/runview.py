from PySide6.QtCore import QSize, QRect, QPoint
from PySide6.QtGui import (
    QFont,
    Qt,
)
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QFormLayout,
    QGroupBox,
    QFrame,
    QHBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QLayout,
    QVBoxLayout,
    QPushButton,
)
from utils.utils import int_list_to_int_str


class RunInfoView(QGroupBox):
    def __init__(self, title="Group", cfg_mgr=None, parent=None):
        super().__init__(title, parent)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.defaults = cfg_mgr.run_view_widgets_config

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


class RunView(QWidget):
    def __init__(self, cfg_mgr):
        super().__init__()
        self._defaults = cfg_mgr.run_view_widgets_config

        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self._layout = FlowLayout()
        # self._layout = QHBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)
        self._view_widgets = {}

        # sections, defaults a

        self._setup()

    def _setup(self):
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.sections = {}

        for section_name, data in self._defaults.items():

            section = RunViewSection(self._view_widgets, section_name, data)
            self.sections[section_name] = section
            self._layout.addWidget(section)

        self._layout.addSpacerItem(spacer)

    def set_data(self, data):
        for key, value in data.items():
            if key in self._view_widgets:

                if isinstance(value, list):
                    value = int_list_to_int_str(value)

                if isinstance(value, int):
                    value = str(value)

                self._view_widgets[key].setText(value)


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


class FlowLayout(QLayout):
    def __init__(self, parent=None, spacing=10):
        super().__init__(parent)
        self.setSpacing(spacing)
        self.itemList = []

    def addItem(self, item):
        self.itemList.append(item)

    def addSpacerItem(self, spacerItem):
        # Simply append spacer item to the item list; it won't affect layout behavior
        self.itemList.append(spacerItem)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index < 0 or index >= len(self.itemList):
            return None
        return self.itemList[index]

    def takeAt(self, index):
        if index < 0 or index >= len(self.itemList):
            return None
        return self.itemList.pop(index)

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.spacing(), 2 * self.spacing())
        return size

    def doLayout(self, rect, testOnly):
        x, y, lineHeight = rect.x(), rect.y(), 0
        for item in self.itemList:
            if isinstance(item, QSpacerItem):
                # Skip spacer items in the layout process
                continue

            widget = item.widget()
            spaceX = self.spacing()
            spaceY = self.spacing()
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y += lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()
