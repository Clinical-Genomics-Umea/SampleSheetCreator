#! python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt


class IndexTreeModel(QtGui.QStandardItemModel):
    def __init__(self, indata):
        super(IndexTreeModel, self).__init__()
        try:
            for method, options1 in indata['Indices'].items():
                method_item = QtGui.QStandardItem(method)
                print(method)
                self.appendRow(method_item)
                index_id_filter = {}
                for instrument, options2 in options1.items():
                    if instrument == 'first_chr_index_id_filter':
                        for index_type, val in options2.items():
                            index_id_filter[index_type] = val
                    else:
                        instrument_item = QtGui.QStandardItem(instrument)
                        method_item.appendRow(instrument_item)
                        for index_type, options3 in options2.items():
                            index_type_item = QtGui.QStandardItem(index_type)
                            instrument_item.appendRow(index_type_item)
                            set_item = QtGui.QStandardItem('*')
                            index_type_item.appendRow(set_item)
                            if index_id_filter[index_type]:
                                set_id_list = []
                                for index_id in options3:
                                    set_id = index_id[0]
                                    set_item = QtGui.QStandardItem(set_id)
                                    if set_id not in set_id_list:
                                        set_id_list.append(set_id)
                                        index_type_item.appendRow(set_item)
        except:
            pass
