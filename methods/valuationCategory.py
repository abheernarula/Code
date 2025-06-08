vals = {
    'ZSC1': ['X'],
    'ZSC2': ['X'],
    'ZRDM': ['BCHRX'],
    'ZVRP': ['BCHRX'],
    'ZANI': ['X'],
}

def validateValuationCat(value, matType):
    valid = vals[matType]
    return str(value).upper() in valid