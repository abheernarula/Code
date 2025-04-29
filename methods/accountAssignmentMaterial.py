import pandas as pd

# valid = pd.read_csv('methods/accountAssignmentMaterial.csv')['Item category group'].to_list()
valid = ['NORM']

def validateAccountAssignment(value):
    try:
        str(int(float(value)))
    except:
        return str(value).upper() in valid
    return str(int(float(value))).upper() in valid