import pandas as pd

vals = pd.read_csv('methods/mrpCOntroller.csv')

def validateMRPcontroller(plant, value):
    valid = vals[vals['Plant']==plant]['MRP Controller'].to_list()
    
    try:
        str(int(float(value)))
    except:
        return str(value).upper() in valid
    return str(int(float(value))).upper() in valid