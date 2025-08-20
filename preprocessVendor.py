import os
import pandas as pd
from tqdm import tqdm
tqdm.pandas()

map_lfa1 = {
    "LIFNR": "Supplier",
    "NAME1": "Name 1",
    "NAME2": "Name 2",
    "NAME3": "Name 3",
    "NAME4": "Name 4",
    "STRAS": "Street",
    "ORT01": "City",
    "LAND1": "Country",
    "PFACH": "PO Box",
    "PSTL2": "P.O. Box Postal Code",
    "PSTLZ": "Postal Code",
    "TELF1": "Telephone 1",
    "TELF2": "Telephone 2",
    "SPRAS": "Language Key",
    "ADRNR": "Address",
    "WERKS": "Plant", 
    "TXJCD": "Tax Jurisdiction",
    "KTOKK": "Account Group",
    "STCD3": "Tax Number 3",
    "ERDAT": "Created on",
    "ERNAM": "Created by",
    "SPERQ": "Block function",
    "SPERZ": "Payment block",
    "NODEL": "Central del.block",
    "SPERR": "Central posting block",
    "SPERM": "Central purchasing block"
}

map_lfb1 = {
    "LIFNR": "Supplier",
    "BUKRS": "Company Code",
    "ZTERM": "Terms of Payment",
    "AKONT": "Reconciliation acct",
    "SPERR": "Posting block for company code",
    "LOEVM": "Deletion Flag for Company Code",
    "FDGRV": "Planning group",
    "TOGRU": "Tolerance group",
    "ZWELS": "Payment methods",
    "ERDAT": "Created on",
    "ERNAM": "Created by",
}

map_lfm1 = {
    "LIFNR": "Supplier",
    "SPERM": "Purch. block for purchasing organization",
    "EKORG": "Purch. Organization",
    "EKGRP": "Purchasing Group",
    "ZTERM": "Terms of Payment",
    "WAERS": "Order currency",
    "BSTAE": "Confirmation Control",
    "INCO1": "Incoterms",
    "INCO2": "Incoterms (Part 2)",
    "ZZMSME_STAT": "MSME Status",              # ⚠️ Likely custom
    "ZZMSME_NUM": "MSME Number",              # ⚠️ Likely custom
    "ZZMSME_DAT": "MSME Issue Date",          # ⚠️ Likely custom
    "ZZABAC_ST": "ABAC Status",         # ⚠️ Custom Z-field assumed
    "ZZREASON": "ABAC Reason",         # ⚠️ Custom Z-field assumed
    "WEBRE": "GR-Based Inv. Verif.",
    "LEBRE": "Service-Based Invoice Verification",
    "LOEVM": "Delete flag for purchasing organization"
}

map_lfbk = {
    "LIFNR": "Supplier",
    "KOINH": "Account holder",
    "BANKS": "Bank Country",
    "BANKL": "Bank Key",
    "BANKN": "Bank Account"
}

map_adrc = {
    "ADDRNUMBER": "Address Number",
    "STREET": "Street",
    "STR_SUPPL1": "Street 2",
    "STR_SUPPL2": "Street 3",
    "STR_SUPPL3": "Street 4",
    "LOCATION": "Street 5",               # Or could be used for locality
    "POST_CODE1": "Postal Code",
    "POST_CODE2": "PO Box Postal Code",
    "PO_BOX": "PO Box",
    "COUNTRY": "Country"
}

map_adr6 = {
    "ADDRNUMBER": "Address Number",           # ⚠️ Not directly in ADR6; link via ADRNR in LFA1/ADRC
    "SMTP_ADDR": "E-Mail Address"
}

map_j1imovend = {
    "LIFNR": "Supplier",
    "J_1IPANNO": "Permanent account number"
}

def checkInactive(table, row, inactiveList : list, visited : set, *cols):
    res = False
    for col in cols:
        if pd.isnull(row[col]) or str(row[col]).strip() == '' or str(row[col]).lower() == 'nan':
            pass
        else:
            res = True
            break
    # return not res
    if res:
        val = row['Supplier']
        if val in visited:
            pass
        else:
            inactiveList.append(val)
            visited.add(val)

def classifyInactive(table, row, inactive: list):
    return row['Supplier'] in inactive

