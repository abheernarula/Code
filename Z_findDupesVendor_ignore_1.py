import pandas as pd
from rapidfuzz import fuzz

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

merged = lfa1.merge(lfbk, on='Supplier', how='left')
df = merged.merge(lfm1, on='Supplier', how='left')

# Define column names
gst = 'Tax Number 3'
# pan = 'Tax Number 1'
bankAcc = 'Bank Account'
abac = 'ABAC Status'
msme = 'MSME Number'
address = 'Address'
accGroup = 'Account Group'

df = df[['Supplier', gst, bankAcc, abac, msme, address, accGroup]]

# 1. Define which columns are mandatory for each account group and whether matching is 'exact' or 'fuzzy'
account_group_config = {
    "Z001": {gst: "exact", bankAcc: "exact", abac: "exact", address: "fuzzy", msme:"exact"},
    "Z002": {bankAcc: "exact", abac: "exact", address: "fuzzy"},
    "Z014": {gst: "exact", bankAcc: "exact", abac: "exact", msme: "exact"},
    "Z019": {address: "fuzzy"},
    "Z016": {bankAcc: "exact", address: "fuzzy"}
}

def matches_criteria(val1, val2, match_type, fuzzy_threshold=80):
    """
    - 'exact' => must be identical strings
    - 'fuzzy' => fuzzy ratio >= fuzzy_threshold
    """
    if match_type == "exact":
        return str(val1).strip().lower() == str(val2).strip().lower()
    elif match_type == "fuzzy":
        # Compute fuzzy ratio (0-100); must be >= threshold
        return fuzz.ratio(str(val1).strip().lower(), str(val2).strip().lower()) >= fuzzy_threshold
    return False

def find_duplicates_by_account_group(df, 
                                     account_group_col,
                                     config=account_group_config,
                                     fuzzy_threshold=80):
    """
    Identifies duplicates based on mandatory columns for each account group.
    Rows in the same account group are compared only by columns 
    marked as 'M' (exact or fuzzy) in the config.
    
    :param df: Input DataFrame
    :param account_group_col: Column name that holds the account group
    :param config: Dictionary mapping account groups to {column: match_type} 
    :param fuzzy_threshold: Fuzzy similarity threshold for 'fuzzy' matches
    :return: A copy of df with a new column 'dup_group' indicating duplicates
    """
    df_result = df.copy()
    df_result["dup_group"] = None
    group_id = 1

    grouped = df_result.groupby(account_group_col)

    for acc_group, group_df in grouped:
        # Check if we have a matching config for this account group
        if acc_group not in config:
            # If no config, skip or treat differently
            continue
        
        # Identify mandatory columns & match types for this account group
        mandatory_cols = config[acc_group]

        # If only 1 row in this group, no duplicates possible
        if len(group_df) < 2:
            continue
        
        indices = group_df.index.tolist()
        visited = set()
        
        for i in indices:
            if i in visited:
                continue
            current_group = [i]
            visited.add(i)

            for j in indices:
                if j in visited or i == j:
                    continue

                # Check all mandatory columns
                all_match = True
                for col, match_type in mandatory_cols.items():
                    val1 = df_result.at[i, col]
                    val2 = df_result.at[j, col]
                    if not matches_criteria(val1, val2, match_type, fuzzy_threshold):
                        all_match = False
                        break

                if all_match:
                    current_group.append(j)
                    visited.add(j)
            
            # If we found more than one row that matched i, assign group_id
            if len(current_group) > 1:
                for idx in current_group:
                    df_result.at[idx, "dup_group"] = group_id
                group_id += 1

    return df_result

# ----------------------------------------------------------------------
# USAGE EXAMPLE:
# 
# 1. Read data from CSV/Excel
# df = pd.read_csv("your_data.csv")
#
# 2. Run the duplicate-finding function
# df_with_dups = find_duplicates_by_account_group(df)
#
# 3. Filter out rows that have a non-null 'dup_group'
# duplicates = df_with_dups[df_with_dups["dup_group"].notnull()]
# duplicates.to_csv("duplicates_found.csv", index=False)
# ----------------------------------------------------------------------

# print(account_group_config['Z001'])

dupes = find_duplicates_by_account_group(df, accGroup, account_group_config, 100)
dupes = dupes[dupes['dup_group'].notnull()]
dupes.to_csv('../Outputs/Duplicates/Vendor.csv')