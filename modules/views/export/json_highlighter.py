from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont


class JsonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Define highlighting rules
        self.highlighting_rules = []

        # JSON key format (strings followed by colon)
        key_format = QTextCharFormat()
        key_format.setForeground(QColor(86, 156, 214))  # Light blue
        key_format.setFontWeight(QFont.Weight.Bold)
        key_pattern = QRegularExpression(r'"[^"]*"\s*:')
        self.highlighting_rules.append((key_pattern, key_format))

        # JSON string values
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(206, 145, 120))  # Light brown/orange
        string_pattern = QRegularExpression(r'"[^"]*"')
        self.highlighting_rules.append((string_pattern, string_format))

        # JSON numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(181, 206, 168))  # Light green
        number_pattern = QRegularExpression(r'\b-?\d+\.?\d*([eE][+-]?\d+)?\b')
        self.highlighting_rules.append((number_pattern, number_format))

        # JSON boolean values
        boolean_format = QTextCharFormat()
        boolean_format.setForeground(QColor(86, 156, 214))  # Light blue
        boolean_format.setFontWeight(QFont.Weight.Bold)
        boolean_pattern = QRegularExpression(r'\b(true|false)\b')
        self.highlighting_rules.append((boolean_pattern, boolean_format))

        # JSON null values
        null_format = QTextCharFormat()
        null_format.setForeground(QColor(86, 156, 214))  # Light blue
        null_format.setFontWeight(QFont.Weight.Bold)
        null_pattern = QRegularExpression(r'\bnull\b')
        self.highlighting_rules.append((null_pattern, null_format))

        # JSON brackets and braces
        bracket_format = QTextCharFormat()
        bracket_format.setForeground(QColor(255, 215, 0))  # Gold
        bracket_format.setFontWeight(QFont.Weight.Bold)
        bracket_pattern = QRegularExpression(r'[\[\]{}]')
        self.highlighting_rules.append((bracket_pattern, bracket_format))

        # JSON colons and commas
        punctuation_format = QTextCharFormat()
        punctuation_format.setForeground(QColor(255, 255, 255))  # White
        punctuation_pattern = QRegularExpression(r'[,:;]')
        self.highlighting_rules.append((punctuation_pattern, punctuation_format))

        # Comments (not standard JSON, but useful for development)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(106, 153, 85))  # Green
        comment_format.setFontItalic(True)
        comment_pattern = QRegularExpression(r'//.*')
        self.highlighting_rules.append((comment_pattern, comment_format))

    def highlightBlock(self, text):
        # Apply all highlighting rules
        for pattern, format in self.highlighting_rules:
            expression = QRegularExpression(pattern)
            match_iterator = expression.globalMatch(text)

            while match_iterator.hasNext():
                match = match_iterator.next()
                start_index = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(start_index, length, format)

        # Handle multi-line strings (though not standard JSON)
        self.setCurrentBlockState(0)

        # Special handling for string highlighting to avoid conflicts
        # Remove string highlighting from keys by re-highlighting keys after strings
        key_pattern = QRegularExpression(r'"[^"]*"\s*:')
        key_format = QTextCharFormat()
        key_format.setForeground(QColor(86, 156, 214))
        key_format.setFontWeight(QFont.Weight.Bold)

        match_iterator = key_pattern.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            start_index = match.capturedStart()
            length = match.capturedLength()
            self.setFormat(start_index, length, key_format)