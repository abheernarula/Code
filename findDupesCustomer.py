import pandas as pd
from rapidfuzz import fuzz

def find_duplicates(df, 
                    name_col="Name", 
                    address_col="Address", 
                    gst_col="GST number", 
                    vat_col="VAT number",
                    name_threshold=80, 
                    address_threshold=80):
    df_result = df.copy()
    df_result["dup_group"] = None
    group_id = 1

    non_null_mask = df_result[gst_col].notnull() & df_result[vat_col].notnull()
    non_null_df = df_result[non_null_mask]
    grouped = non_null_df.groupby([gst_col, vat_col])
    
    for group_key, group_df in grouped:
        print(f'Done - {group_key}')
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
                name_sim = fuzz.ratio(str(df_result.loc[i, name_col]), str(df_result.loc[j, name_col]))
                addr_sim = fuzz.ratio(str(df_result.loc[i, address_col]), str(df_result.loc[j, address_col]))
                if name_sim >= name_threshold and addr_sim >= address_threshold:
                    current_group.append(j)
                    visited.add(j)
            if len(current_group) > 1:
                for idx in current_group:
                    df_result.at[idx, "dup_group"] = group_id
                group_id += 1

    null_mask = df_result[gst_col].isnull() & df_result[vat_col].isnull()
    null_df = df_result[null_mask]
    indices = null_df.index.tolist()
    visited = set()
    for i in indices:
        if i in visited:
            continue
        current_group = [i]
        visited.add(i)
        for j in indices:
            print(f'done -> {i}, {j}')
            if j in visited or i == j:
                continue
            name_sim = fuzz.ratio(str(df_result.loc[i, name_col]), str(df_result.loc[j, name_col]))
            addr_sim = fuzz.ratio(str(df_result.loc[i, address_col]), str(df_result.loc[j, address_col]))
            if name_sim >= name_threshold and addr_sim >= address_threshold:
                current_group.append(j)
                visited.add(j)
        if len(current_group) > 1:
            for idx in current_group:
                df_result.at[idx, "dup_group"] = group_id
            group_id += 1

    return df_result

# df = pd.read_csv('../../.csv', low_memory=False)
df = pd.read_excel('../Customer/CustomerMaster.xlsx', sheet_name='ACCOUNT')

print('Start')

dupes = find_duplicates(df,'Name', 'add_dupe', 'GST_Number__c', 'PAN_Number__c',70,70)
dup_df = dupes[dupes["dup_group"].notnull()]
dup_df.to_csv("customer_duplicate_records_noAccGrp.csv", index=False)


# ----------------------------------------------------------------------------
# USAGE EXAMPLE:
#
# df_duplicates = find_duplicates(df, 
#                                 name_col="Name", 
#                                 address_col="Address", 
#                                 gst_col="GST number", 
#                                 vat_col="VAT number",
#                                 name_threshold=80, 
#                                 address_threshold=80)
#
# Rows with a non-null "dup_group" indicate duplicate groups.
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# USAGE EXAMPLE:
#
# Suppose you have a DataFrame 'df' with columns "Name", "Address",
# "GST number" and "VAT number". To identify duplicates, call:
#
# df_duplicates = find_duplicates(df, 
#                                 name_col="Name", 
#                                 address_col="Address", 
#                                 gst_col="GST number", 
#                                 vat_col="VAT number",
#                                 name_threshold=80, 
#                                 address_threshold=80)
#
# Then, rows with a non-null "dup_group" are flagged as duplicates.
# You can filter and review them:
#
# dup_df = df_duplicates[df_duplicates["dup_group"].notnull()]
# dup_df.to_csv("duplicate_records.csv", index=False)
# ----------------------------------------------------------------------------
