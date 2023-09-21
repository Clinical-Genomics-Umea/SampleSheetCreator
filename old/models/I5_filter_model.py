from PyQt5.QtCore import QSortFilterProxyModel, QModelIndex


class I5FilterProxy(QSortFilterProxyModel):
    """
    Custom QSortFilterProxyModel with possibility to
    disable given columns from model filtering
    """
    def __init__(self, parent=None):
        super(I5FilterProxy, self).__init__(parent)

    def filterAcceptsRow(self, source_row, source_parent):
        index = self.sourceModel().index(source_row, 0, source_parent)
        rowCount = self.sourceModel().rowCount(index)
        cvalue = self.sourceModel().itemData(index)

        for i in range(0, source_row):
            index2 = self.sourceModel().index(i, 0, source_parent)
            if cvalue == self.sourceModel().itemData(index):
                return False

        accepted = QSortFilterProxyModel.filterAcceptsRow(self, source_row, source_parent)

        return accepted
