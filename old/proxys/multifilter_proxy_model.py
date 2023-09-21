from PyQt5.QtCore import QSortFilterProxyModel, Qt

import re

class MultiFilterMode:
    AND = 0
    OR = 1


class MultiFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        QSortFilterProxyModel.__init__(self, *args, **kwargs)
        self.filters = {}
        self.multi_filter_mode = MultiFilterMode.AND

    def setFilterByColumn(self, column, regex):
        print(column, regex)
        if isinstance(regex, str):
            regex = re.compile(regex)
        self.filters[column] = regex
        self.invalidateFilter()

    def clearFilter(self, column):
        del self.filters[column]
        self.invalidateFilter()

    def clearFilters(self):
        self.filters = {}
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if not self.filters:
            return True

        results = []
        for key, regex in self.filters.items():
            text = ''
            index = self.sourceModel().index(source_row, key, source_parent)
            if index.isValid():
                text = self.sourceModel().data(index, Qt.DisplayRole)
                if text is None:
                    text = ''
            results.append(regex.match(text))

        if self.multi_filter_mode == MultiFilterMode.OR:
            return any(results)
        return all(results)