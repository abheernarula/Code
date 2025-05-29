import pandas as pd

valid = pd.read_csv('methods/profitcenter.csv')['Profit Center'].to_list()

def validateProfitCenter(value, matType):
    if matType == 'ZVRP':
        valid = [str(i) for i in valid if str(i).strip().startswith('5100')]
    return int(float(value)) in valid