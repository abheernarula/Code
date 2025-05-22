import pandas as pd
import numpy as np
from rapidfuzz import fuzz

def find_duplicates(df,
                    name_col="Name",
                    # address_col="Address",
                    gst_col="GST number",
                    # vat_col="VAT number",
                    name_threshold=80,
                    address_threshold=80):
    """
    Identical clustering logic, but optimized:
      - Pulls needed columns into NumPy arrays once
      - Uses a NumPy array for dup_group assignments
      - Eliminates .loc/.at calls inside loops
      - Removes debug prints
    """
    df[name_col] = df[name_col].str.lower()
    # df[address_col] = df[address_col].str.lower()
    # 1. Prepare
    df_result = df.copy()
    
    n = len(df_result)
    dup_group = np.full(n, None, dtype=object)
    group_id = 1

    # 2. Extract columns into arrays for fast indexing
    names = df_result[name_col].fillna("").astype(str).to_numpy()
    # addresses = df_result[address_col].fillna("").astype(str).to_numpy()
    gst_vals = df_result[gst_col].to_numpy()
    # vat_vals = df_result[vat_col].to_numpy()

    # 3. Phase 1: exact GST+VAT grouping
    mask_non_null = pd.notna(gst_vals)
    # for group in df_result[mask_non_null]:
    mask = df_result[mask_non_null]
        # print(f'done - {group}')
        # print(type(group))
    indices = mask.index.tolist()
    if len(indices) < 2:
        pass
    visited = set()
    for i in indices:
        if i in visited:
            continue
        ni = names[i]
        cluster = [i]
        visited.add(i)
        for j in indices:
            print(f'done -> {i}, {j}')
            if j in visited:
                continue
            # fuzzy-match both name & address
            if (fuzz.ratio(ni, names[j]) >= name_threshold):
                    # and fuzz.ratio(ai, addresses[j]) >= address_threshold):
                cluster.append(j)
                visited.add(j)
        if len(cluster) > 1:
            dup_group[cluster] = group_id
            group_id += 1

    # 4. Phase 2: both GST & VAT null
    mask_null = pd.isna(gst_vals)
    # mask_null = pd.isna(name_col)
    indices = np.where(mask_null)[0].tolist()
    visited = set()
    for i in indices:
        if i in visited:
            continue
        # ni, ai = names[i], addresses[i]
        ni = names[i]
        cluster = [i]
        visited.add(i)
        for j in indices:
            if j in visited:
                continue
            if (fuzz.ratio(ni, names[j]) >= name_threshold):
                    # and fuzz.ratio(ai, addresses[j]) >= address_threshold):
                cluster.append(j)
                visited.add(j)
        if len(cluster) > 1:
            dup_group[cluster] = group_id
            group_id += 1

    # 5. Assign back and return
    df_result["dup_group"] = dup_group
    return df_result

df = pd.read_excel('../Material/zrdmDupTest.xlsx')

print('Start')

dupes = find_duplicates(df,'Purchase Order Text', 'CAS number (pharm.)', 90, 90)
dup_df = dupes[dupes["dup_group"].notnull()]
dup_df.to_csv("zrdmDupFuzzy100.csv", index=False)


# Example usage:
# df = pd.read_excel('../Customer/CustomerMaster.xlsx', sheet_name='ACCOUNT')
# dupes = find_duplicates(df,
#                         name_col='Name',
#                         address_col='add_dupe',
#                         gst_col='GST_Number__c',
#                         vat_col='PAN_Number__c',
#                         name_threshold=70,
#                         address_threshold=70)
# dup_df = dupes[dupes["dup_group"].notnull()]
# dup_df.to_csv("customer_duplicate_records_optimized.csv", index=False)
