from PySide6.QtWidgets import (
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget, QHeaderView, QLabel, QAbstractItemView
)
from PySide6.QtCore import Qt
import pandas as pd
from typing import Optional, Tuple


class SampleDataOverviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._current_df = None
        self._setup_ui()
        # self._apply_styles()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Status bar
        # self.status_bar = QLabel("Ready")
        # self.status_bar.setStyleSheet("""
        #     QLabel {
        #         background: #f8f9fa;
        #         padding: 4px 8px;
        #         border: 1px solid #dee2e6;
        #         border-radius: 3px;
        #         color: #495057;
        #     }
        # """)
        # layout.addWidget(self.status_bar)

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        layout.addWidget(self.tab_widget)

    # def _apply_styles(self):
    #     self.setStyleSheet("""
    #         QTableWidget {
    #             gridline-color: #dee2e6;
    #             font-size: 11pt;
    #         }
    #         QHeaderView::section {
    #             background-color: #f8f9fa;
    #             padding: 8px;
    #             border: 1px solid #dee2e6;
    #             font-weight: bold;
    #         }
    #         QTableWidget::item {
    #             padding: 6px;
    #         }
    #         QTabBar::tab {
    #             padding: 8px 16px;
    #             margin-right: 2px;
    #             background: #f1f3f5;
    #             border: 1px solid #dee2e6;
    #             border-bottom: none;
    #             border-top-left-radius: 4px;
    #             border-top-right-radius: 4px;
    #         }
    #         QTabBar::tab:selected {
    #             background: white;
    #             margin-bottom: -1px;
    #         }
    #         QTabWidget::pane {
    #             border: 1px solid #dee2e6;
    #             background: white;
    #         }
    #     """)

    def clear(self):
        self.tab_widget.clear()

    def _create_table_widget(self, title: str) -> QTableWidget:
        table = QTableWidget()
        table.setAlternatingRowColors(True)
        table.setSortingEnabled(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.verticalHeader().setVisible(False)

        # Enable smooth scrolling
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        return table

    def _add_tab(self, df: pd.DataFrame, title: str) -> None:
        if df is None or df.empty:
            return

        table = self._create_table_widget(title)

        # Make a copy of the dataframe to avoid modifying the original
        df_display = df.copy()
        
        # Convert any array-like columns to strings
        for col in df_display.columns:
            if df_display[col].apply(lambda x: isinstance(x, (list, tuple, set))).any():
                df_display[col] = df_display[col].apply(
                    lambda x: ', '.join(map(str, x)) if isinstance(x, (list, tuple, set)) else x
                )

        # Set up table data
        rows, cols = df_display.shape
        table.setRowCount(rows)
        table.setColumnCount(cols)
        table.setHorizontalHeaderLabels(df_display.columns)

        # Fill table with data
        for i, row in df_display.iterrows():
            for j, value in enumerate(row):
                # Handle different types of values safely
                if pd.isna(value):
                    display_text = ""
                elif isinstance(value, (list, tuple, set)):
                    display_text = ', '.join(map(str, value))
                else:
                    display_text = str(value)
                
                item = QTableWidgetItem(display_text)
                item.setToolTip(display_text)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                table.setItem(i, j, item)

        # Configure header
        header = table.horizontalHeader()
        for i in range(cols):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(i, QHeaderView.Interactive)

        # Add tab
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(table)

        self.tab_widget.addTab(container, title)
        # self.status_bar.setText(f"Showing {rows} rows, {cols} columns")

    def populate(self, data: Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]) -> None:
        """Update the widget with new data.

        Args:
            data: A tuple containing (original_df, app_exploded_df, lane_exploded_df)
        """
        self.tab_widget.clear()

        if not data or len(data) != 3:
            return

        original_df, app_exploded_df, lane_exploded_df = data

        if not original_df.empty:
            self._add_tab(original_df, "All Samples")
        if not app_exploded_df.empty:
            self._add_tab(app_exploded_df, "By Application")
        if not lane_exploded_df.empty:
            self._add_tab(lane_exploded_df, "By Lane")
