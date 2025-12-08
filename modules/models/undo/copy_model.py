from PySide6.QtCore import QDataStream, QIODevice, QByteArray
from PySide6.QtGui import QStandardItemModel

def copy_model(model: QStandardItemModel) -> QStandardItemModel:
    buffer = QByteArray()
    stream = QDataStream(buffer, QIODevice.WriteOnly)
    stream << model  # serialize the entire model

    new_model = QStandardItemModel()
    stream = QDataStream(buffer)  # read mode
    stream >> new_model  # deserialize into new model

    return new_model