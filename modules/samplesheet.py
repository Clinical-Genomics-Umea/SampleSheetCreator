import numpy as np


def compare_rows(row1: np.array, row2: np.array):
    return np.sum(row1 != row2)


