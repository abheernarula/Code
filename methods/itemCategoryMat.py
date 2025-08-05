vals = {
    'ZSC1': ['NORM'],
    'ZSC2': ['NORM'],
    'ZRDM': ['NORM'],
    'ZVRP': ['VERP'],
    'ZANI': ['NORM'],
    'ZCAP': ['NORM'],
    'ZSTR': ['NORM'],
    'ERSA': ['NORM'],
    'ABF': ['NORM']
}

def validateItemCatMat(value, matType):
    valid = vals[matType]
    return str(value).upper() in valid