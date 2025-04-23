import pandas as pd


valid = pd.read_csv('methods/profitcenter.csv')['Profit Center'].to_list()

def validateProfitCenter(value):
    return int(float(value)) in valid