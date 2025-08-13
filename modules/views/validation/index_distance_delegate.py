from PySide6.QtGui import QColor
from PySide6.QtWidgets import QStyledItemDelegate


class IndexDistanceColorDelegate(QStyledItemDelegate):

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)

        # Get the cell value and check if it's numeric
        try:
            value = int(index.data())
        except (TypeError, ValueError):
            value = None

        # Set background color based on the value
        if value is not None:
            # Calculate a continuous color scale from light-red through yellow to light-green
            # Values 0-5: Light red to yellow
            # Values 5-10: Yellow to light green
            # Values 10+: Light green to darker green
            
            if value <= 5:
                # Scale from light red (255, 200, 200) to yellow (255, 255, 200)
                intensity = value / 5.0
                red = 255
                green = int(200 + (55 * intensity))  # 200-255
                blue = 200
            elif value <= 10:
                # Scale from yellow (255, 255, 200) to light green (200, 255, 200)
                intensity = (value - 5) / 5.0
                red = int(255 - (55 * intensity))  # 255-200
                green = 255
                blue = 200
            else:
                # Scale from light green (200, 255, 200) to darker green (150, 220, 150)
                # Cap value at 15 for color scaling
                capped_value = min(value, 15)
                intensity = (capped_value - 10) / 5.0
                red = int(200 - (50 * intensity))  # 200-150
                green = int(255 - (35 * intensity))  # 255-220
                blue = int(200 - (50 * intensity))  # 200-150
                
            # Ensure text is readable by making a lighter version of the color if needed
            color = QColor(red, green, blue)

            option.backgroundBrush = color
