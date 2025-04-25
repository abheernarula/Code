import pandas as pd

valid = pd.read_csv('methods/purchValueKeyMat.csv')['Purchasing value key'].to_list()

def validatePurchValMat(value):
    try:
        str(int(float(value)))
    except:
        return str(value).upper() in valid
    return str(int(float(value))).upper() in valid