from PySide6.QtGui import QKeyEvent, QClipboard, QCursor, QStandardItemModel, QStandardItem, QFont
from PySide6.QtCore import Qt, QEvent, Signal, QPoint, Slot
from PySide6.QtWidgets import QTableView, QAbstractItemView, QApplication, QMenu, QComboBox, \
    QStyledItemDelegate, QGroupBox, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, QFrame


def calculate_index_range(indexes):
    """
    Calculate the minimum and maximum row and column values from a list of indexes.

    Args:
        indexes (list of QModelIndex): The list of QModelIndex objects.

    Returns:
        tuple: A tuple containing (min_row, max_row, min_col, max_col).
    """
    min_row, max_row, min_col, max_col = None, None, None, None

    for index in indexes:
        row, col = index.row(), index.column()

        if min_row is None or row < min_row:
            min_row = row
        if max_row is None or row > max_row:
            max_row = row
        if min_col is None or col < min_col:
            min_col = col
        if max_col is None or col > max_col:
            max_col = col

    return min_row, max_row, min_col, max_col


def list2d_to_tab_delim_str(data):
    """
    Convert a 2D list to a tab-delimited string using join.

    Args:
        data (list of lists): The input data as a 2D list.

    Returns:
        str: The tab-delimited string.
    """
    tab_delimited_rows = []

    for row in data:
        # Use join to concatenate the elements in each row with tab '\t' as the separator
        tab_delimited_row = '\t'.join(map(str, row))
        tab_delimited_rows.append(tab_delimited_row)

    return '\n'.join(tab_delimited_rows)


def clipboard_text_to_model():
    clipboard = QApplication.clipboard()
    mime_data = clipboard.mimeData()

    if not mime_data.hasText():
        return None

    rows = mime_data.text().split('\n')

    row_counts = [r_count for r_count, r in enumerate(rows) if len(r) > 0]
    col_counts = [c_count for r in rows for c_count, value in enumerate(r.split('\t')) if len(value) > 0]

    max_rows = max(row_counts)
    max_cols = max(col_counts)
    dummy_model = QStandardItemModel(max_rows + 1, max_cols + 1)

    for r_count, r in enumerate(rows):
        for c_count, value in enumerate(r.split('\t')):
            idx = dummy_model.index(r_count, c_count)
            dummy_model.setData(idx, value, Qt.EditRole)

    return dummy_model


def regular_paste(selected_indexes, source_model, model):
    start_target_row = selected_indexes[0].row()
    start_target_col = selected_indexes[0].column()

    source_row_count = source_model.rowCount()
    source_col_count = source_model.columnCount()

    for row_count in range(source_row_count):
        for col_count in range(source_col_count):
            idx = source_model.index(row_count, col_count)
            value = source_model.data(idx, Qt.DisplayRole)
            model.setData(model.index(start_target_row + row_count, start_target_col + col_count), value, Qt.EditRole)

    return True


