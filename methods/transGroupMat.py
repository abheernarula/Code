vals = {
    'ZSC1': ["0001","1"],
    'ZRDM': ["0001","1"],
    'ZVRP': ["0001","1"]
}

def validateTransGroupMat(value, matType):
    valid = vals[matType]
    try:
        str(int(float(value)))
    except:
        return str(value) in valid
    return str(int(float(value))) in valid