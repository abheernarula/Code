import pandas as pd

# valid = pd.read_csv('methods/mrpType.csv')['MRP Type'].to_list()
vals = {
    'ZSC1': ['ND'],
    'ZSC2': ['ND'],
    'ZRDM': ['ND'],
    'ZVRP': ['ND'],
    'ZANI': ['ND']
}

def validateMRP_type(value, matType):
    valid = vals[matType]
    return str(value).upper() in valid