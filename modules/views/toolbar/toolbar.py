from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QAction, QActionGroup, Qt
from PySide6.QtWidgets import QToolBar, QWidget, QSizePolicy
import qtawesome as qta


class ToolBar(QToolBar):

    action_triggered = Signal(str, bool)

    def __init__(self):
        super().__init__()
        self.setMovable(False)
        self.setIconSize(QSize(40, 40))

        # left toolbar actions

        self.action_group = QActionGroup(self)

        self.file_action = QAction("File", self)
        self.run_action = QAction("Run", self)
        self.apps_action = QAction("Apps", self)
        self.indexes_action = QAction("Indexes", self)
        self.override_action = QAction("Override", self)
        self.lane_action = QAction("Lane", self)
        self.validate_action = QAction("Validate", self)
        self.export_action = QAction("Export", self)
        self.settings_action = QAction("Settings", self)

        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setFixedWidth(50)

        self._setup()


    def _setup(self):
        #    action_obj      icon_name     action_id    action_name
        actions = [
            (self.file_action, "msc.files", "file", "file"),
            (self.run_action, "msc.symbol-misc", "run", "run"),
            (self.indexes_action, "mdi6.barcode", "indexes", "index"),
            (self.apps_action, "msc.symbol-method", "apps", "apps"),
            (self.override_action, "msc.sync", "override", "o-ride "),
            (self.lane_action, "mdi6.road", "lane", "lane"),
            (self.validate_action, "msc.check-all", "validate", "valid"),
            (self.export_action, "msc.coffee", "export", "export"),
            (self.settings_action, "msc.settings-gear", "config", "config"),
        ]

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.action_group.setExclusionPolicy(QActionGroup.ExclusionPolicy.ExclusiveOptional)

        for action, action_icon, action_id, action_name in actions:
            action.setCheckable(True)
            action.setChecked(False)
            action.setText(action_name)
            action.setData(action_id)
            action.setIcon(qta.icon(action_icon, options=[{"draw": "image"}]))
            action.triggered.connect(self._action_triggered)
            self.action_group.addAction(action)

        self.addAction(self.file_action)
        self.addAction(self.run_action)
        self.addAction(self.indexes_action)
        self.addAction(self.apps_action)
        self.addAction(self.override_action)
        self.addAction(self.lane_action)
        self.addAction(self.validate_action)
        self.addAction(self.export_action)
        self.addWidget(spacer)
        self.addAction(self.settings_action)

    def _action_triggered(self):

        action = self.sender()
        action_id = action.data()
        is_checked = action.isChecked()

        self.action_triggered.emit(action_id, is_checked)
