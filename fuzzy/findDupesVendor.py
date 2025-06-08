import pandas as pd

def check_duplicates_vendor(df: pd.DataFrame, accGroupCol, accGroupConfig, output_path="duplicates_vendor.xlsx"):
    
    grouped = df.groupby(accGroupCol)
    
    result = pd.DataFrame()
    
    for group, chunk in grouped:
        subset_columns = accGroupConfig[group]
        duplicate_mask = chunk.duplicated(subset=subset_columns, keep=False)
        duplicates = chunk[duplicate_mask]
        result = pd.concat([result, duplicates], ignore_index=True)
    
    result.to_excel(output_path, index=False)
    print(f"Duplicate records saved to: {output_path}")
    
    # return result


# Load data
lfa1 = pd.read_csv('../Vendor/LFA1.csv')
lfbk = pd.read_csv('../Vendor/LFBK.csv')
lfm1 = pd.read_csv('../Vendor/LFM1.csv')

lfa1 = lfa1[['Supplier', 'Name 1', 'Name 2', 'Name 3', 'Name 4', 'Street', 'City', 'Country', 'PO Box', 
             'P.O. Box Postal Code', 'Postal Code', 'Telephone 1', 'Telephone 2', 'Language Key', 'Address', 
             'Plant', 'Tax Jurisdiction', 'Account Group', 'Tax Number 3', 'Created on', 'Created by']]

lfbk = lfbk[['Supplier', 'Account holder', 'Bank Country', 'Bank Key', 'Bank Account']]

lfm1 = lfm1[['Supplier', 'Purch. block for purchasing organization', 'Purch. Organization', 'Purchasing Group', 
             'Order currency', 'Confirmation Control', 'Incoterms', 'Incoterms (Part 2)', 'MSME Status', 
             'MSME Number', 'MSME Issue Date', 'ABAC Status', 'ABAC Reason', 'GR-Based Inv. Verif.', 
             'Service-Based Invoice Verification', 'Delete flag for purchasing organization']]

# Define column names
gst = 'Tax Number 3'
bankKey = 'Bank Key'
bankAcc = 'Bank Account'
abac = 'ABAC Status'
msme = 'MSME Number'
# address = 'Address'
accGroup = 'Account Group'

account_group_config = {
    "Z001": [gst, bankAcc, abac, bankKey, msme],
    "Z002": [bankAcc, abac, bankKey],
    "Z014": [gst, bankAcc, abac, msme],
    "Z019": [bankKey],
    "Z016": [bankAcc, bankKey]
}

merged = pd.merge(lfa1, lfbk, on='Supplier', how='left')
df = pd.merge(merged, lfm1, on='Supplier', how='left')

df = df.drop_duplicates(subset=['Supplier'], keep='first')
# gst, pan, bank account, abac, msme, bankKey
# print(check_duplicates_vendor(columns))
# print(list(set(df[accGroup])))

# print(check_duplicates_vendor(df,accGroup,account_group_config))
df.to_excel('merged_vendor_master.xlsx', index=False)
check_duplicates_vendor(df,accGroup,account_group_config)