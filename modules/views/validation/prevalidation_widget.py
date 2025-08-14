from enum import Enum, auto
from typing import List, Tuple, Optional, Dict, Any

from PySide6.QtCore import Qt, Slot, QSize, Signal
from PySide6.QtGui import (QBrush, QColor, QFont, QIcon, QPainter, 
                          QPalette, QPixmap, QStandardItemModel)
from PySide6.QtWidgets import (QAbstractItemView, QCheckBox, QComboBox, QFrame, 
                              QHBoxLayout, QHeaderView, QLabel, QLineEdit, 
                              QPushButton, QSizePolicy, QStyle, QStyledItemDelegate,
                              QTableWidget, QTableWidgetItem, QToolButton, 
                              QVBoxLayout, QWidget)

from modules.models.validation.prevalidation.validators import ValidationResult, StatusLevel


class StatusLevel(Enum):
    """Severity levels for validation results."""
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


class LevelDelegate(QStyledItemDelegate):
    """Custom delegate for rendering severity levels with background colors."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.colors = {
            "INFO": QColor(230, 245, 230),  # Light green
            "WARNING": QColor(255, 250, 205),  # Light yellow
            "ERROR": QColor(255, 230, 230)  # Light red
        }
        self.text_colors = {
            "INFO": QColor(0, 100, 0),  # Dark green
            "WARNING": QColor(153, 102, 0),  # Dark yellow/brown
            "ERROR": QColor(139, 0, 0)  # Dark red
        }
    
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        severity = index.data(Qt.DisplayRole)
        if severity in self.colors:
            option.backgroundBrush = QBrush(self.colors[severity])
            option.palette.setColor(QPalette.Text, self.text_colors[severity])
            option.palette.setColor(QPalette.HighlightedText, self.text_colors[severity])


class StatusDelegate(QStyledItemDelegate):
    """Custom delegate for rendering status with background colors."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.colors = {
            "SUCCESS": QColor(230, 245, 230),  # Light green
            "FAIL": QColor(255, 230, 230)  # Light red
        }
        self.text_colors = {
            "SUCCESS": QColor(0, 100, 0),  # Dark green
            "FAIL": QColor(139, 0, 0)  # Dark red
        }
    
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        status = index.data(Qt.DisplayRole)
        if status in self.colors:
            option.backgroundBrush = QBrush(self.colors[status])
            option.palette.setColor(QPalette.Text, self.text_colors[status])
            option.palette.setColor(QPalette.HighlightedText, self.text_colors[status])

