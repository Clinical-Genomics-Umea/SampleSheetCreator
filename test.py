import re
import pandas as pd

def generate_lanes_dataframe():
    """
    Generates a pandas DataFrame with the column 'Lanes' containing strings of digits from 1 to 8.

    Returns:
        pandas.DataFrame: DataFrame with the 'Lanes' column.
    """
    data = {'Lane': [','.join(str(i) for i in range(0, 9)),
                      ' '.join(str(i) for i in range(1, 9)),
                      '-'.join(str(i) for i in range(1, 12))]}

    df = pd.DataFrame(data)
    return df


def extract_numbers_from_string(input_string):
    """
    Extracts all numbers in a string that are one digit or longer.

    Parameters:
        input_string (str): The input string to extract numbers from.

    Returns:
        list: A list of all numbers found in the input string.
    """
    return re.findall(r'\d+', input_string)


def lane_validation(df):
    allowed_lanes = {'1', '2', '3', '4', '5', '6', '7', '8'}
    lane_strs = set(df['Lane'])

    used_lanes = set()
    for lane_str in lane_strs:
        lanes_list = extract_numbers_from_string(lane_str)
        used_lanes.update(lanes_list)

    print(used_lanes.difference(allowed_lanes))


df = generate_lanes_dataframe()
lane_validation(df)

