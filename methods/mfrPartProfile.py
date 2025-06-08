vals = {
    'ZSC1': ['Z001'],
    'ZSC2': ['Z001'],
    'ZRDM': ['Z001'],
    'ZVRP': ['Z001'],
    'ERSA': ['Z001']
}

def validateMfrPartProfile(value, matType):
    valid = vals[matType]
    return str(value).upper() in valid