def preprocessVendorData(vendorMaster):
    
    lfa1 = pd.read_excel(vendorMaster, sheet_name='LFA1', dtype=str).rename(columns=map_lfa1)
    lfb1 = pd.read_excel(vendorMaster, sheet_name='LFB1', dtype=str).rename(columns=map_lfb1)
    lfm1 = pd.read_excel(vendorMaster, sheet_name='LFM1', dtype=str).rename(columns=map_lfm1)
    lfbk = pd.read_excel(vendorMaster, sheet_name='LFBK', dtype=str).rename(columns=map_lfbk)
    adrc = pd.read_excel(vendorMaster, sheet_name='ADRC', dtype=str).rename(columns=map_adrc)
    j_1imovend = pd.read_excel(vendorMaster, sheet_name='J_1IMOVEND', dtype=str).rename(columns=map_j1imovend)
    adr6 = pd.read_excel(vendorMaster, sheet_name='V_ADR6', dtype=str).rename(columns=map_adr6)
    
    # print(adrc)
    # try:
    #     j1imovend = pd.read_excel(vendorMaster, sheet_name='J1IMOVEND')
    # except:
    #     pass
    
    adrc_required = adrc[['Address Number', 'Postal Code', 'Street', 'Street 2', 'Street 3', 'Street 4', 'Street 5', 
                          'Postal Code', 'PO Box Postal Code', 'PO Box']]
    # right = lfa1[['Supplier', 'Address', 'Last PO Date', 'Last BFN Date', 'Invoice Open?', 
    #               'Last Invoice Posting Date', 'Country']]
    right = lfa1[['Supplier', 'Address', 'Country']]
    adrc = pd.merge(adrc_required, right, how='left', left_on='Address Number', right_on='Address')
    
    adr6_required = adr6[['Address Number', 'E-Mail Address']]
    # right = lfa1[['Supplier', 'Address', 'Last PO Date', 'Last BFN Date', 'Invoice Open?', 
    #               'Last Invoice Posting Date', 'Country']]
    right = lfa1[['Supplier', 'Address', 'Country']]
    adr6 = pd.merge(adr6_required, right, how='left', left_on='Address Number', right_on='Address')
    
    # try:
    #     lfa1 = pd.merge(lfa1,j1imovend,'left','Supplier')
    # except:
    #     pass 
    
    city = lfa1[['Supplier', 'City', 'Country']]
    lfm1 = pd.merge(lfm1, city, 'left', 'Supplier')
    
    isMSME = lfm1[['Supplier', 'MSME Status']]
    country = lfa1[['Supplier', 'Country']]
    lfb1 = pd.merge(lfb1, isMSME, 'left', 'Supplier')
    lfb1 = pd.merge(lfb1, country, 'left', 'Supplier')
    # print(lfb1.columns)
    
    inactiveVendors = []
    visited = set()
    lfb1.progress_apply(lambda row: checkInactive(lfb1, row, inactiveVendors, visited,
                                                'Posting block for company code', 
                                                'Deletion Flag for Company Code'), axis=1)
    
    lfm1.progress_apply(lambda row: checkInactive(lfm1, row, inactiveVendors, visited,
                                                'Purch. block for purchasing organization', 
                                                'Delete flag for purchasing organization'), axis=1)
    
    lfa1.progress_apply(lambda row: checkInactive(lfm1, row, inactiveVendors, visited,
                                                'Block function', 'Payment block', 'Central del.block',
                                                'Central posting block', 'Central purchasing block'), axis=1)
    lfa1['Inactive'] = lfa1.progress_apply(lambda row: classifyInactive(lfa1, row, inactiveVendors), axis=1)
    lfb1['Inactive'] = lfb1.progress_apply(lambda row: classifyInactive(lfb1, row, inactiveVendors), axis=1)
    lfm1['Inactive'] = lfm1.progress_apply(lambda row: classifyInactive(lfm1, row, inactiveVendors), axis=1)
    lfbk['Inactive'] = lfbk.progress_apply(lambda row: classifyInactive(lfbk, row, inactiveVendors), axis=1)
    adrc['Inactive'] = adrc.progress_apply(lambda row: classifyInactive(adrc, row, inactiveVendors), axis=1)
    adr6['Inactive'] = adr6.progress_apply(lambda row: classifyInactive(adr6, row, inactiveVendors), axis=1)
    j_1imovend['Inactive'] = j_1imovend.progress_apply(lambda row: classifyInactive(j_1imovend, row, inactiveVendors), axis=1)

    # Comment [line 52 - 60] for Inctive Vendor output
    lfa1_active = lfa1[lfa1['Inactive']==False]
    lfb1_active = lfb1[lfb1['Inactive']==False]
    lfm1_active = lfm1[lfm1['Inactive']==False]
    lfbk_active = lfbk[lfbk['Inactive']==False]
    adrc_active = adrc[adrc['Inactive']==False]
    adr6_active = adr6[adr6['Inactive']==False]
    j_1imovend_active = j_1imovend[j_1imovend['Inactive']==False]
    
    output_dir = "/".join(vendorMaster.split('/')[:-1])
    output_path = os.path.join(output_dir, 'activeVendorMaster.xlsx')
    tables = [lfa1_active, lfb1_active, lfm1_active, lfbk_active, adrc_active, adr6_active, j_1imovend_active]
    sheets = ['LFA1', 'LFB1', 'LFM1', 'LFBK', 'ADRC', 'V_ADR6', 'J_1IMOVEND']
    
    # Comment [line 64 - 72] for Active Vendor output
    # lfa1_inactive = lfa1[lfa1['Inactive']==True]
    # lfb1_inactive = lfb1[lfb1['Inactive']==True]
    # lfm1_inactive = lfm1[lfm1['Inactive']==True]
    # lfbk_inactive = lfbk[lfbk['Inactive']==True]
    # adrc_inactive = adrc[adrc['Inactive']==True]
    
    # output_dir = "/".join(vendorMaster.split('/')[:-1])
    # output_path = os.path.join(output_dir, 'inactiveVendorMaster.xlsx')
    # tables = [lfa1_inactive, lfb1_inactive, lfm1_inactive, lfbk_inactive, adrc_inactive]
    # sheets = ['LFA1', 'LFB1', 'LFM1', 'LFBK', 'ADRC']
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for idx, table in enumerate(tables):
            table.to_excel(writer, sheet_name=sheets[idx], index=False)
            
    return output_path
    
    


# print(len(set(load_vendor_data('Vendor/LFA1_Syngene.xlsx')[0])))
# print()
# print(len(load_vendor_data('../Vendor/LFA1_Syngene.xlsx')[0]))
# print(len(load_vendor_data('../Vendor/LFA1_Syngene.xlsx')[1]))
# print(len(load_vendor_data('../Vendor/LFA1_Syngene.xlsx')[2]))
# print(len(load_vendor_data('../Vendor/LFA1_Syngene.xlsx')[3]))
 
# print(preprocessVendorData())