from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QHeaderView, QSplitter, QLabel, QTableView, QDialog)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont

from modules.models.workdata.workdata_model import WorkDataModel, UniqueWorksheetCreatedProxyModel, \
    WorksheetFilterProxyModel


class FetchWorkDataView(QDialog):
    """
    A widget that displays worksheets in a master-detail view.
    Left table shows worksheet names and creation dates.
    Right table shows the contents of the selected worksheet.
    """

    # def __init__(self, model: WorkDataModel, parent=None):
    def __init__(self, model: WorkDataModel):
        super().__init__()

        self._model = model

        # Set up the UI
        self.setup_ui()

        # Set dialog properties
        self.setWindowTitle("Fetch Work Data")
        self.setModal(True)
        self.setMinimumSize(1000, 600)

        # # Initialize proxy models
        self._unique_worksheet_proxy_model = UniqueWorksheetCreatedProxyModel()
        self._content_proxy_model = WorksheetFilterProxyModel()

        # Set up models after UI is ready
        self._unique_worksheet_proxy_model.setSourceModel(self._model)
        self._worksheets_table.setModel(self._unique_worksheet_proxy_model)

        self._content_proxy_model.setSourceModel(self._model)
        self._contents_table.setModel(self._content_proxy_model)


        self._worksheets_table.selectionModel().selectionChanged.connect(self.on_worksheet_selected)


    def setup_ui(self):
        """Initialize the UI components."""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Add title
        self.setLayout(main_layout)

        # Create splitter for the two tables
        splitter = QSplitter(Qt.Horizontal)

        # Create worksheets table (left)
        self._worksheets_table = QTableView()
        # self._worksheets_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        # self._worksheets_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._worksheets_table.setSelectionBehavior(QTableWidget.SelectRows)
        # self._worksheets_table.setSelectionMode(QTableWidget.SingleSelection)
        #
        # Create contents table (right)
        self._contents_table = QTableView()
        #
        # for i in range(3):
        #     self._contents_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
        #
        # Add tables to splitter
        splitter.addWidget(self._worksheets_table)
        splitter.addWidget(self._contents_table)
        splitter.setSizes([300, 600])  # Initial sizes
        #
        # # Add splitter to main layout
        main_layout.addWidget(splitter)

    def on_worksheet_selected(self):
        """Handle worksheet selection change."""
        selected = self._worksheets_table.selectionModel().selectedRows()
        if not selected:
            return

        # Get the first selected row
        row = selected[0].row()
        worksheet_index = self._worksheets_table.model().index(row, 0)
        worksheet_name = worksheet_index.data()

        # Update the content proxy model
        if worksheet_name:
            self._content_proxy_model.set_worksheet(worksheet_name)
