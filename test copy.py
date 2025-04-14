from tqdm import tqdm
import pandas as pd
tqdm.pandas()
# def _add(num, *args):
#     return num*sum([i for i in args])


# print(_add(5,2,5,3))
def check(row,col):
    return row[col]>20

s = pd.DataFrame(pd.Series([20, 21, 12], index=['London', 'New York', 'Helsinki']))

s['>20'] = s.progress_apply(lambda row: check(row,'0'))
print(s)