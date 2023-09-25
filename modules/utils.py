from PySide6.QtGui import QPainter, QAction
from PySide6.QtWidgets import QPushButton, QGraphicsScene, QGraphicsView


def get_vertical_button_view(pushbutton: QPushButton) -> QPushButton:
    button.setFixedHeight(20)
    button.setFixedWidth(100)
    button.setContentsMargins(0, 0, 0, 0)
    button.setStyleSheet("QPushButton {border-width: 0px;}")
    button.setIcon(qta.icon('ph.rows-light'))

    button_size = button.size()
    print(button_size)

    scene = QGraphicsScene()
    proxy_widget = scene.addWidget()
    proxy_widget.setRotation(90)
    view = QGraphicsView(self.right_sidebar_widget)
    view.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
    view.setFrameStyle(QFrame.NoFrame)
    view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    view.setFixedHeight(button_size.width() + 2)
    view.setFixedWidth(button_size.height() + 2)
    view.setScene(scene)
    view.setContentsMargins(0, 0, 0, 0)



