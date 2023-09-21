#! python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt


class IndexModel(QtCore.QAbstractTableModel):
    def __init__(self, indata):
        super(IndexModel, self).__init__()

        data = []

        for method in indata['Indices']:
            for instrument in indata['Indices'][method]:
                if instrument != 'first_chr_index_id_filter':
                    for index_type in indata['Indices'][method][instrument]:
                        if indata['Indices'][method][instrument][index_type]:
                            for index_id in indata['Indices'][method][instrument][index_type]:
                                row = [method, instrument, index_type, index_id]
                                data.append(row)

        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    def flags(self, index):
        f = QtCore.QAbstractTableModel.flags(self, index)
        return Qt.ItemFlags(f | Qt.ItemIsDragEnabled)

