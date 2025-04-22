import pandas as pd

valid = pd.read_csv('methods/mrpType.csv')['MRP Type'].to_list()

def validateMRP_type(value):
    return str(value).upper() in valid