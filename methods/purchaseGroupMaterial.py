import pandas as pd

# valid = pd.read_csv('methods/purchasegroupMaterial.csv')['Purchasing Group'].to_list()
vals = {
    'ZSC1': [501, '501'],
    'ZRDM': [501, '501']
}

def validatePurchaseGroupMaterial(value, matType):
    valid = vals[matType]
    try:
        str(int(float(value)))
    except:
        return str(value).upper() in valid
    return str(int(float(value))).upper() in valid 