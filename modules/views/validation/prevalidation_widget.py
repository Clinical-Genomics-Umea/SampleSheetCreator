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


class Severity(Enum):
    """Severity levels for validation results."""
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


class SeverityDelegate(QStyledItemDelegate):
    """Custom delegate for rendering severity icons in the table."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.icons = {
            Severity.INFO: self._create_icon(Qt.blue, "i"),
            Severity.WARNING: self._create_icon(Qt.darkYellow, "!"),
            Severity.ERROR: self._create_icon(Qt.red, "X")
        }
    
    def _create_icon(self, color: Qt.GlobalColor, text: str) -> QIcon:
        """Create a colored icon with the given text."""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(color)
        painter.setBrush(color)
        painter.drawEllipse(2, 2, 12, 12)
        painter.setPen(Qt.white)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, text)
        painter.end()
        return QIcon(pixmap)
    
    def paint(self, painter, option, index):
        """Paint the severity icon in the cell."""
        if index.column() == 1:  # Status column
            severity = index.data(Qt.UserRole)
            if severity in self.icons:
                icon = self.icons[severity]
                icon.paint(painter, option.rect, Qt.AlignCenter)
                return
        super().paint(painter, option, index)


class PreValidationWidget(QWidget):
    """Widget for displaying validation results with filtering and sorting capabilities."""
    
    # Signal emitted when validation status changes
    validation_status_changed = Signal(bool)  # True if all validations passed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Track validation status
        self._has_errors = False
        self._has_warnings = False
        
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
        self.severity_filter.addItem("Info Only", Severity.INFO)
        self.severity_filter.addItem("Warnings", Severity.WARNING)
        self.severity_filter.addItem("Errors", Severity.ERROR)
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
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Validation", "Status", "Message"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        
        # Set custom delegate for status column
        self.table.setItemDelegateForColumn(1, SeverityDelegate(self))
        
        # Add widgets to main layout
        layout.addLayout(filter_layout)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.table, 1)  # Allow table to expand

    def _get_severity_style(self, severity: Severity) -> str:
        """Get the stylesheet for a given severity level.
        
        Args:
            severity: The severity level
            
        Returns:
            str: CSS style string for the severity level
        """
        styles = {
            Severity.INFO: "color: #0066cc;",
            Severity.WARNING: "color: #996600; font-weight: bold;",
            Severity.ERROR: "color: #cc0000; font-weight: bold;"
        }
        return styles.get(severity, "")
    
    def _add_row(self, validator_name: str, is_valid: bool, message: str, severity: Severity = None):
        """Add a validation result row to the table.
        
        Args:
            validator_name: Name of the validator
            is_valid: Whether the validation passed
            message: Validation message
            severity: Severity level (defaults to ERROR for failures, INFO for passes)
        """
        if severity is None:
            severity = Severity.ERROR if not is_valid else Severity.INFO
            
        # Update error/warning tracking
        if severity == Severity.ERROR:
            self._has_errors = True
        elif severity == Severity.WARNING:
            self._has_warnings = True
        
        # Insert new row
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Validator name
        name_item = QTableWidgetItem(validator_name)
        name_item.setToolTip(validator_name)
        
        # Status with severity icon
        status_item = QTableWidgetItem()
        status_item.setData(Qt.DisplayRole, "PASS" if is_valid else "FAIL")
        status_item.setData(Qt.UserRole, severity)  # Store severity for filtering
        status_item.setTextAlignment(Qt.AlignCenter)
        
        # Message with tooltip
        message_item = QTableWidgetItem(message)
        message_item.setToolTip(message)
        
        # Set items in table
        self.table.setItem(row, 0, name_item)
        self.table.setItem(row, 1, status_item)
        self.table.setItem(row, 2, message_item)
        
        # Apply styling based on severity
        for col in range(3):
            item = self.table.item(row, col)
            if item:
                item.setForeground(QBrush(QColor("#333333")))
                if not is_valid:
                    item.setBackground(QBrush(QColor(255, 230, 230)))
                    item.setFont(QFont("", weight=QFont.Bold))
                
                # Apply severity-specific styling
                if severity == Severity.WARNING:
                    item.setBackground(QBrush(QColor(255, 255, 200)))
                elif severity == Severity.INFO and is_valid:
                    item.setForeground(QBrush(QColor(0, 100, 0)))
                    item.setBackground(QBrush(QColor(230, 255, 230)))
    
    def _update_summary(self):
        """Update the summary label with current validation status."""
        if not hasattr(self, 'table') or self.table.rowCount() == 0:
            self.summary_label.setText("No validation results to display.")
            return
        
        total = self.table.rowCount()
        errors = sum(1 for i in range(total) 
                    if self.table.item(i, 1).data(Qt.UserRole) == Severity.ERROR)
        warnings = sum(1 for i in range(total) 
                      if self.table.item(i, 1).data(Qt.UserRole) == Severity.WARNING)
        
        if errors > 0:
            self.summary_label.setText(
                f"<span style='color: #cc0000;'>{errors} errors</span>, "
                f"<span style='color: #996600;'>{warnings} warnings</span> "
                f"({total} total validations)"
            )
            self.validation_status_changed.emit(False)
        elif warnings > 0:
            self.summary_label.setText(
                f"<span style='color: #0066cc;'>All validations passed</span> "
                f"with <span style='color: #996600;'>{warnings} warnings</span> "
                f"({total} total validations)"
            )
            self.validation_status_changed.emit(True)
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
    def populate(self, validation_results: List[Tuple[str, bool, str, str]]):
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
            if len(result) >= 4:
                self._add_row(*result[:4])  # name, is_valid, message, severity
            else:
                # Backward compatibility with old format (name, is_valid, message)
                self._add_row(*result, Severity.ERROR if not result[1] else Severity.INFO)
        
        # Update summary and apply initial filters
        self._update_summary()
        self._apply_filters()
        
        # Auto-expand the table to show all content
        self.table.resizeRowsToContents()
