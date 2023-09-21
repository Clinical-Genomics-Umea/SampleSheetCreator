from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QStandardItem


def item_checked(item):
    return item.checkState() == Qt.Checked


def item_toggle_checked_state(item):
    item.setCheckState(Qt.Checked if item.checkState() == Qt.Unchecked else Qt.Unchecked)


class ColumnVisibilityMapper:
    def __init__(self):

        self.tv = None
        self.cb = None

        self.cb_model = None
        self.tableview_model = None

        self.columns = []

    def set_map(self, custom_combobox, tableview):

        self.tv = tableview
        self.cb = custom_combobox
        self.cb_model = self.cb.model()

        columns_visibility_dict = self.tv.get_columns_visibility()
        self.columns = list(columns_visibility_dict)
        self.cb.addItemsVisibility(columns_visibility_dict)

        self.cb_model.itemChanged.connect(self.on_item_changed)
        self.tv.columnHiddenChanged.connect(self.on_column_hidden_changed)

    @Slot(int, bool)
    def on_column_hidden_changed(self, column_index, hidden):
        item = self.cb_model.item(column_index)
        checkbox_checked = item_checked(item)
        column_visible = not hidden

        if checkbox_checked == column_visible:
            return

        item_toggle_checked_state(item)

    @Slot(QStandardItem)
    def on_item_changed(self, item):
        field = item.text()
        cb_checked = item_checked(item)
        cb_col = self.columns.index(field)
        tv_visible = not self.tv.isColumnHidden(cb_col)

        if cb_checked != tv_visible:
            self.tv.setColumnHidden(cb_col, not cb_checked)

