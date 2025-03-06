import logging


class StatusBarLogHandler(logging.Handler):
    """ Custom log handler to send warning messages to the status bar. """
    def __init__(self, status_bar):
        super().__init__()
        self.status_bar = status_bar
        self.status_bar.setStyleSheet(f"color: red;")

        self.setLevel(logging.INFO)  # Only log warnings and above
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        self.setFormatter(formatter)

    def emit(self, record):
        # Only show warnings and above
        msg = self.format(record)

        if "WARNING" in msg:
            self.status_bar.showMessage(msg, 7000)