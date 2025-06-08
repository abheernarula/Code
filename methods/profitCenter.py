import pandas as pd

def validateProfitCenter(value, matType):
    valid = pd.read_csv('methods/profitcenter.csv')['Profit Center'].to_list()
    if matType == 'ZVRP' or matType == 'ERSA':
        valid2 = [str(i) for i in valid if str(i).strip().startswith('5100')]
        valid = valid2
    return int(float(value)) in valid