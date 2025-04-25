#!/usr/bin/env python3
"""
find_sf_duplicates_export.py

Scan a customer master CSV for duplicates (GST, PAN, AccountGroup exact;
Name & Address fuzzy), tag them by group, and export duplicate rows to CSV.
"""

import pandas as pd
from rapidfuzz import fuzz

# Thresholds for fuzzy matching (0–100)
NAME_THRESHOLD = 80
ADDR_THRESHOLD = 80
GST = 'GST_Number__c'
PAN = 'PAN_Number__c'
AccountGroup = 'KTOKD__c'
Name = 'Name'
Address = 'add_dupe'

def is_potential_duplicate(r1, r2,
                           name_thresh=NAME_THRESHOLD,
                           addr_thresh=ADDR_THRESHOLD):
    def exact_or_empty(a, b):
        return pd.isna(a) or pd.isna(b) or (a == b)
    
    gst_ok = exact_or_empty(r1[GST], r2[GST])
    pan_ok = exact_or_empty(r1[PAN], r2[PAN])
    grp_ok = exact_or_empty(r1[AccountGroup], r2[AccountGroup])
    
    name_score = fuzz.token_sort_ratio(str(r1[Name]), str(r2[Name]))
    addr_score = fuzz.token_sort_ratio(str(r1[Address]), str(r2[Address]))
    name_ok = pd.isna(r1[Name]) or pd.isna(r2[Name]) or (name_score >= name_thresh)
    addr_ok = pd.isna(r1[Address]) or pd.isna(r2[Address]) or (addr_score >= addr_thresh)
    
    return gst_ok and pan_ok and grp_ok and name_ok and addr_ok

def find_duplicates(df: pd.DataFrame):
    df = df.reset_index(drop=True)
    n = len(df)
    visited = set()
    dup_groups = []
    
    for i in range(n):
        if i in visited:
            continue
        group = [i]
        for j in range(i+1, n):
            if j in visited:
                continue
            if is_potential_duplicate(df.loc[i], df.loc[j]):
                group.append(j)
                visited.add(j)
        if len(group) > 1:
            dup_groups.append(group)
    
    return dup_groups

def main():
    
    df = pd.read_excel("../Customer/CustomerMaster.xlsx", sheet_name='ACCOUNT')
    
    # 1. Find duplicate groups
    groups = find_duplicates(df)
    
    if not groups:
        print("🎉 No duplicates found!")
        return
    
    # 2. Tag each duplicate row with its group ID
    df['dup_group'] = pd.NA
    for idx, grp in enumerate(groups, start=1):
        for row in grp:
            df.at[row, 'dup_group'] = f"Group {idx}"
    
    # 3. Export only the duplicates
    dup_df = df[df['dup_group'].notna()]
    dup_df.to_csv("duplicate_records.csv", index=False)
    print(f"✅ Exported {len(dup_df)} duplicate rows across {len(groups)} groups to duplicate_records.csv")

if __name__ == "__main__":
    main()
