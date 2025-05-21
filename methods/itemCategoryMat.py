vals = {
    'ZSC1': ['NORM'],
    'ZRDM': ['NORM']
}

def validateItemCatMat(value, matType):
    valid = vals[matType]
    return str(value).upper() in valid