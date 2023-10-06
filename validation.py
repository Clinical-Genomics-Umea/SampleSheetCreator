from PySide6.QtWidgets import QDialog, QVBoxLayout, QHeaderView

import modules.validation


class HeatmapDialog(QDialog):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle('Heatmap Dialog')
        self.setLayout(QVBoxLayout())
        self.heatmap_table = modules.validation.validation.create_heatmap_table(data)
        self.layout().addWidget(self.heatmap_table)

        self.heatmap_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.heatmap_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)


        # explode_df = explode_df_by_lane(df)
        # split_df_dict = split_df_by_lane(df)
        #
        # print(explode_df.to_string())
        # print(split_df_dict)
