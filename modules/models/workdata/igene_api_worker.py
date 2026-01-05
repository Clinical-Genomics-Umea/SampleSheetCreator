from PySide6.QtCore import QObject, Signal, Slot, QRunnable
import httpx
import json

class IgeneApiWorker(QRunnable):
    def __init__(self, url, headers):
        super().__init__()
        self.url = url
        self.headers = headers
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            with httpx.Client(timeout=10, headers=self.headers) as client:
                response = client.get(self.url)
                # Parse JSON response before emitting
                data = response.json() if response.content else None
                self.signals.finished.emit(self.url, data)

        except Exception as e:
            self.signals.failed.emit(self.url, str(e))

class WorkerSignals(QObject):
    # Changed second argument to object to handle both dict and list types
    finished = Signal(str, object)   # url, result (parsed JSON)
    failed = Signal(str, str)        # url, error