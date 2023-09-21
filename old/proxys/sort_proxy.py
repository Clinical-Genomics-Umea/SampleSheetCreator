from PyQt5.QtCore import QSortFilterProxyModel


class SortProxyModel(QSortFilterProxyModel):
    """Custom proxy model that ignores child elements in filtering"""

