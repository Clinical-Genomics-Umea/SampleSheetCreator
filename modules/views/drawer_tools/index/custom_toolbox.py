from PySide6.QtWidgets import QToolBox, QWidget, QVBoxLayout, QLabel


class IndexToolBox(QToolBox):
    def __init__(self):
        super().__init__()
        self.widget_visibility = {}  # Track visibility of each widget
        self.currentChanged.connect(self._toggle_section)

    def add_section(self, title, content):
        """
        Add a section with the given title and content to the toolbox.
        """
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(content))
        widget.setLayout(layout)
        self.addItem(widget, title)
        self.widget_visibility[widget] = True  # Default visibility is True

    def set_disabled(self, index, status):
        if status:
            self.setItemEnabled(index, status)
            widget = self.widget(index)
            widget.setHidden(False)
        else:
            self.setItemEnabled(index, status)
            widget = self.widget(index)
            widget.setHidden(True)

    def _toggle_section(self, index):
        """
        Toggle the visibility of the widget for the selected section.
        """
        if index == -1:  # No section is selected
            return

        widget = self.widget(index)
        is_visible = self.widget_visibility.get(widget, True)

        # Toggle visibility
        if is_visible:
            widget.hide()
        else:
            widget.show()

        # Update visibility tracking
        self.widget_visibility[widget] = not is_visible

        # Prevent collapsing if the widget is hidden (reset selection)
        if not is_visible:
            self.setCurrentIndex(index)
