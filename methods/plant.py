import pandas as pd

valid = pd.read_csv('methods/plant.csv')['Plant'].to_list()

def validatePlant(value):
    return int(float(value)) in valid