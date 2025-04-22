import pandas as pd


valid = pd.read_csv('methods/profitcenter.csv')['Profit Center'].to_list()

def validateProfitCenter(value):
    return str(int(float(value))) in valid