from PySide6.QtWidgets import (
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
)


class DataSetValidationWidget(QTabWidget):
    def __init__(self):
        super().__init__()

        self.content_widget = QWidget()
        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setLayout(self.layout)

        self.layout = QVBoxLayout()

        self.setContentsMargins(0, 0, 0, 0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setLayout(self.layout)

    def clear(self):
        # Remove and delete each tab widget
        while self.count() > 0:
            widget = self.widget(0)  # Get the first widget in the tab widget
            self.removeTab(0)  # Remove the tab
            widget.deleteLater()

    def populate(self, samples_dfs):

        # Add main data tab
        self.addTab(self.get_widget_table(samples_dfs["no_explode"]), "all data")

        # Add application profile names tab
        app_profile_tab = QTabWidget()
        self.addTab(app_profile_tab, "application profile")
        unique_app_profile_names = samples_dfs["apn_explode"][
            "ApplicationName"
        ].unique()

        for app_profile_name in unique_app_profile_names:
            df_app_profile = samples_dfs["apn_explode"][
                samples_dfs["apn_explode"]["ApplicationProfile"] == app_profile_name
            ]
            app_profile_widget = self.get_widget_table(df_app_profile)
            app_profile_tab.addTab(app_profile_widget, app_profile_name)

        # Add lanes tab
        lane_tab = QTabWidget()
        self.addTab(lane_tab, "lanes")
        unique_lanes = samples_dfs["lane_explode"]["Lane"].unique()

        for lane in unique_lanes:
            lane_name = f"lane {lane}"
            df_lane = samples_dfs["lane_explode"][
                samples_dfs["lane_explode"]["Lane"] == lane
            ]
            lane_widget = self.get_widget_table(df_lane)
            lane_tab.addTab(lane_widget, lane_name)

    @staticmethod
    def get_widget_table(dataframe):
        widget = QWidget()
        table = QTableWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        layout.addWidget(table)

        # Set row and column count
        table.setRowCount(dataframe.shape[0])
        table.setColumnCount(dataframe.shape[1])

        # Set column headers
        table.setHorizontalHeaderLabels(dataframe.columns)

        # Populate the table with DataFrame data
        for row_idx in range(dataframe.shape[0]):
            for col_idx in range(dataframe.shape[1]):
                cell_value = str(dataframe.iloc[row_idx, col_idx])
                table.setItem(row_idx, col_idx, QTableWidgetItem(cell_value))

        return widget
