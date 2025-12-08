from PySide6.QtGui import (
    QKeyEvent,
    QCursor,
    QStandardItemModel,
)
from PySide6.QtCore import (
    Qt,
    Signal,
    QPoint,
    Slot,
    QItemSelectionModel,
    QSortFilterProxyModel,
    QTimer,
)
from PySide6.QtWidgets import (
    QTableView,
    QAbstractItemView,
    QApplication,
    QMenu,
    QVBoxLayout,
    QLabel,
    QHeaderView,
    QWidget,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QSizePolicy,
    QDialog,
    QDialogButtonBox,
)

from modules.models.application.application_profile import ApplicationProfile
from modules.utils.utils import json_to_obj, obj_to_json

from modules.models.sample.sample_model import CustomProxyModel
from modules.utils.utils import header_to_index_map
from modules.views.sample.column_visibility_view import ColumnVisibilityWidget


def list2d_to_tabbed_str(data):
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
        tab_delimited_row = "\t".join(map(str, row))
        tab_delimited_rows.append(tab_delimited_row)

    return "\n".join(tab_delimited_rows)


def clipboard_text_to_model():
    clipboard = QApplication.clipboard()
    mime_data = clipboard.mimeData()

    if not mime_data.hasText():
        return None

    text = mime_data.text()
    rows = text.split("\n")
    rows = [row for row in rows if row]  # remove empty rows

    max_cols = max(len(row.split("\t")) for row in rows)
    dummy_model = QStandardItemModel(len(rows), max_cols)

    for r_count, r in enumerate(rows):
        for c_count, value in enumerate(r.split("\t")):
            dummy_model.setData(dummy_model.index(r_count, c_count), value, Qt.EditRole)

    return dummy_model


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
            target_proxy_model.setData(
                target_proxy_model.index(start_row + row, start_col + col),
                value,
                Qt.EditRole,
            )

    target_proxy_model.blockSignals(False)

    target_model.refresh_view()

    return True


