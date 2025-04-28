import os
import pandas as pd
from tqdm import tqdm
tqdm.pandas()

def checkActive(table, row, activeList : list, visited : set, *cols):
    res = False
    for col in cols:
        if not (pd.isnull(row[col]) or str(row[col]).strip() == '' or str(row[col]).lower() == 'nan'):
            res = res or row[col]

    # if res:
    #     if 'SAP_Account_Number__c' in row.index.to_list():
    #         val = row['SAP_Account_Number__c']
    #     else:
    #         val = row['Customer']
            
    #     if val in visited:
    #         pass
    #     else:
    #         activeList.append(val)
    #         visited.add(val)
    return res

# def classifyActive(table, row, active: list):
#     if 'SAP_Account_Number__c' in row.index.to_list():
#         return row['SAP_Account_Number__c'] in active
#     else: 
#         return row['Customer'] in active

def preprocessCustomerData(customerMaster):
    
    kna1 = pd.read_excel(customerMaster, sheet_name='KNA1')
    knb1 = pd.read_excel(customerMaster, sheet_name='KNB1')
    knkk = pd.read_excel(customerMaster, sheet_name='KNKK')
    knvv = pd.read_excel(customerMaster, sheet_name='KNVV')
    knvk = pd.read_excel(customerMaster, sheet_name='KNVK')
    knb5 = pd.read_excel(customerMaster, sheet_name='KNB5')
    adr6 = pd.read_excel(customerMaster, sheet_name='ADR6')
    account = pd.read_excel(customerMaster, sheet_name='ACCOUNT')
    contact = pd.read_excel(customerMaster, sheet_name='CONTACT')
    
    activeCustomers = []
    visited = set()
    
    kna1['IsActive'] = kna1.progress_apply(lambda row: checkActive(kna1, row, activeCustomers, visited,
                                                'Open Pipeline', 'All Time Customer', 'Open Project?',
                                                'Open Sales Order?', 'Open Invoices'), axis=1)
    account['IsActive'] = account.progress_apply(lambda row: checkActive(kna1, row, activeCustomers, visited,
                                                   'Open Pipeline', 'All Time Customer', 'Open Project?',
                                                   'Open Sales Order?', 'Open Invoices'), axis=1)
    knb1['IsActive'] = knb1.progress_apply(lambda row: checkActive(kna1, row, activeCustomers, visited,
                                                   'Open Pipeline', 'All Time Customer', 'Open Project?',
                                                   'Open Sales Order?', 'Open Invoices'), axis=1)
    knkk['IsActive'] = knkk.progress_apply(lambda row: checkActive(kna1, row, activeCustomers, visited,
                                                   'Open Pipeline', 'All Time Customer', 'Open Project?',
                                                   'Open Sales Order?', 'Open Invoices'), axis=1)
    knvv['IsActive'] = knvv.progress_apply(lambda row: checkActive(kna1, row, activeCustomers, visited,
                                                   'Open Pipeline', 'All Time Customer', 'Open Project?',
                                                   'Open Sales Order?', 'Open Invoices'), axis=1)
    knvk['IsActive'] = knvk.progress_apply(lambda row: checkActive(kna1, row, activeCustomers, visited,
                                                   'Open Pipeline', 'All Time Customer', 'Open Project?',
                                                   'Open Sales Order?', 'Open Invoices'), axis=1)
    knb5['IsActive'] = knb5.progress_apply(lambda row: checkActive(kna1, row, activeCustomers, visited,
                                                   'Open Pipeline', 'All Time Customer', 'Open Project?',
                                                   'Open Sales Order?', 'Open Invoices'), axis=1)
    adr6['IsActive'] = adr6.progress_apply(lambda row: checkActive(kna1, row, activeCustomers, visited,
                                                   'Open Pipeline', 'All Time Customer', 'Open Project?',
                                                   'Open Sales Order?', 'Open Invoices'), axis=1)
    contact['IsActive'] = contact.progress_apply(lambda row: checkActive(kna1, row, activeCustomers, visited,
                                                   'Open Pipeline', 'All Time Customer', 'Open Project?',
                                                   'Open Sales Order?', 'Open Invoices'), axis=1)
    
    # kna1['IsActive'] = kna1.progress_apply(lambda row: classifyActive(kna1, row, activeCustomers), axis=1)
    # knb1['IsActive'] = knb1.progress_apply(lambda row: classifyActive(knb1, row, activeCustomers), axis=1)
    # knvv['IsActive'] = knvv.progress_apply(lambda row: classifyActive(knvv, row, activeCustomers), axis=1)
    # knvk['IsActive'] = knvk.progress_apply(lambda row: classifyActive(knvk, row, activeCustomers), axis=1)
    # knkk['IsActive'] = knkk.progress_apply(lambda row: classifyActive(knkk, row, activeCustomers), axis=1)
    # knb5['IsActive'] = knb5.progress_apply(lambda row: classifyActive(knb5, row, activeCustomers), axis=1)
    # adr6['IsActive'] = adr6.progress_apply(lambda row: classifyActive(adr6, row, activeCustomers), axis=1)
    # account['IsActive'] = account.progress_apply(lambda row: classifyActive(account, row, activeCustomers), axis=1)
    # contact['IsActive'] = contact.progress_apply(lambda row: classifyActive(contact, row, activeCustomers), axis=1)

    # Comment [line 62 - 76] for Active Customer output
    kna1_active = kna1[kna1['IsActive']==True]
    knb1_active = knb1[knb1['IsActive']==True]
    knkk_active = knkk[knkk['IsActive']==True]
    knvv_active = knvv[knvv['IsActive']==True]
    knvk_active = knvk[knvk['IsActive']==True]
    knb5_active = knb5[knb5['IsActive']==True]
    adr6_active = adr6[adr6['IsActive']==True]
    account_active = account[account['IsActive']==True]
    contact_active = contact[contact['IsActive']==True]
    
    output_dir = "/".join(customerMaster.split('/')[:-1])
    output_path = os.path.join(output_dir, 'activeCustomerMaster.xlsx')
    tables = [kna1_active, knb1_active, knvv_active, knkk_active, knvk_active, knb5_active, adr6_active, 
              account_active, contact_active]
    sheets = ["KNA1", 'KNB1', "KNVV", 'KNKK', 'KNVK', 'KNB5', 'ADR6', 'ACCOUNT', 'CONTACT']
    
    # Comment [line 79 - 93] for Inactive Customer output
    # kna1_inactive = kna1[kna1['IsActive']==False]
    # knb1_inactive = knb1[knb1['IsActive']==False]
    # knkk_inactive = knkk[knkk['IsActive']==False]
    # knvv_inactive = knvv[knvv['IsActive']==False]
    # knvk_inactive = knvk[knvk['IsActive']==False]
    # knb5_inactive = knb5[knb5['IsActive']==False]
    # adr6_inactive = adr6[adr6['IsActive']==False]
    # account_inactive = account[account['IsActive']==False]
    # contact_inactive = contact[contact['IsActive']==False]
    
    # output_dir = "/".join(customerMaster.split('/')[:-1])
    # output_path = os.path.join(output_dir, 'activeCustomerMaster.xlsx')
    # tables = [kna1_inactive, knb1_inactive, knvv_inactive, knkk_inactive, knvk_inactive, knb5_inactive, adr6_inactive, 
    #           account_inactive, contact_inactive]
    # sheets = ["KNA1", 'KNB1', "KNVV", 'KNKK', 'KNVK', 'KNB5', 'ADR6', 'ACCOUNT', 'CONTACT']
 
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for idx, table in enumerate(tables):
            table.to_excel(writer, sheet_name=sheets[idx], index=False)
            
    return output_path