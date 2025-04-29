# valid = [
#     "01", "1",
#     "02", "2",
#     "CH",
#     "DR",
#     "KP",
#     "R2",
#     "S2",
#     "Y2"
# ]

valid = [
    'KP'
]

def validateAvailCheck(value):
    try:
        str(int(float(value)))
    except:
        return str(value).upper() in valid
    return str(int(float(value))).upper() in valid