import re
from PySide6.QtGui import QValidator


class PatternValidator(QValidator):
    def __init__(self, template=None, parent=None):
        super().__init__(parent)
        self.template = None
        self.template_values = []
        if template:
            self.set_template(template)

    def set_template(self, template):
        """Set a new template dynamically."""

        if not template:
            return

        self.template = template
        self.template_values = self._parse_template(template)

    def get_template(self):
        """Get the current template."""
        return self.template

    def _parse_template(self, template):
        """Parse the template string into a list of integers."""

        try:
            parts = template.split('-')
            if len(parts) != 4:
                raise ValueError("Template must have exactly 4 parts separated by dashes")
            return [int(part) for part in parts]
        except (ValueError, AttributeError):
            raise ValueError(f"Invalid template format: {template}")

    def validate(self, input_str, pos):
        """
        Validate the input string.
        Returns just the State:
        - QValidator.Invalid: Input is invalid and should be rejected
        - QValidator.Intermediate: Input is incomplete but could become valid
        - QValidator.Acceptable: Input is fully valid
        """
        # If no template is set, only allow intermediate state
        if not self.template_values:
            if not input_str:
                return QValidator.State.Intermediate
            return QValidator.State.Invalid

        if not input_str:
            return QValidator.State.Intermediate

        # Check for invalid characters (only digits and dashes allowed)
        if not re.match(r'^[0-9-]*$', input_str):
            return QValidator.State.Invalid

        # Split by dashes and analyze
        parts = input_str.split('-')

        # Check for too many parts (more than 4)
        if len(parts) > 4:
            return QValidator.State.Invalid

        # Check for consecutive dashes
        if '--' in input_str:
            return QValidator.State.Invalid

        # Don't allow starting with dash, but ending with dash is OK for intermediate input
        if input_str.startswith('-'):
            return QValidator.State.Invalid

        # Validate each part
        for i, part in enumerate(parts):
            if part == '':  # Empty part means we're in the middle of typing
                continue

            # Check if part is a valid integer
            try:
                value = int(part)
                # Check if value exceeds template limit
                if i < len(self.template_values) and value > self.template_values[i]:
                    return QValidator.State.Invalid
            except ValueError:
                return QValidator.State.Invalid

        # Check if we have exactly 4 complete parts
        if len(parts) == 4 and all(part.isdigit() for part in parts):
            # All parts are complete integers
            return QValidator.State.Acceptable
        elif len(parts) <= 4:
            # Incomplete but potentially valid
            return QValidator.State.Intermediate
        else:
            return QValidator.State.Invalid

    def fixup(self, input_str):
        """
        Optional: Attempt to fix the input string.
        This method can be used to automatically correct common mistakes.
        """
        # Remove any invalid characters
        fixed = re.sub(r'[^0-9-]', '', input_str)

        # Remove multiple consecutive dashes
        fixed = re.sub(r'-+', '-', fixed)

        # Remove leading/trailing dashes
        fixed = fixed.strip('-')

        return fixed