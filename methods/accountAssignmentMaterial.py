import pandas as pd

# valid = pd.read_csv('methods/accountAssignmentMaterial.csv')['Item category group'].to_list()
vals = {
    'ZSC1': ['NORM'],
    'ZSC2': ['NORM'],
    'ZRDM': ['NORM'],
    'ZVRP': ['NORM'],
    'ZANI': ['NORM'],
    'ZCAP': ['NORM'],
    'ZSTR': ['NORM'],
    'ERSA': ['NORM']
}

def validateAccountAssignment(value, matType):
    valid = vals[matType]
    try:
        str(int(float(value)))
    except:
        return str(value).upper() in valid
    return str(int(float(value))).upper() in valid