class SampleTableView(QTableView):

    columnHiddenChanged = Signal(int, bool)

    def __init__(self):
        super().__init__()

        self.setDragDropMode(QAbstractItemView.DropOnly)
        self.setDefaultDropAction(Qt.CopyAction)

        self.setSelectionBehavior(QTableView.SelectItems)

        self.setSelectionMode(QTableView.ContiguousSelection)

        self.clipboard = QClipboard()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.table_popup)

        self.table_context_menu = QMenu(self)
        self.table_context_menu_setup()

        self.header_context_menu = QMenu(self)
        header = self.horizontalHeader()
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self.header_popup)

    def table_popup(self):
        self.table_context_menu.exec(QCursor.pos())

    def table_context_menu_setup(self):
        copy_action = self.table_context_menu.addAction("Copy")
        paste_action = self.table_context_menu.addAction("Paste")
        delete_action = self.table_context_menu.addAction("Delete")

        copy_action.triggered.connect(self.copy_selection)
        paste_action.triggered.connect(self.paste_clipboard_content)
        delete_action.triggered.connect(self.delete_selection)

    def setColumnHidden(self, column, hide):
        super().setColumnHidden(column, hide)
        self.columnHiddenChanged.emit(column, hide)

    def get_columns_visibility(self):
        return {
            self.model().fields[i]: not self.isColumnHidden(i)
            for i in range(self.model().columnCount())
            }

    def header_popup(self, pos: QPoint):
        """
        Display a context menu when right-clicking on the header of the SampleTableView.

        Args:
            pos (QPoint): The position of the right-click event.
        """
        # Get the index and clicked column of the clicked header
        index = self.indexAt(pos)
        clicked_column = index.column()

        selected_columns = self.get_selected_columns()

        # Get the name of the clicked column
        colname = self.model().fields[clicked_column]

        # Clear the context menu
        self.header_context_menu.clear()

        # Create an action to hide the selected clicked column
        if not selected_columns:
            hide_clicked_action = self.header_context_menu.addAction(f"Hide field ({colname})")
            hide_clicked_action.triggered.connect(lambda: self.setColumnHidden(clicked_column, True))
            self.header_context_menu.exec(QCursor.pos())
            return

        # Create an action to hide the selected columns
        if len(selected_columns) > 0:
            hide_selected_cols = self.header_context_menu.addAction("Hide selected fields")
            hide_selected_cols.triggered.connect(lambda: self.set_columns_hidden(selected_columns))
            self.header_context_menu.exec(QCursor.pos())
            return

    def set_columns_hidden(self, selected_columns):
        """
        Set the specified columns as hidden in the table.

        Parameters:
            selected_columns (list): A list of integers representing the indices of the columns to be hidden.

        Returns:
            None
        """
        for col in selected_columns:
            self.setColumnHidden(col, True)

        self.clearSelection()

    def get_selected_columns(self):
        selection_model = self.selectionModel()
        selected_indexes = selection_model.selectedColumns()
        return [column.column() for column in selected_indexes]

    def get_column_states(self):
        fields = self.model().fields
        return {
            fields[i]: not self.isColumnHidden(i)
            for i in range(self.model().columnCount())
        }

    def copy_selection(self):
        selected_data = self.get_selected_data()
        selected_csv = list2d_to_tab_delim_str(selected_data)
        self.clipboard.setText(selected_csv)

    def get_selected_data(self):
        selected_indexes = self.selectedIndexes()
        selected_data = []

        rows = []
        cols = []

        for index in selected_indexes:
            rows.append(index.row())
            cols.append(index.column())

        min_row, max_row = min(rows), max(rows)
        min_col, max_col = min(cols), max(cols)

        for row_count in range(min_row, max_row + 1):
            row_items = [
                self.model().data(
                    self.model().index(row_count, col_count), Qt.DisplayRole
                )
                for col_count in range(min_col, max_col + 1)
            ]
            selected_data.append(row_items)

        return selected_data

    def delete_selection(self):
        model = self.model()
        selected_indexes = self.selectedIndexes()

        for idx in selected_indexes:
            model.setData(idx, "", Qt.EditRole)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_C:
            self.copy_selection()
            return True
        elif event.key() == Qt.Key_V:
            self.paste_clipboard_content()
            return True
        elif event.key() == Qt.Key_Delete:
            self.delete_selection()
            return True

        return False

    def paste_clipboard_content(self):
        model = self.model()

        source_model = clipboard_text_to_model()

        if source_model is not None:
            selected_indexes = self.selectedIndexes()

            if not selected_indexes:
                return False

            if len(selected_indexes) == 1:

                return regular_paste(
                    selected_indexes, source_model, model
                )
            if len(selected_indexes) > 1:
                if source_model.rowCount() == 1 and source_model.columnCount() == 1:
                    source_index = source_model.index(0, 0)
                    for idx in selected_indexes:
                        model.setData(idx, source_model.data(source_index,  Qt.DisplayRole), Qt.EditRole)

                return True

        return False


class CheckableComboBox(QComboBox):

    # Subclass Delegate to increase item height
    class Delegate(QStyledItemDelegate):
        def sizeHint(self, option, index):
            size = super().sizeHint(option, index)
            size.setHeight(20)
            return size

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make the combo editable to set a custom text, but readonly
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)

        # Remove the border
        self.setFrame(False)

        # Use custom delegate
        self.setItemDelegate(CheckableComboBox.Delegate())

        # Hide and show popup when clicking the line edit
        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False

        # Prevent popup from closing when clicking on an item
        self.view().viewport().installEventFilter(self)

    def resizeEvent(self, event):
        # Recompute text to elide as needed
        self.updateText()
        super().resizeEvent(event)

    def eventFilter(self, obj, event):
        if obj == self.lineEdit():
            if event.type() == QEvent.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    self.hide_popup()
                else:
                    self.show_popup()
                return True
            return False

        if obj == self.view().viewport() and event.type() == QEvent.MouseButtonRelease:
            index = self.view().indexAt(event.pos())
            item = self.model().item(index.row())

            if item.checkState() == Qt.Checked:
                item.setCheckState(Qt.Unchecked)
            else:
                item.setCheckState(Qt.Checked)
            return True
        return False

    def show_popup(self):
        super().showPopup()
        # When the popup is displayed, a click on the lineedit should close it
        self.closeOnLineEditClick = True

    def hide_popup(self):
        super().hidePopup()
        # Used to prevent immediate reopening when clicking on the lineEdit
        self.startTimer(100)
        # Refresh the display text when closing
        self.updateText()

    def timerEvent(self, event):
        # After timeout, kill timer, and reenable click on line edit
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False

    def updateText(self):

        self.lineEdit().setText("-- Show/Hide Columns --")

    def addItem(self, text):
        item = QStandardItem()
        item.setText(text)
        item.setData(text)

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        item.setData(Qt.Unchecked, Qt.CheckStateRole)
        self.model().appendRow(item)

    def addItemVisibility(self, field_name, visibility_state):
        item = QStandardItem()
        item.setText(field_name)

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)

        if visibility_state is True:
            item.setData(Qt.Checked, Qt.CheckStateRole)
        else:
            item.setData(Qt.Unchecked, Qt.CheckStateRole)

        self.model().appendRow(item)

    def addItems(self, texts, datalist=None):
        for i, text in enumerate(texts):
            try:
                data = datalist[i]
            except (TypeError, IndexError):
                data = None
            self.addItem(text, data)

    def addItemsVisibility(self, columns_visibility):

        for field, state in columns_visibility.items():
            self.addItemVisibility(field, state)

        self.model().dataChanged.connect(self.updateText)

    def currentData(self):
        return [
            self.model().item(i).data()
            for i in range(self.model().rowCount())
            if self.model().item(i).checkState() == Qt.Checked
        ]












