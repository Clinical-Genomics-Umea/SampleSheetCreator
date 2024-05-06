from PySide6.QtGui import QKeyEvent, QClipboard, QCursor, QStandardItemModel, QStandardItem, QFont
from PySide6.QtCore import Qt, QEvent, Signal, QPoint, Slot, QItemSelectionModel, QItemSelection, QSortFilterProxyModel
from PySide6.QtWidgets import QTableView, QAbstractItemView, QApplication, QMenu, QComboBox, \
    QStyledItemDelegate, QGroupBox, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, QFrame, QHeaderView, QWidget, \
    QLineEdit


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

    text = mime_data.text()
    rows = text.split('\n')
    rows = [row for row in rows if row]  # remove empty rows

    max_cols = max(len(row.split('\t')) for row in rows)
    dummy_model = QStandardItemModel(len(rows), max_cols)

    for r_count, r in enumerate(rows):
        for c_count, value in enumerate(r.split('\t')):
            dummy_model.setData(dummy_model.index(r_count, c_count), value, Qt.EditRole)

    return dummy_model

# def clipboard_text_to_model():
#     clipboard = QApplication.clipboard()
#     mime_data = clipboard.mimeData()
#
#     if not mime_data.hasText():
#         return None
#
#     rows = mime_data.text().split('\n')
#
#     row_counts = [r_count for r_count, r in enumerate(rows) if len(r) > 0]
#     col_counts = [c_count for r in rows for c_count, value in enumerate(r.split('\t')) if len(value) > 0]
#
#     max_rows = max(row_counts)
#     max_cols = max(col_counts)
#     dummy_model = QStandardItemModel(max_rows + 1, max_cols + 1)
#
#     for r_count, r in enumerate(rows):
#         for c_count, value in enumerate(r.split('\t')):
#             idx = dummy_model.index(r_count, c_count)
#             dummy_model.setData(idx, value, Qt.EditRole)
#
#     return dummy_model

#
# def regular_paste(selected_indexes, source_model, model):
#     start_target_row = selected_indexes[0].row()
#     start_target_col = selected_indexes[0].column()
#
#     source_row_count = source_model.rowCount()
#     source_col_count = source_model.columnCount()
#
#     for row_count in range(source_row_count):
#         for col_count in range(source_col_count):
#             idx = source_model.index(row_count, col_count)
#             value = source_model.data(idx, Qt.DisplayRole)
#             model.setData(model.index(start_target_row + row_count, start_target_col + col_count), value, Qt.EditRole)
#
#     return True


def regular_paste(selected_indexes, source_model, target_proxy_model):
    start_row = selected_indexes[0].row()
    start_col = selected_indexes[0].column()

    source_row_count = source_model.rowCount()
    source_col_count = source_model.columnCount()

    target_model = target_proxy_model.sourceModel()


    target_proxy_model.blockSignals(True)

    for row in range(source_row_count):
        for col in range(source_col_count):
            idx = source_model.index(row, col)
            value = source_model.data(idx, Qt.DisplayRole)
            target_proxy_model.setData(target_proxy_model.index(start_row + row, start_col + col), value, Qt.EditRole)

    target_proxy_model.blockSignals(False)

    target_model.refresh_view()

    return True