class SamplesWidget(QWidget):

    selection_data = Signal(object)

    def __init__(self, samples_settings):
        super().__init__()

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)

        self.setEnabled(False)

        self.samples_settings = samples_settings

        self.filter_edit = QLineEdit()
        self.samples_model = None

        self.sample_view = SampleTableView()

        self.extended_selection_pushbutton = QPushButton("extended selection")
        self.extended_selection_pushbutton.setCheckable(True)
        self.clear_selection_btn = QPushButton("clear selection")
        self.column_visibility_btn = QPushButton("column visibility")
        self.delete_rows_btn = QPushButton("delete selected rows")
        self.column_visibility_ctrl = ColumnVisibilityWidget(samples_settings)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox_filter = QHBoxLayout()
        hbox_filter.setContentsMargins(0, 0, 0, 0)

        hbox_filter.addWidget(QLabel("filter: "))
        hbox_filter.addWidget(self.filter_edit)

        hbox.addWidget(self.extended_selection_pushbutton)
        hbox.addWidget(self.clear_selection_btn)
        hbox.addWidget(self.delete_rows_btn)
        hbox.addLayout(hbox_filter)
        hbox.addWidget(self.column_visibility_btn)

        vbox.addLayout(hbox)

        hbox2 = QHBoxLayout()
        hbox2.setContentsMargins(0, 0, 0, 0)
        hbox2.addWidget(self.sample_view)
        hbox2.addWidget(self.column_visibility_ctrl)
        vbox.addLayout(hbox2)

        # vbox.addWidget(self.cell_value)
        self.setLayout(vbox)

        self.sample_view.setContextMenuPolicy(Qt.CustomContextMenu)
        header = self.sample_view.horizontalHeader()
        header.setMinimumSectionSize(100)

        self.extended_selection_pushbutton.clicked.connect(self._set_selection_mode)
        horizontal_header = self.sample_view.horizontalHeader()
        horizontal_header.setSectionsClickable(False)
        self._set_selection_mode()

        # self.appname_delegate = ApplicationNameDelegate()

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.column_visibility_ctrl.hide()

        self.column_visibility_ctrl.column_visibility_control.field_visibility_state_changed.connect(
            self.sample_view.set_column_visibility_state
        )
        self.sample_view.field_visibility_state_changed.connect(
            self.column_visibility_ctrl.column_visibility_control.set_column_visibility_state
        )
        self.column_visibility_btn.clicked.connect(self._toggle_column_visibility_ctrl)
        self.delete_rows_btn.clicked.connect(self.sample_view.del_selected_rows)

    def enable(self):
        self.setEnabled(True)

    def disable(self):
        self.setEnabled(False)

    def flash_table(self):
        self.sample_view.flash_error()

    def _toggle_column_visibility_ctrl(self):
        if self.column_visibility_ctrl.isVisible():
            self.column_visibility_ctrl.hide()
        else:
            self.column_visibility_ctrl.show()

    def _get_column_index_by_header(self, header_label):
        """
        Get the column index for the specified header label in a QTableView.

        :param view: QTableView object
        :param header_label: The header label to search for
        :return: Column index (int) if found, otherwise -1
        """
        model = self.sample_view.model()  # Get the model associated with the view
        if model is None:
            return -1

        for column in range(model.columnCount()):
            # Get the header text for each column
            header_text = model.headerData(column, Qt.Horizontal, Qt.DisplayRole)
            if header_text == header_label:
                return column
        return -1

    def set_model(self, samples_proxy_model: CustomProxyModel):
        self.sample_view.setModel(samples_proxy_model)
        self.filter_edit.textChanged.connect(samples_proxy_model.set_filter_text)

        self.sample_view.selectionModel().selectionChanged.connect(
            self._on_sampleview_selection_changed
        )
        # header_index_map = header_to_index_map(samples_proxy_model)

        header = self.sample_view.horizontalHeader()
        for col in range(samples_proxy_model.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)

    def _set_selection_mode(self):
        if self.extended_selection_pushbutton.isChecked():
            self.sample_view.setSelectionMode(QAbstractItemView.ExtendedSelection)

        else:
            self.sample_view.setSelectionMode(QAbstractItemView.ContiguousSelection)

    @staticmethod
    def _selected_rows_columns_count(selected_indexes):

        selected_rows = {index.row() for index in selected_indexes}
        selected_columns = {index.column() for index in selected_indexes}

        return len(selected_rows), len(selected_columns)

    def _on_sampleview_selection_changed(self):
        selection_model = self.sample_view.selectionModel()
        selected_indexes = selection_model.selectedIndexes()
        srows, scols = self._selected_rows_columns_count(selected_indexes)

        data = {"rows": srows, "cols": scols}

        self.selection_data.emit(data)


class WarningDialog(QDialog):
    def __init__(self, msg):
        super().__init__()

        self.setWindowTitle("Warning!")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        message = QLabel(msg)
        layout.addWidget(message)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


