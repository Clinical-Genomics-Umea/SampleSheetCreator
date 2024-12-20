import re

# Define the regex pattern

read_cycle_patterns = {
    "Read1Cycles": {
        "findall": r"(Y\d+|N\d+|U\d+|Y{r1})",
        "validate": r"^(Y\d+|N\d+|U\d+)*(Y{r1})(Y\d+|N\d+|U\d+)*$",
    },
    "Index1Cycles": {
        "findall": r"(I\d+|N\d+|U\d+|I{i1})",
        "validate": r"^(I\d+|N\d+|U\d+)*(I{i1})(I\d+|N\d+|U\d+)*$",
    },
    "Index2Cycles": {
        "findall": r"(I\d+|N\d+|U\d+|I{i2})",
        "validate": r"^(I\d+|N\d+|U\d+)*(I{i2})(I\d+|N\d+|U\d+)*$",
    },
    "Read2Cycles": {
        "findall": r"(Y\d+|N\d+|U\d+|Y{r2})",
        "validate": r"^(Y\d+|N\d+|U\d+)*(Y{r2})(Y\d+|N\d+|U\d+)*$",
    },
}

# read_cycle_patterns = {
#     "Read1Cycles": {
#         "findall": r"(Y\d+|N\d+|U\d+|Y{r})",
#         "validate": r"^(Y\d+|N\d+|U\d+)*(Y{r})(Y\d+|N\d+|U\d+)*$",
#     },
#     "Index1Cycles": {
#         "findall": r"(I\d+|N\d+|U\d+|I{i})",
#         "validate": r"^(I\d+|N\d+|U\d+)*(I{i})(I\d+|N\d+|U\d+)*$",
#     },
#     "Index2Cycles": {
#         "findall": r"(I\d+|N\d+|U\d+|I{i})",
#         "validate": r"^(I\d+|N\d+|U\d+)*(I{i})(I\d+|N\d+|U\d+)*$",
#     },
#     "Read2Cycles": {
#         "findall": r"(Y\d+|N\d+|U\d+|Y{r})",
#         "validate": r"^(Y\d+|N\d+|U\d+)*(Y{r})(Y\d+|N\d+|U\d+)*$",
#     },
# }

pattern = r"^(Y\d+|N\d+|U\d+)*(Y{r1})(Y\d+|N\d+|U\d+)*$"


# Example test cases
test_cases = [
    "N10Y7N123U456Y{r1}N2N3",
    "U789N321Y{r1}",
    "Y{r1}N555",
    "Y{r1}N2N3",
    "N1234Y{r1}U567",
    "N123N456Y{r1}U789",
    "Y{r1}",  # Valid with only one 'Y{r1}'
    "X123N456",  # Invalid (contains 'X')
    "123X456Y{r1}",  # Invalid (contains 'X')
]

# Testing the regular expression
for test in test_cases:
    if re.fullmatch(pattern, test):
        print(f"'{test}' is valid.")
    else:
        print(f"'{test}' is invalid.")
