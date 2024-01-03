import pandas as pd
import numpy as np

# Create a Pandas DataFrame with two columns containing NumPy arrays
df = pd.DataFrame({'column1': [np.array([1, 2]), np.array([3, 4]), np.array([5, 6])],
                   'column2': [np.array([7, 8]), np.array([9, 10]), np.array([11, 12])]})

# Function to append arrays from column1 to column2


def append_arrays(arr1, arr2):
    return np.append(arr1, arr2)


# Apply the function to create the new column
df['appended_column'] = df.apply(lambda row: append_arrays(row['column1'], row['column2']), axis=1)

# Print the modified DataFrame
print(df)


