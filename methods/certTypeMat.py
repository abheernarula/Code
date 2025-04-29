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


def validateCertTypeMat(plant, value):
    if plant in gmp:
        return value == "S06"