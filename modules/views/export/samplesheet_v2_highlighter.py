import re
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget


class IlluminaSamplesheetV2Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        # State tracking for different sections
        self.IN_NORMAL_SECTION = 0
        self.IN_DATA_SECTION = 1
        self.IN_DATA_HEADER = 2
        self.IN_DATA_ROWS = 3

        # Define highlighting formats
        self.setup_formats()

        # Track current section type
        self.current_section_type = self.IN_NORMAL_SECTION
        self.data_section_name = ""

    def setup_formats(self):
        # Section headers [Header]
        self.section_format = QTextCharFormat()
        self.section_format.setForeground(QColor(86, 156, 214))  # Light blue
        self.section_format.setFontWeight(QFont.Weight.Bold)

        # Data section headers [Header_Data]
        self.data_section_format = QTextCharFormat()
        self.data_section_format.setForeground(QColor(255, 165, 0))  # Orange
        self.data_section_format.setFontWeight(QFont.Weight.Bold)

        # INI-style keys
        self.key_format = QTextCharFormat()
        self.key_format.setForeground(QColor(156, 220, 254))  # Light cyan
        self.key_format.setFontWeight(QFont.Weight.Bold)

        # INI-style values
        self.value_format = QTextCharFormat()
        self.value_format.setForeground(QColor(206, 145, 120))  # Light brown

        # CSV headers (column names in data sections)
        self.csv_header_format = QTextCharFormat()
        self.csv_header_format.setForeground(QColor(78, 201, 176))  # Teal
        self.csv_header_format.setFontWeight(QFont.Weight.Bold)

        # CSV data cells
        self.csv_data_format = QTextCharFormat()
        self.csv_data_format.setForeground(QColor(220, 220, 220))  # Light gray

        # CSV separators (commas)
        self.csv_separator_format = QTextCharFormat()
        self.csv_separator_format.setForeground(QColor(128, 128, 128))  # Gray

        # Comments
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor(106, 153, 85))  # Green
        self.comment_format.setFontItalic(True)

        # Numbers in CSV data
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor(181, 206, 168))  # Light green

        # Empty/missing values
        self.empty_format = QTextCharFormat()
        self.empty_format.setForeground(QColor(128, 128, 128))  # Gray
        self.empty_format.setFontItalic(True)

    def highlightBlock(self, text):
        # Handle comments first (lines starting with # or ;)
        comment_pattern = QRegularExpression(r'^[#;].*')
        comment_match = comment_pattern.match(text)
        if comment_match.hasMatch():
            self.setFormat(0, len(text), self.comment_format)
            return

        # Handle empty lines
        if not text.strip():
            return

        # Check for section headers
        section_pattern = QRegularExpression(r'^\[([^\]]+)\]')
        section_match = section_pattern.match(text)

        if section_match.hasMatch():
            section_name = section_match.captured(1)

            # Check if this is a data section
            if '_Data' in section_name:
                self.setFormat(0, len(text), self.data_section_format)
                self.setCurrentBlockState(self.IN_DATA_SECTION)
                self.data_section_name = section_name
            else:
                self.setFormat(0, len(text), self.section_format)
                self.setCurrentBlockState(self.IN_NORMAL_SECTION)
                self.data_section_name = ""
            return

        # Get previous block state to understand context
        previous_state = self.previousBlockState() if self.previousBlockState() != -1 else self.IN_NORMAL_SECTION

        # Handle content based on section type
        if previous_state == self.IN_DATA_SECTION:
            # First line after data section header should be CSV headers
            self.highlight_csv_header(text)
            self.setCurrentBlockState(self.IN_DATA_HEADER)
        elif previous_state == self.IN_DATA_HEADER or previous_state == self.IN_DATA_ROWS:
            # Subsequent lines are CSV data rows
            if text.strip():  # Only if line has content
                self.highlight_csv_data(text)
                self.setCurrentBlockState(self.IN_DATA_ROWS)
            else:
                self.setCurrentBlockState(previous_state)
        else:
            # Regular INI-style key=value pairs
            self.highlight_ini_line(text)
            self.setCurrentBlockState(self.IN_NORMAL_SECTION)

    def highlight_csv_header(self, text):
        """Highlight CSV header row (column names)"""
        # Split by comma and highlight each header
        parts = text.split(',')
        position = 0

        # Define the same column colors as in highlight_csv_data
        column_colors = [
            QColor(255, 120, 120),  # Bright red - Lane/Sample_ID
            QColor(100, 200, 255),  # Bright blue - Sample names
            QColor(200, 120, 255),  # Bright purple - Plate/Well info
            QColor(255, 180, 60),  # Bright orange - Index IDs
            QColor(100, 255, 150),  # Bright green - Index sequences
            QColor(255, 120, 200),  # Bright pink - Projects
            QColor(100, 220, 255),  # Bright cyan - Descriptions
        ]

        for i, part in enumerate(parts):
            part_stripped = part.strip()

            # Find the actual position of this part in the original text
            start_pos = text.find(part, position)
            if start_pos != -1:
                if part_stripped:
                    # Create format for this header
                    header_format = QTextCharFormat()
                    color_index = i % len(column_colors)
                    header_format.setForeground(column_colors[color_index])
                    header_format.setFontWeight(QFont.Weight.Bold)

                    self.setFormat(start_pos, len(part_stripped), header_format)
                else:
                    self.setFormat(start_pos, len(part), self.empty_format)

                position = start_pos + len(part)

                # Highlight comma separator
                if i < len(parts) - 1:
                    comma_pos = text.find(',', position)
                    if comma_pos != -1:
                        self.setFormat(comma_pos, 1, self.csv_separator_format)
                        position = comma_pos + 1

    def highlight_csv_data(self, text):
        """Highlight CSV data rows"""
        parts = text.split(',')
        position = 0

        # Define column colors (cycle through them)
        column_colors = [
            QColor(255, 120, 120),  # Bright red - Lane/Sample_ID
            QColor(100, 200, 255),  # Bright blue - Sample names
            QColor(200, 120, 255),  # Bright purple - Plate/Well info
            QColor(255, 180, 60),   # Bright orange - Index IDs
            QColor(100, 255, 150),  # Bright green - Index sequences
            QColor(255, 120, 200),  # Bright pink - Projects
            QColor(100, 220, 255),  # Bright cyan - Descriptions
        ]

        for i, part in enumerate(parts):
            part_stripped = part.strip()

            # Find the actual position of this part in the original text
            start_pos = text.find(part, position)
            if start_pos != -1:
                if part_stripped:
                    # Create format for this column
                    column_format = QTextCharFormat()

                    # Check if it's a number
                    if self.is_numeric(part_stripped):
                        column_format.setForeground(QColor(181, 206, 168))  # Light green for numbers
                        column_format.setFontWeight(QFont.Weight.Bold)
                    else:
                        # Use column-specific color
                        color_index = i % len(column_colors)
                        column_format.setForeground(column_colors[color_index])

                    self.setFormat(start_pos, len(part_stripped), column_format)
                else:
                    # Empty cell
                    self.setFormat(start_pos, len(part), self.empty_format)

                position = start_pos + len(part)

                # Highlight comma separator
                if i < len(parts) - 1:
                    comma_pos = text.find(',', position)
                    if comma_pos != -1:
                        self.setFormat(comma_pos, 1, self.csv_separator_format)
                        position = comma_pos + 1

    def highlight_ini_line(self, text):
        """Highlight INI-style key=value pairs"""
        # Pattern for key=value
        ini_pattern = QRegularExpression(r'^([^=]+?)=(.*)$')
        match = ini_pattern.match(text)

        if match.hasMatch():
            # Highlight the key
            key = match.captured(1)
            self.setFormat(match.capturedStart(1), len(key), self.key_format)

            # Highlight the equals sign
            self.setFormat(match.capturedStart(2) - 1, 1, self.csv_separator_format)

            # Highlight the value
            value = match.captured(2)
            if value:  # Only try to highlight if there's a value
                if self.is_numeric(value.strip()):
                    self.setFormat(match.capturedStart(2), len(value), self.number_format)
                else:
                    self.setFormat(match.capturedStart(2), len(value), self.value_format)

    def is_numeric(self, text):
        """Check if text represents a numeric value"""
        try:
            float(text)
            return True
        except ValueError:
            return False
