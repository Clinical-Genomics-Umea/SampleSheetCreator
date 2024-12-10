from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSizePolicy,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QTextEdit,
    QHBoxLayout,
    QPushButton,
    QHeaderView,
)


class ExportWidget(QWidget):
    def __init__(self, dataset_mgr, parent=None):
        super().__init__(parent)

        self.dataset_mgr = dataset_mgr

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.json_tree = None
        self.samplesheet = None

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        self.show_json_btn = QPushButton("Show Data")
        self.export_json_btn = QPushButton("Export Json")
        self.export_samplesheet_v2_btn = QPushButton("Export SampleSheet V2")

        hbox.addWidget(self.show_json_btn)
        hbox.addWidget(self.export_json_btn)
        hbox.addWidget(self.export_samplesheet_v2_btn)
        hbox.addStretch()

        self.layout.addLayout(hbox)
        self.layout.addWidget(self.tab_widget)
        self.show_json_btn.clicked.connect(self.show_data_tree)
        self.export_samplesheet_v2_btn.clicked.connect(self.export_samplesheet_v2)

    def show_data_tree(self):
        if self.json_tree:
            self.json_tree.deleteLater()

        data = self.dataset_mgr.samplesheet_obj()

        print(data)

        self.json_tree = JsonTreeWidget(data)
        header = self.json_tree.header()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tab_widget.addTab(self.json_tree, "Data Structure")

    def export_json(self):
        pass

    def export_samplesheet_v2(self):
        pass

    # def populate(self, data):
    #     self._clear_tabs()
    #
    #     self.json_tree = JsonTreeWidget(data)
    #     self.tab_widget.addTab(self.json_tree, "JSON Tree")
    #
    # def _clear_tabs(self):
    #     # Remove and delete each tab widget
    #     while self.tab_widget.count() > 0:
    #         widget = self.tab_widget.widget(0)  # Get the first widget in the tab widget
    #         self.tab_widget.removeTab(0)  # Remove the tab
    #         widget.deleteLater()


class JsonTreeWidget(QTreeWidget):
    def __init__(self, json_data, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(["Key", "Value"])
        self.setColumnCount(2)
        self.load_json(json_data)

    def load_json(self, json_data):
        """Populate the QTreeWidget with the JSON data."""
        self.clear()
        self._populate_tree(self, json_data)

    def _populate_tree(self, parent, json_data):
        """Recursive function to add JSON data to the tree."""
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                item = QTreeWidgetItem(parent, [key, ""])
                self._populate_tree(item, value)
        elif isinstance(json_data, list):
            for index, value in enumerate(json_data):
                item = QTreeWidgetItem(parent, [f"[{index}]", ""])
                self._populate_tree(item, value)
        else:
            # Primitive value, set as a leaf
            QTreeWidgetItem(parent, ["", str(json_data)])


class SampleSheetWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
