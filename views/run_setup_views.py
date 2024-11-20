from PySide6.QtCore import Signal, Slot, QSize, QRect, QPoint, QTimer
from PySide6.QtGui import (
    QFont,
    Qt,
    QRegularExpressionValidator,
    QValidator,
    QIntValidator,
)
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QLabel,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
    QGroupBox,
    QFrame,
    QHBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QLayout,
)
import yaml
from utils.utils import uuid, int_list_to_int_str
import re


def load_from_yaml(config_file):
    with open(config_file, "r") as file:
        return yaml.safe_load(file)


class RunSetupWidget(QWidget):

    setup_commited = Signal(dict)

    def __init__(self, cfg_mgr):
        super().__init__()

        self.cfg_mgr = cfg_mgr

        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)

        top_label = QLabel("Run Setup")
        top_label.setStyleSheet("font-weight: bold")

        self.set_button = QPushButton("Commit")

        layout.addWidget(top_label)
        layout.addWidget(self.set_button)

        self.form = QFormLayout()

        self.setLayout(layout)
        layout.addLayout(self.form)

        self.input_widgets = {}
        self._create_run_widgets()

        self.populate_investigators()
        self._populate_instruments()
        self._populate_flowcells()
        self._populate_samplesheet_version()
        self._populate_reagent_kits()
        self._populate_read_cycles()

        self.input_widgets["Instrument"].currentTextChanged.connect(
            self._populate_flowcells
        )
        self.input_widgets["Instrument"].currentTextChanged.connect(
            self._populate_samplesheet_version
        )

        self.input_widgets["Flowcell"].currentTextChanged.connect(
            self._populate_reagent_kits
        )

        self.input_widgets["Flowcell"].currentTextChanged.connect(
            self._populate_read_cycles
        )

        self.input_widgets["ReagentKit"].currentTextChanged.connect(
            self._populate_read_cycles
        )

        self.input_widgets["ReadCycles"].currentTextChanged.connect(
            self._set_custom_read_cycle_validator
        )

        layout.addStretch()

        self.set_button.clicked.connect(self._commit)

    @Slot(list)
    def show_error(self, fields):
        for field in fields:
            self._flash_widget(self.input_widgets[field])

    def _flash_widget(self, widget):
        original_style = widget.styleSheet()
        widget.setStyleSheet("border: 1px solid red;")
        QTimer.singleShot(500, lambda: widget.setStyleSheet(original_style))

    def _populate_instruments(self):
        instruments = self.cfg_mgr.instruments
        self.input_widgets["Instrument"].clear()
        self.input_widgets["Instrument"].addItems(instruments)

    def _populate_flowcells(self):
        current_instrument = self.input_widgets["Instrument"].currentText()
        flowcells = self.cfg_mgr.instrument_flowcells[current_instrument][
            "Flowcell"
        ].keys()
        self.input_widgets["Flowcell"].clear()
        self.input_widgets["Flowcell"].addItems(flowcells)

    def _populate_samplesheet_version(self):
        current_instrument = self.input_widgets["Instrument"].currentText()
        samplesheet_version = self.cfg_mgr.instrument_flowcells[current_instrument][
            "SampleSheetVersion"
        ]
        self.input_widgets["SampleSheetVersion"].clear()
        self.input_widgets["SampleSheetVersion"].setText(str(samplesheet_version))

    def _populate_reagent_kits(self):
        current_instrument = self.input_widgets["Instrument"].currentText()

        if not len(current_instrument) > 0:
            return

        current_flowcell = self.input_widgets["Flowcell"].currentText()

        if not len(current_flowcell) > 0:
            return

        reagent_kits = list(
            self.cfg_mgr.instrument_flowcells[current_instrument]["Flowcell"][
                current_flowcell
            ]["ReagentKit"].keys()
        )

        self.input_widgets["ReagentKit"].clear()
        self.input_widgets["ReagentKit"].addItems(reagent_kits)

    def _populate_read_cycles(self):
        current_instrument = self.input_widgets["Instrument"].currentText()

        if not len(current_instrument) > 0:
            return

        current_flowcell = self.input_widgets["Flowcell"].currentText()

        if not len(current_flowcell) > 0:
            return

        current_reagent_kit = self.input_widgets["ReagentKit"].currentText()

        if not len(current_reagent_kit) > 0:
            return

        read_cycles = self.cfg_mgr.instrument_flowcells[current_instrument]["Flowcell"][
            current_flowcell
        ]["ReagentKit"][current_reagent_kit]
        self.input_widgets["ReadCycles"].clear()
        self.input_widgets["ReadCycles"].addItems(read_cycles)

        self.input_widgets["CustomReadCycles"].clear()
        template = self.input_widgets["ReadCycles"].currentText()
        self.input_widgets["CustomReadCycles"].setValidator(PatternValidator(template))

    def _create_run_widgets(self):
        for (
            section_name,
            section_config,
        ) in self.cfg_mgr.run_setup_widgets_config.items():
            self.form.addRow(QLabel(section_name))
            for widget_name, widget_type in section_config.items():
                if widget_type == "lineedit":
                    widget_class = QLineEdit
                elif widget_type == "combobox":
                    widget_class = QComboBox
                else:
                    raise ValueError(f"Unknown widget type: {widget_type}")

                widget = widget_class()
                self.input_widgets[widget_name] = widget
                self.form.addRow(QLabel(widget_name), widget)

            self.form.addRow(QLabel(""))

    @Slot()
    def populate_investigators(self):
        users = self.cfg_mgr.users
        self.input_widgets["Investigator"].clear()
        self.input_widgets["Investigator"].addItems(users)

    def _set_custom_read_cycle_validator(self):
        self.input_widgets["CustomReadCycles"].clear()
        template = self.input_widgets["ReadCycles"].currentText()
        self.input_widgets["CustomReadCycles"].setValidator(PatternValidator(template))

    def _commit(self):
        data = {}
        for field, widget in self.input_widgets.items():
            data[field] = self._extract(widget)

        self.setup_commited.emit(data)  # set(data)

    @staticmethod
    def _extract(widget):
        if isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QLineEdit):
            return widget.text()

        return None


