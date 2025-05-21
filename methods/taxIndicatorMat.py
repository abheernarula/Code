vals = {
    'ZSC1': ['0'],
    'ZRDM': ['0']
}

def validateTaxIndicatorMat(value, matType):
    valid = vals[matType]
    return str(int(float(value))) in valid