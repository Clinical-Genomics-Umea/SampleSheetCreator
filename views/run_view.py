from PySide6.QtGui import QFont, Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QLabel,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QGridLayout,
    QPushButton,
    QGroupBox,
    QFrame,
    QHBoxLayout,
    QSpacerItem,
    QSizePolicy,
)
import yaml

from views.ui.run_settings_form_grid import Ui_Form


def extract_widget_data(widget):
    """
    Extracts data from a given widget.

    :param widget: The widget to extract data from.
    :type widget: QWidget
    :return: The extracted data from the widget.
    :rtype: str or None
    """
    if isinstance(widget, QLineEdit):
        return widget.text()
    if isinstance(widget, QComboBox):
        return widget.currentText()
    return widget.text() if isinstance(widget, QLabel) else ""


def make_widget(widget_type, data):
    """
    Get a widget based on the given type and data.

    Parameters:
        widget_type (str): The type of widget to create. Valid options are "label", "lineedit", and "combobox".
        data: The data to be used when creating the widget. For "label" and "lineedit" types, this should
        be a string. For "combobox" type, this should be a list of strings.

    Returns:
        QLabel or QLineEdit or QComboBox or None: The created widget based on the given type and data.
        If the type is not valid, None is returned.
    """
    if widget_type == "label":
        return QLabel(data)
    elif widget_type == "lineedit":
        return QLineEdit(data)
    elif widget_type == "combobox":
        cb = QComboBox()
        cb.addItems(data)
        return cb
    else:
        return None


def load_from_yaml(config_file):
    with open(config_file, "r") as file:
        return yaml.safe_load(file)


class RunSetupWidget(QWidget):
    def __init__(self, run_config):
        super().__init__()

        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)

        top_label = QLabel("Run Setup")
        top_label.setStyleSheet("font-weight: bold")

        self.set_button = QPushButton("Set Run Params")

        layout.addWidget(top_label)
        layout.addWidget(self.set_button)

        form = QFormLayout()

        self.setLayout(layout)
        layout.addLayout(form)

        self.run_config = load_from_yaml(run_config)

        self.input_widgets = {}

        for section in self.run_config:
            form.addRow(QLabel(""), QLabel(""))
            form.addRow(QLabel(f"[{section}]"), QLabel(""))
            self.input_widgets[section] = {}

            for field in self.run_config[section]:

                widget_type = self.run_config[section][field]["control"]
                widget_data = self.run_config[section][field]["data"]
                widget = make_widget(widget_type, widget_data)

                self.input_widgets[section][field] = widget

                form.addRow(QLabel(field), widget)

        layout.addStretch()

    def get_data(self):
        return {
            section: {
                field: extract_widget_data(widget) for field, widget in fields.items()
            }
            for section, fields in self.input_widgets.items()
        }


class RunInfoViewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.sections = {}

    def setup(self, data):
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.sections = {}

        for section_name, section_data in data.items():

            section = RunInfoSection(section_name, section_data)
            self.sections[section_name] = section
            self.layout.addWidget(section)

        self.layout.addSpacerItem(spacer)

    def set_data(self, data: dict):
        for section, subdata in data.items():
            print(f"Setting data for {section}: {subdata}")
            self.sections[section].set_data(subdata)

    def add_widget(self, widget):
        widget.setMinimumWidth(200)
        widget.setMaximumWidth(300)
        self.layout.addWidget(widget)

    def get_data(self):
        sections_data = {}
        for section_name, section in self.sections.items():
            sections_data[section_name] = section.get_data()

        return sections_data


class RunInfoSection(QGroupBox):
    def __init__(self, title: str, run_info: dict):
        super().__init__()

        self.setContentsMargins(0, 0, 0, 0)

        col_width_min = 100
        col_width_max = 300

        self.setTitle(title)
        self.fields = {}

        font = QFont()
        font.setPointSize(8)

        hlayout = QHBoxLayout()
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        hlayout.setContentsMargins(3, 5, 3, 3)
        self.setLayout(hlayout)
        form_layouts = [QFormLayout()]
        form_layouts[-1].setContentsMargins(3, 3, 3, 3)
        form_layouts[-1].setSpacing(3)
        hlayout.addLayout(form_layouts[-1])

        for row_count, (key, value) in enumerate(run_info.items()):
            if row_count > 0 and row_count % 2 == 0:
                hlayout.addWidget(self.get_line())
                form_layouts.append(QFormLayout())
                form_layouts[-1].setContentsMargins(3, 3, 3, 3)
                hlayout.addLayout(form_layouts[-1])

            self.fields[key] = QLabel(value)

            key_widget = QLabel(key)
            value_widget = self.fields[key]
            key_widget.setFont(font)
            value_widget.setFont(font)

            form_layouts[-1].addRow(key_widget, self.fields[key])

        self.setMinimumWidth(col_width_min * len(form_layouts))
        self.setMaximumWidth(col_width_max * len(form_layouts))

    def get_line(self):
        line = QFrame(self)
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)

        return line

    def set_data(self, data):
        for key, value in data.items():
            if key in self.fields:
                self.fields[key].setText(value)

    def get_data(self):
        return {key: self.fields[key].text() for key in self.fields}
