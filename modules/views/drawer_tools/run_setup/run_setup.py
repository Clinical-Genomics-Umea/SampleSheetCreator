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

from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.state.state_model import StateModel
from modules.views.drawer_tools.run_setup.pattern_validator import PatternValidator
from modules.views.ui_components import HorizontalLine


class RunSetupWidget(QWidget):

    setup_commited = Signal(dict)

    def __init__(self, configuration_manager: ConfigurationManager, state_model: StateModel):
        super().__init__()

        self._configuration_manager = configuration_manager
        self._state_model = state_model

        self._investigator_cb = QComboBox()  # combobox
        self._run_name_le = QLineEdit()  # RunName: lineedit
        self._run_description_le = QLineEdit()  # RunDescription: lineedit
        self._instrument_cb = QComboBox()  # Instrument: combobox
        self._flowcell_cb = QComboBox()  # Flowcell: combobox
        self._reagent_kit_cb = QComboBox()  # ReagentKit: combobox
        self._read_cycles_cb = QComboBox()  # ReadCycles: combobox
        self._custom_read_cycles_le = QLineEdit()  # CustomReadCycles: lineedit


        self._commit_btn = QPushButton("Commit")

        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)

        top_label = QLabel("Run Setup")
        top_label.setStyleSheet("font-weight: bold")

        layout.addWidget(top_label)
        layout.addWidget(HorizontalLine())
        layout.addWidget(self._commit_btn)

        self._form = QFormLayout()

        self.setLayout(layout)
        layout.addLayout(self._form)

        self._populate_investigators()
        self._populate_instruments()
        self._populate_flowcells()
        self._populate_reagent_kits()
        self._populate_read_cycles()

        self._instrument_cb.currentTextChanged.connect(
            self._populate_flowcells
        )
        self._flowcell_cb.currentTextChanged.connect(
            self._populate_reagent_kits
        )
        self._flowcell_cb.currentTextChanged.connect(
            self._populate_read_cycles
        )
        self._reagent_kit_cb.currentTextChanged.connect(
            self._populate_read_cycles
        )
        self._read_cycles_cb.currentTextChanged.connect(
            self._set_custom_read_cycle_validator
        )

        self._setup_ui()

        layout.addStretch()

        self._commit_btn.clicked.connect(self._commit)

    def _setup_ui(self):
        self._form.addRow(QLabel("General"))
        self._form.addRow("Investigator", self._investigator_cb)
        self._form.addRow("Run Name", self._run_name_le)
        self._form.addRow("Run Description", self._run_description_le)
        self._form.addRow(QLabel("Sequencing"))
        self._form.addRow("Instrument", self._instrument_cb)
        self._form.addRow("Flowcell", self._flowcell_cb)
        self._form.addRow("Reagent Kit", self._reagent_kit_cb)
        self._form.addRow("Read Cycles", self._read_cycles_cb)
        self._form.addRow("Custom Read Cycles", self._custom_read_cycles_le)

    def _populate_instruments(self):
        instruments = self._configuration_manager.instruments
        self._instrument_cb.clear()
        self._instrument_cb.addItems(instruments)

    def _populate_flowcells(self):
        current_instrument = self._instrument_cb.currentText()
        flowcells = self._configuration_manager.instrument_flowcells[current_instrument][
            "Flowcell"
        ].keys()
        self._flowcell_cb.clear()
        self._flowcell_cb.addItems(flowcells)

    def _populate_reagent_kits(self):
        current_instrument = self._instrument_cb.currentText()

        if not len(current_instrument) > 0:
            return

        current_flowcell = self._flowcell_cb.currentText()

        if not len(current_flowcell) > 0:
            return

        reagent_kits = list(
            self._configuration_manager.instrument_flowcells[current_instrument]["Flowcell"][
                current_flowcell
            ]["ReagentKit"].keys()
        )

        self._reagent_kit_cb.clear()
        self._reagent_kit_cb.addItems(reagent_kits)

    def _populate_read_cycles(self):
        current_instrument = self._instrument_cb.currentText()

        if not len(current_instrument) > 0:
            return

        current_flowcell = self._flowcell_cb.currentText()

        if not len(current_flowcell) > 0:
            return

        current_reagent_kit = self._reagent_kit_cb.currentText()

        if not len(current_reagent_kit) > 0:
            return

        read_cycles = self._configuration_manager.instrument_flowcells[current_instrument]["Flowcell"][
            current_flowcell
        ]["ReagentKit"][current_reagent_kit]
        self._read_cycles_cb.clear()
        self._read_cycles_cb.addItems(read_cycles)

        self._custom_read_cycles_le.clear()
        template = self._read_cycles_cb.currentText()
        self._custom_read_cycles_le.setValidator(PatternValidator(template))  # self.input_widgets["CustomReadCycles"].setValidator(PatternValidator(template))

    @Slot()
    def _populate_investigators(self):
        users = self._configuration_manager.users
        self._investigator_cb.clear()
        self._investigator_cb.addItems(users)

    def _set_custom_read_cycle_validator(self):
        self._custom_read_cycles_le.clear()
        template = self._read_cycles_cb.currentText()  # self.input_widgets["ReadCycles"].currentText()
        self._custom_read_cycles_le.setValidator(PatternValidator(template))

    def _commit(self):
        """Commit the data from the input widgets."""

        self._state_model.set_investigator(self._investigator_cb.currentText())
        self._state_model.set_run_name(self._run_name_le.text())
        self._state_model.set_run_description(self._run_description_le.text())
        self._state_model.set_instrument(self._instrument_cb.currentText())
        self._state_model.set_flowcell(self._flowcell_cb.currentText())
        self._state_model.set_reagent_kit(self._reagent_kit_cb.currentText())

        read_cycles = self._read_cycles_cb.currentText()
        read1_cycles, index1_cycles, index2_cycles, read2_cycles = read_cycles.split("-")

        self._state_model.set_read1_cycles(int(read1_cycles))
        self._state_model.set_read2_cycles(int(read2_cycles))
        self._state_model.set_index1_cycles(int(index1_cycles))
        self._state_model.set_index2_cycles(int(index2_cycles))

        self._state_model.set_lookup_data()

    @staticmethod
    def extract_data(widget):
        """Extract data from the given widget."""
        if isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QLineEdit):
            return widget.text()

    def _validate_read_cycles(self, data):
        """Validate the readcycles field."""
        read_cycles = list(map(int, data["ReadCycles"].split("-")))
        index_maxlens = self.dataset_mgr.index_maxlens()

        for i, value in enumerate(read_cycles):
            if index_maxlens is not None:
                if i == 1 and index_maxlens["IndexI7_maxlen"] > value:
                    return False
                if i == 2 and index_maxlens["IndexI5_maxlen"] > value:
                    return False

        return True
