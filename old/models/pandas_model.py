import sys
import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, Qt, QVariant, QDataStream
from PyQt5.QtGui import QColor


class PandasModel(QAbstractTableModel):
    def __init__(self, data, fields_dict, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._data = data
        self._fields_dict = fields_dict

        self._colnames = list(self._data.columns)
        self._sample_id_col = self._colnames.index("Sample_ID")
        self._sample_name_col = self._colnames.index("Sample_Name")

    def isempty(self, row):
        totlen = 0
        for item in row:
            totlen += len(item)
        if totlen == 0:
            return False
        else:
            return True

    def update_view(self, top_left_index, bottom_right_index):
#        self.dataChanged.emit(top_left_index, bottom_right_index)
        self.beginResetModel()

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
            if role == Qt.EditRole:
                return str(self._data.iloc[index.row(), index.column()])

        return None

    def setData(self, index, value, role) -> bool:

        if not index.isValid():
            return False
        if role != Qt.EditRole:
            return False
        row = index.row()
        if row < 0 or row >= len(self._data.values):
            return False
        column = index.column()
        if column < 0 or column >= self._data.columns.size:
            return False
        self._data.values[row][column] = value

        if column == self._sample_id_col:
            self._data.values[row][self._sample_name_col] = value

        self.dataChanged.emit(index, index)
        return True

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[section]
        if orientation == Qt.Horizontal and role == Qt.ToolTipRole:
            col_name = self._data.columns[section]
            if 'tooltip' in self._fields_dict['model_fields'][col_name]:
                return self._fields_dict['model_fields'][col_name]['tooltip']

        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return section+1
        return None

    def flags(self, mi):
        """Reimplemented to set editable and movable status."""

        flags = (
            Qt.ItemIsSelectable
            | Qt.ItemIsEnabled
            | Qt.ItemIsDropEnabled
            | Qt.ItemIsEditable

        )

        return flags

    def dropMimeData(self, mimedata, action, row, column, parentIndex):
        if mimedata.hasFormat('application/x-qabstractitemmodeldatalist'):
            bytearray = mimedata.data('application/x-qabstractitemmodeldatalist')
            data_items = self.decodeMimeData(bytearray)

            col = parentIndex.column()
            row = parentIndex.row()
            # pmodel = parentIndex.model()
            #
            # print(row, col, pmodel)

            for i in range(len(data_items)):
                text = data_items[i][Qt.DisplayRole]
                row2 = row + i
                self.setData(self.index(row2, col), text, Qt.EditRole)

            return True

        return False

    def decodeMimeData(self, data):
        result = []
        value = QVariant()
        stream = QDataStream(data)
        while not stream.atEnd():
            row = stream.readInt32()
            col = stream.readInt32()
            item = {}
            for role in range(stream.readInt32()):
                key = Qt.ItemDataRole(stream.readInt32())
                stream >> value
                item[key] = value.value()
                result.append(item)

        return result
