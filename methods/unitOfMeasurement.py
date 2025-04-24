import pandas as pd

valid = pd.read_csv('methods/unitOfMeasurement.csv', engine='python')['UOM'].to_list()
additional = [
    '"',
    '"2',
    '"3'
]

def validateUOM(value):
    try:
        str(int(float(value)))
    except:
        return str(value).upper() in valid or str(value).upper() in additional
    return str(int(float(value))).upper() in valid or str(int(float(value))).upper() in additional