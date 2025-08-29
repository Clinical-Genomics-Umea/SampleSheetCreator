from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QSizePolicy,
    QVBoxLayout,
    QPushButton,
    QWidget,
    QHBoxLayout,
    QFormLayout,
    QLabel,
)

from modules.utils.utils import int_list_to_int_str


class RunInfoView(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

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


        self._date_lbl = QLabel("None")
        self._investigator_lbl = QLabel("None")
        self._run_name_lbl = QLabel("None")
        self._run_desc_lbl = QLabel("None")

        self._instrument_lbl = QLabel("None")
        self._flowcell_lbl = QLabel("None")
        self._lanes_lbl = QLabel("None")
        self._reagent_kit_lbl = QLabel("None")
        self._chemistry_lbl = QLabel("None")
        self._i5_seq_orientation_lbl = QLabel("None")

        self._read1_cycles_lbl = QLabel("None")
        self._index1_cycles_lbl = QLabel("None")
        self._index2_cycles_lbl = QLabel("None")
        self._read2_cycles_lbl = QLabel("None")
        self._custom_cycles_lbl = QLabel("False")

        self._assess_color_balance_lbl = QLabel("None")

        self._uuid_lbl = QLabel("None")

        self._a_lbl = QLabel("None")
        self._t_lbl = QLabel("None")
        self._g_lbl = QLabel("None")
        self._c_lbl = QLabel("None")

        self._index1_minlen_lbl = QLabel("0")
        self._index1_maxlen_lbl = QLabel("0")
        self._index2_minlen_lbl = QLabel("0")
        self._index2_maxlen_lbl = QLabel("0")

        self._sample_profile_names_lbl = QLabel("None")

        self._setup()

    def _setup(self):
        # General
        form_general = QFormLayout()
        form_general.setContentsMargins(0, 0, 0, 0)
        form_general.addRow(QLabel("General"))
        form_general.addRow(QLabel("Date:"), self._date_lbl)
        form_general.addRow(QLabel("Investigator:"), self._investigator_lbl)
        form_general.addRow(QLabel("RunName:"), self._run_name_lbl)
        form_general.addRow(QLabel("RunDescription:"), self._run_desc_lbl)
        form_general.addRow(QLabel("UUID:"), self._uuid_lbl)
        self.content_layout.addLayout(form_general)


        # Sequencing
        form_sequencing = QFormLayout()
        form_sequencing.setContentsMargins(0, 0, 0, 0)
        form_sequencing.addRow(QLabel("Sequencing"))
        form_sequencing.addRow(QLabel("Instrument:"), self._instrument_lbl)
        form_sequencing.addRow(QLabel("Flowcell:"), self._flowcell_lbl)
        form_sequencing.addRow(QLabel("Lanes:"), self._lanes_lbl)
        form_sequencing.addRow(QLabel("ReagentKit"), self._reagent_kit_lbl)
        form_sequencing.addRow(QLabel("Chemistry:"), self._chemistry_lbl)
        self.content_layout.addLayout(form_sequencing)

        # Read cycles
        form_read_cycles = QFormLayout()
        form_read_cycles.setContentsMargins(0, 0, 0, 0)
        form_read_cycles.addRow(QLabel("ReadCycles"))

        form_read_cycles.addRow(QLabel("Read1Cycles:"), self._read1_cycles_lbl)
        form_read_cycles.addRow(QLabel("Index1Cycles:"), self._index1_cycles_lbl)
        form_read_cycles.addRow(QLabel("Index2Cycles:"), self._index2_cycles_lbl)
        form_read_cycles.addRow(QLabel("Read2Cycles:"), self._read2_cycles_lbl)
        form_read_cycles.addRow(QLabel("CustomCycles:"), self._custom_cycles_lbl)
        self.content_layout.addLayout(form_read_cycles)

        # Validation
        form_validation = QFormLayout()
        form_validation.setContentsMargins(0, 0, 0, 0)
        form_validation.addRow(QLabel("Validation"))
        form_validation.addRow(QLabel("ColorBalance:"), self._assess_color_balance_lbl)
        self.content_layout.addLayout(form_validation)



        # Colors
        form_colors = QFormLayout()
        form_colors.setContentsMargins(0, 0, 0, 0)
        form_colors.addRow(QLabel("Colors"))

        form_colors.addRow(QLabel("A:"), self._a_lbl)
        form_colors.addRow(QLabel("T:"), self._t_lbl)
        form_colors.addRow(QLabel("G:"), self._g_lbl)
        form_colors.addRow(QLabel("C:"), self._c_lbl)
        self.content_layout.addLayout(form_colors)

        # Sample Index lengths
        form_sample_data = QFormLayout()
        form_sample_data.setContentsMargins(0, 0, 0, 0)
        form_sample_data.addRow(QLabel("Sample overview"))

        form_sample_data.addRow(QLabel("Index1 min:"), self._index1_minlen_lbl)
        form_sample_data.addRow(QLabel("Index1 max:"), self._index1_maxlen_lbl)
        form_sample_data.addRow(QLabel("Index2 min:"), self._index2_minlen_lbl)
        form_sample_data.addRow(QLabel("Index2 max:"), self._index2_maxlen_lbl)
        form_sample_data.addRow(QLabel("Application profile names:"), self._sample_profile_names_lbl)
        self.content_layout.addLayout(form_sample_data)

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


    def set_run_cycles_labels(self, read1_cycles: int, index1_cycles: int, index2_cycles: int, read2_cycles: int):
        self._read1_cycles_lbl.setText(str(read1_cycles))
        self._index1_cycles_lbl.setText(str(index1_cycles))
        self._index2_cycles_lbl.setText(str(index2_cycles))
        self._read2_cycles_lbl.setText(str(read2_cycles))

    def set_date_label(self, date: str):
        self._date_lbl.setText(date)

    def set_investigator_label(self, investigator: str):
        self._investigator_lbl.setText(investigator)

    def set_run_name_label(self, run_name: str):
        self._run_name_lbl.setText(run_name)

    def set_run_desc_label(self, run_desc: str):
        self._run_desc_lbl.setText(run_desc)

    def set_instrument_label(self, instrument: str):
        self._instrument_lbl.setText(instrument)

    def set_flowcell_label(self, flowcell: str):
        self._flowcell_lbl.setText(flowcell)

    def set_lanes_label(self, lanes: list[int]):
        lanes = int_list_to_int_str(lanes)
        self._lanes_lbl.setText(lanes)

    def set_reagent_kit_label(self, reagent_kit: str):
        self._reagent_kit_lbl.setText(reagent_kit)

    def set_chemistry_label(self, chemistry: str):
        self._chemistry_lbl.setText(chemistry)

    def set_i5_seq_orientation_label(self, i5_seq_orientation: str):
        self._i5_seq_orientation_lbl.setText(i5_seq_orientation)

    def set_uuid(self, uuid: str):
        self._uuid_lbl.setText(uuid)

    # def set_bcl2fastq_ss_i5_orient_lbl(self, bcl2fastq_ss_i5_orient: str):
    #     self._bcl2fastq_ss_i5_orient_lbl.setText(bcl2fastq_ss_i5_orient)
    #
    # def set_bclconvert_ss_i5_orient_lbl(self, bclconvert_ss_i5_orient: str):
    #     self._bclconvert_ss_i5_orient_lbl.setText(bclconvert_ss_i5_orient)

    def set_read1_cycles_label(self, read1_cycles: int):
        self._read1_cycles_lbl.setText(str(read1_cycles))

    def set_index1_cycles_label(self, index1_cycles: int):
        self._index1_cycles_lbl.setText(str(index1_cycles))

    def set_index2_cycles_label(self, index2_cycles: int):
        self._index2_cycles_lbl.setText(str(index2_cycles))

    def set_read2_cycles_label(self, read2_cycles: int):
        self._read2_cycles_lbl.setText(str(read2_cycles))

    def set_custom_cycles_label(self, custom_cycles: bool):
        self._custom_cycles_lbl.setText(str(custom_cycles))

    def set_assess_color_balance_label(self, assess_color_balance: bool):
        self._assess_color_balance_lbl.setText(str(assess_color_balance))

    def set_a_label(self, a: str):
        a_str = str(a)
        self._a_lbl.setText(a_str)

    def set_t_label(self, t: str):
        t_str = str(t)
        self._t_lbl.setText(t_str)

    def set_g_label(self, g: str):
        g_str = str(g)
        self._g_lbl.setText(g_str)

    def set_c_label(self, c: str):
        c_str = str(c)
        self._c_lbl.setText(c_str)

    def set_sample_index1_minlen_label(self, current_index1_minlen: int):
        self._index1_minlen_lbl.setText(str(current_index1_minlen))

    def set_sample_index1_maxlen_label(self, current_index1_maxlen: int):
        self._index1_maxlen_lbl.setText(str(current_index1_maxlen))

    def set_sample_index2_minlen_label(self, current_index2_minlen: int):
        self._index2_minlen_lbl.setText(str(current_index2_minlen))

    def set_sample_index2_maxlen_label(self, current_index2_maxlen: int):
        self._index2_maxlen_lbl.setText(str(current_index2_maxlen))

    # def set_bcl2fastq_ss_i5_orient_label(self, bcl2fastq: str):
    #     self._bcl2fastq_ss_i5_orient_lbl.setText(bcl2fastq)
    #
    # def set_bclconvert_ss_i5_orient_label(self, bclconvert: str):
    #     self._bclconvert_ss_i5_orient_lbl.setText(bclconvert)

    def set_profile_names(self, profile_names: list[str]):
        if isinstance(profile_names, list):
            self._sample_profile_names_lbl.setText(", ".join(profile_names))
        else:
            self._sample_profile_names_lbl.setText(str(profile_names) if profile_names is not None else "None")