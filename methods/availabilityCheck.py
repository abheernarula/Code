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

vals = {
    'ZSC1' : ['KP'],
    'ZSC2' : ['KP'],
    'ZRDM' : ['01','1'],
    'ZVRP' : ['KP']
}

def validateAvailCheck(value, matType):
    valid = vals[matType]
    try:
        str(int(float(value)))
    except:
        return str(value).upper() in valid
    return str(int(float(value))).upper() in valid