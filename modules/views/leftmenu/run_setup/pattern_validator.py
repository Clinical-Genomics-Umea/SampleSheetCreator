from PySide6.QtGui import QValidator


class PatternValidator(QValidator):
    def __init__(self, pattern, parent=None):
        super().__init__(parent)
        self.pattern = pattern
        if pattern == "":
            self.pattern_parts = []
        else:
            self.pattern_parts = [int(part) for part in pattern.split("-")]

    def validate(self, input_text, pos):
        # Allow empty input as an intermediate state
        if input_text == "":
            return QValidator.Intermediate, input_text, pos

        # Check for multiple consecutive dashes
        if "--" in input_text:
            return QValidator.Invalid, input_text, pos

        # Split the input text into parts
        input_parts = input_text.split("-")

        # Check if the number of parts exceeds the pattern
        if len(input_parts) > len(self.pattern_parts):
            return QValidator.Invalid, input_text, pos

        for i, part in enumerate(input_parts):
            # Allow incomplete trailing dashes (e.g., "51-")
            if part == "":
                # Invalid if it's not the last part and it's empty
                if i < len(input_parts) - 1:
                    return QValidator.Invalid, input_text, pos
                continue

            # Ensure each part is numeric
            if not part.isdigit():
                return QValidator.Invalid, input_text, pos

            # Check if the part exceeds the corresponding pattern value
            if i < len(self.pattern_parts) and int(part) > self.pattern_parts[i]:
                return QValidator.Invalid, input_text, pos

        # Allow trailing dashes as valid intermediate states
        if input_text[-1] == "-" and len(input_parts) <= len(self.pattern_parts):
            return QValidator.Intermediate, input_text, pos

        return QValidator.Acceptable, input_text, pos

    def fixup(self, input_text):
        # If invalid, return an empty string
        return ""