class GeneralValidationWidget(QWidget):
    """Widget for displaying validation results with filtering and sorting capabilities."""
    
    # Signal emitted when validation status changes
    validation_status_changed = Signal(bool)  # True if all validations passed
    
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize UI components
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        # Severity filter
        self.severity_filter = QComboBox()
        self.severity_filter.addItem("All", None)
        self.severity_filter.addItem("Info Only", StatusLevel.INFO)
        self.severity_filter.addItem("Warnings", StatusLevel.WARNING)
        self.severity_filter.addItem("Errors", StatusLevel.ERROR)
        self.severity_filter.currentIndexChanged.connect(self._apply_filters)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search messages...")
        self.search_box.textChanged.connect(self._apply_filters)
        
        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear)
        
        # Add controls to filter layout
        filter_layout.addWidget(QLabel("Filter by:"))
        filter_layout.addWidget(self.severity_filter)
        filter_layout.addWidget(QLabel("Search:"))
        filter_layout.addWidget(self.search_box, 1)  # Allow search box to expand
        filter_layout.addWidget(clear_btn)
        
        # Results summary
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("font-weight: bold;")
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Validator", "Status", "Level", "Message"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        
        # Set custom delegate for status column
        # self.table.setItemDelegateForColumn(2, LevelDelegate(self))
        # self.table.setItemDelegateForColumn(1, StatusDelegate(self))
        
        # Add widgets to main layout
        layout.addLayout(filter_layout)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.table, 1)  # Allow table to expand

    def _add_row(self, name: str, level: StatusLevel, message: str):
        # Get the string name of the enum value (e.g., 'INFO', 'WARNING', 'ERROR')
        level_str = level.name if level else "UNKNOWN"
        
        # Set status based on severity level
        # INFO level means validation passed, WARNING or ERROR means it failed
        # We also check if the message is empty, as some validations might pass with no message
        status_str = "SUCCESS" if (level and level.name == 'INFO' or level.name == 'WARNING') or not message.strip() else "FAIL"


        # Insert new row
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        
        # Validator name
        name_item = QTableWidgetItem()
        name_item.setData(Qt.DisplayRole, str(name))
        name_item.setTextAlignment(Qt.AlignLeft)
        name_item.setToolTip(name)
        
        # Status with severity icon
        status_item = QTableWidgetItem()
        status_item.setData(Qt.DisplayRole, str(status_str))
        status_item.setTextAlignment(Qt.AlignCenter)

        level_item = QTableWidgetItem()
        level_item.setData(Qt.DisplayRole, level_str)
        level_item.setTextAlignment(Qt.AlignCenter)

        message_item = QTableWidgetItem()
        message_item.setData(Qt.DisplayRole, str(message))
        message_item.setTextAlignment(Qt.AlignCenter)

        # Set items in table
        self.table.setItem(row_count, 0, name_item)
        self.table.setItem(row_count, 1, status_item)
        self.table.setItem(row_count, 2, level_item)
        self.table.setItem(row_count, 3, message_item)


    def _update_summary(self):
        """Update the summary label with current validation status.
        
        The summary will report:
        - All validations passed successfully (if all rows have 'SUCCESS' status)
        - Validation failed (if any row has 'FAIL' status)
        """
        if not hasattr(self, 'table') or self.table.rowCount() == 0:
            self.summary_label.setText("No validation results to display.")
            self.validation_status_changed.emit(True)
            return
        
        total = self.table.rowCount()
        has_failures = False
        
        # Check if any row has 'FAIL' status
        for i in range(total):
            status_item = self.table.item(i, 1)
            if status_item and status_item.text() == "FAIL":
                has_failures = True
                break
        
        if has_failures:
            self.summary_label.setText(
                f"<span style='color: #cc0000;'>Validation failed - check validation results below</span>"
            )
            self.validation_status_changed.emit(False)
        else:
            self.summary_label.setText(
                f"<span style='color: #009900;'>All {total} validations passed successfully!</span>"
            )
            self.validation_status_changed.emit(True)
    
    def _apply_filters(self):
        """Apply filters to show/hide rows based on current filter settings."""
        if not hasattr(self, 'table'):
            return
            
        severity_filter = self.severity_filter.currentData()
        search_text = self.search_box.text().lower()
        
        for row in range(self.table.rowCount()):
            # Get item data
            message = self.table.item(row, 2).text().lower()
            severity = self.table.item(row, 1).data(Qt.UserRole)
            
            # Apply filters
            show = True
            if severity_filter and severity != severity_filter:
                show = False
            if search_text and search_text not in message:
                show = False
                
            # Show/hide row
            self.table.setRowHidden(row, not show)
    
    def clear(self):
        """Clear all validation results and reset the widget."""
        if hasattr(self, 'table'):
            self.table.setRowCount(0)
        if hasattr(self, 'summary_label'):
            self.summary_label.clear()
        if hasattr(self, 'search_box'):
            self.search_box.clear()
        if hasattr(self, 'severity_filter'):
            self.severity_filter.setCurrentIndex(0)
        
        self._has_errors = False
        self._has_warnings = False
        self.validation_status_changed.emit(True)
    
    @Slot(list)
    def populate(self, validation_results: List[ValidationResult]):
        """Populate the widget with validation results.
        
        Args:
            validation_results: List of tuples containing:
                - validator_name: Name of the validator
                - is_valid: Whether validation passed
                - message: Validation message
                - severity: Severity level (optional, defaults to ERROR for failures)
        """
        self.clear()
        
        if not validation_results:
            self._update_summary()
            return
        
        for result in validation_results:
            self._add_row(result.name, result.severity, result.message)

        # Set up delegates for status and level columns
        self.table.setItemDelegateForColumn(1, StatusDelegate(self.table))
        self.table.setItemDelegateForColumn(2, LevelDelegate(self.table))
        
        # Update summary and apply initial filters
        self._update_summary()
        self._apply_filters()
        
        # Auto-expand the table to show all content
        self.table.resizeRowsToContents()
