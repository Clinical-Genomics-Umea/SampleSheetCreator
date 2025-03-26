import logging

from modules.views.log.log_widget import LogWidget


class LogWidgetHandler(logging.Handler):
    """ Custom log handler to send warning messages to the status bar. """
    def __init__(self, log_widget: LogWidget):
        super().__init__()
        self.log_widget = log_widget
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        self.setFormatter(formatter)

    def emit(self, record):

        msg = self.format(record)
        self.log_widget.append_log(msg)