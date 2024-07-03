import pandas as pd
import re

# Ordinary string with placeholder
test_str = "testing {test} bla bla bla"

# Variables to be used in the formatted string
context = {'test': 'example'}

# Convert to formatted string
formatted_str = test_str.format(**context)

print(formatted_str)  # Output: testing example bla bla bla