class SampleWidget(QWidget):
    def __init__(self, samplemodel: QStandardItemModel):
        super().__init__()

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)

        self.filter_edit = QLineEdit()
        self.samplemodel = samplemodel

        filter_proxy_model = CustomProxyModel()
        filter_proxy_model.setSourceModel(samplemodel)

        self.sampleview = SampleTableView()
        self.cellvalue = QLabel("")
        self.cellvalue.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.cellvalue.setFont(QFont("Arial", 8))

        vbox.addWidget(self.filter_edit)
        vbox.addWidget(self.sampleview)
        vbox.addWidget(self.cellvalue)
        self.setLayout(vbox)

        self.sampleview.setModel(filter_proxy_model)

        self.sampleview.setContextMenuPolicy(Qt.CustomContextMenu)
        header = self.sampleview.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setMinimumSectionSize(100)

        self.sampleview.selectionModel().selectionChanged.connect(self.on_sampleview_selection_changed)
        # self.sampleview.selectionModel().currentChanged.connect(self.on_sampleview_selection_changed)
        # self.sampleview.model().dataChanged.connect(self.on_sampleview_selection_changed)

        self.filter_edit.textChanged.connect(filter_proxy_model.set_filter_text)


    def selected_rows_columns_count(self, selected_indexes):

        selected_rows = {index.row() for index in selected_indexes}
        selected_columns = {index.column() for index in selected_indexes}

        return len(selected_rows), len(selected_columns)

    def on_sampleview_selection_changed(self):
        selection_model = self.sampleview.selectionModel()
        selected_indexes = selection_model.selectedIndexes()
        srows, scols = self.selected_rows_columns_count(selected_indexes)

        if srows == 1 and scols == 1 and selected_indexes:
            model = self.sampleview.model()

            data = model.data(selected_indexes[0], Qt.DisplayRole)
            column = selected_indexes[0].column()
            row = selected_indexes[0].row() + 1
            column_name = self.sampleview.horizontalHeader().model().headerData(column, Qt.Horizontal)

            if data is None:
                data = "Empty"
            elif data == "":
                data = "Empty"

            self.cellvalue.setText(f"{column_name}, {row}:  {data}")

        elif srows > 1 or scols > 1 and selected_indexes:
            self.cellvalue.setText(f"multiple ... ")
        else:
            self.cellvalue.setText("")


class CustomProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_text = ''

    def filterAcceptsRow(self, source_row, source_parent):
        if not self.filter_text:
            return True
        for column in range(self.sourceModel().columnCount()):
            index = self.sourceModel().index(source_row, column, source_parent)
            data = self.sourceModel().data(index, Qt.DisplayRole)
            if self.filter_text.lower() in str(data).lower():
                return True
        return False

    def set_filter_text(self, text):
        self.filter_text = text
        self.invalidateFilter()



# class MultiColumnFilterProxyModel(QSortFilterProxyModel):
#     def filterAcceptsRow(self, sourceRow, sourceParent):
#         # If the filter string is empty, display all rows
#         if not self.filterRegularExpression().isEmpty():
#             for column in range(self.sourceModel().columnCount()):
#                 sourceIndex = self.sourceModel().index(sourceRow, column, sourceParent)
#                 # If any column matches the filter, return True
#                 if self.filterRegularExpression().indexIn(self.sourceModel().data(sourceIndex)) >= 0:
#                     return True
#             # If no columns match the filter, return False
#             return False
#         else:
#             # If the filter string is empty, display all rows
#             return True


