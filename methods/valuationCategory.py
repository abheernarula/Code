vals = {
    'ZSC1': ['X'],
    'ZSC2': ['X'],
    'ZRDM': ['BCHRX'],
    'ZVRP': ['BCHRX'],
    'ZANI': ['X'],
    'ZCAP': ['X'],
    'ZSTR': ['X'],
    'ERSA': ['X']
}

def validateValuationCat(value, matType):
    valid = vals[matType]
    return str(value).upper() in valid