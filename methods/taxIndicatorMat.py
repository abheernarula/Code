vals = {
    'ZSC1': ['0'],
    'ZSC2': ['0'],
    'ZRDM': ['0'],
    'ZVRP': ['0'],
    'ZANI': ['0'],
    'ZCAP': ['0'],
    'ZSTR': ['0'],
    'ERSA': ['0'],
    'ABF': ['0']
}

def validateTaxIndicatorMat(value, matType):
    valid = vals[matType]
    return str(int(float(value))) in valid