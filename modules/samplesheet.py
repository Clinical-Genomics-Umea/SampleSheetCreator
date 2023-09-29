import pandas as pd
import re
from PySide6.QtGui import QStandardItemModel, QStandardItem
from modules.va


def qstandarditemmodel_to_dataframe(model):
    """
    Converts a QStandardItemModel to a Pandas DataFrame, keeping rows with alphanumeric values in at least one column.

    Args:
        model (QStandardItemModel): The QStandardItemModel to convert.

    Returns:
        pd.DataFrame: The Pandas DataFrame representation of the QStandardItemModel with rows containing alphanumeric values in at least one column.
    """
    if not isinstance(model, QStandardItemModel):
        raise ValueError("Input must be a QStandardItemModel")

    # Create an empty DataFrame with column names
    columns = [model.horizontalHeaderItem(col).text() for col in range(model.columnCount())]
    df = pd.DataFrame(columns=columns)

    # Iterate through the rows of the model and populate the DataFrame
    for row in range(model.rowCount()):
        row_data = []
        has_alphanumeric = False  # Flag to track if the row contains alphanumeric values
        for col in range(model.columnCount()):
            item = model.item(row, col)
            if item is not None:
                text = item.text()
                # Check if the text contains alphanumeric characters
                if re.search(r'\w', text):
                    row_data.append(text)
                    has_alphanumeric = True
                else:
                    row_data.append(None)
            else:
                row_data.append(None)
        # Only add rows with at least one alphanumeric value
        if has_alphanumeric:
            df.loc[row] = row_data

    return df


def validate_data(model):
    df = qstandarditemmodel_to_dataframe(model)


