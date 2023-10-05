import sys
import time
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QProgressBar
from PySide6.QtCore import QThread, Signal

class WorkerThread(QThread):
    finished = Signal()

    def run(self):
        # Perform the long-running calculation here
        time.sleep(5)

        # Emit the finished signal
        self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Spinner Example")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.start_button = QPushButton("Start Calculation")
        self.start_button.clicked.connect(self.start_calculation)
        self.layout.addWidget(self.start_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Set the range to 0 to display an indeterminate progress bar
        self.layout.addWidget(self.progress_bar)

        self.worker_thread = WorkerThread()
        self.worker_thread.finished.connect(self.calculation_finished)

    def start_calculation(self):
        self.start_button.setEnabled(False)
        self.progress_bar.setRange(0, 0)  # Set the range to 0 to display an indeterminate progress bar

        # Start the worker thread
        self.worker_thread.start()

    def calculation_finished(self):
        self.start_button.setEnabled(True)
        self.progress_bar.setRange(0, 1)  # Reset the range to display a regular progress bar

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())