from PySide6.QtCore import Qt, QTimer, QObject, Slot
from PySide6.QtGui import QPainter, QBrush, QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton


class Notify(QObject):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.error_widget = None  # Store a reference to prevent garbage collection

    @Slot(dict)
    def app_not_allowed(self, appobj):
        print("app_not_allowed, notify")

        appname = appobj.get("ApplicationName", "Unknown App")
        message = f"{appname} incompatible with already set apps."

        # Create and store a reference to the widget
        self.error_widget = FloatingErrorWidget(message)

        # Position in the upper right corner of the main window
        main_window_geo = self.main_window.geometry()

        # Calculate x position: right side of main window minus widget width
        x = (
            main_window_geo.right() - self.error_widget.width() - 10
        )  # 20px padding from right edge

        # Calculate y position: top of main window plus some padding
        y = main_window_geo.top() + 10  # 20px padding from top edge

        self.error_widget.move(x, y)
        self.error_widget.show()


class FloatingErrorWidget(QWidget):
    def __init__(self, message, parent=None):
        super().__init__(parent)

        # Ensure it appears above other windows
        self.setWindowFlags(
            Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        self.content_widget = QWidget(self)
        main_layout.addWidget(self.content_widget)

        content_layout = QVBoxLayout(self.content_widget)

        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.content_widget.setStyleSheet(
            """
                QWidget {
                    background-color: rgba(200, 60, 60);
                    border-radius: 2px;
                    padding: 0px;
                }
            """
        )

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.addStretch()
        close_btn = QPushButton("X")
        close_btn.setStyleSheet(
            "background-color: transparent; color: white; border: none;"
        )
        close_btn.clicked.connect(self.close)
        top_row.addWidget(close_btn)

        label = QLabel(message)
        label.setStyleSheet("background-color: transparent; color: white;")
        label.setWordWrap(True)

        content_layout.addLayout(top_row)
        content_layout.addWidget(label)

        content_layout.addLayout(top_row)
        content_layout.addWidget(label)

        self.auto_close_timer = QTimer(self)
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.timeout.connect(self.close)
        self.auto_close_timer.start(2000)  # 2 seconds

        # Adjust size after setting up layout
        self.adjustSize()

    def paintEvent(self, event):
        # Custom paint for the translucent parent widget
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(200, 60, 60, 230)))  # Black with 50% opacity
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)  # Rounded corners
