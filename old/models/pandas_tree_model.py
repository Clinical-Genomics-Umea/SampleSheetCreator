from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QVariant


# class SortProxyModel(QtCore.QSortFilterProxyModel):
#     def lessThan(self, source_left, source_right):
#         data_left = source_left.data()
#         data_right = source_right.data()
#         if type(data_left) == type(data_right) == str:
#             return data_left < data_right
#         return super(SortProxyModel, self).lessThan(source_left, source_right)


class CustomNode(object):
    def __init__(self, data):
        self._data = data
        if type(data) == tuple:
            self._data = list(data)
        if type(data) is str or not hasattr(data, '__getitem__'):
            self._data = [data]

        self._columncount = len(self._data)
        self._children = []
        self._parent = None
        self._row = 0

    def data(self, column):
        if 0 <= column < len(self._data):
            return self._data[column]

    def setData(self, column, value):
        if 0 <= column < len(self._data):
            self._data[column] = value
            return True

    def columnCount(self):
        return self._columncount

    def childCount(self):
        return len(self._children)

    def child(self, row):
        if 0 <= row < self.childCount():
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
    def __init__(self, nodes, header):
        QtCore.QAbstractItemModel.__init__(self)
        self._root = CustomNode(None)
        self.__headers = header
        print(nodes)
        for node in nodes.keys():
            self._root.addChild(nodes[node])

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
            return node.data(index.column())
        return None

    def setData(self, index, value, role=QtCore.Qt.EditRole):

        node = index.internalPointer()
        node.setData(index.column(), value)

        print(node.data(index.column()))
        self.dataChanged.emit(index, index)

        return True

    def flags(self, index):
        if not index.isValid():
            return 0
        flags = QtCore.QAbstractItemModel.flags(self, index)
#        col = index.column()
#        if self.editable[col]:
        flags |= QtCore.Qt.ItemIsEditable
#        if self.dragable:
#            flags |= QtCore.Qt.ItemIsDragEnabled
        return flags

    def headerData(self, col, orientation=QtCore.Qt.Horizontal, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(str(self.__headers[col]))
        return QtCore.QVariant()
