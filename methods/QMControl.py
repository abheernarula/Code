valid = [
    "0000",
    "0",
    "9000",
    "Z9000",
    "ZSY1"
]

def validateQMControl(value):
    try:
        str(int(float(value)))
    except:
        return str(value).upper() in valid
    return str(int(float(value))).upper() in valid 