class SampleTableView(QTableView):

    field_visibility_state_changed = Signal(str, bool)
    cell_selected = Signal(str)

    def __init__(self):
        super().__init__()

        self.setDragDropMode(QAbstractItemView.DropOnly)
        self.setDefaultDropAction(Qt.CopyAction)
        self.setSelectionBehavior(QTableView.SelectItems)
        self.setSelectionMode(QTableView.ExtendedSelection)

        self.clipboard = QClipboard()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.table_popup)

        self.table_context_menu = QMenu(self)
        self.table_context_menu_setup()

        self.header_context_menu = QMenu(self)
        header = self.horizontalHeader()
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self.header_popup)

        self.original_top_left_selection = None

        self.resizeColumnsToContents()


    @Slot(dict)
    def set_profiles_data(self, profiles_data):
        selection_model = self.selectionModel()
        selected_rows = selection_model.selectedRows()

        print(selected_rows)

    def on_after_model_set(self):
        self.selectionModel().selectionChanged.connect(self.on_selection_changed)
        # self.model().dataChanged.connect(self.on_selection_changed)

    def on_selection_changed(self):
        selection_model = self.selectionModel()
        selected_indexes = selection_model.selectedIndexes()

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

        field = self.model().fields[column]
        state = not self.isColumnHidden(column)

        self.field_visibility_state_changed.emit(field, state)

    def get_columns_visibility_state(self):
        return {
            self.model().fields[i]: not self.isColumnHidden(i)
            for i in range(self.model().columnCount())
            }

    @Slot(str, bool)
    def set_column_visibility_state(self, field, state):

        print(field, state)

        i = self.model().fields.index(field)

        column_visible = not self.isColumnHidden(i)

        if column_visible == state:
            return

        self.setColumnHidden(i, not state)

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

    # def get_selected_data(self):
    #     selected_indexes = self.selectedIndexes()
    #     selected_data = []
    #
    #     rows = []
    #     cols = []
    #
    #     for index in selected_indexes:
    #         rows.append(index.row())
    #         cols.append(index.column())
    #
    #     min_row, max_row = min(rows), max(rows)
    #     min_col, max_col = min(cols), max(cols)
    #
    #     for row_count in range(min_row, max_row + 1):
    #         row_items = [
    #             self.model().data(
    #                 self.model().index(row_count, col_count), Qt.DisplayRole
    #             )
    #             for col_count in range(min_col, max_col + 1)
    #         ]
    #         selected_data.append(row_items)
    #
    #     return selected_data

    def get_selected_data(self):
        selected_indexes = self.selectedIndexes()
        selected_data = []

        rows = [index.row() for index in selected_indexes]
        cols = [index.column() for index in selected_indexes]

        min_row = min(rows)
        max_row = max(rows)
        min_col = min(cols)
        max_col = max(cols)

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

        model.blockSignals(True)
        for idx in selected_indexes:
            model.setData(idx, "", Qt.EditRole)

        model.blockSignals(False)
        model.dataChanged.emit(
            model.index(0, 0),
            model.index(model.rowCount() - 1, model.columnCount() - 1),
            Qt.DisplayRole
        )

    def keyPressEvent(self, event: QKeyEvent):
        current_index = self.selectionModel().currentIndex()
        if not current_index.isValid():
            return

        # Delete needs to be in a separate if statement to work (for mysterious reasons)
        if event.key() == Qt.Key_Delete:
            print("delete")
            self.delete_selection()
            return True

        match event.key(), event.modifiers():

            case Qt.Key_Left:
                new_index = self.selectionModel().index(current_index.row(), current_index.column() - 1)
                self.selectionModel().setCurrentIndex(new_index, QItemSelectionModel.ClearAndSelect)
                self.scrollTo(new_index)
                return True

            case Qt.Key_Right:
                new_index = self.selectionModel().index(current_index.row(), current_index.column() + 1)
                self.selectionModel().setCurrentIndex(new_index, QItemSelectionModel.ClearAndSelect)
                self.scrollTo(new_index)
                return True

            case Qt.Key_Up:
                new_index = self.selectionModel().index(current_index.row() - 1, current_index.column())
                self.selectionModel().setCurrentIndex(new_index, QItemSelectionModel.ClearAndSelect)
                self.scrollTo(new_index)
                return True

            case Qt.Key_Down:
                new_index = self.selectionModel().index(current_index.row() + 1, current_index.column())
                self.selectionModel().setCurrentIndex(new_index, QItemSelectionModel.ClearAndSelect)
                self.scrollTo(new_index)
                return True

            case  Qt.Key_C, Qt.ControlModifier:
                self.copy_selection()
                return True

            case Qt.Key_V, Qt.ControlModifier:
                print("paste")
                self.paste_clipboard_content()
                return True

            case Qt.Key_Return, Qt.Key_Enter:
                if self.state() != QAbstractItemView.EditingState:
                    self.edit(self.currentIndex())
                    return True

            case _:
                super().keyPressEvent(event)

    def paste_clipboard_content(self):
        model = self.model()

        source_model = clipboard_text_to_model()

        if source_model is not None:
            selected_indexes = self.selectedIndexes()

            if not selected_indexes:
                return False

            elif len(selected_indexes) == 1:
                print("single")
                # self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
                regular_paste(selected_indexes, source_model, model)
                self.selectionModel().clearSelection()
                self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
                return True

            elif len(selected_indexes) > 1:
                if source_model.rowCount() == 1 and source_model.columnCount() == 1:
                    source_index = source_model.index(0, 0)
                    # self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

                    for idx in selected_indexes:
                        model.setData(idx, source_model.data(source_index,  Qt.DisplayRole), Qt.EditRole)

                    # self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

                return True

        return False

