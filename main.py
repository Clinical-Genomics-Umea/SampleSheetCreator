import sys

import pywinstyles
import qdarktheme
from PySide6.QtCore import QRect
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6'))
    # app.setStyle('fusion')
    qdarktheme.setup_theme("dark")
    window = MainWindow()
    pywinstyles.apply_style(window, "dark")
    window.setGeometry(QRect(300, 300, 640, 480))  # arbitrary size/location
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
