vals = {
    'ZSC1': ['90'],
    'ZSC2': ['90'],
    'ZRDM': ['90'],
    'ZVRP': ['90']
}

def validateAcctAssmtGrpMat(value, matType):
    valid = vals[matType]
    try:
        str(int(float(value)))
    except:
        return str(value).upper() in valid
    return str(int(float(value))).upper() in valid