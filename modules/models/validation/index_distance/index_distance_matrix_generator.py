from logging import Logger

from PySide6.QtCore import QObject, QThread, Slot

from modules.models.dataset.dataset_manager import DataSetManager
from modules.models.sample.sample_model import SampleModel
from modules.models.validation.index_distance.index_distance_matrices_worker import IndexDistanceMatricesWorker
from modules.views.validation.index_distance_validation_widget import IndexDistanceValidationWidget


class IndexDistanceValidator(QObject):

    def __init__(
        self,
        sample_model: SampleModel,
        dataset_manager: DataSetManager,
        index_distance_validation_widget: IndexDistanceValidationWidget,
        logger: Logger
    ):
        super().__init__()

        if sample_model is None:
            raise ValueError("model cannot be None")

        self._sample_model = sample_model
        self._dataset_manager = dataset_manager
        self._index_distance_validation_widget = index_distance_validation_widget
        self._logger = logger

        self.thread = None
        self.worker = None

    def generate(self):

        if self.thread is not None or self.worker is not None:
            return

        i5_seq_orientation = self._dataset_manager.i5_seq_orientation
        i5_seq_rc = i5_seq_orientation == "rc"

        self.thread = QThread()
        self.worker = IndexDistanceMatricesWorker(self._dataset_manager, i5_seq_rc)

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.results_ready.connect(self._receiver)
        self.worker.error.connect(self._receiver)

        self.thread.start()

    @Slot(object)
    def _receiver(self, results):

        self.thread.quit()
        self.worker.deleteLater()
        self.thread.deleteLater()
        self.thread = None
        self.worker = None

        self._index_distance_validation_widget.populate(results)