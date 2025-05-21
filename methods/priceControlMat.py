vals ={
    'ZSC1': ['V'],
    'ZRDM': ['V']
}

def validatePriceControlMat(value, matType):
    valid = vals[matType]
    return str(value).upper() in valid