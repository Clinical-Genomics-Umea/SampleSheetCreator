from PySide6.QtCore import QSize, QRect, QPoint
from PySide6.QtGui import (
    Qt,
)
from PySide6.QtWidgets import (
    QWidget,
    QSpacerItem,
    QSizePolicy,
    QLayout,
)
from utils.utils import int_list_to_int_str
from views.run.run_view_section import RunViewSection


class RunView(QWidget):
    def __init__(self, cfg_mgr):
        super().__init__()
        self._defaults = cfg_mgr.run_view_widgets_config

        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self._layout = FlowLayout()
        # self._layout = QHBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)
        self._view_widgets = {}

        # sections, defaults a

        self._setup()

    def _setup(self):
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.sections = {}

        for section_name, data in self._defaults.items():

            section = RunViewSection(self._view_widgets, section_name, data)
            self.sections[section_name] = section
            self._layout.addWidget(section)

        self._layout.addSpacerItem(spacer)

    def set_data(self, data):
        for key, value in data.items():
            if key in self._view_widgets:

                if isinstance(value, list):
                    value = int_list_to_int_str(value)

                if isinstance(value, int):
                    value = str(value)

                self._view_widgets[key].setText(value)


class FlowLayout(QLayout):
    def __init__(self, parent=None, spacing=10):
        super().__init__(parent)
        self.setSpacing(spacing)
        self.itemList = []

    def addItem(self, item):
        self.itemList.append(item)

    def addSpacerItem(self, spacerItem):
        # Simply append spacer item to the item list; it won't affect layout behavior
        self.itemList.append(spacerItem)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index < 0 or index >= len(self.itemList):
            return None
        return self.itemList[index]

    def takeAt(self, index):
        if index < 0 or index >= len(self.itemList):
            return None
        return self.itemList.pop(index)

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.spacing(), 2 * self.spacing())
        return size

    def doLayout(self, rect, testOnly):
        x, y, lineHeight = rect.x(), rect.y(), 0
        for item in self.itemList:
            if isinstance(item, QSpacerItem):
                # Skip spacer items in the layout process
                continue

            widget = item.widget()
            spaceX = self.spacing()
            spaceY = self.spacing()
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y += lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()
