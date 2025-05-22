import pandas as pd

# valid = [
#     "B00",
#     "B01",
#     "B03",
#     "B04",
#     "S00",
#     "S01",
#     "S02",
#     "S03",
#     "S04",
#     "S05",
#     "S06"
# ]
plants = pd.read_csv('methods/PlantsGMP.csv')
gmp = plants[plants['GMP']=='X']['Plant'].to_list()

vals = {
    'ZSC1': ['S06'],
    'ZRDM': ['S06']
}

def validateCertTypeMat(value, plant, matType):
    valid = vals[matType]
    if plant in gmp:
        return str(value).upper() in valid