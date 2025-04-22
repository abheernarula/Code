import pandas as pd

valid_values = pd.read_csv('methods/materialType.csv')['Material Type'].to_list()

def validateMaterialType(value):
    return str(value).upper() in valid_values