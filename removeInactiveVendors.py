import argparse
from tqdm import tqdm
import pandas as pd
tqdm.pandas()


parser = argparse.ArgumentParser(
    description='Remove inactive vendors'
)

parser.add_argument('--lfm1', required=True, help='Path to csv file - lfm1')
parser.add_argument('--lfbk', required=True, help='Path to csv file - lfbk')
parser.add_argument('--lfa1', required=True, help='Path to csv file - lfa1')
parser.add_argument('--lfb1', required=True, help='Path to csv file - lfb1')
# parser.add_argument('--adr6', required=True, help='Path to csv file - adr6')

args = parser.parse_args()

lfa1 = pd.read_csv(args.lfa1)
lfb1 = pd.read_csv(args.lfb1)
lfm1 = pd.read_csv(args.lfm1)
lfbk = pd.read_csv(args.lfbk)
# adr6 = pd.read_csv(args.adr6)

def checkActive(table, row, *cols):
    res = False
    for col in cols:
        if pd.isnull(row[col]) or str(row[col]).strip() == '' or str(row[col]).lower() == 'nan':
            pass
        else:
            res = res or row[col] == 'X'
    return not res

def classifyInactiveCustomers(table, row, inactive: list):
    return row['Supplier'] in inactive

print("\n[CHECKING RECORDS]...")
lfm1['IsActive'] = lfm1.progress_apply(lambda row: checkActive(lfm1, row, 'Purch. block for purchasing organization', 'Delete flag for purchasing organization'), axis=1)
lfm1_inactive = lfm1[lfm1['IsActive']==False]
lfb1['IsActive'] = lfb1.progress_apply(lambda row: checkActive(lfb1, row, 'Posting block for company code', 'Deletion Flag for Company Code'), axis=1)
lfb1_inactive = lfb1[lfb1['IsActive']==False]

inactiveCustomers = lfm1_inactive['Supplier'].to_list()
inactiveCustomers.append(i for i in lfb1_inactive['Supplier'].to_list())
inactiveCustomers = list(set(inactiveCustomers))

print('\n[FILTERING ACTIVE RECORDS - LFA1]...')
lfa1['Inactive'] = lfa1.progress_apply(lambda row: classifyInactiveCustomers(lfa1, row, inactiveCustomers), axis=1)

print('\n[FILTERING ACTIVE RECORDS - LFBK]...')
lfbk['Inactive'] = lfbk.progress_apply(lambda row: classifyInactiveCustomers(lfbk, row, inactiveCustomers), axis=1)

print('\n[FILTERING ACTIVE RECORDS - LFB1]...')
lfb1['Inactive'] = lfb1.progress_apply(lambda row: classifyInactiveCustomers(lfb1, row, inactiveCustomers), axis=1)

print('\n[FILTERING ACTIVE RECORDS - LFM1]...')
lfm1['Inactive'] = lfm1.progress_apply(lambda row: classifyInactiveCustomers(lfm1, row, inactiveCustomers), axis=1)


# print(lfa1)
# print(lfb1)
# print(lfbk)
print('\n[SAVING RESULTS]...')
lfa1_active = lfa1[lfa1['Inactive']==False]
lfbk_active = lfbk[lfbk['Inactive']==False]
lfb1_active = lfb1[lfb1['Inactive']==False]
lfm1_active = lfm1[lfm1['Inactive']==False]

lfa1_active.to_excel('lfa1_active.xlsx')
lfb1_active.to_excel('lfb1_active.xlsx')
lfbk_active.to_excel('lfbk_active.xlsx')
lfm1_active.to_excel('lfm1_active.xlsx')

print('\n[DONE]')
# print(lfm1)
# lfm1_active.to_excel('lfm1_active.xlsx')