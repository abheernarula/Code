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
        return str(value) in valid or str(value)  in additional
    return str(int(float(value))) in valid or str(int(float(value))) in additional
