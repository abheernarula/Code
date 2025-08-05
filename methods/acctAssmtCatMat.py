vals = {
    'ZSC1': ['Q'],
    'ZSC2': ['Q'],
    'ZRDM': ['Q'],
    'ZVRP': ['P'],
    'ZANI': ['P'],
    'ZCAP': ['P'],
    'ZSTR': ['P'],
    'ERSA': ['P'],
    'ABF': ['P']
}

def validateAcctAssmtCat(value, matType):
    valid = vals[matType]
    return str(value).upper() in valid