from PySide6.QtWidgets import (QVBoxLayout, QTableWidget,QSplitter,
                               QTableView, QDialog, QDialogButtonBox, QPushButton)
from PySide6.QtCore import Qt, Signal


from modules.models.workdata.worksheets_models import WorksheetPandasModel, UniqueWorksheetProxyModel, \
    WorksheetDetailProxyModel


class FetchWorksheetView(QDialog):
    """
    A widget that displays worksheets in a master-detail view.
    Left table shows worksheet names and creation dates.
    Right table shows the contents of the selected worksheet.
    """

    # def __init__(self, model: WorkDataModel, parent=None):
    # Signal emitted when fetch button is clicked
    refresh_worksheet_data = Signal()

    def __init__(self, worksheets_model: WorksheetPandasModel):
        super().__init__()

        self._worksheets_model = worksheets_model

        # Set up the UI
        self.setup_ui()

        # Set dialog properties
        self.setWindowTitle("Fetch WorkSheet Data")
        self.setModal(True)
        self.setMinimumSize(1000, 600)

        # self._worksheets_table.setModel(self._model)

        # Initialize proxy models
        self._unique_worksheet_proxy_model = UniqueWorksheetProxyModel()
        self._detail_proxy_model = WorksheetDetailProxyModel()

        # Set up models after UI is ready
        self._unique_worksheet_proxy_model.setSourceModel(self._worksheets_model)
        self._worksheets_table.setModel(self._unique_worksheet_proxy_model)

        self._detail_proxy_model.setSourceModel(self._worksheets_model)
        self._detail_table.setModel(self._detail_proxy_model)

        # Now it's safe to connect the selection model
        self._worksheets_table.selectionModel().selectionChanged.connect(self.on_worksheet_selected)

    def update_dataframe(self, df):
        """Update the model with a new DataFrame and refresh views"""
        # Update the model
        self._worksheets_model.set_dataframe(df)

        # Reset the unique worksheet filter so it recalculates unique values
        self._unique_worksheet_proxy_model.reset_filter()

        # Clear the detail view selection
        self._detail_proxy_model.set_worksheet_filter(None)

        # Clear selection in worksheet view
        self._worksheets_table.clearSelection()

        # Re-hide columns in worksheet view (they become visible after model reset)
        for col in range(1, len(df.columns)):
            colname = df.columns[col]

            if not colname == "WorksheetID":
                self._worksheets_table.setColumnHidden(col, True)


    def setup_ui(self):
        """Initialize the UI components."""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Add title
        self.setLayout(main_layout)

        # Create fetch button
        self.fetch_button = QPushButton("Fetch Data")
        self.fetch_button.clicked.connect(self.fetch_data)
        main_layout.addWidget(self.fetch_button)
        
        # Add some spacing
        main_layout.addSpacing(10)

        # Create splitter for the two tables
        splitter = QSplitter(Qt.Horizontal)

        # Create worksheets table (left)
        self._worksheets_table = QTableView()
        self._worksheets_table.setSelectionBehavior(QTableWidget.SelectRows)
        self._detail_table = QTableView()
        #

        # Add tables to splitter
        splitter.addWidget(self._worksheets_table)
        splitter.addWidget(self._detail_table)
        splitter.setSizes([300, 600])  # Initial sizes
        #
        # # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Create button box for Import and Close buttons
        button_box = QDialogButtonBox(Qt.Horizontal, self)
        
        # Create buttons
        self.import_button = QPushButton("Import")
        close_button = QPushButton("Close")
        
        # Connect buttons
        self.import_button.clicked.connect(self.accept)
        close_button.clicked.connect(self.reject)
        
        # Add buttons to button box
        button_box.addButton(self.import_button, QDialogButtonBox.AcceptRole)
        button_box.addButton(close_button, QDialogButtonBox.RejectRole)
        
        # Add button box to main layout
        main_layout.addWidget(button_box)

    def update_worksheet_visibility(self):
        worksheet_col = self._worksheets_model.get_column_index("WorksheetID")

        # Otherwise, show only the WorksheetID column
        for col in range(self._worksheets_model.columnCount()):

            print(col, col != worksheet_col)

            self._worksheets_table.setColumnHidden(col, col != worksheet_col)


    def fetch_data(self):
        """Fetch fresh data from the data source."""
        self.refresh_worksheet_data.emit()

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
            self._detail_proxy_model.set_worksheet_filter(worksheet_name)
