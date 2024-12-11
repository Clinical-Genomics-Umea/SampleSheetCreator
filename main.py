import sys

import pywinstyles
import qdarktheme
from PySide6.QtCore import QRect
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow

# !/usr/bin/env python3
# main.py

import sys
import os
import argparse
import logging
from pathlib import Path
from contextlib import contextmanager

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QIcon

from controllers.main_controller import MainController

# from .utils.logger import setup_logger
# from .config.settings import ApplicationSettings
from utils.exceptions import ApplicationError


class Application(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        # Set application metadata
        self.setApplicationName("SampleCheater")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("Region Västerbotten")
        self.setOrganizationDomain("regionvasterbotten.se")

        # Initialize logger
        # self.logger = setup_logger(__name__)

    # def setup_exception_handling(self):
    #     """Set up global exception handling"""
    #     sys.excepthook = self.handle_exception
    #
    # def handle_exception(self, exc_type, exc_value, exc_traceback):
    #     """Global exception handler"""
    #     if issubclass(exc_type, KeyboardInterrupt):
    #         # Handle Ctrl+C gracefully
    #         sys.__excepthook__(exc_type, exc_value, exc_traceback)
    #         return
    #
    #     self.logger.critical(
    #         "Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback)
    #     )
    #     # You could also show a dialog to the user here


@contextmanager
def application_context(argv):
    """Context manager for the Qt application"""
    app = Application(argv)
    try:
        yield app
    finally:
        app.quit()


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="MyQtApp - Description of your application"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--config", type=Path, help="Path to config file")
    return parser.parse_args()


def initialize_resources():
    # Set up application icon
    icon_path = ":/icons/app_icon.png"
    if QIcon.hasThemeIcon("app_icon"):
        app_icon = QIcon.fromTheme("app_icon")
    else:
        app_icon = QIcon(icon_path)
    QApplication.setWindowIcon(app_icon)


def setup_environment():
    """Set up the application environment"""
    # Set environment variables if needed
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    # You might want to set other environment variables here
    # os.environ['QT_STYLE_OVERRIDE'] = 'fusion'


def main():
    """Application entry point"""
    # Parse command line arguments
    # args = parse_arguments()

    # Set up environment
    setup_environment()

    # Create and run application
    with application_context(sys.argv) as app:
        try:

            qdarktheme.setup_theme("dark")

            # Set up exception handling
            # app.setup_exception_handling()

            # Initialize resources
            # initialize_resources()

            # Load application settings
            # settings = ApplicationSettings()
            # if args.config:
            #     settings.load_from_file(args.config)
            #
            # # Set up logging level
            # if args.debug:
            #     logging.getLogger().setLevel(logging.DEBUG)

            # Create main controller
            controller = MainController()

            # Show the main window
            controller._main_window.show()

            # Optional: Set up auto-save timer
            # autosave_timer = QTimer()
            # autosave_timer.timeout.connect(controller.save_data)
            # autosave_timer.start(300000)  # Auto-save every 5 minutes

            # Start the event loop
            return app.exec()

        except ApplicationError as e:
            print(f"Application error: {e}")
            return 1
        #
        #
        # except ApplicationError as e:
        #     app.logger.error(f"Application error: {e}")
        #     return 1
        # except Exception as e:
        #     app.logger.critical(f"Unexpected error: {e}", exc_info=True)
        #     return 2


if __name__ == "__main__":
    sys.exit(main())


# def main():
#     app = QApplication(sys.argv)
#     # app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6'))
#     # app.setStyle('fusion')
#     qdarktheme.setup_theme("dark")
#     window = MainWindow()
#     pywinstyles.apply_style(window, "dark")
#     window.setGeometry(QRect(300, 300, 640, 480))  # arbitrary size/location
#     window.show()
#     sys.exit(app.exec())


if __name__ == "__main__":
    main()
