valid_values = [
    "0001",
    "0003",
    "0005",
    "1000",
    "1001",
    "1002",
    "INST",
    "YB30"
]


def validate_dunning(value):
    return str(value) in valid_values