from PySide6.QtCore import Signal, Slot, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFormLayout,
    QLineEdit,
    QComboBox,
)

from modules.views.leftmenu.run_setup.pattern_validator import PatternValidator
from modules.views.ui_components import HorizontalLine


class RunSetupWidget(QWidget):

    setup_commited = Signal(dict)

    def __init__(self, cfg_mgr, dataset_mgr):
        super().__init__()

        self.cfg_mgr = cfg_mgr
        self.dataset_mgr = dataset_mgr

        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)

        top_label = QLabel("Run Setup")
        top_label.setStyleSheet("font-weight: bold")

        self.commit_btn = QPushButton("Commit")

        layout.addWidget(top_label)
        layout.addWidget(HorizontalLine())
        layout.addWidget(self.commit_btn)

        self.form = QFormLayout()

        self.setLayout(layout)
        layout.addLayout(self.form)

        self.input_widgets = {}
        self._create_run_widgets()

        self.populate_investigators()
        self._populate_instruments()
        self._populate_flowcells()
        # self._populate_samplesheet_version()
        self._populate_reagent_kits()
        self._populate_read_cycles()
        self._populate_fastq_extract_tool()

        self.input_widgets["Instrument"].currentTextChanged.connect(
            self._populate_flowcells
        )
        # self.input_widgets["Instrument"].currentTextChanged.connect(
        #     self._populate_samplesheet_version
        # )
        self.input_widgets["Instrument"].currentTextChanged.connect(
            self._populate_fastq_extract_tool
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

        self.commit_btn.clicked.connect(self.commit)

    @Slot(list)
    def show_error(self, fields):
        for field in fields:
            self.flash_widget(self.input_widgets[field])

    @staticmethod
    def flash_widget(widget):
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

    # def _populate_samplesheet_version(self):
    #     current_instrument = self.input_widgets["Instrument"].currentText()
    #     samplesheet_version = self.cfg_mgr.instrument_flowcells[current_instrument][
    #         "SampleSheetVersion"
    #     ]
    #     self.input_widgets["SampleSheetVersion"].clear()
    #     self.input_widgets["SampleSheetVersion"].setText(str(samplesheet_version))

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

    def _populate_fastq_extract_tool(self):
        current_instrument = self.input_widgets["Instrument"].currentText()

        if not len(current_instrument) > 0:
            return

        fastq_extract_tools = self.cfg_mgr.instrument_flowcells[current_instrument][
            "FastqExtractTool"
        ]

        self.input_widgets["FastqExtractTool"].clear()
        self.input_widgets["FastqExtractTool"].addItems(fastq_extract_tools)

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

    @staticmethod
    def _validate_readcycles(index_maxlens, data):
        readcycles = map(int, data["ReadCycles"].split("-"))

        for i, value in enumerate(readcycles):
            if i == 1:
                if index_maxlens["IndexI7_maxlen"] > value:
                    return False
            if i == 2:
                if index_maxlens["IndexI5_maxlen"] > value:
                    return False

        return True

    def commit(self):
        """Commit the data from the input widgets."""
        data = {}
        for field, widget in self.input_widgets.items():
            data[field] = self.extract_data(widget)

        if not self.validate_readcycles(data):
            self.flash_widget(self.input_widgets["ReadCycles"])
            return

        self.setup_commited.emit(data)

    @staticmethod
    def extract_data(widget):
        """Extract data from the given widget."""
        if isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QLineEdit):
            return widget.text()

    def validate_readcycles(self, data):
        """Validate the readcycles field."""
        readcycles = list(map(int, data["ReadCycles"].split("-")))
        index_maxlens = self.dataset_mgr.index_maxlens()

        for i, value in enumerate(readcycles):
            if index_maxlens is not None:
                if i == 1 and index_maxlens["IndexI7_maxlen"] > value:
                    return False
                if i == 2 and index_maxlens["IndexI5_maxlen"] > value:
                    return False

        return True

    @staticmethod
    def _extract(widget):
        if isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QLineEdit):
            return widget.text()

        return None
