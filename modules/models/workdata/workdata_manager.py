import logging
from typing import Dict

import httpx
import pandas as pd
from PySide6.QtCore import QThreadPool, Signal, QRunnable, QObject, Slot

from modules.models.configuration.configuration_manager import ConfigurationManager
from modules.models.workdata.worksheets_models import WorksheetSamplesModel, WorksheetIDModel


class WorkDataManager(QObject):
    worksheet_data_ready = Signal(object)
    worksheets_failed = Signal(object)
    loading_state_changed = Signal(bool)  # True when loading starts, False when done

    def __init__(self, configuration_manager: ConfigurationManager,
                 worksheet_samples_model: WorksheetSamplesModel,
                 worksheet_id_model: WorksheetIDModel,
                 logger: logging.Logger):
        super().__init__()

        self._logger = logger
        self._configuration_manager = configuration_manager

        self.pool = QThreadPool.globalInstance()

        self.worksheet_samples_model = worksheet_samples_model
        self.worksheet_id_model = worksheet_id_model

        self.current_workdata = pd.DataFrame()
        self.selected_worklist_id = None

    def fetch_data(self):
        key = self._configuration_manager.igene_key
        base_url = self._configuration_manager.igene_url
        headers = {"api-key": key, "page": "1", "page_size": "20", "status": "A"}
        
        # Create and start the worker thread
        data_fetcher = DataFetcher(base_url, headers)
        
        # Connect signals
        data_fetcher.signals.result.connect(self._on_worksheet_data_received)
        data_fetcher.signals.error.connect(self._on_worksheet_error)
        data_fetcher.signals.finished.connect(self._on_finished)
        
        # Start loading
        self.loading_state_changed.emit(True)
        self.pool.start(data_fetcher)

    def _on_finished(self):
        self.loading_state_changed.emit(False)

    def _on_worksheet_data_received(self, df):
        try:
            self.current_workdata = df
            self.set_worksheet_samples_data(df)
            self.set_worksheet_id_model(df)
        except Exception as e:
            self._logger.error(f"Error processing worksheet data: {e}")

    def set_current_worklist_id(self, worklist_id):
        self.selected_worklist_id = worklist_id

    def _on_worksheet_error(self, error_msg):
        self._logger.error(f"Error fetching worksheet data: {error_msg}")

    def set_worksheet_samples_data(self, df):
        self.worksheet_samples_model.set_dataframe(df)

    def set_worksheet_id_model(self, df):
        unique_id_df = df[['AL', 'Investigator', 'updatedAt']].drop_duplicates()
        self.worksheet_id_model.set_dataframe(unique_id_df)


class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread."""
    result = Signal(object)  # Send the result of the processing
    error = Signal(str)      # Send error message if one occurs
    finished = Signal()      # Signal that the work is done


class DataFetcher(QRunnable):
    def __init__(self, base_url: str, headers: Dict[str, str]):
        super().__init__()
        self.base_url = base_url
        self.headers = headers
        self.signals = WorkerSignals()  # Create signals instance
        self.setAutoDelete(True)  # Auto-delete when done

    @Slot()
    def run(self) -> None:
        try:
            url = f"{self.base_url}/samplesheet_creator"

            response = httpx.get(url, headers=self.headers, timeout=10, verify=False)
            response.raise_for_status()
            data = response.json()[0]
            rows = []

            for entry in data:
                for sample_id, assay in entry["samples"].items():
                    rows.append({
                        "AL": entry["AL"],
                        "Investigator": entry["Investigator"],
                        "updatedAt": entry["updatedAt"],
                        "sample_id": sample_id,
                        "assay": assay
                    })

            # Create DataFrame and emit result
            df = pd.DataFrame(rows)
            self.signals.result.emit(df)
            
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()
