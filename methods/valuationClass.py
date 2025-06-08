import pandas as pd

# valid = pd.read_csv('methods/valuationClass.csv')['Valuation Class'].to_list()
vals = {
    "ZSC1": [9040, '9040'],
    "ZSC2": [9040, '9040'],
    'ZRDM': [9000, '9000'],
    'ZVRP': [9010, '9010', '9011', 9011],
    'ZANI': ['ZANI'],
    'ZCAP': [9010, '9010'],
    'ZSTR': ['ZSTR'],
    "ERSA": [9030, '9030']
}

def validateValuationClass(value, matType):
    valid = vals[matType]
    try:
        str(int(float(value)))
    except:
        return str(value).upper() in valid
    return str(int(float(value))).upper() in valid 