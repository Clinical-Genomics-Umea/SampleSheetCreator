from typing import Dict, Any, Optional

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtWidgets import (
    QTabWidget, QVBoxLayout, QSizePolicy, QLabel, 
    QWidget, QTabBar, QScrollArea, QFrame
)
from modules.views.validation.index_distance_lane_area_widget import IndexDistanceLaneAreaWidget


class IndexDistanceOverviewWidget(QTabWidget):
    """A tabbed widget for displaying index distance matrices for each lane.
    
    This widget shows distance matrices for I7, I5, and combined I7-I5 indexes
    in separate tabs for each lane. It provides a clean, modern interface with
    proper error handling and loading states.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()
        self._apply_styles()
        
    def _setup_ui(self) -> None:
        """Initialize the UI components."""
        self.setDocumentMode(True)
        self.setMovable(True)
        self.setTabsClosable(False)
        self.setElideMode(Qt.ElideRight)
        self.setUsesScrollButtons(True)
        
        # Ensure the tab bar is visible
        self.tabBar().setDocumentMode(True)
        self.tabBar().setExpanding(False)
        
        # Apply custom tab bar styling
        # self.setStyleSheet("""
        #     QTabBar::tab {
        #         background: #f0f0f0;
        #         color: #505050;
        #         border: 1px solid #d0d0d0;
        #         border-bottom: none;
        #         padding: 6px 12px;
        #         margin-right: 2px;
        #         border-top-left-radius: 4px;
        #         border-top-right-radius: 4px;
        #         min-width: 80px;
        #     }
        #     QTabBar::tab:selected {
        #         background: #ffffff;
        #         color: #000000;
        #         border-bottom: 2px solid #2196F3;
        #         font-weight: bold;
        #     }
        #     QTabBar::tab:hover:!selected {
        #         background: #e0e0e0;
        #     }
        #     QTabBar::tab:disabled {
        #         background: #f8f8f8;
        #         color: #a0a0a0;
        #     }
        #     QTabWidget::pane {
        #         border: 1px solid #d0d0d0;
        #         background: white;
        #         padding: 0px;
        #     }
        #     QLabel {
        #         color: #333333;
        #     }
        # """)
        
    def _apply_styles(self) -> None:
        """Apply additional styles to the widget."""
        # Make the tab bar more compact
        self.setIconSize(QSize(16, 16))
        
        # Set a minimum size for better UX
        self.setMinimumSize(800, 600)
        
    def populate(self, results: Dict[str, Any]) -> None:
        """Populate the widget with index distance data.
        
        Args:
            results: A dictionary mapping lane numbers to their index distance data
        """
        self.clear()
        
        if not results:
            self._show_message("No index distance data available.")
            return
            
        if isinstance(results, str):
            self._show_error(results)
            return
            
        try:
            # Sort lanes numerically for consistent ordering
            lanes = sorted(
                (lane for lane in results.keys() if str(lane).isdigit()),
                key=int
            )
            
            if not lanes:
                self._show_message("No valid lane data found.")
                return
                
            for lane in lanes:
                lane_data = results.get(lane)
                if lane_data:
                    tab = IndexDistanceLaneAreaWidget(lane_data)
                    self.addTab(tab, f"Lane {lane}")
                    
        except Exception as e:
            self._show_error(f"Error displaying index distances: {str(e)}")
    
    def _show_message(self, message: str) -> None:
        """Display an informational message.
        
        Args:
            message: The message to display
        """
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        self.addTab(label, "Information")
    
    def _show_error(self, error_message: str) -> None:
        """Display an error message.
        
        Args:
            error_message: The error message to display
        """
        label = QLabel(f"<b>Error:</b> {error_message}")
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        label.setStyleSheet("color: #d32f2f;")
        self.addTab(label, "Error")
    
    def clear(self) -> None:
        """Clear all tabs and clean up resources."""
        while self.count() > 0:
            widget = self.widget(0)
            self.removeTab(0)
            if widget:
                widget.deleteLater()
    
    def sizeHint(self) -> QSize:
        """Provide a reasonable default size for the widget."""
        return QSize(1000, 700)
