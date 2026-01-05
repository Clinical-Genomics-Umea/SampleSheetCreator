import logging

import httpx
import pandas as pd
from PySide6.QtCore import QObject, QThreadPool, Signal
from natsort import natsorted

from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.workdata.igene_api_worker import IgeneApiWorker
# from modules.models.workdata.worksheets_models import WorkSheetsModel



class WorkDataManager(QObject):

    worksheet_data_ready = Signal(object)
    worksheets_failed = Signal(object)

    def __init__(self, configuration_manager: ConfigurationManager, logger: logging.Logger):
        super().__init__()

        self._logger = logger
        self._configuration_manager = configuration_manager

        self.pool = QThreadPool.globalInstance()

        self.output = []
        self.threads = []
        self.total_jobs = 0
        self.detail_completed = 0
        self.results = {}

    def get_data(self):
        key = self._configuration_manager.igene_key
        base_url = self._configuration_manager.igene_url

        headers = {"api-key": key}

        worksheet_ids = self.get_worksheet_ids(base_url, headers)

        print(worksheet_ids)

        worksheet_ids_sorted = natsorted(worksheet_ids, reverse=True)
        latest_10_worksheet_ids = worksheet_ids_sorted[0:10]
        self.submit_detail_jobs(latest_10_worksheet_ids, base_url, headers)

    @staticmethod
    def get_worksheet_ids(base_url, headers):

        url = base_url + "/worksheets/"

        with httpx.Client(timeout=10, headers=headers) as client:
            response = client.get(url, timeout=10)

        print(response)

        return response.json()

    def submit_detail_jobs(self, ws_ids, base_url, headers):
        self.total_jobs = len(ws_ids)
        self.detail_completed = 0
        self.results = {}

        for ws_id in ws_ids:
            url = base_url + "/worksheets/" + ws_id
            worker = IgeneApiWorker(url, headers)
            # Store the URL in the worker instance
            worker.url = url
            # Connect signals with proper URL binding
            worker.signals.finished.connect(self.on_detail_success)
            worker.signals.failed.connect(lambda error, url=url: self.on_detail_failure(url, error))
            self.pool.start(worker)

    def on_detail_success(self, url, result):
        self.results[url] = result
        self.check_detail_done()

    def on_detail_failure(self, url, error):
        self.results[url] = None
        self.check_detail_done()

    def check_detail_done(self):
        self.detail_completed += 1
        if self.detail_completed == self.total_jobs:
            worksheets_data = []
            for url, data in self.results.items():
                if data is not None:
                    print(f"{url} -> Received data")
                    # Data is already parsed JSON from the worker
                    if isinstance(data, list) and data:  # If it's a non-empty list
                        worksheets_data.append(pd.DataFrame(data))
                    elif isinstance(data, dict):  # If it's a single dictionary
                        worksheets_data.append(pd.DataFrame([data]))
            
            if worksheets_data:
                merged_worksheets_df = pd.concat(worksheets_data, ignore_index=True)
                self.worksheet_data_ready.emit(merged_worksheets_df)
            else:
                print("No valid worksheet data received")
                self.worksheets_failed.emit("No valid worksheet data received")

