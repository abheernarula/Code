valid = [
    "B00",
    "B01",
    "B03",
    "B04",
    "S00",
    "S01",
    "S02",
    "S03",
    "S04",
    "S05",
    "S06"
]

def validateCertTypeMat(value):
    return str(value).upper() in valid