class PatternValidator(QValidator):
    def __init__(self, pattern, parent=None):
        super().__init__(parent)
        self.pattern = pattern
        if pattern == "":
            self.pattern_parts = []
        else:
            self.pattern_parts = [int(part) for part in pattern.split("-")]

    def validate(self, input_text, pos):
        # Allow empty input as an intermediate state
        if input_text == "":
            return QValidator.Intermediate, input_text, pos

        # Check for multiple consecutive dashes
        if "--" in input_text:
            return QValidator.Invalid, input_text, pos

        # Split the input text into parts
        input_parts = input_text.split("-")

        # Check if the number of parts exceeds the pattern
        if len(input_parts) > len(self.pattern_parts):
            return QValidator.Invalid, input_text, pos

        for i, part in enumerate(input_parts):
            # Allow incomplete trailing dashes (e.g., "51-")
            if part == "":
                # Invalid if it's not the last part and it's empty
                if i < len(input_parts) - 1:
                    return QValidator.Invalid, input_text, pos
                continue

            # Ensure each part is numeric
            if not part.isdigit():
                return QValidator.Invalid, input_text, pos

            # Check if the part exceeds the corresponding pattern value
            if i < len(self.pattern_parts) and int(part) > self.pattern_parts[i]:
                return QValidator.Invalid, input_text, pos

        # Allow trailing dashes as valid intermediate states
        if input_text[-1] == "-" and len(input_parts) <= len(self.pattern_parts):
            return QValidator.Intermediate, input_text, pos

        return QValidator.Acceptable, input_text, pos

    def fixup(self, input_text):
        # If invalid, return an empty string
        return ""


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
