import pandas as pd

valid_values = pd.read_csv('methods/materialGroup.csv')['Material Group'].to_list()

def validateMaterialGroup(value):
    return str(value).upper() in valid_values