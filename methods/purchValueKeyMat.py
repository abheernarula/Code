# valid = pd.read_csv('methods/purchValueKeyMat.csv')['Purchasing value key'].to_list()
valid = [
    "ZM00"
]

def validatePurchValMat(value):
    # try:
    #     str(int(float(value)))
    # except:
        return str(value).upper() in valid
    # return str(int(float(value))).upper() in valid