vals = {
    'ZSC1': ['Q'],
    'ZRDM': ['Q']
}

def validateAcctAssmtCat(value, matType):
    valid = vals[matType]
    return str(value).upper() in valid