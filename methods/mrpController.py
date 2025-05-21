import pandas as pd

# vals = pd.read_csv('methods/mrpController.csv')
vals = {
    'ZSC1': ['S00'],
    'ZRDM': ['S00']
}

def validateMRPcontroller(value, matType, plant:int=0):
    # valid = vals[vals['Plant']==plant]['MRP Controller'].to_list()
    valid = vals[matType]
    if matType=='ZRDM':
        if plant == 5183 or plant == 5193:
            valid = ['N10']
    try:
        str(int(float(value)))
    except:
        return str(value).upper() in valid
    return str(int(float(value))).upper() in valid