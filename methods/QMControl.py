import pandas as pd

valid = ["0000","0","9000","Z9000","ZSY1"]
plantGMP = pd.read_csv('methods/PlantsGMP.csv')
plantGMP = plantGMP[plantGMP['GMP']=='X']['Plant'].to_list()

def validateQMControl(value, matType, plant, valid=valid):
    if matType == 'ZVRP':
        if plant in plantGMP:
            valid = ['9000']
        else:
            valid = ['0','0000']
        
    try:
        str(int(float(value)))
    except:
        return str(value).upper() in valid
    return str(int(float(value))).upper() in valid