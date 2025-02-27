from pathlib import Path

import pandas as pd


def load_worksheet(file: Path):
    # TODO: read a worksheet file (csv) into a pandas dataframe and return
    df = pd.read_csv(file)
    return df


