vals = {
    'ZSC1': ["0001", "1"],
    'ZSC2': ["0001", "1"],
    'ZRDM': ["0001", "1"],
    'ZVRP': ["0001", "1"],
    'ZANI': ["0001", "1"],
    'ZCAP': ["0001", "1"],
    'ZSTR': ["0001", "1"],
    'ERSA': ["0001", "1"],
    'ABF': ['0001', '1']
}


def validateLoadingGroup(value, matType):
    valid = vals[matType]
    try:
        str(int(float(value)))
    except:
        return str(value).upper() in valid
    return str(int(float(value))).upper() in valid 