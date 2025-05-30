vals = {
    'ZSC1': ['Q'],
    'ZSC2': ['Q'],
    'ZRDM': ['Q'],
    'ZVRP': ['P'],
}

def validateAcctAssmtCat(value, matType):
    valid = vals[matType]
    return str(value).upper() in valid