class SampleTableView(QTableView):

    field_visibility_state_changed = Signal(str, bool)
    cell_selected = Signal(str)
    override_patterns_ready = Signal(list)

    def __init__(self):
        super().__init__()

        self.setDragDropMode(QAbstractItemView.DropOnly)
        self.setDefaultDropAction(Qt.CopyAction)
        self.setSelectionBehavior(QTableView.SelectItems)
        self.setSelectionMode(QTableView.ExtendedSelection)

        self.clipboard = QApplication.clipboard()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._table_popup)

        self.table_context_menu = QMenu(self)
        self._table_context_menu_setup()

        self.header_context_menu = QMenu(self)
        header = self.horizontalHeader()
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self._header_popup)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def flash_error(self):
        original_style = self.styleSheet()
        self.setStyleSheet("border: 1px solid red;")
        QTimer.singleShot(500, lambda: self.setStyleSheet(original_style))

    def _get_column_index_by_header(self, header_label):
        """
        Get the column index for the specified header label in a QTableView.

        :param view: QTableView object
        :param header_label: The header label to search for
        :return: Column index (int) if found, otherwise -1
        """
        model = self.model()  # Get the model associated with the view
        if model is None:
            return -1

        for column in range(model.columnCount()):
            # Get the header text for each column
            header_text = model.headerData(column, Qt.Horizontal, Qt.DisplayRole)
            if header_text == header_label:
                return column
        return -1

    def del_selected_rows(self):
        selected_rows = self.selectionModel().selectedRows()
        self.model().removeRows(selected_rows[0].row(), len(selected_rows))

    @Slot(dict)
    def remove_application_profile_id(self, application_profile: ApplicationProfile) -> None:

        print("remove", application_profile)

        proxy_model = self.model()
        source_model = proxy_model.sourceModel()
        selection_model = self.selectionModel()
        selected_rows = [index.row() for index in selection_model.selectedRows()]

        if not selected_rows:
            return

        header_index_map = header_to_index_map(proxy_model)

        appname_column = header_index_map["ApplicationProfileId"]
        application_profile_id = application_profile.id
        application_name = application_profile.application_name
        application_profile_data = application_profile.data

        source_model.blockSignals(True)

        for row in selected_rows:
            app_profile_ids_json = (
                proxy_model.data(proxy_model.index(row, appname_column), Qt.DisplayRole)
                or "[]"
            )
            app_profile_ids_list = json_to_obj(app_profile_ids_json)
            if application_profile_id in app_profile_ids_list:
                app_profile_ids_list.remove(application_profile_id)

            app_profile_ids_json = obj_to_json(app_profile_ids_list)

            proxy_model.setData(
                proxy_model.index(row, appname_column),
                app_profile_ids_json,
                Qt.EditRole,
            )

            if application_name == "BCLConvert":
                self._set_bclconvert_data_empty(
                    proxy_model, row, header_index_map, application_profile_data
                )

        source_model.blockSignals(False)

        source_model.dataChanged.emit(
            source_model.index(0, 0),
            source_model.index(
                source_model.rowCount() - 1, source_model.columnCount() - 1
            ),
            Qt.DisplayRole,
        )

        # self._set_dynamic_column_width()

    @Slot(object)
    def set_application_profile_id(self, application_profile: ApplicationProfile) -> None:
        """
        Sets the application_name data for the selected rows in the model.

        This method updates the specified rows in the proxy model with the application_name data
        provided in the application_object. If the application_name is already set in the selection,
        a warning dialog is displayed. Special handling is performed for the "BCLConvert"
        application_name to set additional data.

        Parameters:
        - application_object (dict): A dictionary containing the application_name details, including:
            - "Data": The data to be set for the application_name.
            - "ApplicationName": The name of the application_name.
            - "Application": The type of application_name.

        Returns:
        - None
        """

        print("application_profile", application_profile)

        data = application_profile.data

        proxy_model = self.model()
        source_model = proxy_model.sourceModel()
        selection_model = self.selectionModel()
        selected_rows = [index.row() for index in selection_model.selectedRows()]

        if not selected_rows:
            return

        header_index_map = header_to_index_map(proxy_model)

        app_name_column = header_index_map["ApplicationProfileId"]
        app_profile_id = application_profile.id
        application_name = application_profile.application_name

        source_model.blockSignals(True)

        for row in selected_rows:
            self._set_str_to_json(proxy_model, row, app_name_column, app_profile_id)

            if application_name == "BCLConvert":
                self._set_bclconvert_data(
                    proxy_model, row, header_index_map, data
                )

        source_model.blockSignals(False)
        source_model.dataChanged.emit(
            source_model.index(0, 0),
            source_model.index(
                source_model.rowCount() - 1, source_model.columnCount() - 1
            ),
            Qt.DisplayRole,
        )

    @Slot(list)
    def set_lanes(self, lanes: list) -> None:
        proxy_model = self.model()
        source_model = proxy_model.sourceModel()
        selection_model = self.selectionModel()
        selected_rows = [index.row() for index in selection_model.selectedRows()]

        if not selected_rows:
            return

        lanes_json = obj_to_json(lanes)

        header_index_map = header_to_index_map(proxy_model)
        lane_column = header_index_map["Lane"]

        source_model.blockSignals(True)

        for row in selected_rows:
            proxy_model.setData(
                proxy_model.index(row, lane_column), lanes_json, Qt.EditRole
            )

        source_model.blockSignals(False)

        source_model.dataChanged.emit(
            source_model.index(0, 0),
            source_model.index(
                source_model.rowCount() - 1, source_model.columnCount() - 1
            ),
            Qt.DisplayRole,
        )

    @staticmethod
    def _set_bclconvert_data(
        proxy_model: QSortFilterProxyModel,
        row: int,
        header_index_map: dict,
        app_data: dict,
    ) -> None:
        """
        Sets BCLConvert data in the specified row of the proxy model.

        Parameters:
        - proxy_model: The QSortFilterProxyModel to set data in.
        - row: The row index in the proxy model.
        - header_index_map: A dictionary mapping header keys to column indices.
        - app_data: A dictionary of data to set.
        """
        if not proxy_model or row < 0 or not app_data:
            return

        for key, value in app_data.items():
            column = header_index_map.get(key)
            if column is not None:
                proxy_model.setData(proxy_model.index(row, column), value)

    @staticmethod
    def _set_bclconvert_data_empty(
        proxy_model: QSortFilterProxyModel,
        row: int,
        header_index_map: dict,
        app_data: dict,
    ) -> None:
        """
        Sets BCLConvert data in the specified row of the proxy model.

        Parameters:
        - proxy_model: The QSortFilterProxyModel to set data in.
        - row: The row index in the proxy model.
        - header_index_map: A dictionary mapping header keys to column indices.
        - app_data: A dictionary of data to set.
        """
        if not proxy_model or row < 0 or not app_data:
            return

        for key, value in app_data.items():
            column = header_index_map.get(key)
            if column is not None:
                proxy_model.setData(proxy_model.index(row, column), "")

    @staticmethod
    def _json_data_as_obj(model: QSortFilterProxyModel, row: int, column: int) -> str:
        """
        Retrieve JSON data from a specified cell in the model and return it as a Python object.

        Parameters:
        - model: The QAbstractItemModel from which data is retrieved.
        - row: The row index of the cell.
        - column: The column index of the cell.

        Returns:
        - The JSON data from the specified cell, parsed as a Python object.
        """
        data = model.data(model.index(row, column), Qt.DisplayRole) or "[]"
        return json_to_obj(data)

    @staticmethod
    def _set_str_to_json(model, row: int, column: int, value: str) -> None:
        """
        Sets the value of the specified cell to the given value, stored as a json
        array. If the cell is currently empty, it will be initialized with an
        empty list.
        """
        current_data = model.data(model.index(row, column), Qt.DisplayRole) or "[]"
        data = json_to_obj(current_data)
        if value not in data:
            data.append(value)
            model.setData(model.index(row, column), obj_to_json(data))

    def _table_popup(self):
        self.table_context_menu.exec(QCursor.pos())

    def _table_context_menu_setup(self):
        copy_action = self.table_context_menu.addAction("Copy")
        paste_action = self.table_context_menu.addAction("Paste")
        delete_action = self.table_context_menu.addAction("Delete")

        copy_action.triggered.connect(self._copy_selection)
        paste_action.triggered.connect(self.paste_clipboard_content)
        delete_action.triggered.connect(self._delete_selection)

    def setColumnHidden(self, column, hide):
        super().setColumnHidden(column, hide)

        field = self.model().sourceModel().fields[column]
        state = not self.isColumnHidden(column)

        self.field_visibility_state_changed.emit(field, state)

    @Slot(str, bool)
    def set_column_visibility_state(self, field: str, state: bool) -> None:
        i = self.model().sourceModel().fields.index(field)

        column_visible = not self.isColumnHidden(i)

        if column_visible == state:
            return

        self.setColumnHidden(i, not state)

    def _header_popup(self, pos: QPoint):
        """
        Display a context menu when right-clicking on the header of the SampleTableView.

        Args:
            pos (QPoint): The position of the right-click event.
        """
        # Get the index and clicked column of the clicked header
        index = self.indexAt(pos)
        clicked_column = index.column()

        selected_columns = self._get_selected_columns()

        # Get the name of the clicked column
        colname = self.model().sourceModel().fields[clicked_column]

        # Clear the context menu
        self.header_context_menu.clear()

        # Create an action to hide the selected clicked column
        if not selected_columns:
            hide_clicked_action = self.header_context_menu.addAction(
                f"Hide field ({colname})"
            )
            hide_clicked_action.triggered.connect(
                lambda: self.setColumnHidden(clicked_column, True)
            )
            self.header_context_menu.exec(QCursor.pos())
            return

        # Create an action to hide the selected columns
        if len(selected_columns) > 0:
            hide_selected_cols = self.header_context_menu.addAction(
                "Hide selected fields"
            )
            hide_selected_cols.triggered.connect(
                lambda: self._set_columns_hidden(selected_columns)
            )
            self.header_context_menu.exec(QCursor.pos())
            return

    def _set_columns_hidden(self, selected_columns):

        for col in selected_columns:
            self.setColumnHidden(col, True)

        self.clearSelection()

    def _get_selected_columns(self):
        selection_model = self.selectionModel()
        selected_indexes = selection_model.selectedColumns()
        return [column.column() for column in selected_indexes]

    def _copy_selection(self):
        selected_data = self._get_selected_data()
        selected_csv = list2d_to_tabbed_str(selected_data)
        self.clipboard.setText(selected_csv)

    def _get_selected_data(self):
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

    def _delete_selection(self):

        model = self.model()
        selected_indexes = self.selectedIndexes()

        model.blockSignals(True)
        for idx in selected_indexes:
            model.setData(idx, "", Qt.EditRole)

        model.blockSignals(False)
        model.dataChanged.emit(
            model.index(0, 0),
            model.index(model.rowCount() - 1, model.columnCount() - 1),
            Qt.DisplayRole,
        )

    def keyPressEvent(self, event: QKeyEvent):
        current_index = self.selectionModel().currentIndex()
        if not current_index.isValid():
            return

        # Delete needs to be in a separate if statement to work (for mysterious reasons)
        if event.key() == Qt.Key_Delete:
            self._delete_selection()
            return True

        match event.key(), event.modifiers():

            case Qt.Key_Left:
                new_index = self.selectionModel().index(
                    current_index.row(), current_index.column() - 1
                )
                self.selectionModel().setCurrentIndex(
                    new_index, QItemSelectionModel.ClearAndSelect
                )
                self.scrollTo(new_index)
                return True

            case Qt.Key_Right:
                new_index = self.selectionModel().index(
                    current_index.row(), current_index.column() + 1
                )
                self.selectionModel().setCurrentIndex(
                    new_index, QItemSelectionModel.ClearAndSelect
                )
                self.scrollTo(new_index)
                return True

            case Qt.Key_Up:
                new_index = self.selectionModel().index(
                    current_index.row() - 1, current_index.column()
                )
                self.selectionModel().setCurrentIndex(
                    new_index, QItemSelectionModel.ClearAndSelect
                )
                self.scrollTo(new_index)
                return True

            case Qt.Key_Down:
                new_index = self.selectionModel().index(
                    current_index.row() + 1, current_index.column()
                )
                self.selectionModel().setCurrentIndex(
                    new_index, QItemSelectionModel.ClearAndSelect
                )
                self.scrollTo(new_index)
                return True

            case Qt.Key_C, Qt.ControlModifier:
                self._copy_selection()
                return True

            case Qt.Key_V, Qt.ControlModifier:
                self.paste_clipboard_content()
                return True

            case Qt.Key_Return, Qt.Key_Enter:
                if self.state() != QAbstractItemView.EditingState:
                    self.edit(self.currentIndex())
                    return True

            case _:
                super().keyPressEvent(event)

    def paste_clipboard_content(self) -> bool:
        """
        Paste the content from the clipboard into the selected cell(s) of the model.

        This function retrieves text data from the clipboard, converts it into a model,
        and pastes it into the selected indexes of the current model. If only one cell
        is selected, the entire clipboard content is pasted starting from that cell. If
        multiple cells are selected and the clipboard content is a single cell, it is
        duplicated across the selected cells.
        
        The function blocks model signals during the paste operation and emits
        a single signal when done to improve performance.

        Returns:
            bool: True if the paste operation was successful, False otherwise.
        """
        model = self.model()
        
        # Block signals before making changes
        model.blockSignals(True)
        source_model = clipboard_text_to_model()
        source_model.blockSignals(True)

        if source_model is not None:
            selected_indexes = self.selectedIndexes()

            if not selected_indexes:
                model.blockSignals(False)  # Unblock signals before returning
                return False

            try:
                if len(selected_indexes) == 1:
                    regular_paste(selected_indexes, source_model, model)
                    self.selectionModel().clearSelection()
                    self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
                elif len(selected_indexes) > 1:
                    if source_model.rowCount() == 1 and source_model.columnCount() == 1:
                        source_index = source_model.index(0, 0)
                        for idx in selected_indexes:
                            model.setData(
                                idx,
                                source_model.data(source_index, Qt.DisplayRole),
                                Qt.EditRole,
                            )
                
                # Emit dataChanged for all affected items after unblocking signals
                if selected_indexes:
                    top_left = selected_indexes[0]
                    bottom_right = selected_indexes[-1]
                    model.blockSignals(False)
                    source_model.blockSignals(False)
                    # Unblock signals
                    model.dataChanged.emit(top_left, bottom_right)
                    return True
                    
            except Exception as e:
                model.blockSignals(False)  # Make sure to unblock signals even if error occurs
                source_model.blockSignals(False)
                raise e

        model.blockSignals(False)
        source_model.blockSignals(False)
        # Unblock signals if we get here
        return False

    @Slot(str)
    def set_override_pattern(self, pattern: str) -> None:
        """
        Sets the OverrideCyclesPattern for the selected rows to the given pattern.

        If no rows are selected, this does nothing.

        :param pattern: The pattern to set
        """
        selection_model = self.selectionModel()
        if not selection_model:
            return

        selected_rows = [index.row() for index in selection_model.selectedRows()]

        source_model = self.model()
        if not source_model:
            return

        header_labels = [
            source_model.headerData(col, Qt.Horizontal, Qt.DisplayRole)
            for col in range(source_model.columnCount())
        ]
        override_col = header_labels.index("OverrideCyclesPattern")

        for row in selected_rows:
            index = source_model.index(row, override_col)
            if index.isValid():
                source_model.setData(index, pattern, Qt.EditRole)

    def get_override_pattern(self) -> None:
        """Get the override pattern for the selected rows in the table view.

        This function retrieves the OverrideCyclesPattern column data for the selected
        rows in the table view. The data is then emitted via the override_patterns_ready
        signal.

        :return: None
        :rtype: None
        """
        model = self.model()
        if not model:
            return

        selected_indexes = self.selectedIndexes()
        if not selected_indexes:
            return

        header_labels = [
            model.headerData(col, Qt.Horizontal, Qt.DisplayRole)
            for col in range(model.columnCount())
        ]

        override_col = header_labels.index("OverrideCyclesPattern")

        data = []
        for index in selected_indexes:
            if not index.isValid():
                continue

            row = index.row()
            if row < 0 or row >= model.rowCount():
                continue

            index = model.index(row, override_col)
            if not index.isValid():
                continue

            data.append(model.data(index, Qt.DisplayRole))

        self.override_patterns_ready.emit(data)
