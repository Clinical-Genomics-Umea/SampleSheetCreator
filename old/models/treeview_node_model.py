import sys
from PyQt5 import QtCore, QtWidgets


class CustomNode(object):
    def __init__(self, data=False, df_index=False, columncount=1):
        self._data = data
        self._df_index = df_index
        self._columncount = columncount
        self._children = []
        self._parent = None
        self._row = 0

    def data(self, column):
        if column >= 0 and column < len(self._data):
            return self._data[column]

    def columnCount(self):
        return self._columncount

    def childCount(self):
        return len(self._children)

    def child(self, row):
        if row >= 0 and row < self.childCount():
            return self._children[row]

    def parent(self):
        return self._parent

    def row(self):
        return self._row

    def addChild(self, child):
        child._parent = self
        child._row = len(self._children)
        self._children.append(child)
        self._columncount = max(child.columnCount(), self._columncount)


class CustomModel(QtCore.QAbstractItemModel):
    def __init__(self, nodes, dfdata):
        QtCore.QAbstractItemModel.__init__(self)
        self._dfdata = dfdata
        self._root = CustomNode(None)
        for node in nodes:
            self._root.addChild(node)

    def rowCount(self, index):
        if index.isValid():
            return index.internalPointer().childCount()
        return self._root.childCount()

    def addChild(self, node, _parent):
        if not _parent or not _parent.isValid():
            parent = self._root
        else:
            parent = _parent.internalPointer()
        parent.addChild(node)

    def index(self, row, column, _parent=None):
        if not _parent or not _parent.isValid():
            parent = self._root
        else:
            parent = _parent.internalPointer()

        if not QtCore.QAbstractItemModel.hasIndex(self, row, column, _parent):
            return QtCore.QModelIndex()

        child = parent.child(row)
        if child:
            return QtCore.QAbstractItemModel.createIndex(self, row, column, child)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if index.isValid():
            p = index.internalPointer().parent()
            if p:
                return QtCore.QAbstractItemModel.createIndex(self, p.row(), 0, p)
        return QtCore.QModelIndex()

    def columnCount(self, index):
        if index.isValid():
            return index.internalPointer().columnCount()
        return self._root.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            if node.data:
                return node.data(index.column())
            else:
                return str(self._dfdata.iloc[index.row(), index.column()])
                return node.data(index.column())
        return None