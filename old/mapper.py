from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QStandardItem


def item_checked(item):
    return item.checkState() == Qt.Checked


def item_toggle_checked_state(item):
    item.setCheckState(Qt.Checked if item.checkState() == Qt.Unchecked else Qt.Unchecked)


class ColumnVisibilityMapper:
    def __init__(self):

        self.tv = None
        self.lv = None

        self.tableview_model = None
        self.columns = []

    def set_map(self, tableview, columns_listview):

        self.tv = tableview
        self.lv = columns_listview

        columns_visibility_dict = self.tv.get_columns_visibility_state()
        self.columns = list(columns_visibility_dict)

        self.lv.set_items(columns_visibility_dict)
        self.tv.field_visibility_state_changed.connect(self.on_column_show_state_changed)

    @Slot(str, bool)
    def on_column_visibility_state_changed(self, field_name, hidden):

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

