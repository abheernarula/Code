#!/usr/bin/env python3
"""
fast_find_duplicates.py

– Block on AccountGroup (you can add GST or PAN blocks too)
– Within each block, batch‐compute name & address scores
– Only compare pairs that pass exact_or_empty(GST, PAN, AccountGroup)
"""

import pandas as pd
from rapidfuzz import fuzz
from rapidfuzz.process import cdist

# thresholds
NAME_THRESH = 55
ADDR_THRESH = 55
GST = 'GST_Number__c'
PAN = 'PAN_Number__c'
AccountGroup = 'KTOKD__c'

def exact_or_empty(a, b):
    print(a," -> ", b)
    print(pd.isna(a) or pd.isna(b) or (str(a).strip() == str(b).strip()) or str(a).lower().strip() == 'nan' or str(a).strip() == '')
    return pd.isna(a) or pd.isna(b) or (str(a).strip() == str(b).strip()) or str(a).lower().strip() == 'nan' or str(a).strip() == ''

def find_duplicates(df):
    df = df.reset_index(drop=True)
    dup_groups = []
    visited = set()

    # 1) BLOCK on AccountGroup
    for _, block in df.groupby('KTOKD__c', dropna=False):
        idxs = block.index.to_list()
        if len(idxs) < 2:
            continue

        # 2) BATCH fuzzy
        names = block['Name'].fillna('').astype(str).to_list()
        adds  = block['add_dupe'].fillna('').astype(str).to_list()

        # shape = (M, M)
        name_scores = cdist(names, names, scorer=fuzz.token_sort_ratio)
        addr_scores = cdist(adds,  adds,  scorer=fuzz.token_sort_ratio)

        # 3) only check i<j and exact fields
        for i, id1 in enumerate(idxs):
            print(f'\nWorking... - {i}')
            if id1 in visited: 
                continue
            group = [id1]

            for j, id2 in enumerate(idxs[i+1:], start=i+1):
                if id2 in visited:
                    continue

                # quick fuzzy filter
                if name_scores[i, j] < NAME_THRESH or addr_scores[i, j] < ADDR_THRESH:
                    continue

                r1, r2 = df.loc[id1], df.loc[id2]
                if (exact_or_empty(r1[GST], r2[GST]) or exact_or_empty(r1[PAN], r2[PAN])):
                    group.append(id2)
                    visited.add(id2)

            if len(group) > 1:
                dup_groups.append(group)

    return dup_groups

def main():
    df = pd.read_excel('../Customer/CustomerMaster.xlsx', sheet_name='ACCOUNT')
    df = df[df[ 'Name', 'GST_Number__c', 'PAN_Number__c', 'BillingStreet', 'BillingAddress.street',
                'BillingStateCode', 'BillingPostalCode', 'SAP_Account_Number__c', 'BillingCountryCode', 'BillingAddress.countryCode', 'BillingCity', 'KTOKD__c',
                'Customer_Type__c', 'SAP_Customer_Creation_Date__c', 'CreatedDate', 'CreatedById','ZTERM__c',
                'AKONT__c', 'MAHNA__c', 'Total_Credit_Limit__c', 'Credit_Limit__c', 'VSBED__c', 
                'Sales_Organization__c','INCO1__c', 'INCO2__c', 'SPART__c', 'VTWEG__c', 'KALKS__c', 'KTGRD__c', 
                'CurrencyIsoCode', 'Account_Currency__c','Company_Size__c', 'Business_Unit__c', 'Portfolio__c', 
                'Customer_Category__c']]
    # df = pd.read_csv("customer_dump.csv", dtype=str)
    groups = find_duplicates(df)

    if not groups:
        print("No duplicates found.")
        return

    # tag & export
    df['dup_group'] = pd.NA
    for gid, grp in enumerate(groups, start=1):
        for idx in grp:
            df.at[idx, 'dup_group'] = f"{gid}"

    df[df.dup_group.notna()] \
      .to_csv("duplicates_blocked.csv", index=False)
    print(f"Exported {df.dup_group.notna().sum()} rows into duplicates_blocked.csv")

if __name__ == "__main__":
    main()
