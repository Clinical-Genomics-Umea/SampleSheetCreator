import sys
import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, QAbstractItemModel, QModelIndex, Qt, QVariant
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import yaml
import numpy as np


class PandasModel(QStandardItemModel):
    def __init__(self, data, parent=None):
        super(PandasModel, self).__init__()

        with open('config/fields.yml', 'r') as stream:
            self.fields_yaml = yaml.load(stream, Loader=yaml.FullLoader)

        self.setHorizontalHeaderLabels(self.fields_yaml['review_fields_order'])

        groups_dict = dict()

        for index, row in data.iterrows():
            groups = row['Group'].split(',')
            for g in groups:
                groups_dict[g] = 0

        for g in groups_dict:
            parent_item = QStandardItem(g)
            self.appendRow(parent_item)
            for index, row in data.iterrows():
                if g in row['Group']:
                    row_list = []
                    for key in self.fields_yaml['review_fields_order']:
                        print(key)
                        if row[key] is np.nan:
                            row_list.append(QStandardItem(str("")))
                        else:
                            row_list.append(QStandardItem(str(row[key])))

                    parent_item.appendRow(row_list)
