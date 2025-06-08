vals = {
    'ZSC1': ['NORM'],
    'ZSC2': ['NORM'],
    'ZRDM': ['NORM'],
    'ZVRP': ['VERP'],
    'ZANI': ['NORM']
}

def validateItemCatMat(value, matType):
    valid = vals[matType]
    return str(value).upper() in valid