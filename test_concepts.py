from pydantic import BaseModel, validator
import pandas as pd

# Define a Pydantic model for DataFrame validation
class DataFrameValidator(BaseModel):
    name: str
    age: int

    @validator('age')
    def age_must_be_positive(cls, value):
        if value < 0:
            raise ValueError("Age must be a positive integer")
        return value

    @validator('name')
    def name_must_not_contain_numbers(cls, value):
        if any(char.isdigit() for char in value):
            raise ValueError("Name must not contain numbers")
        return value

    @validator('name')
    def name_must_be_unique(cls, value, values):
        # Check if the name already exists in the DataFrame
        if 'df' in values and values['df'] is not None and values['df']['name'].duplicated().any():
            raise ValueError("Name must be unique")
        return value

# Sample data as a list of dictionaries
data = [{'name': 'Alice', 'age': 30},
        {'name': 'Bob', 'age': 25},
        {'name': 'Alice', 'age': 35},  # Duplicate name
        {'name': 'David', 'age': 40}]

# Create a Pandas DataFrame from the sample data
df = pd.DataFrame(data)

# Iterate over DataFrame rows and validate using Pydantic model
for idx, row in df.iterrows():
    try:
        DataFrameValidator(df=df, **row.to_dict())
        print(f"Row {idx} is valid")
    except ValueError as e:
        print(f"Row {idx} is invalid: {str(e)}")