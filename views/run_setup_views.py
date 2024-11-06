from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QFont
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

        self._setup_header_ui()
        self._setup_reads_ui()
        self._setup_extra()
        self._setup_widget_default_data()
        self.populate_investigators()

        self.input_widgets["Instrument"].currentTextChanged.connect(
            self._repopulate_widget_data
        )

        layout.addStretch()

        self.set_button.clicked.connect(self._commit)

    @Slot()
    def populate_investigators(self):
        print("populating investigators")
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

        self.input_widgets["I5IndexOrientation"] = QLineEdit()
        self.input_widgets["I5IndexOrientation"].setReadOnly(True)
        self.form.addRow(
            QLabel("I5IndexOrientation"), self.input_widgets["I5IndexOrientation"]
        )

        self.form.addRow(QLabel(""))

    def _setup_extra(self):
        # Run Extra
        self.form.addRow(QLabel("Run Extra"))

        self.input_widgets["Lanes"] = QComboBox()
        self.form.addRow(QLabel("Lanes"), self.input_widgets["Lanes"])

        self.input_widgets["Investigator"] = QComboBox()
        self.form.addRow(QLabel("Investigator"), self.input_widgets["Investigator"])

        self.form.addRow(QLabel(""))

    def _setup_widget_default_data(self):
        instruments = list(self.cfg_mgr.run_widget_data_hierarchy.keys())
        self.input_widgets["Instrument"].addItems(instruments)
        current_instrument = self.input_widgets["Instrument"].currentText()

        for widget_name, data in self.cfg_mgr.run_widget_data_hierarchy[
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

        for widget_name, data in self.cfg_mgr.run_widget_data_hierarchy[
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
        self._layout = QHBoxLayout()
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
                "I5IndexOrientation": "NA",
            },
            "Extra": {
                "Lanes": "NA",
                "Investigator": "NA",
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
