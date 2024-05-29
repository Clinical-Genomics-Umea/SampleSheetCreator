import pandas as pd
import re

# Create a sample DataFrame with three columns
data = {
    'ID': [1, 2, 3, 4],
    'Name': ['Alice', 'Bob', 'Charlie', 'David'],
    'Lane': ['1,2,    3', '4 5  6', '7|8| 9', '10 ']
}
df = pd.DataFrame(data)

print("Original DataFrame:")
print(df)

# Function to split by non-integer characters
def split_lanes(lane):
    return re.split(r'\D+', lane.strip())

# Apply the split function and then explode the resulting lists into separate rows
df['Lane'] = df['Lane'].apply(split_lanes)
df = df.explode('Lane')

# Convert the "Lane" column to integers
df['Lane'] = df['Lane'].astype(int)

print("\nDataFrame after splitting and exploding 'Lane' column:")
print(df)
