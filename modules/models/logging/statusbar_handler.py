import logging


class StatusBarLogHandler(logging.Handler):
    """ Custom log handler to send warning messages to the status bar. """
    def __init__(self, status_bar):
        super().__init__()
        self.status_bar = status_bar
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        self.setFormatter(formatter)

    def emit(self, record):

        print(record)

        msg = self.format(record)
        level = record.levelname

        print(msg, level)
        self.status_bar.display_message(level, msg)

