from PySide6.QtCore import Signal, Slot, QSize, QRect, QPoint
from PySide6.QtGui import QFont, Qt
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
from utils.utils import uuid


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

        # self.input_widgets["Instrument"].currentTextChanged.connect(
        #     self._repopulate_widget_data
        # )

        layout.addStretch()

        self.set_button.clicked.connect(self._commit)

    def _populate_instruments(self):
        instruments = self.cfg_mgr.instruments
        self.input_widgets["Instrument"].clear()
        self.input_widgets["Instrument"].addItems(instruments)

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

    def _setup_header_ui(self):
        # header
        self.form.addRow(QLabel("Header"))

        self.input_widgets["Instrument"] = QComboBox()
        self.form.addRow(QLabel("Instrument"), self.input_widgets["Instrument"])

        self.input_widgets["SampleSheetVersion"] = QLineEdit()
        self.input_widgets["SampleSheetVersion"].setReadOnly(True)
        self.form.addRow(
            QLabel("SampleSheetVersion"),
            self.input_widgets["SampleSheetVersion"],
        )

        self.input_widgets["RunName"] = QLineEdit()
        self.form.addRow(QLabel("RunName"), self.input_widgets["RunName"])

        self.input_widgets["RunDescription"] = QLineEdit()
        self.form.addRow(QLabel("RunDescription"), self.input_widgets["RunDescription"])

        self.form.addRow(QLabel(""))

    def _setup_reads_ui(self):
        # Reads
        self.form.addRow(QLabel("Reads"))

        self.input_widgets["ReadCycles"] = QComboBox()
        self.form.addRow(QLabel("ReadCycles"), self.input_widgets["ReadCycles"])

        self.input_widgets["I5SeqOrientation"] = QLineEdit()
        self.input_widgets["I5SeqOrientation"].setReadOnly(True)
        self.form.addRow(
            QLabel("I5SeqOrientation"), self.input_widgets["I5SeqOrientation"]
        )
        self.input_widgets["I5SampleSheetOrientation"] = QLineEdit()
        self.input_widgets["I5SampleSheetOrientation"].setReadOnly(True)
        self.form.addRow(
            QLabel("I5SampleSheetOrientation"),
            self.input_widgets["I5SampleSheetOrientation"],
        )

        self.form.addRow(QLabel(""))

    def _setup_extra_ui(self):
        # Run Extra
        self.form.addRow(QLabel("Run Extra"))

        self.input_widgets["Lanes"] = QComboBox()
        self.form.addRow(QLabel("Lanes"), self.input_widgets["Lanes"])

        self.input_widgets["Investigator"] = QComboBox()
        self.form.addRow(QLabel("Investigator"), self.input_widgets["Investigator"])

        self.form.addRow(QLabel(""))

    def _setup_widget_default_data(self):
        instruments = list(self.cfg_mgr.run_setup_widgets_config.keys())
        self.input_widgets["Instrument"].addItems(instruments)
        current_instrument = self.input_widgets["Instrument"].currentText()

        for widget_name, data in self.cfg_mgr.run_setup_widgets_config[
            current_instrument
        ].items():
            if isinstance(self.input_widgets[widget_name], QComboBox):
                self.input_widgets[widget_name].addItems(data)
            elif isinstance(self.input_widgets[widget_name], QLineEdit):
                self.input_widgets[widget_name].setText(data)

    @Slot()
    def _repopulate_widget_data(self):
        instrument_cb = self.sender()
        instrument = instrument_cb.currentText()

        for widget_name, data in self.cfg_mgr.run_setup_widgets_config[
            instrument
        ].items():
            if isinstance(self.input_widgets[widget_name], QComboBox):
                self.input_widgets[widget_name].clear()
                self.input_widgets[widget_name].addItems(data)
            elif isinstance(self.input_widgets[widget_name], QLineEdit):
                self.input_widgets[widget_name].setText(data)

    def _commit(self):
        data = {}
        for field, widget in self.input_widgets.items():
            data[field] = self.extract(widget)

        self.setup_commited.emit(data)  # set(data)

    @staticmethod
    def extract(widget):
        if isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QLineEdit):
            return widget.text()

        return None


class RunView(QWidget):
    def __init__(self):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self._layout = FlowLayout()
        # self._layout = QHBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)
        self._view_widgets = {}

        # sections, defaults a

        self._defaults = {
            "Header": {
                "Instrument": "NA",
                "SampleSheetVersion": "NA",
                "RunName": "NA",
                "RunDescription": "NA",
            },
            "Reads": {
                "ReadCycles": "NA",
                "I5SampleSheetOrientation": "NA",
                "I5SeqOrientation": "NA",
                "FastqExtractTool": "NA",
            },
            "Fluorophores": {"A": "NA", "T": "NA", "G": "NA", "C": "NA"},
            "Extra": {
                "Lanes": "NA",
                "Investigator": "NA",
                "Chemistry": "NA",
                "AssessBalance": "NA",
            },
        }

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

        print(data)

        for key, value in data.items():
            if key in self._view_widgets:
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
            key1, value1 = data_items[i]
            value_label = QLabel(value1)
            form_layout.addRow(QLabel(key1), value_label)
            self._view_widgets[key1] = value_label

            # Check if there's a second row, if not, fill with empty strings
            if i + 1 < len(data_items):

                key2, value2 = data_items[i + 1]

                value_label = QLabel(value2)
                form_layout.addRow(QLabel(key2), value_label)
                self._view_widgets[key2] = value_label

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
