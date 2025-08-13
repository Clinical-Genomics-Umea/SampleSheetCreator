import json
from typing import Any, Dict, Optional, Union

from PySide6.QtCore import QEvent, QModelIndex, QSize, Qt, QRect
from PySide6.QtGui import (
    QColor,
    QPainter,
    QTextBlockFormat,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
    QTextFormat,
    QTextOption,
    QIntValidator,
)
from PySide6.QtWidgets import (
    QLineEdit,
    QMenu,
    QPushButton,
    QStyleOptionViewItem,
    QStyledItemDelegate,
)


class ColorBalanceRowDelegate(QStyledItemDelegate):
    """
    A delegate for rendering color balance information in a table view.
    Handles special rendering for color balance rows and adjacent G-base warnings.
    """
    
    # Define warning colors
    WARNING_COLOR = QColor(255, 200, 200)  # Light red for warnings
    WARNING_TEXT_COLOR = QColor(180, 0, 0)  # Dark red for warning text
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._document_cache = {}

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        """
        Paint the cell with appropriate formatting based on its content and position.
        """
        if not index.isValid():
            return
            
        last_row = index.model().rowCount() - 1
        column = index.column()
        
        try:
            # Handle special rows and columns
            if column >= 2 and index.row() == last_row:
                self._paint_color_balance_row(painter, option, index)
            elif column in (2, 3):  # Check for adjacent G bases
                self._paint_adjacent_g_warning(painter, option, index)
            else:
                super().paint(painter, option, index)
        except Exception as e:
            # Fallback to default painting on error
            super().paint(painter, option, index)

    def _paint_adjacent_g_warning(self, painter: QPainter, option: QStyleOptionViewItem, 
                                index: QModelIndex) -> None:
        """
        Highlight cells with adjacent 'G' bases that might cause color balance issues.
        """
        model = index.model()
        current_value = model.data(index, Qt.DisplayRole)
        
        # Get the adjacent column (2 <-> 3)
        adjacent_col = 3 if index.column() == 2 else 2
        adjacent_index = model.index(index.row(), adjacent_col, index.parent())
        adjacent_value = model.data(adjacent_index, Qt.DisplayRole)
        
        # Check for adjacent G bases
        if current_value == adjacent_value == "G":
            painter.save()
            
            # Draw warning background
            painter.fillRect(option.rect, self.WARNING_COLOR)
            
            # Draw text with warning color
            text = str(current_value or "")
            text_rect = option.rect.adjusted(2, 0, -2, 0)  # Add some padding
            
            # Center the text
            text_option = option
            text_option.displayAlignment = Qt.AlignCenter
            
            # Draw text with warning color
            painter.setPen(self.WARNING_TEXT_COLOR)
            painter.drawText(text_rect, text_option.displayAlignment, text)
            
            # Draw a subtle border
            painter.setPen(QColor(200, 150, 150))
            painter.drawRect(option.rect.adjusted(0, 0, -1, -1))
            
            painter.restore()
        else:
            super().paint(painter, option, index)

    def _paint_color_balance_row(self, painter: QPainter, option: QStyleOptionViewItem, 
                               index: QModelIndex) -> None:
        """
        Render the color balance summary row with formatted text and warnings.
        """
        json_data = index.data(Qt.DisplayRole)
        if not json_data:
            return

        try:
            data = json.loads(json_data)
            
            # Create a document with formatted text
            doc = QTextDocument()
            doc.setDocumentMargin(2)  # Reduce margins
            
            # Configure default text format
            default_format = QTextCharFormat()
            default_format.setFontPointSize(9)  # Slightly smaller font
            
            # Create cursor for text insertion
            cursor = QTextCursor(doc)
            cursor.setCharFormat(default_format)
            
            # Add colors section
            self._add_section(cursor, "Colors", data.get("colors", {}), default_format)
            
            # Add a single dashed line as separator
            cursor.insertBlock()
            separator_format = QTextCharFormat(default_format)
            separator_format.setFontPointSize(8)  # Slightly smaller for separator
            cursor.insertText("-" * 8, separator_format)  # Single dashed line
            cursor.insertBlock()
            
            # Add bases section
            self._add_section(cursor, "Bases", data.get("bases", {}), default_format)
            
            # Check for warnings
            colors = data.get("colors", {})
            if colors.get("G", 0) < 0.1:  # Low green warning
                self._add_warning_background(doc, "Low green channel detected")
            
            # Draw the document
            painter.save()
            painter.translate(option.rect.topLeft())
            doc.setTextWidth(option.rect.width())
            doc.drawContents(painter)
            painter.restore()
            
        except (json.JSONDecodeError, AttributeError) as e:
            # Fallback to default rendering on error
            super().paint(painter, option, index)

    def _add_section(self, cursor: QTextCursor, title: str, 
                    data: Dict[str, Any], default_format: QTextCharFormat) -> None:
        """Add a section with title and key-value pairs to the document."""
        # Add section title
        title_format = QTextCharFormat(default_format)
        title_format.setFontWeight(600)  # Make title bold
        cursor.insertText(f"{title}:\n", title_format)
        
        # Add key-value pairs
        for key, value in data.items():
            cursor.insertText(f"  {key}: ", default_format)
            
            # Format values differently based on type
            value_format = QTextCharFormat(default_format)
            if isinstance(value, (int, float)):
                if key.lower() == 'g' and value < 0.1:  # Highlight low green values
                    value_format.setForeground(Qt.red)
                    value_format.setFontWeight(600)
                value_text = f"{value:.2f}" if isinstance(value, float) else str(value)
            else:
                value_text = str(value)
                
            cursor.insertText(value_text, value_format)
            cursor.insertText("\n", default_format)

    def _add_warning_background(self, doc: QTextDocument, message: str) -> None:
        """Add a warning background to the document."""
        cursor = QTextCursor(doc)
        cursor.movePosition(QTextCursor.Start)
        
        # Apply background to the first block (colors section)
        block_format = QTextBlockFormat()
        block_format.setBackground(self.WARNING_COLOR)
        cursor.select(QTextCursor.BlockUnderCursor)
        cursor.mergeBlockFormat(block_format)
        
        # Add a tooltip with the warning message
        char_format = QTextCharFormat()
        char_format.setToolTip(message)
        cursor.mergeCharFormat(char_format)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        """
        Return the size hint for the item at the given index.
        """
        if not index.isValid():
            return super().sizeHint(option, index)
            
        last_row = index.model().rowCount() - 1
        
        # Only calculate custom size for color balance rows
        if index.column() >= 2 and index.row() == last_row:
            # Use cached document if available
            cache_key = f"{index.row()}_{index.column()}"
            if cache_key not in self._document_cache:
                doc = QTextDocument()
                doc.setDocumentMargin(2)
                doc.setPlainText(str(index.data(Qt.DisplayRole) or ""))
                doc.setTextWidth(option.rect.width())
                self._document_cache[cache_key] = doc
            
            doc = self._document_cache[cache_key]
            return QSize(
                int(doc.idealWidth() + 4),  # Add some padding
                int(doc.size().height() + 4)
            )
            
        return super().sizeHint(option, index)

    def editorEvent(self, event: QEvent, model: Any, option: QStyleOptionViewItem, 
                   index: QModelIndex) -> bool:
        """
        Handle editor events for the item.
        """
        if event.type() == QEvent.MouseButtonDblClick and index.column() == 0:
            self._show_context_menu(event.globalPos(), index)
            return True
        return super().editorEvent(event, model, option, index)

    def _show_context_menu(self, pos, index):
        """Show a context menu for the item."""
        menu = QMenu()
        # Add your custom actions here
        menu.addAction("View Details", lambda: self._handle_menu_action(index, "view"))
        menu.addAction("Edit...", lambda: self._handle_menu_action(index, "edit"))
        menu.exec_(pos)

    def _handle_menu_action(self, index: QModelIndex, action: str) -> None:
        """Handle menu actions."""
        # Implement your action handling logic here
        print(f"Action '{action}' on row {index.row()}")

    def createEditor(self, parent, option, index):
        """
        Create an editor for the item.
        """
        if index.column() == 1:  # Only create editor for proportion column
            editor = QLineEdit(parent)
            editor.setValidator(QIntValidator(1, 1000, parent))
            return editor
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        """
        Set the data for the editor.
        """
        if isinstance(editor, QLineEdit):
            editor.setText(str(index.data(Qt.EditRole) or ""))
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        """
        Set the data from the editor to the model.
        """
        if isinstance(editor, QLineEdit):
            model.setData(index, editor.text(), Qt.EditRole)
        else:
            super().setModelData(editor, model, index)
