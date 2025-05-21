vals = {
    'ZSC1': ['X'],
    'ZRDM': ['X']
}

def validateValuationCat(value, matType):
    valid = vals[matType]
    return str(value).upper() in valid