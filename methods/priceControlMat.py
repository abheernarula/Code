vals ={
    'ZSC1': ['V'],
    'ZSC2': ['V'],
    'ZRDM': ['V'],
    'ZVRP': ['V'],
    'ZANI': ['V'],
    'ZCAP': ['V'],
    'ZSTR': ['V'],
    'ERSA': ['V']
}

def validatePriceControlMat(value, matType):
    valid = vals[matType]
    return str(value).upper() in valid