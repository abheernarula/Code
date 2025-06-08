# valid = pd.read_csv('methods/purchValueKeyMat.csv')['Purchasing value key'].to_list()
vals = {
    'ZSC1': ["ZM00"],
    'ZSC2': ["ZM00"],
    'ZRDM': ["ZM00"],
    'ZVRP': ["ZM00"],
    'ZANI': ["ZM00"],
    'ZCAP': ["ZM00"],
    'ZSTR': ["ZM00"],
    'ERSA': ["ZM00"]
}

def validatePurchValMat(value, matType):
    valid = vals[matType]
    # try:
    #     str(int(float(value)))
    # except:
    return str(value).upper() in valid
    # return str(int(float(value))).upper() in valid