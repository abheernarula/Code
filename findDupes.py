import pandas as pd
from rapidfuzz import fuzz
import argparse

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


parser = argparse.ArgumentParser(
    description="Find duplicates"
)

parser.add_argument("--data", required=True, help="Path to excel data")
parser.add_argument("--output", default="dupes.xlsx", help="Path for output file")
parser.add_argument('--name', required=True, help='FUZZY - Column name for "Name"')
parser.add_argument('--address', required=True, help="FUZZY - Column name for 'Address'")
parser.add_argument('--field1', required=True, help='EXACT - Column name for tax 1')
parser.add_argument('--field2', required=True, help="EXACT - Column name for tax 2")
parser.add_argument('--name_th', required=True, help="Threshold for fuzzy - Name")
parser.add_argument('--address_th', required=True, help="Threshold for fuzzy - Address")
args = parser.parse_args()

input_path = args.data
output_path = args.output
name = args.name
address = args.address
tax1 = args.field1
tax2 = args.field2
th_name = int(args.name_th)
th_address = int(args.address_th)

df = pd.read_excel(input_path)

dupes = find_duplicates(df,name,address,tax1,tax2,th_name,th_address)
dup_df = dupes[dupes["dup_group"].notnull()]
dup_df.to_csv("duplicate_records.csv", index=False)


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
