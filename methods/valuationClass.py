import pandas as pd

# valid = pd.read_csv('methods/valuationClass.csv')['Valuation Class'].to_list()
valid = [
    9040, '9040'
]

def validateValuationClass(value):
    try:
        str(int(float(value)))
    except:
        return str(value).upper() in valid
    return str(int(float(value))).upper() in valid 