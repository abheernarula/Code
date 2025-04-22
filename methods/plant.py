import pandas as pd

valid = pd.read_csv('methods/plant.csv')['Plant'].to_list()

def validatePlant(value):
    try:
        str(int(float(value)))
    except:
        return str(value).upper() in valid
    return str(int(float(value))).upper() in valid