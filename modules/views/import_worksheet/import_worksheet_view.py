from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QVBoxLayout, QTableWidget, QSplitter,
                               QTableView, QDialog, QDialogButtonBox,
                               QPushButton, QProgressDialog, QApplication, QLabel, QProgressBar, QHBoxLayout,
                               QGraphicsDropShadowEffect, QWidget)
from PySide6.QtCore import Qt, Signal, QTimer

from modules.models.workdata.workdata_manager import WorkDataManager
from modules.models.workdata.worksheet_id_model import WorkSheetIDModel
from modules.models.workdata.worksheets_models import WorksheetSamplesModel, \
    WorksheetDetailProxyModel as WorkSheetIDModelProxyModel, WorksheetIDModel, WorksheetDetailProxyModel


class FetchWorksheetView(QDialog):
    """
    A widget that displays worksheets in a master-detail view.
    Left table shows worksheet names and creation dates.
    Right table shows the contents of the selected worksheet.
    """

    # def __init__(self, model: WorkDataModel, parent=None):
    # Signal emitted when fetch button is clicked
    refresh_worksheet_data = Signal()
    import_data = Signal()
    selected_worklist_id = Signal(str)

    def __init__(self, workdata_manager: WorkDataManager):
        super().__init__()

        self._workdata_manager = workdata_manager

        # Set up the UI
        self.setup_ui()

        # Set dialog properties
        self.setWindowTitle("Fetch WorkSheet Data")
        self.setModal(True)
        self.setMinimumSize(1000, 600)

        # Initialize proxy models
        self._detail_proxy_model = WorksheetDetailProxyModel()

        # Set up models after UI is ready
        self._worksheet_id_table.setModel(self._workdata_manager.worksheet_id_model)
        self._detail_proxy_model.setSourceModel(self._workdata_manager.worksheet_samples_model)
        self._detail_table.setModel(self._detail_proxy_model)

        # Set up loading dialog
        self._loading_dialog = LoadingDialog("Fetching worksheet data...", self)
        self._loading_dialog.rejected.connect(self._on_loading_canceled)

        # Connect workdata manager signals
        self._workdata_manager.loading_state_changed.connect(self.on_loading_state_changed)
        self.import_button.clicked.connect(self.import_data)

        # Now it's safe to connect the selection model
        self._worksheet_id_table.selectionModel().selectionChanged.connect(self.on_worksheet_selected)


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
        self._worksheet_id_table = QTableView()
        self._worksheet_id_table.setSelectionBehavior(QTableWidget.SelectRows)
        self._detail_table = QTableView()
        #

        # Add tables to splitter
        splitter.addWidget(self._worksheet_id_table)
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


    def on_loading_state_changed(self, loading: bool):
        """Handle loading state changes from the workdata manager."""
        self.fetch_button.setEnabled(not loading)
        
        if loading:
            # Show the dialog immediately
            self._loading_dialog.show()
        else:
            # Hide the dialog immediately
            self._loading_dialog.hide()
            
        # Force the UI to update
        QApplication.processEvents()
    
    def _on_loading_canceled(self):
        """Handle cancellation of the loading operation."""
        # Note: This won't actually cancel the HTTP request, just hide the dialog
        # To properly cancel, we'd need to implement request cancellation in WorkDataManager
        self._loading_dialog.hide()
        self.fetch_button.setEnabled(True)
    
    def fetch_data(self):
        """Fetch fresh data from the data source."""
        self.refresh_worksheet_data.emit()

    def on_worksheet_selected(self):
        """Handle worksheet selection change."""
        selected = self._worksheet_id_table.selectionModel().selectedRows()
        if not selected:
            return

        # Get the first selected row
        row = selected[0].row()

        worksheet_index = self._worksheet_id_table.model().index(row, 0)
        worksheet_id = worksheet_index.data()

        self.selected_worklist_id.emit(worksheet_id)

        # Update the content proxy model
        if worksheet_id:
            self._detail_proxy_model.set_worksheet_filter(worksheet_id)


# class LoadingDialog(QDialog):
#     def __init__(self, message="Loading...", parent=None):
#         super().__init__(parent)
#         self.setWindowTitle("Loading")
#         self.setModal(True)
#         self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
#
#         layout = QVBoxLayout(self)
#
#         # Message label
#         self.label = QLabel(message)
#         layout.addWidget(self.label)
#
#         # Indeterminate progress bar
#         self.progress = QProgressBar()
#         self.progress.setRange(0, 0)  # Indeterminate
#         layout.addWidget(self.progress)
#
#         # Cancel button (optional)
#         self.cancel_btn = QPushButton("Cancel")
#         self.cancel_btn.clicked.connect(self.reject)
#         layout.addWidget(self.cancel_btn)
#
#         self.setFixedSize(300, 120)
#

class LoadingDialog(QDialog):
    def __init__(self, message="Loading...", parent=None):
        super().__init__(parent)

        # Set window properties for a clean, modern look
        self.setWindowFlags(
            Qt.FramelessWindowHint |  # Remove window frame
            Qt.Dialog |
            Qt.WindowStaysOnTopHint  # Keep on top of other windows
        )

        # Set window attributes for a modern look
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)

        # Main layout with some padding
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Container widget for the content (for better shadow effect)
        container = QWidget()
        container.setObjectName("container")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(25, 25, 25, 25)
        container_layout.setSpacing(20)


        # Message label with styling
        self.label = QLabel(message)
        self.label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333;
                padding: 5px;
                font-weight: 500;
                text-align: center;
            }
        """)

        # Progress bar with modern styling
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(4)
        self.progress.setStyleSheet("""
            QProgressBar {
                border-radius: 2px;
                background-color: #e0e0e0;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 2px;
            }
        """)

        # Add widgets to container
        container_layout.addWidget(self.label)
        container_layout.addWidget(self.progress)

        # Add container to main layout
        layout.addWidget(container)

        # Set fixed size for the dialog
        self.setFixedSize(280, 140)

        # Apply styles to the container and dialog
        self.setStyleSheet("""
            QDialog {
                background: transparent;
            }
            #container {
                background-color: white;
                border-radius: 12px;
            }
        """)

        # Add a subtle shadow effect to the container
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 30))
        container.setGraphicsEffect(shadow)

    def set_message(self, message: str):
        """Update the loading message."""
        self.label.setText(message)