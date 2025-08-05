from typing import Dict, Any
from PySide6.QtWidgets import (
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
)
import pandas as pd


class DataSetValidationWidget(QTabWidget):
    """A widget for displaying and validating dataset information in a tabbed interface.
    
    This widget provides different views of the dataset including:
    - Full dataset view
    - Application profile-based views
    - Lane-based views
    """
    
    def __init__(self, parent: QWidget = None):
        """Initialize the DataSetValidationWidget.
        
        Args:
            parent: The parent widget, if any
        """
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the user interface components."""
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Main layout
        self._main_layout = QVBoxLayout()
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._main_layout)

    def clear(self) -> None:
        """Clear all tabs and clean up resources."""
        while self.count() > 0:
            widget = self.widget(0)
            self.removeTab(0)
            if widget:
                widget.deleteLater()

    def populate(self, df_tuple: tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]) -> None:
        """Populate the widget with data from the provided dataframes.
        
        Args:
            df_tuple: A tuple containing three dataframes:
                     - Full dataset
                     - Application profile exploded view
                     - Lane exploded view
        """
        self.clear()
        
        if not df_tuple or len(df_tuple) != 3:
            return
            
        df, df_appname_explode, df_lane_explode = df_tuple
        
        # Add main data tab
        self._add_main_data_tab(df)
        
        # Add application profile tabs
        self._add_application_profile_tabs(df_appname_explode)
        
        # Add lane tabs
        self._add_lane_tabs(df_lane_explode)
    
    def _add_main_data_tab(self, df: pd.DataFrame) -> None:
        """Add the main data tab with the full dataset.
        
        Args:
            df: The full dataset dataframe
        """
        self.addTab(self._create_table_widget(df), "All Data")
    
    def _add_application_profile_tabs(self, df: pd.DataFrame) -> None:
        """Add tabs for each application profile.
        
        Args:
            df: The application profile exploded dataframe
        """
        if df.empty or "ApplicationProfile" not in df.columns:
            return
            
        profile_tab = QTabWidget()
        self.addTab(profile_tab, "By Application Profile")
        
        for ap_name in df["ApplicationProfile"].unique():
            ap_df = df[df["ApplicationProfile"] == ap_name].copy(deep=True)
            if not ap_df.empty:
                tab = self._create_table_widget(ap_df)
                profile_tab.addTab(tab, str(ap_name))
    
    def _add_lane_tabs(self, df: pd.DataFrame) -> None:
        """Add tabs for each lane.
        
        Args:
            df: The lane exploded dataframe
        """
        if df.empty or "Lane" not in df.columns:
            return
            
        lane_tab = QTabWidget()
        self.addTab(lane_tab, "By Lane")
        
        for lane in sorted(df["Lane"].unique()):
            lane_df = df[df["Lane"] == lane].copy(deep=True)
            if not lane_df.empty:
                tab = self._create_table_widget(lane_df)
                lane_tab.addTab(tab, f"Lane {lane}")
    
    @staticmethod
    def _create_table_widget(dataframe: pd.DataFrame) -> QWidget:
        """Create a table widget populated with dataframe data.
        
        Args:
            dataframe: The pandas DataFrame to display
            
        Returns:
            QWidget: A widget containing the table
        """
        if dataframe.empty:
            return QWidget()
            
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        table = QTableWidget()
        layout.addWidget(table)
        
        # Configure table dimensions
        rows, cols = dataframe.shape
        table.setRowCount(rows)
        table.setColumnCount(cols)
        
        # Set headers
        table.setHorizontalHeaderLabels(dataframe.columns)
        
        # Populate table
        for row in range(rows):
            for col in range(cols):
                value = str(dataframe.iat[row, col])
                table.setItem(row, col, QTableWidgetItem(value))
        
        return widget
