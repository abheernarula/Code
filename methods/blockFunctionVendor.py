valid_values = [
    "01", "1",
    "02", "2",
    "03", "3",
    "04", "4",
    "99",
    "S1",
    "S2",
    "S3",
    "S4",
    "S5",
    "S6",
    "S7",
    "S8",
    "S9",
    "SA",
    "W1",
    "W2",
    "Y0",
    "Y1",
    "Y2",
    "Y3",
    "Y4",
    "Y5",
    "Y6",
    "Y7",
    "Y8",
    "Y9",
    "Z1",
    "Z3",
    "Z4",
    "Z5"
]


def validateBlockFunction(value):
    try:
        str(int(float(value)))
    except:
        return str(value).upper() in valid_values
    return str(int(float(value))).upper() in valid_values